import os
import json
import asyncio
from typing import Optional, List
from datetime import datetime

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.ai.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.ai.schemas import RegulatoryAnalysis
from src.utils.logger import get_logger
from src.utils.errors import AIProcessingException
from src.config import settings

logger = get_logger(__name__)

class GeminiEngine:
    """Production-grade wrapper for Gemini 2.0-Flash AI Engine."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT
        )
        self._semaphore = asyncio.Semaphore(10)  # Limit concurrency to manage quota
        self.timeout_seconds = getattr(settings, 'gemini_timeout_seconds', 30)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((asyncio.TimeoutError, Exception)),
    )
    async def _call_gemini(self, prompt: str) -> str:
        """Internal method to call Gemini API with retry logic and timeout."""
        async with self._semaphore:
            try:
                # Using the synchronous SDK in a threadpool
                loop = asyncio.get_event_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: self.model.generate_content(
                            prompt,
                            generation_config={"response_mime_type": "application/json"}
                        )
                    ),
                    timeout=self.timeout_seconds
                )
                return response.text
            except asyncio.TimeoutError:
                logger.error(
                    f"Gemini API timeout after {self.timeout_seconds} seconds",
                    extra={"timeout_seconds": self.timeout_seconds}
                )
                raise AIProcessingException(
                    f"Gemini API timeout after {self.timeout_seconds} seconds"
                )

    async def analyze_regulation(self, text: str) -> RegulatoryAnalysis:
        """
        Analyzes raw regulatory text and returns a validated RegulatoryAnalysis object.
        """
        if not text or len(text.strip()) == 0:
            raise AIProcessingException("Empty text provided for analysis")

        prompt = USER_PROMPT_TEMPLATE.format(text=text)

        try:
            raw_json = await self._call_gemini(prompt)
            # Parse and validate via Pydantic
            data = json.loads(raw_json)
            return RegulatoryAnalysis(**data)
        except json.JSONDecodeError as e:
            logger.error(f"AI returned invalid JSON: {str(e)}", extra={"raw_response": raw_json})
            raise AIProcessingException(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            raise AIProcessingException(f"AI processing error: {str(e)}")
