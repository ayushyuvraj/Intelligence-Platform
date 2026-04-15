"""
SEBI Scraper

Scrapes regulatory updates from SEBI (Securities and Exchange Board of India).
Fetches RSS feed and extracts individual notifications/circulars.
"""

import feedparser
import hashlib
import asyncio
from datetime import datetime
from typing import List
from email.utils import parsedate_to_datetime

from src.scraper.base import BaseScraper, ScrapedRegulation
from src.utils.logger import get_logger
from src.utils.errors import ScraperException

logger = get_logger(__name__)


class SEBIScraper(BaseScraper):
    """Scraper for SEBI regulatory updates."""

    # SEBI RSS feeds - multiple feeds for different document types
    SEBI_FEEDS = [
        "https://www.sebi.gov.in/rss/rss_notifications.xml",  # Notifications
        "https://www.sebi.gov.in/rss/rss_circulars.xml",  # Circulars
    ]

    def __init__(self):
        """Initialize SEBI scraper."""
        super().__init__(
            source_body="SEBI",
            base_url="https://www.sebi.gov.in",
            timeout_seconds=30,
            max_retries=2,
        )

    async def fetch(self) -> List[ScrapedRegulation]:
        """
        Fetch latest SEBI regulations from RSS feeds.

        Returns:
            List of ScrapedRegulation objects
        """
        start_time = datetime.utcnow()
        all_regulations = []
        errors = []

        logger.info("Starting SEBI scraper")

        for feed_url in self.SEBI_FEEDS:
            try:
                logger.debug(f"Fetching SEBI feed: {feed_url}")
                feed_content = await self._request(feed_url)
                regulations = self._parse_rss_feed(feed_content)
                all_regulations.extend(regulations)
                logger.info(
                    f"Fetched {len(regulations)} from {feed_url}",
                    extra={
                        "feed_url": feed_url,
                        "count": len(regulations),
                    },
                )
            except ScraperException as e:
                logger.warning(
                    f"Failed to fetch SEBI feed {feed_url}",
                    extra={
                        "error": str(e),
                        "feed_url": feed_url,
                    },
                )
                errors.append(str(e))
            except Exception as e:
                logger.error(
                    f"Unexpected error fetching SEBI feed {feed_url}: {str(e)}",
                    extra={
                        "error": str(e),
                        "feed_url": feed_url,
                    },
                )
                errors.append(f"Unexpected: {str(e)}")

        processing_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._log_scrape_result(len(all_regulations), processing_time_ms, errors)

        logger.info(
            f"SEBI scraper completed: {len(all_regulations)} regulations found",
            extra={
                "total": len(all_regulations),
                "errors": len(errors),
                "time_ms": int(processing_time_ms),
            },
        )

        return all_regulations

    def _parse_rss_feed(self, feed_content: str) -> List[ScrapedRegulation]:
        """
        Parse RSS feed and extract regulations.

        Args:
            feed_content: Raw RSS feed content

        Returns:
            List of ScrapedRegulation objects
        """
        regulations = []

        try:
            feed = feedparser.parse(feed_content)

            if feed.bozo:
                logger.warning(
                    f"RSS feed parsing error: {feed.bozo_exception}",
                    extra={
                        "error": str(feed.bozo_exception),
                    },
                )

            for entry in feed.entries:
                try:
                    # Extract fields from RSS entry
                    title = entry.get("title", "").strip()
                    link = entry.get("link", "").strip()
                    pub_date_str = entry.get("published", "")
                    description = entry.get("summary", "").strip()

                    # Skip if missing critical fields
                    if not title or not link:
                        logger.warning(
                            "Skipping SEBI entry: missing title or link",
                            extra={
                                "title": title[:50] if title else "",
                                "has_link": bool(link),
                            },
                        )
                        continue

                    # Parse publication date
                    try:
                        pub_date = parsedate_to_datetime(pub_date_str) if pub_date_str else datetime.utcnow()
                    except (TypeError, ValueError):
                        logger.warning(
                            f"Could not parse SEBI publication date: {pub_date_str}",
                            extra={
                                "date_str": pub_date_str,
                            },
                        )
                        pub_date = datetime.utcnow()

                    # Generate content hash for deduplication
                    content_hash = self._generate_content_hash(title, link)

                    # Determine domain based on title keywords
                    domains = self._classify_domains(title)

                    # Create regulation object
                    regulation = ScrapedRegulation(
                        source_body="SEBI",
                        source_url=link,
                        original_title=title,
                        original_date=pub_date,
                        full_text=description,
                        content_hash=content_hash,
                    )

                    regulations.append(regulation)
                    logger.debug(
                        f"Parsed SEBI regulation: {title[:50]}",
                        extra={
                            "title": title[:50],
                            "hash": content_hash,
                            "domains": domains,
                        },
                    )

                except Exception as e:
                    logger.warning(
                        f"Error parsing SEBI RSS entry: {str(e)}",
                        extra={
                            "error": str(e),
                        },
                    )
                    continue

        except Exception as e:
            logger.error(
                f"Error parsing SEBI RSS feed: {str(e)}",
                extra={
                    "error": str(e),
                },
            )
            raise ScraperException(
                f"Failed to parse RSS feed: {str(e)}",
                "SEBI",
                "parsing_error",
            )

        return regulations

    @staticmethod
    def _generate_content_hash(title: str, url: str) -> str:
        """
        Generate content hash for deduplication.

        Args:
            title: Regulation title
            url: Regulation URL

        Returns:
            16-character hex hash
        """
        content = f"{title}|{url}".lower()
        hash_value = hashlib.sha256(content.encode()).hexdigest()
        return hash_value[:16]

    @staticmethod
    def _classify_domains(title: str) -> List[str]:
        """
        Classify regulation into domains based on title keywords.

        Args:
            title: Regulation title

        Returns:
            List of domain classifications
        """
        title_lower = title.lower()
        domains = []

        # Domain keyword mappings
        domain_keywords = {
            "securities": [
                "securities",
                "stocks",
                "equity",
                "share",
                "listing",
                "stock exchange",
            ],
            "banking": [
                "bank",
                "banking",
                "deposit",
                "loan",
                "credit",
                "merchant",
            ],
            "insurance": [
                "insurance",
                "claim",
                "premium",
                "insurer",
                "policy",
            ],
            "pension": [
                "pension",
                "retirement",
                "superannuation",
                "annuity",
                "provident",
            ],
            "finance": [
                "finance",
                "financial",
                "credit rating",
                "intermediaries",
                "broker",
            ],
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                domains.append(domain)

        # Default to 'securities' if no match (SEBI is primary securities regulator)
        if not domains:
            domains = ["securities"]

        return domains
