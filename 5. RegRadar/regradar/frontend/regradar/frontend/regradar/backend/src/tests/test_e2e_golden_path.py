import pytest
import asyncio
from playwright.async_api import async_playwright, expect
from src.database import DatabaseManager
from src.models import Regulation
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test constants
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

@pytest.fixture(scope="session")
async def setup_golden_record():
    """Insert a known 'golden' record into the DB for E2E testing."""
    # Note: In a real scenario, we would use a separate test DB
    db_engine = create_engine("sqlite:///regradar.db")
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()

    reg = Regulation(
        source_body="SEBI",
        source_url="https://sebi.gov.in/test",
        original_title="E2E Test Regulation",
        ai_title="AI Summary of E2E Test",
        ai_tldr="This is a golden path test record.",
        ai_what_changed="Added E2E testing validation.",
        ai_who_affected="All Compliance Officers",
        ai_action_required="Verify this record appears in UI",
        ai_impact_level="HIGH",
        domains='["securities"]',
        processing_status="completed",
        content_hash="golden_hash_123"
    )
    session.merge(reg)
    session.commit()
    reg_id = reg.id
    session.close()
    return reg_id

@pytest.mark.asyncio
async def test_golden_path_e2e(setup_golden_record):
    """
    Test the 'Golden Path':
    DB Record -> API Response -> Frontend Feed -> Detail Page
    """
    reg_id = setup_golden_record

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 1. Verify API returns the record
        # (Normally we'd use a request lib, but Playwright can also check API)

        # 2. Navigate to Frontend Feed
        await page.goto(FRONTEND_URL)

        # 3. Search for the golden record
        search_input = page.locator('input[placeholder="Search regulations..."]')
        await search_input.fill("E2E Test")
        await page.keyboard.press("Enter")

        # 4. Assert record is visible in the feed
        expect(page.locator("text=AI Summary of E2E Test")).to_be_visible()

        # 5. Click the card to go to Detail Page
        await page.locator("text=AI Summary of E2E Test").click()

        # 6. Assert Detail Page content is correct
        expect(page.locator("h1")).to_contain_text("AI Summary of E2E Test")
        expect(page.locator("text=This is a golden path test record.")).to_be_visible()
        expect(page.locator("text=HIGH IMPACT")).to_be_visible()

        await browser.close()
