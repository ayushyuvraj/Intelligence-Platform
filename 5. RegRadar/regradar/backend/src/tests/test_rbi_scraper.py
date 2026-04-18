import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.scraper.rbi import RBIScraper
from src.scraper.base import ScrapedRegulation
from bs4 import BeautifulSoup

@pytest.mark.asyncio
async def test_rbi_scraper_initialization():
    """Test that the RBI scraper initializes with correct settings."""
    scraper = RBIScraper()
    assert scraper.source_body == "RBI"
    assert scraper.base_url == "https://www.rbi.org.in"
    assert scraper.timeout_seconds == 60

@pytest.mark.asyncio
async def test_rbi_extract_content_success():
    """Test extraction of content from a detail page."""
    html = '<html><body><div id="content">This is a test regulation content.</div></body></html>'
    soup = BeautifulSoup(html, 'html.parser')
    scraper = RBIScraper()
    content = scraper._extract_content(soup)
    assert content == "This is a test regulation content."

@pytest.mark.asyncio
async def test_rbi_extract_content_fallback():
    """Test fallback content extraction when no specific div is found."""
    html = '<html><body><p>General text content</p></body></html>'
    soup = BeautifulSoup(html, 'html.parser')
    scraper = RBIScraper()
    content = scraper._extract_content(soup)
    assert content == "General text content"

@pytest.mark.asyncio
async def test_rbi_parse_date_valid():
    """Test date parsing with standard RBI format."""
    scraper = RBIScraper()
    date_str = "18-04-2026"
    parsed = scraper._parse_date(date_str)
    assert parsed.year == 2026
    assert parsed.month == 4
    assert parsed.day == 18

@pytest.mark.asyncio
async def test_rbi_parse_date_invalid():
    """Test date parsing with invalid input returns current time."""
    scraper = RBIScraper()
    parsed = scraper._parse_date("invalid-date")
    assert parsed is not None

@pytest.mark.asyncio
async def test_rbi_generate_content_hash():
    """Test consistent hash generation."""
    scraper = RBIScraper()
    title = "Test Title"
    url = "http://example.com"
    hash1 = scraper._generate_content_hash(title, url)
    hash2 = scraper._generate_content_hash(title, url)
    assert hash1 == hash2
    assert len(hash1) == 16

@pytest.mark.asyncio
async def test_rbi_extract_asp_tokens():
    """Test extraction of ASP.NET state tokens."""
    html = """
    <html>
        <input type="hidden" id="__VIEWSTATE" value="viewstate_123">
        <input type="hidden" id="__EVENTVALIDATION" value="eventval_456">
    </html>
    """
    scraper = RBIScraper()
    tokens = scraper._extract_asp_tokens(html)
    assert tokens["__VIEWSTATE"] == "viewstate_123"
    assert tokens["__EVENTVALIDATION"] == "eventval_456"
