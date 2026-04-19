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

    with engine_lock:
        if cache_key in engine_cache:
            return engine_cache[cache_key]

        # Temporarily set environment variable, instantiate, then reset
        old_val = os.environ.get(f"{provider.upper()}_API_KEY")
        try:
            # Map provider name to env var name
            env_var_map = {
                "gemini": "GEMINI_API_KEY",
                "claude": "ANTHROPIC_API_KEY",
                "openai": "OPENAI_API_KEY",
                "openrouter": "OPENROUTER_API_KEY",
            }
            env_key = env_var_map.get(provider, f"{provider.upper()}_API_KEY")
            os.environ[env_key] = api_key
            os.environ["LLM_PROVIDER"] = provider

            # Import here to avoid circular imports
            if engine_type == "rag":
                # Force reimport to pick up updated env vars
                import importlib
                import sys
                # Reload config first to pick up new env vars
                if "src.config" in sys.modules:
                    importlib.reload(sys.modules["src.config"])
                if "src.rag_engine" in sys.modules:
                    importlib.reload(sys.modules["src.rag_engine"])
                from src.rag_engine import get_rag_engine
                engine = get_rag_engine()
            else:
                raise ValueError(f"Unknown engine type: {engine_type}")

            engine_cache[cache_key] = engine
            return engine
        finally:
            # Restore old value
            if old_val is None:
                os.environ.pop(env_key, None)
            else:
                os.environ[env_key] = old_val


def clear_engine_cache():
    """Clear all cached engines (used when switching providers)"""
    with engine_lock:
        engine_cache.clear()


def get_engine(provider: str, api_key: str):
    """Get or create a RAG engine for this provider/key combo"""
    return get_engine_from_cache(provider, api_key, "rag")
