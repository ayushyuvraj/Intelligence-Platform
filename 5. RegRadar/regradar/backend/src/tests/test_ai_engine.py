import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.ai.engine import GeminiEngine
from src.ai.schemas import RegulatoryAnalysis
from src.utils.errors import AIProcessingException

@pytest.mark.asyncio
async def test_gemini_engine_analysis_success():
    """Test successful analysis and validation."""
    # Mock the Gemini API response
    mock_response_text = '{"ai_title": "Test Title", "ai_tldr": "Test TLDR", "ai_what_changed": "Test Change", "ai_who_affected": ["A", "B"], "ai_action_required": ["Action 1"], "ai_impact_level": "HIGH", "domains": ["domain1"]}'

    with patch("google.generativeai.GenerativeModel.generate_content") as mock_gen:
        mock_gen.return_value = MagicMock(text=mock_response_text)

        # Mock API key
        with patch("os.getenv", return_value="test-key"):
            engine = GeminiEngine()
            result = await engine.analyze_regulation("Some raw text")

            assert isinstance(result, RegulatoryAnalysis)
            assert result.ai_title == "Test Title"
            assert result.ai_impact_level == "HIGH"

@pytest.mark.asyncio
async def test_gemini_engine_invalid_json():
    """Test handling of malformed JSON from AI."""
    mock_response_text = '{"ai_title": "Incomplete JSON'

    with patch("google.generativeai.GenerativeModel.generate_content") as mock_gen:
        mock_gen.return_value = MagicMock(text=mock_response_text)

        with patch("os.getenv", return_value="test-key"):
            engine = GeminiEngine()
            with pytest.raises(AIProcessingException) as excinfo:
                await engine.analyze_regulation("Some raw text")
            assert "Invalid JSON" in str(excinfo.value)

@pytest.mark.asyncio
async def test_gemini_engine_validation_error():
    """Test Pydantic validation failure (missing required field)."""
    # Missing ai_impact_level
    mock_response_text = '{"ai_title": "Test", "ai_tldr": "T", "ai_what_changed": "W", "ai_who_affected": [], "ai_action_required": [], "domains": []}'

    with patch("google.generativeai.GenerativeModel.generate_content") as mock_gen:
        mock_gen.return_value = MagicMock(text=mock_response_text)

        with patch("os.getenv", return_value="test-key"):
            engine = GeminiEngine()
            with pytest.raises(AIProcessingException):
                await engine.analyze_regulation("Some raw text")
