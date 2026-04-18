"""
RBI Scraper
Scrapes regulatory notifications and circulars from the Reserve Bank of India (RBI).
Handles HTML table parsing and ASP.NET state management for navigation.
"""

import hashlib
import asyncio
import re
from datetime import datetime
from typing import List, Optional, Dict
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from src.scraper.base import BaseScraper, ScrapedRegulation
from src.utils.logger import get_logger
from src.utils.errors import ScraperException

logger = get_logger(__name__)

class RBIScraper(BaseScraper):
    """Scraper for RBI regulatory updates."""

    # RBI Notifications URL
    NOTIFICATIONS_URL = "https://www.rbi.org.in/scripts/NotificationUser.aspx"

    def __init__(self):
        """Initialize RBI scraper."""
        super().__init__(
            source_body="RBI",
            base_url="https://www.rbi.org.in",
            timeout_seconds=60,  # Increased for slow ASP.NET responses
            max_retries=3,
        )

    async def fetch(self) -> List[ScrapedRegulation]:
        """
        Fetch latest RBI regulations from the notifications page.

        Returns:
            List of ScrapedRegulation objects
        """
        start_time = datetime.utcnow()
        all_regulations = []
        errors = []

        logger.info("Starting RBI scraper")

        try:
            # 1. Fetch the main notifications index page
            html = await self._request(self.NOTIFICATIONS_URL)
            soup = BeautifulSoup(html, 'html.parser')

            # 2. Identify the notifications table
            # RBI typically uses tables with specific classes or IDs.
            # We look for the main data table.
            table = soup.find("table", {"class": "table-striped"}) or \
                    soup.find("table", {"id": re.compile(r"ctl00_PlaceHolderMain")})

            if not table:
                logger.warning("RBI notifications table not found on page")
                return []

            # 3. Parse table rows (skipping header)
            rows = table.find_all("tr")[1:]

            for row in rows:
                try:
                    cols = row.find_all("td")
                    if len(cols) < 2:
                        continue

                    # Extract basic info from the index table
                    # Title is usually in the first or second column and contains a link
                    link_tag = row.find("a", href=True)
                    if not link_tag:
                        continue

                    title = link_tag.text.strip()
                    relative_url = link_tag['href']
                    detail_url = self._ensure_absolute_url(relative_url)

                    # Date is usually in one of the columns
                    date_text = ""
                    for col in cols:
                        if any(char.isdigit() for char in col.text) and len(col.text.strip()) < 20:
                            date_text = col.text.strip()
                            break

                    parsed_date = self._parse_date(date_text)

                    # 4. Fetch detail page for full content
                    detail_html = await self._request(detail_url)
                    detail_soup = BeautifulSoup(detail_html, 'html.parser')
                    full_text = self._extract_content(detail_soup)

                    # 5. Generate content hash for deduplication
                    content_hash = self._generate_content_hash(title, detail_url)

                    # Create regulation object
                    regulation = ScrapedRegulation(
                        source_body=self.source_body,
                        source_url=detail_url,
                        original_title=title,
                        original_date=parsed_date,
                        full_text=full_text,
                        content_hash=content_hash,
                    )

                    all_regulations.append(regulation)
                    logger.debug(f"Parsed RBI regulation: {title[:50]}")

                except Exception as e:
                    logger.warning(f"Error parsing RBI row: {str(e)}")
                    errors.append(str(e))
                    continue

            processing_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._log_scrape_result(len(all_regulations), processing_time_ms, errors)

        except Exception as e:
            logger.error(f"Unexpected error in RBI fetch: {str(e)}")
            raise ScraperException(f"RBI fetch failed: {str(e)}", "RBI", "fetch_error")

        return all_regulations

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main text content from the RBI detail page.
        """
        # RBI detail pages often have content in a specific div or table
        # We try to find the most likely content containers
        content_div = soup.find("div", {"id": "content"}) or \
                      soup.find("div", {"class": "main-content"}) or \
                      soup.find("table", {"class": "table-striped"})

        if content_div:
            # Remove script and style elements
            for element in content_div(["script", "style"]):
                element.decompose()
            return content_div.get_text(separator=" ", strip=True)

        # Fallback: get all text from body
        return soup.body.get_text(separator=" ", strip=True) if soup.body else ""

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse RBI date strings into datetime objects.
        """
        if not date_str:
            return datetime.utcnow()

        try:
            return date_parser.parse(date_str)
        except (ValueError, TypeError):
            logger.warning(f"Could not parse RBI date: {date_str}")
            return datetime.utcnow()

    def _generate_content_hash(self, title: str, url: str) -> str:
        """
        Generate a unique content hash for deduplication.
        """
        content = f"{title}|{url}".lower()
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _extract_asp_tokens(self, html: str) -> Dict[str, str]:
        """
        Extract ASP.NET state tokens (__VIEWSTATE, __EVENTVALIDATION).
        """
        soup = BeautifulSoup(html, 'html.parser')
        viewstate = soup.find("input", {"id": "__VIEWSTATE"})
        event_val = soup.find("input", {"id": "__EVENTVALIDATION"})

        return {
            "__VIEWSTATE": viewstate["value"] if viewstate else "",
            "__EVENTVALIDATION": event_val["value"] if event_val else ""
        }

    async def _trigger_postback(self, event_target: str, event_argument: str, html: str) -> str:
        """
        Trigger an ASP.NET PostBack and return the resulting HTML.
        """
        tokens = self._extract_asp_tokens(html)

        payload = {
            "__EVENTTARGET": event_target,
            "__EVENTARGUMENT": event_argument,
            **tokens
        }

        # Note: We use the internal _request method but for a POST
        # BaseScraper._request currently only handles GET. We need to extend it or use aiohttp directly.
        # For now, we'll use a aiohttp post via the session.
        async with self.session.post(self.NOTIFICATIONS_URL, data=payload) as response:
            return await response.text()
