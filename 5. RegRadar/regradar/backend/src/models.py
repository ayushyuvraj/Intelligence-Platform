"""
SQLAlchemy Models for RegRadar

Defines database schema for regulations, user preferences, scraper runs,
and AI processing history.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Regulation(Base):
    """Regulatory update model."""

    __tablename__ = "regulations"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Source Information
    source_body = Column(String(50), nullable=False, index=True)  # RBI, SEBI, MCA, etc
    original_title = Column(String(500), nullable=False)
    original_date = Column(DateTime, nullable=False, index=True)
    source_url = Column(String(2000), unique=True, nullable=False, index=True)
    full_text = Column(Text)
    content_hash = Column(String(64), unique=True, nullable=False, index=True)

    # AI-Generated Fields
    ai_title = Column(String(500), nullable=False)
    ai_tldr = Column(Text, nullable=False)
    ai_what_changed = Column(Text)
    ai_who_affected = Column(Text)
    ai_action_required = Column(Text)
    ai_effective_date = Column(String(100))
    ai_compliance_deadline = Column(String(100))
    ai_impact_level = Column(String(20), nullable=False, index=True)  # HIGH, MEDIUM, LOW
    ai_related_regulations = Column(Text)  # JSON array
    ai_confidence_score = Column(Float)

    # Metadata
    domains = Column(Text, nullable=False, index=True)  # JSON array of domain tags
    processing_status = Column(String(50), default="pending", index=True)  # pending, processed, failed, review_pending
    processing_error = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)

    # Relationships
    ai_history = relationship("AIProcessingHistory", back_populates="regulation", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Regulation(id={self.id}, title={self.ai_title[:50]}, source={self.source_body})>"


class UserPreference(Base):
    """User preferences and session tracking."""

    __tablename__ = "user_preferences"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Session Management
    session_id = Column(String(100), unique=True, nullable=False, index=True)

    # Preferences
    selected_domains = Column(Text, nullable=False)  # JSON array of domains

    # Email (Phase 2)
    email = Column(String(255))
    email_frequency = Column(String(50))  # daily, weekly, never
    email_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<UserPreference(id={self.id}, session_id={self.session_id[:20]})>"


class ScraperRun(Base):
    """Scraper execution history."""

    __tablename__ = "scraper_runs"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Execution Info
    source_body = Column(String(50), nullable=False, index=True)
    run_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(50), nullable=False)  # success, partial, failed
    duration_seconds = Column(Integer)

    # Results
    regulations_found = Column(Integer)
    regulations_new = Column(Integer)
    regulations_duplicated = Column(Integer)
    error_message = Column(Text)

    def __repr__(self) -> str:
        return f"<ScraperRun(id={self.id}, source={self.source_body}, status={self.status})>"


class AIProcessingHistory(Base):
    """AI processing audit trail."""

    __tablename__ = "ai_processing_history"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # References
    regulation_id = Column(Integer, ForeignKey("regulations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Processing Info
    attempt_number = Column(Integer)
    status = Column(String(50), nullable=False)  # success, failed, retry
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    processing_time_ms = Column(Integer)
    error_message = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    regulation = relationship("Regulation", back_populates="ai_history")

    def __repr__(self) -> str:
        return f"<AIProcessingHistory(id={self.id}, regulation_id={self.regulation_id}, status={self.status})>"


class RegulationRelationship(Base):
    """Regulation relationships (Phase 2)."""

    __tablename__ = "regulation_relationships"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # References
    regulation_id = Column(Integer, ForeignKey("regulations.id", ondelete="CASCADE"), nullable=False, index=True)
    related_regulation_id = Column(Integer, ForeignKey("regulations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationship Info
    relationship_type = Column(String(50), nullable=False)  # supersedes, amended_by, relates_to
    confidence_score = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Unique constraint
    __table_args__ = (
        UniqueConstraint("regulation_id", "related_regulation_id", "relationship_type", name="uq_regulation_relationships"),
    )

    def __repr__(self) -> str:
        return f"<RegulationRelationship(id={self.id}, type={self.relationship_type})>"


class EmailDigest(Base):
    """Email digest tracking (Phase 2)."""

    __tablename__ = "email_digests"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # User Info
    user_id = Column(String(100), nullable=False, index=True)

    # Period Info
    period = Column(String(50))  # daily, weekly
    period_start = Column(DateTime)
    period_end = Column(DateTime)

    # Content
    regulations_count = Column(Integer)

    # Tracking
    sent_at = Column(DateTime)
    opened_at = Column(DateTime)
    click_count = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<EmailDigest(id={self.id}, user_id={self.user_id}, period={self.period})>"


# Define indexes for performance
Index("idx_regulations_date", Regulation.original_date.desc())
Index("idx_regulations_source", Regulation.source_body)
Index("idx_regulations_impact", Regulation.ai_impact_level)
Index("idx_regulations_domains", Regulation.domains)
Index("idx_regulations_hash", Regulation.content_hash)
Index("idx_regulations_created", Regulation.created_at.desc())
Index("idx_scraper_runs_source", ScraperRun.source_body, ScraperRun.run_timestamp.desc())
Index("idx_user_prefs_session", UserPreference.session_id)
Index("idx_ai_history_regulation", AIProcessingHistory.regulation_id)
