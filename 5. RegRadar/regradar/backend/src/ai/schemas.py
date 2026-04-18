from pydantic import BaseModel, Field
from typing import List, Literal

class RegulatoryAnalysis(BaseModel):
    """Validated AI analysis output for a regulation."""
    ai_title: str = Field(..., description="Professional summary title (max 10 words)")
    ai_tldr: str = Field(..., description="2-3 sentence plain-English summary")
    ai_what_changed: str = Field(..., description="Precise delta between old and new requirements")
    ai_who_affected: List[str] = Field(..., description="List of specific stakeholders affected")
    ai_action_required: List[str] = Field(..., description="Bulleted list of mandatory steps for compliance officers")
    ai_impact_level: Literal["HIGH", "MEDIUM", "LOW"] = Field(..., description="Severity of regulatory risk")
    domains: List[str] = Field(..., description="Relevant regulatory domains")
