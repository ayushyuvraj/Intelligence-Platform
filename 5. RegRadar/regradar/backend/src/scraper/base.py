"""
Base Scraper Class

Abstract base class for all regulatory body scrapers.
Provides common functionality:
- Retry logic with exponential backoff
- Rate limiting between requests
- Error handling and classification
- Logging and telemetry
"""

import asyncio
import aiohttp
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from src.utils.logger import get_logger
from src.utils.errors import ScraperException
from typing import List, Optional, Dict, Any

logger = get_logger(__name__)


class ScrapedRegulation:
    """Data class for scraped regulation data."""

    def __init__(
        self,
        source_body: str,
        source_url: str,
        original_title: str,
        original_date: datetime,
        full_text: Optional[str] = None,
        content_hash: Optional[str] = None,
    ):
        self.source_body = source_body
        self.source_url = source_url
        self.original_title = original_title
        self.original_date = original_date
        self.full_text = full_text
        self.content_hash = content_hash


class BaseScraper(ABC):
    """
    Abstract base class for all regulatory body scrapers.

    Subclasses must implement the `fetch()` method.
    """

    def __init__(
        self,
        source_body: str,
        base_url: str,
        timeout_seconds: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize base scraper.

        Args:
            source_body: Name of regulatory body (SEBI, RBI, etc.)
            base_url: Base URL for scraper requests
            timeout_seconds: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.source_body = source_body
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.last_request_time = 0
        self.min_request_delay = 2  # Minimum 2 seconds between requests

    async def fetch(self) -> List[ScrapedRegulation]:
        """
        Fetch regulations from the source.

        Must be implemented by subclasses.

        Returns:
            List of ScrapedRegulation objects
        """
        raise NotImplementedError("Subclasses must implement fetch()")

    async def _request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """
        Make HTTP request with retry logic and rate limiting.

        Args:
            url: URL to request
            method: HTTP method (GET, POST)
            headers: Optional request headers
            timeout: Optional timeout override

        Returns:
            Response text

        Raises:
            ScraperException: If request fails after retries
        """
        # Rate limiting
        await self._rate_limit()

        timeout_val = timeout or self.timeout_seconds
        headers = headers or {"User-Agent": self._get_user_agent()}

        for attempt in range(self.max_retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method,
                        url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=timeout_val),
                    ) as response:
                        # Check for errors
                        if response.status == 429:  # Rate limit
                            wait_time = int(
                                response.headers.get("Retry-After", 60)
                            )
                            logger.warning(
                                f"Rate limited by {url}, waiting {wait_time}s",
                                extra={
                                    "status": 429,
                                    "retry_after": wait_time,
                                    "source": self.source_body,
                                },
                            )
                            if attempt < self.max_retries:
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                raise ScraperException(
                                    f"Rate limited after {self.max_retries} retries",
                                    self.source_body,
                                    "rate_limit",
                                )

                        if response.status >= 500:  # Server error (transient)
                            logger.warning(
                                f"Server error {response.status} from {url}",
                                extra={
                                    "status": response.status,
                                    "source": self.source_body,
                                    "attempt": attempt + 1,
                                },
                            )
                            if attempt < self.max_retries:
                                await asyncio.sleep(self._backoff_delay(attempt))
                                continue
                            else:
                                raise ScraperException(
                                    f"Server error {response.status}",
                                    self.source_body,
                                    "server_error",
                                )

                        if response.status >= 400:  # Client error (permanent)
                            raise ScraperException(
                                f"HTTP {response.status}",
                                self.source_body,
                                "http_error",
                            )

                        text = await response.text()
                        logger.debug(
                            f"Successfully fetched {url}",
                            extra={
                                "source": self.source_body,
                                "size_bytes": len(text),
                            },
                        )
                        return text

            except asyncio.TimeoutError:
                logger.warning(
                    f"Timeout fetching {url}",
                    extra={
                        "source": self.source_body,
                        "attempt": attempt + 1,
                        "timeout": timeout_val,
                    },
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(self._backoff_delay(attempt))
                    continue
                else:
                    raise ScraperException(
                        f"Timeout after {self.max_retries} retries",
                        self.source_body,
                        "timeout",
                    )

            except aiohttp.ClientConnectorError as e:
                logger.warning(
                    f"Connection error fetching {url}: {str(e)}",
                    extra={
                        "source": self.source_body,
                        "attempt": attempt + 1,
                    },
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(self._backoff_delay(attempt))
                    continue
                else:
                    raise ScraperException(
                        "Connection failed",
                        self.source_body,
                        "network_error",
                    )

            except aiohttp.ClientSSLError as e:
                logger.warning(
                    f"SSL error fetching {url}",
                    extra={
                        "source": self.source_body,
                        "attempt": attempt + 1,
                    },
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(self._backoff_delay(attempt))
                    continue
                else:
                    raise ScraperException(
                        "SSL certificate error",
                        self.source_body,
                        "ssl_error",
                    )

        raise ScraperException(
            f"Failed to fetch {url} after {self.max_retries} retries",
            self.source_body,
            "max_retries_exceeded",
        )

    async def _rate_limit(self):
        """
        Enforce rate limiting (minimum delay between requests).

        Ensures at least min_request_delay seconds between consecutive requests.
        """
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_delay:
            wait_time = self.min_request_delay - elapsed
            await asyncio.sleep(wait_time)
        self.last_request_time = time.time()

    @staticmethod
    def _backoff_delay(attempt: int) -> float:
        """
        Calculate exponential backoff delay.

        Progression: 1s, 2s, 4s, 8s...

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        return min(2 ** attempt, 30)  # Cap at 30 seconds

    @staticmethod
    def _get_user_agent() -> str:
        """Get user agent string for requests."""
        return "RegRadar/1.0 (+https://regradar.io; +https://regradar.io/about)"

    def _log_scrape_result(
        self,
        regulations_found: int,
        processing_time_ms: float,
        errors: Optional[List[str]] = None,
    ):
        """
        Log scraping results.

        Args:
            regulations_found: Number of regulations found
            processing_time_ms: Processing time in milliseconds
            errors: Any errors encountered
        """
        logger.info(
            f"Scraping completed for {self.source_body}",
            extra={
                "source_body": self.source_body,
                "regulations_found": regulations_found,
                "processing_time_ms": int(processing_time_ms),
                "errors": len(errors) if errors else 0,
            },
        )
