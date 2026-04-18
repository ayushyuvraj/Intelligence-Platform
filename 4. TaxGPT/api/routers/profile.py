"""Taxpayer profile analysis endpoints"""
from fastapi import APIRouter, Depends
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from api.schemas.profile import (
    ProfileListResponse, ProfileItem, ProfileRequest, ProfileResponse
)
from api.dependencies import get_api_key_config, APIKeyConfig
from profile_analyzer import ProfileAnalyzer

router = APIRouter(prefix="/api/v1", tags=["profile"])


@router.get("/profiles", response_model=ProfileListResponse)
async def list_profiles() -> ProfileListResponse:
    """List all available taxpayer profiles"""
    profiles = [
        ProfileItem(id="salaried", label="Salaried Employee"),
        ProfileItem(id="business", label="Business Owner"),
        ProfileItem(id="investor", label="Investor"),
        ProfileItem(id="nri", label="NRI"),
        ProfileItem(id="freelancer", label="Freelancer"),
    ]
    return ProfileListResponse(profiles=profiles)


@router.post("/profiles/analyze", response_model=ProfileResponse)
async def analyze_profile(
    request: ProfileRequest,
    api_config: APIKeyConfig = Depends(get_api_key_config),
) -> ProfileResponse:
    """Analyze tax implications for a specific taxpayer profile"""
    try:
        api_config.set_env_vars()
        analyzer = ProfileAnalyzer()
        result = analyzer.analyze(request.profile_type)
        return ProfileResponse(**result)
    except Exception as e:
        return ProfileResponse(
            profile=request.profile_type,
            label="Analysis Failed",
            analysis=str(e),
            source="error",
            error=True,
        )
