"""
Pydantic Schemas for API Requests and Responses

Defines request/response models with validation for all endpoints.
Ensures type safety and automatic documentation generation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ImpactLevel(str, Enum):
    """Regulatory impact level classification."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SourceBody(str, Enum):
    """Supported regulatory sources."""

    SEBI = "SEBI"
    RBI = "RBI"
    MCA = "MCA"  # Phase 2
    MEITY = "MEITY"  # Phase 2
    DPIIT = "DPIIT"  # Phase 2


class ProcessingStatus(str, Enum):
    """Regulation processing status."""

    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"
    REVIEW_PENDING = "review_pending"


class DomainType(str, Enum):
    """Regulatory domains/categories."""

    BANKING = "banking"
    SECURITIES = "securities"
    INSURANCE = "insurance"
    PENSION = "pension"
    FINANCE = "finance"


class RegulationResponse(BaseModel):
    """Response model for a single regulation."""

    id: int
    source_body: SourceBody
    original_title: str = Field(..., min_length=1, max_length=500)
    original_date: datetime
    source_url: str = Field(..., min_length=1, max_length=2000)
    ai_title: str = Field(..., min_length=1, max_length=500)
    ai_tldr: str = Field(..., min_length=1, max_length=5000)
    ai_what_changed: Optional[str] = Field(None, max_length=5000)
    ai_who_affected: Optional[str] = Field(None, max_length=5000)
    ai_action_required: Optional[str] = Field(None, max_length=5000)
    ai_impact_level: ImpactLevel
    domains: List[str]
    processing_status: ProcessingStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class RegulationListResponse(BaseModel):
    """Response model for listing regulations."""

    regulations: List[RegulationResponse]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    has_more: bool


class DomainCount(BaseModel):
    """Domain with regulation count."""

    name: str
    count: int = Field(..., ge=0)


class DomainsResponse(BaseModel):
    """Response model for listing domains."""

    domains: List[DomainCount]


class StatsResponse(BaseModel):
    """Response model for statistics dashboard."""

    total_regulations: int = Field(..., ge=0)
    by_source: Dict[str, int]
    by_impact: Dict[str, int]
    by_domain: Dict[str, int]
    last_updated: datetime


class SessionRequest(BaseModel):
    """Request model for creating a session."""

    domains: List[DomainType] = Field(default_factory=list, max_length=5)

    @field_validator("domains")
    @classmethod
    def validate_domains(cls, v: List[str]) -> List[str]:
        """Validate that domains are from allowed list."""
        valid_domains = {d.value for d in DomainType}
        for domain in v:
            if domain not in valid_domains:
                raise ValueError(f"Invalid domain: {domain}")
        return v


class SessionResponse(BaseModel):
    """Response model for session creation/retrieval."""

    session_id: str = Field(..., min_length=32, max_length=64)
    domains: List[str]
    created_at: datetime
    last_accessed: datetime


class PreferenceUpdateRequest(BaseModel):
    """Request model for updating preferences."""

    domains: Optional[List[DomainType]] = None

    @field_validator("domains")
    @classmethod
    def validate_domains(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate that domains are from allowed list."""
        if v is None:
            return v
        valid_domains = {d.value for d in DomainType}
        for domain in v:
            if domain not in valid_domains:
                raise ValueError(f"Invalid domain: {domain}")
        return v


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    error_code: str
    status_code: int
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    version: str
    database: Dict[str, Any]
    environment: str
    response_time_ms: int


class ScraperRunResponse(BaseModel):
    """Response model for scraper run information."""

    id: int
    source_body: str
    status: str
    regulations_found: Optional[int] = None
    regulations_new: Optional[int] = None
    regulations_duplicated: Optional[int] = None
    duration_seconds: Optional[int] = None
    run_timestamp: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class PaginationParams(BaseModel):
    """Common pagination parameters."""

    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """Ensure limit is within bounds."""
        if v < 1 or v > 100:
            raise ValueError("Limit must be between 1 and 100")
        return v

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, v: int) -> int:
        """Ensure offset is non-negative."""
        if v < 0:
            raise ValueError("Offset must be non-negative")
        return v
