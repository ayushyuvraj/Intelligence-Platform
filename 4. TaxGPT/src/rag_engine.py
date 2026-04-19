"""RAG Engine: Retrieve relevant chunks and generate answers"""

import json
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    GENERATION_MODEL,
    FAISS_INDEX_DIR,
    RETRIEVAL_TOP_K,
    CONTEXT_TOKEN_BUDGET,
    CHAT_HISTORY_CONTEXT,
)
from prompts import TAX_QA_SYSTEM_PROMPT, TAX_QA_USER_PROMPT_TEMPLATE, GENERAL_DISCLAIMER
from content_filter import get_content_filter
from query_logger import get_query_logger
from ragas_evaluator import get_ragas_evaluator
from providers.base import EmbeddingProvider, GenerationProvider

try:
    import faiss
    import numpy as np
except ImportError:
    faiss = None
    np = None


class TaxRAGEngine:
    """Retrieve-Augment-Generate for tax Q&A (provider-agnostic)"""

    def __init__(self, embedding_provider: EmbeddingProvider, generation_provider: GenerationProvider):
        self.embedding_provider = embedding_provider
        self.generation_provider = generation_provider
        self.index = None
        self.chunks = []
        self._load_index()

    def _load_index(self):
        """Load FAISS index and chunks metadata"""
        index_path = FAISS_INDEX_DIR / "index.faiss"
        chunks_path = FAISS_INDEX_DIR / "chunks.json"

        if not index_path.exists() or not chunks_path.exists():
            return None

        try:
            if faiss:
                self.index = faiss.read_index(str(index_path))
            with open(chunks_path) as f:
                self.chunks = json.load(f)
            return self.index
        except Exception as e:
            print(f"[WARN] Could not load FAISS index: {e}")
            return None

    def _embed_query(self, query: str) -> list:
        """Embed query using configured embedding provider"""
        if not self.embedding_provider:
            return None

        try:
            embeddings = self.embedding_provider.embed_texts([query])
            embedding = embeddings[0]
            return np.array([embedding], dtype=np.float32)
        except Exception as e:
            print(f"[ERROR] Failed to embed query: {e}")
            return None

    def _detect_old_section(self, query: str) -> str:
        """Detect old section references in query (e.g., 'Section 80C')"""
        # Match patterns like "Section 80C", "80D", "143(1)", etc.
        match = re.search(r"(?:Section\s+)?(\d+[A-Z]*(?:\(\d+\))?)", query, re.IGNORECASE)
        return match.group(1) if match else None

    def retrieve(self, query: str, top_k: int = RETRIEVAL_TOP_K) -> list:
        """Retrieve top-k relevant chunks for a query"""
        if not self.index or not self.chunks:
            return []

        # Embed query
        query_embedding = self._embed_query(query)
        if query_embedding is None:
            return []

        # Normalize for cosine similarity
        query_embedding = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)

        # Search FAISS
        distances, indices = self.index.search(query_embedding, min(top_k, len(self.chunks)))

        # Retrieve chunks
        results = []
        seen_sections = set()

        for idx in indices[0]:
            if idx < len(self.chunks):
                chunk = self.chunks[int(idx)]
                # Dedup: don't add same section twice
                if chunk.get("section_number") not in seen_sections:
                    results.append(chunk)
                    seen_sections.add(chunk.get("section_number"))

        return results[:top_k]

    def answer(
        self, question: str, chat_history: list = None, language: str = "English"
    ) -> dict:
        """Generate answer using RAG pipeline with logging and evaluation"""
        # Generate unique ID for this query
        query_id = str(uuid.uuid4())[:8]
        logger = get_query_logger()
        evaluator = get_ragas_evaluator()
        start_time = time.time()

        if not self.embedding_provider or not self.generation_provider:
            return {
                "answer": "LLM providers not configured. Please configure an AI provider.",
                "error": True,
                "sources": [],
            }

        # Log incoming query
        logger.log_query(
            query_id=query_id,
            feature="rag_qa",
            question=question,
            is_tax_related=None,  # Will update after filter check
            relevance_score=0.0,
            language=language,
        )

        # Content filtering: Check if question is tax-related
        content_filter = get_content_filter()
        is_tax_related, relevance_score, reason = content_filter.is_tax_related(question)

        # Log filter decision
        logger.log_filter_decision(query_id, question, is_tax_related, relevance_score, reason)

        if not is_tax_related:
            # Log the filter rejection
            logger.log_feature_output(
                query_id=query_id,
                feature="rag_qa",
                output={"filtered": True},
                processing_time_ms=(time.time() - start_time) * 1000,
                success=True,
            )
            return {
                "answer": content_filter.get_rejection_response(question),
                "error": False,
                "sources": [],
            }

        try:
            # Retrieve relevant chunks with timing
            retrieval_start = time.time()
            retrieved_chunks = self.retrieve(question, RETRIEVAL_TOP_K)
            retrieval_time = (time.time() - retrieval_start) * 1000

            # Log retrieval
            logger.log_retrieval(
                query_id=query_id,
                query=question,
                retrieved_chunks=retrieved_chunks,
                num_results=len(retrieved_chunks),
                retrieval_time_ms=retrieval_time,
            )

            if not retrieved_chunks:
                context = "[No matching sections found in knowledge base]"
                sources = []
            else:
                # Format context
                context = "\n\n".join(
                    [f"**{c['source']}**:\n{c['text'][:500]}..." for c in retrieved_chunks[:3]]
                )
                sources = [{"source": c["source"], "section": c.get("section_number")} for c in retrieved_chunks]

            # Format chat history
            history_text = ""
            if chat_history:
                for turn in chat_history[-CHAT_HISTORY_CONTEXT :]:
                    history_text += f"Q: {turn.get('question', '')}\nA: {turn.get('answer', '')[:200]}...\n"

            # Build prompt
            user_prompt = TAX_QA_USER_PROMPT_TEMPLATE.format(
                question=question, context=context, chat_history=history_text
            )

            # Call generation provider with timing
            generation_start = time.time()
            answer_text = self.generation_provider.generate(
                prompt=user_prompt,
                system_prompt=TAX_QA_SYSTEM_PROMPT
            )
            generation_time = (time.time() - generation_start) * 1000

            answer_text = answer_text + GENERAL_DISCLAIMER

            # Log generation
            logger.log_generation(
                query_id=query_id,
                answer=answer_text,
                generation_time_ms=generation_time,
                model=GENERATION_MODEL,
            )

            # Log feature completion
            logger.log_feature_output(
                query_id=query_id,
                feature="rag_qa",
                output={"answer_length": len(answer_text), "sources": len(sources)},
                processing_time_ms=(time.time() - start_time) * 1000,
                success=True,
            )

            # Evaluate response quality (async in background, non-blocking)
            # Only evaluate a sample of responses to save on API calls
            import random
            if random.random() < 0.2:  # Evaluate 20% of responses
                try:
                    full_context = "\n\n".join([c.get("text", "") for c in retrieved_chunks[:3]])
                    evaluation = evaluator.evaluate_response(
                        query_id=query_id,
                        question=question,
                        retrieved_context=full_context,
                        generated_answer=answer_text,
                    )
                except Exception as e:
                    # Silently fail if evaluation fails - don't block user response
                    logger.log_error(query_id, "rag_qa", "evaluation_error", str(e))

            return {"answer": answer_text, "error": False, "sources": sources}

        except Exception as e:
            # Log error
            error_str = str(e)
            logger.log_error(
                query_id=query_id,
                feature="rag_qa",
                error_type=type(e).__name__,
                error_message=error_str,
            )

            # Provide user-friendly error messages
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                user_message = """**API Quota Exceeded**

Your Gemini API free tier quota has been exhausted. You have 3 options:

1. **Upgrade to Gemini Paid Tier** (Recommended)
   - Visit: https://console.cloud.google.com/billing
   - Add payment method - only ~$0.10 per 1M tokens
   - Quota resets with ~50x higher limits

2. **Wait for Quota Reset**
   - Free tier quota resets in ~24 hours

3. **Use Different LLM Provider**
   - Switch to Claude/OpenAI in .env (see README)

**In the meantime**, use the offline features which work perfectly:
- **Tab 2**: Section Mapper (103 mappings)
- **Tab 3**: Profile Analyzer (5 profiles)
- **Tab 4**: Notice Decoder (regex-based)
"""
            else:
                user_message = f"Error generating answer: {error_str}. Please try again."

            return {
                "answer": user_message,
                "error": True,
                "sources": [],
            }


