#!/usr/bin/env python3
"""
RegRadar Seed Data Script

Populates the database with sample regulations for testing and demo purposes.
Run this after database initialization to load initial data.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "regradar" / "backend"))

from src.database import init_db, get_db
from src.models import Regulation
from sqlalchemy import insert

SEED_REGULATIONS = [
    {
        "title": "RBI Notification on Tokenization of Credit and Debit Cards",
        "source_body": "RBI",
        "source_url": "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11839",
        "content": "The Reserve Bank of India has issued guidelines on tokenization of credit and debit cards...",
        "summary": "New guidelines for card tokenization to enhance security in digital payments",
        "ai_summary": "RBI has mandated tokenization of credit and debit cards for secure online payments",
        "ai_impact_level": "HIGH",
        "ai_action_required": "Implement card tokenization in payment systems\nUpdate customer communication\nEnsure compliance by March 31, 2023",
        "published_date": datetime.now() - timedelta(days=5),
        "processing_status": "completed",
        "ai_tokens_used": 450,
    },
    {
        "title": "SEBI Order on Market Manipulation during IPO Period",
        "source_body": "SEBI",
        "source_url": "https://www.sebi.gov.in/sebi_data/sebi_notices/1234567890.html",
        "content": "SEBI has issued directives to prevent market manipulation during IPO subscription periods...",
        "summary": "SEBI tightens rules on market activity during IPO periods to prevent manipulation",
        "ai_summary": "SEBI has strengthened oversight of trading activities during IPO periods",
        "ai_impact_level": "MEDIUM",
        "ai_action_required": "Review IPO-related trading policies\nEnhance monitoring systems\nTrain compliance team on new rules",
        "published_date": datetime.now() - timedelta(days=3),
        "processing_status": "completed",
        "ai_tokens_used": 380,
    },
    {
        "title": "RBI Policy Rate Unchanged at 6.50%",
        "source_body": "RBI",
        "source_url": "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11840",
        "content": "RBI Monetary Policy Committee has decided to keep policy rate unchanged...",
        "summary": "RBI maintains policy rate at 6.50% in latest monetary policy decision",
        "ai_summary": "RBI holds steady on interest rates amid inflation concerns",
        "ai_impact_level": "MEDIUM",
        "ai_action_required": "Review interest rate implications for products\nUpdate loan pricing\nCommunicate to customers",
        "published_date": datetime.now() - timedelta(days=2),
        "processing_status": "completed",
        "ai_tokens_used": 320,
    },
    {
        "title": "SEBI Guidelines on ESG Disclosures for Listed Companies",
        "source_body": "SEBI",
        "source_url": "https://www.sebi.gov.in/sebi_data/sebi_notices/1234567891.html",
        "content": "SEBI has released comprehensive guidelines on Environmental, Social and Governance disclosures...",
        "summary": "Listed companies must enhance ESG reporting and disclosures",
        "ai_summary": "New ESG reporting requirements for all listed companies effective immediately",
        "ai_impact_level": "HIGH",
        "ai_action_required": "Establish ESG reporting framework\nCollect ESG data from departments\nPrepare disclosures for annual report",
        "published_date": datetime.now() - timedelta(days=1),
        "processing_status": "completed",
        "ai_tokens_used": 520,
    },
    {
        "title": "RBI Cyber Security Framework for Banks",
        "source_body": "RBI",
        "source_url": "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11841",
        "content": "RBI has updated cyber security framework requirements for all banks and financial institutions...",
        "summary": "Banks must enhance cyber security measures and incident reporting",
        "ai_summary": "RBI mandates strengthened cybersecurity with real-time threat monitoring",
        "ai_impact_level": "HIGH",
        "ai_action_required": "Audit current security infrastructure\nImplement real-time monitoring\nUpdate incident response procedures\nConduct security training",
        "published_date": datetime.now(),
        "processing_status": "completed",
        "ai_tokens_used": 650,
    },
    {
        "title": "SEBI Regulatory Sandbox for Fintech",
        "source_body": "SEBI",
        "source_url": "https://www.sebi.gov.in/sebi_data/sebi_notices/1234567892.html",
        "content": "SEBI announces new regulatory sandbox framework for fintech innovations...",
        "summary": "SEBI opens sandbox for fintech companies to test innovative products",
        "ai_summary": "SEBI establishes sandbox environment for fintech experimentation with relaxed regulations",
        "ai_impact_level": "LOW",
        "ai_action_required": "Review fintech innovation opportunities\nEvaluate sandbox participation benefits",
        "published_date": datetime.now() - timedelta(days=7),
        "processing_status": "completed",
        "ai_tokens_used": 280,
    },
    {
        "title": "RBI Circular on Unsecured Personal Loans",
        "source_body": "RBI",
        "source_url": "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11842",
        "content": "RBI has issued guidelines on risk assessment for unsecured personal loans...",
        "summary": "RBI tightens lending standards for unsecured personal loans",
        "ai_summary": "New risk assessment criteria for personal loan portfolios",
        "ai_impact_level": "MEDIUM",
        "ai_action_required": "Update risk assessment models\nReview current loan portfolio\nAdjust lending criteria",
        "published_date": datetime.now() - timedelta(days=10),
        "processing_status": "completed",
        "ai_tokens_used": 410,
    },
    {
        "title": "SEBI Code of Conduct for Merchant Bankers",
        "source_body": "SEBI",
        "source_url": "https://www.sebi.gov.in/sebi_data/sebi_notices/1234567893.html",
        "content": "SEBI updates code of conduct for merchant bankers with new conflict of interest rules...",
        "summary": "Enhanced conflict of interest and independence requirements for merchant bankers",
        "ai_summary": "SEBI strengthens merchant banker independence with stricter conflict rules",
        "ai_impact_level": "MEDIUM",
        "ai_action_required": "Review independence policies\nUpdate staff conflict guidelines\nImplement disclosure mechanisms",
        "published_date": datetime.now() - timedelta(days=12),
        "processing_status": "completed",
        "ai_tokens_used": 370,
    },
]


async def seed_database():
    """Seed the database with initial regulation data."""
    print("Initializing database...")
    await init_db()

    print("Seeding regulations...")
    try:
        db = next(get_db())

        for reg_data in SEED_REGULATIONS:
            regulation = Regulation(**reg_data)
            db.add(regulation)

        db.commit()
        print(f"✓ Seeded {len(SEED_REGULATIONS)} regulations")

    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
    print("✓ Database seeding complete!")
