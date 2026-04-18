"""Profile analyzer request/response schemas"""

from pydantic import BaseModel, Field
from typing import Literal


class ProfileItem(BaseModel):
    """Available profile option"""
    id: str
    label: str


class ProfileListResponse(BaseModel):
    """List of available taxpayer profiles"""
    profiles: list[ProfileItem]


class ProfileRequest(BaseModel):
    """Request to analyze a profile"""
    profile_type: Literal["salaried", "business", "investor", "nri", "freelancer"] = Field(
        description="Type of taxpayer profile"
    )


class ProfileResponse(BaseModel):
    """Response with profile analysis"""
    profile: str
    label: str
    analysis: str
    source: str  # "gemini" or "fallback"
    error: bool = False
