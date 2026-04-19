"""Google Gemini provider implementation"""

import time
from typing import List, Optional
from google import genai

from .base import EmbeddingProvider, GenerationProvider


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Gemini embedding provider"""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-embedding-001"
        self.dimension = 768  # Gemini embedding dimension

    def embed_texts(self, texts: List[str], batch_size: int = 5) -> List[List[float]]:
        """Embed texts using Gemini with rate limiting"""
        embeddings = []
        max_retries = 3
        initial_backoff = 2

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            backoff = initial_backoff

            for attempt in range(max_retries):
                try:
                    result = self.client.models.embed_content(
                        model=self.model, contents=batch
                    )
                    for embedding_obj in result.embeddings:
                        embeddings.append(embedding_obj.values)
                    break

                except Exception as e:
                    error_str = str(e)
                    # Don't retry auth errors — fail immediately
                    if "401" in error_str or "403" in error_str or "API_KEY" in error_str or "INVALID_ARGUMENT" in error_str:
                        raise
                    # Only retry rate limit errors
                    if attempt < max_retries - 1 and ("429" in error_str or "RESOURCE_EXHAUSTED" in error_str):
                        print(f"    Retry {attempt + 1}/{max_retries} after {backoff}s (rate limited)...")
                        time.sleep(backoff)
                        backoff = min(backoff * 2, 60)
                    else:
                        raise

            if i + batch_size < len(texts):
                time.sleep(1)

        return embeddings

    def get_embedding_dimension(self) -> int:
        return self.dimension


class GeminiGenerationProvider(GenerationProvider):
    """Gemini generation provider"""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Gemini"""
        try:
            if system_prompt:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    system_instruction=system_prompt,
                )
            else:
                response = self.client.models.generate_content(
                    model=self.model, contents=prompt
                )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini generation failed: {e}")

    def stream_generate(self, prompt: str, system_prompt: Optional[str] = None):
        """Stream generation from Gemini"""
        try:
            if system_prompt:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    system_instruction=system_prompt,
                    stream=True,
                )
            else:
                response = self.client.models.generate_content(
                    model=self.model, contents=prompt, stream=True
                )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            raise Exception(f"Gemini streaming failed: {e}")