# Singleton instance
def _detect_index_dimensions() -> int:
    """Read the FAISS index dimension to know which embedding provider to use"""
    index_path = FAISS_INDEX_DIR / "index.faiss"
    if not index_path.exists():
        return 0
    try:
        if faiss:
            idx = faiss.read_index(str(index_path))
            return idx.d
    except Exception:
        pass
    return 0


def get_rag_engine():
    """Create RAG engine with providers from environment.

    Embedding provider is selected based on the FAISS index dimension:
    - 1536 dims → OpenAI (text-embedding-3-small)
    - 768 dims  → Gemini (gemini-embedding-001)
    Generation provider follows LLM_PROVIDER env var.
    """
    import os
    from providers.factory import get_generation_provider

    index_dims = _detect_index_dimensions()

    # Select embedding provider based on what the index was built with
    if index_dims == 1536:
        from providers.openai import OpenAIEmbeddingProvider
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if not openai_key:
            raise ValueError(
                "This knowledge base requires an OpenAI API key for search "
                "(the index was built with OpenAI text-embedding-3-small). "
                "Please provide X-OpenAI-Key header."
            )
        embedding_provider = OpenAIEmbeddingProvider(openai_key)
    elif index_dims == 768:
        from providers.gemini import GeminiEmbeddingProvider
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if not gemini_key:
            raise ValueError(
                "This knowledge base requires a Gemini API key for search "
                "(the index was built with Gemini gemini-embedding-001). "
                "Please provide X-Gemini-Key header."
            )
        embedding_provider = GeminiEmbeddingProvider(gemini_key)
    else:
        from providers.factory import get_embedding_provider
        embedding_provider = get_embedding_provider()

    generation_provider = get_generation_provider()
    return TaxRAGEngine(embedding_provider, generation_provider)
