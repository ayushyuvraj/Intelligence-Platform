"""Global state for background jobs and engine caching"""

import os
import threading
from dataclasses import dataclass, field
from collections import deque
from typing import Dict, Tuple, Optional, Any
from datetime import datetime


@dataclass
class IngestionState:
    """Tracks background FAISS ingestion job"""
    status: str = "idle"  # idle, running, complete, error
    progress_pct: float = 0.0
    messages: deque = field(default_factory=lambda: deque(maxlen=100))
    thread: Optional[threading.Thread] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    job_id: str = ""

    def add_message(self, msg: str):
        """Thread-safe message append"""
        self.messages.append(msg)


# Global ingestion state
ingestion_state = IngestionState()
ingestion_lock = threading.Lock()

# Engine cache: (provider, api_key) -> engine instance
# Prevents re-instantiating the same engine for the same API key
engine_cache: Dict[Tuple[str, str], Any] = {}
engine_lock = threading.Lock()


def get_engine_from_cache(provider: str, api_key: str, engine_type: str) -> Any:
    """
    Get or create a cached engine instance for the given provider/key combo.

    Args:
        provider: "gemini", "claude", "openai", etc.
        api_key: The API key for this provider
        engine_type: "rag" or "section_mapper"

    Returns:
        The engine instance (TaxRAGEngine or SectionMapper)
    """
    cache_key = (provider, api_key, engine_type)
    print(f"[DEBUG] get_engine_from_cache: provider={provider}, key_len={len(api_key) if api_key else 0}")

    with engine_lock:
        if cache_key in engine_cache:
            print(f"[DEBUG] Using cached engine for {provider}")
            return engine_cache[cache_key]

        try:
            # Import here to avoid circular imports
            if engine_type == "rag":
                from src.providers.factory import get_embedding_provider, get_generation_provider
                from src.rag_engine import TaxRAGEngine

                # Temporarily set environment variables for provider
                env_var_map = {
                    "gemini": "GEMINI_API_KEY",
                    "claude": "ANTHROPIC_API_KEY",
                    "openai": "OPENAI_API_KEY",
                    "openrouter": "OPENROUTER_API_KEY",
                }
                env_key = env_var_map.get(provider, f"{provider.upper()}_API_KEY")
                old_val = os.environ.get(env_key)
                old_provider = os.environ.get("LLM_PROVIDER")

                try:
                    os.environ[env_key] = api_key
                    os.environ["LLM_PROVIDER"] = provider

                    # Create providers with the new API key
                    embedding_provider = get_embedding_provider(provider)
                    generation_provider = get_generation_provider(provider)

                    # Create engine with providers
                    engine = TaxRAGEngine(embedding_provider, generation_provider)
                    engine_cache[cache_key] = engine
                    return engine
                finally:
                    # Restore old env vars
                    if old_val is None:
                        os.environ.pop(env_key, None)
                    else:
                        os.environ[env_key] = old_val
                    if old_provider is None:
                        os.environ.pop("LLM_PROVIDER", None)
                    else:
                        os.environ["LLM_PROVIDER"] = old_provider
            else:
                raise ValueError(f"Unknown engine type: {engine_type}")
        except Exception as e:
            print(f"[ERROR] Failed to create engine: {e}")
            raise


def clear_engine_cache():
    """Clear all cached engines (used when switching providers)"""
    with engine_lock:
        engine_cache.clear()


def get_engine(provider: str, api_key: str):
    """Get or create a RAG engine for this provider/key combo"""
    return get_engine_from_cache(provider, api_key, "rag")
