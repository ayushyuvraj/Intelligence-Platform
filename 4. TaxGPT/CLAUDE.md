# TaxGPT India

RAG-powered AI tool helping 80M+ Indian taxpayers navigate the Income Tax Act 2025 (effective April 1, 2026), which replaced the 1961 Act. Every section number, form number, and core terminology changed. This tool answers tax questions citing NEW Act sections, maps old-to-new sections, provides personalized impact analysis, and decodes tax notices.

**Author:** Ayush Yuvraj
**Platform:** Windows (bash shell in Claude Code, but Python paths must handle Windows)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + TypeScript + Vite + Tailwind CSS + Framer Motion |
| Backend | FastAPI (Python 3.11+) |
| AI/LLM | Google Gemini (`gemini-2.0-flash` for generation, `gemini-embedding-001` for embeddings) |
| Vector Store | FAISS (`faiss-cpu`, `IndexFlatIP` with L2 normalization for cosine similarity) |
| PDF Parsing | PyPDF2 |
| State Management | Zustand (client), FastAPI dependency injection (server) |
| Data Fetching | React Query (@tanstack/react-query) |
| Deployment | Google Cloud Run (Docker) or local development |

### Critical: API Package

The package is **`google-genai`**, NOT `google-generativeai`. These are different packages.

```python
# CORRECT
from google import genai
client = genai.Client(api_key=GEMINI_API_KEY)

# Embeddings
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=["text1", "text2"],
)
vectors = result.embeddings[0].values  # list[float]

# Generation
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="your prompt here",
)
answer = response.text
```

### Critical: .env BOM Handling (Windows)

Windows-created `.env` files have a UTF-8 BOM. Without `encoding="utf-8-sig"`, the first key gets a hidden prefix and fails silently.

```python
try:
    from dotenv import load_dotenv
    load_dotenv(encoding="utf-8-sig")
except Exception:
    pass
```

---

## Project Structure

```
taxgpt-india/
├── frontend/                           # React + Vite frontend
│   ├── src/
│   │   ├── main.tsx                    # React entry point
│   │   ├── App.tsx                     # Root component
│   │   ├── components/                 # Reusable React components
│   │   ├── hooks/                      # Custom hooks (useQA, useMapper, useProfile, useNotice, useIngestion)
│   │   ├── store/                      # Zustand stores (apiKeyStore, chatStore)
│   │   ├── lib/                        # Utilities (api.ts, types.ts, queryClient.ts)
│   │   └── styles/                     # Tailwind + global styles
│   ├── vite.config.ts                  # Vite config with API proxy (localhost:8000)
│   ├── package.json                    # Node dependencies
│   └── tsconfig.json                   # TypeScript config
├── api/                                # FastAPI backend
│   ├── main.py                         # FastAPI app factory & startup
│   ├── dependencies.py                 # Shared dependencies
│   ├── state.py                        # Global state management
│   ├── routers/                        # API endpoints
│   │   ├── health.py                   # Health check endpoint
│   │   ├── qa.py                       # /api/v1/qa - RAG query endpoint
│   │   ├── mapper.py                   # /api/v1/mapper - Section mapping
│   │   ├── profile.py                  # /api/v1/profile - Profile analysis
│   │   ├── notice.py                   # /api/v1/notice - Notice decoding
│   │   ├── ingestion.py                # /api/v1/ingest - FAISS index building
│   │   └── compare.py                  # /api/v1/compare - Mapping comparison
│   ├── schemas/                        # Pydantic request/response models
│   │   ├── qa.py, mapper.py, profile.py, notice.py, ingestion.py, etc.
│   └── utils/                          # API utilities
│       └── section_extractor.py        # PDF section analysis
├── src/                                # Core Python business logic (shared by backend & CLI)
│   ├── config.py                       # All configuration, API keys, constants
│   ├── ingest.py                       # PDF ingestion -> semantic chunks -> embeddings -> FAISS
│   ├── rag_engine.py                   # RAG pipeline: embed query -> FAISS search -> Gemini generate
│   ├── section_mapper.py               # Old-to-new section mapping (JSON-first, RAG fallback)
│   ├── profile_analyzer.py             # Personalized impact analysis by taxpayer profile
│   ├── notice_decoder.py               # Tax notice decoder with severity rating
│   ├── prompts.py                      # ALL Gemini prompt templates (centralized)
│   ├── query_logger.py                 # Query event logging to JSONL
│   ├── ragas_evaluator.py              # Quality evaluation using RAGAS metrics
│   ├── content_filter.py               # Offline tax relevance filtering
│   ├── providers/                      # LLM provider abstraction (Gemini, OpenAI, Claude, Ollama, OpenRouter)
│   ├── analytics.py, security.py       # Analytics tracking & security controls
│   └── app.py                          # Legacy Streamlit app (replaced by FastAPI + React)
├── data/
│   ├── pdfs/                           # Source PDFs (gitignored)
│   │   ├── Income Tax Act 2025/        # 536 individual section PDFs + 16 schedule PDFs
│   │   ├── Income_Tax_Act_2025_as_amended_by_FA_Act_2026.pdf
│   │   ├── Income Tax Rules 2026.pdf
│   │   ├── Finance Bill 2026.pdf
│   │   └── The_Income-tax_Bill,_2025.pdf
│   ├── faiss_index/                    # Generated FAISS index (built)
│   │   ├── index.faiss                 # FAISS vector index (11M)
│   │   ├── chunks.json                 # Chunk metadata (5.2M)
│   │   ├── checkpoint.json             # Ingestion progress checkpoint
│   │   └── ingestion_progress.json     # Final ingestion status (100%)
│   ├── section_mapping.json            # Old-to-new section mapping (COMMITTED, offline backbone)
│   └── dropdown_options_raw.json       # Raw scraped mapping data
├── tools/
│   ├── scrape_mapping.py               # Playwright scraper for govt mapping utility
│   └── analyze_logs.py                 # Query log and RAGAS analysis tool
├── requirements.txt                    # Python dependencies (backend + src)
├── .env.example                        # GEMINI_API_KEY=your-key-here
├── .gitignore
├── Dockerfile                          # Multi-stage: builds frontend, copies to backend
├── docker-compose.yml                  # (Optional) Local development
├── CLAUDE.md                           # This file
├── plan.md, PRD.md, IDEA.md, README.md
├── PROJECT_STATUS.md                   # Current status & completion
└── PHASE*_*.md                         # Phase completion docs
```

### File Purposes

| File | Role | Can modify independently? |
|------|------|--------------------------|
| `config.py` | Loads .env, exports API keys, model names, chunk sizes, retrieval params. No magic numbers elsewhere. | Yes |
| `prompts.py` | All prompt templates as string constants. Logic-free. | Yes |
| `ingest.py` | Standalone script. Run once to build FAISS index from PDFs. | Yes |
| `rag_engine.py` | Core RAG class: `retrieve()` and `answer()`. All other modules depend on this. | Carefully |
| `section_mapper.py` | `SectionMapper` class. Works entirely from JSON offline; RAG is optional enhancement. | Yes |
| `profile_analyzer.py` | `ProfileAnalyzer` class. 5 profiles, each with focus sections and RAG queries. | Yes |
| `notice_decoder.py` | `NoticeDecoder` class. Gemini-powered with regex fallback. | Yes |
| `app.py` | Streamlit UI. Wires all modules together. Session state management. | Yes |
| `section_mapping.json` | **Offline backbone.** Must always work without API. ~120+ verified mappings. | Yes (data only) |

---

## How to Run

### First-time setup
```bash
# 1. Python backend
python -m venv venv
source venv/Scripts/activate  # Windows bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 2. Node frontend
cd frontend
npm install
cd ..
```

### Ingestion (run once, or when PDFs change)
```bash
python src/ingest.py
```
Reads all PDFs from `data/pdfs/` (recursive), creates semantic chunks, generates embeddings via `gemini-embedding-001`, builds FAISS index. Saves to `data/faiss_index/`. Checkpoints after every batch -- safe to interrupt and resume.
**Status:** ✅ COMPLETED (1,842 vectors built)

### Run locally (development)
```bash
# Terminal 1: Backend (FastAPI on port 8000)
python api/main.py
# or: uvicorn api.main:app --reload

# Terminal 2: Frontend (React/Vite on port 5173)
cd frontend
npm run dev

# Opens at http://localhost:5173 (proxies /api to 8000)
```

### Run tests
```bash
python test_integration.py       # Test all features offline
python test_performance.py       # Performance benchmarks
python tools/analyze_logs.py     # Analyze query logs & RAGAS metrics
```

### Docker deployment
Multi-stage Dockerfile: builds React frontend, copies to backend, serves from FastAPI on port 8000.
```bash
# Build
docker build -t taxgpt-india .

# Run locally
docker run -p 8080:8000 -e GEMINI_API_KEY=your-key taxgpt-india

# Or Cloud Run
gcloud run deploy taxgpt-india \
  --image gcr.io/PROJECT_ID/taxgpt-india \
  --region us-central1 \
  --memory 2Gi \
  --set-env-vars GEMINI_API_KEY=your-key
```

---

## Architecture Decisions

### Modular, self-contained classes
Each feature is an independent class with a clear interface. You can swap FAISS for Pinecone, Gemini for GPT-4, or static JSON for a live API -- without touching other modules. Interfaces:
- `TaxRAGEngine.answer(question, chat_history, language) -> dict`
- `SectionMapper.map_section(old_section) -> dict`
- `ProfileAnalyzer.analyze(profile_type) -> dict`
- `NoticeDecoder.decode(notice_text) -> dict`

### Graceful degradation strategy
Every feature has a fallback when the Gemini API is unavailable:

| Failure | Section Mapper | Tax Q&A | Profile Analyzer | Notice Decoder |
|---------|---------------|---------|-----------------|----------------|
| Gemini API down | Full functionality from JSON | Error msg + suggest Section Mapper | Pre-written static summaries | Regex-based section detection + generic guidance |
| FAISS index missing | JSON still works | Show: "Run `python src/ingest.py` to build the knowledge base" | Show: same setup message | Show: same setup message |
| Both down | JSON still works | Setup instructions | Setup instructions | Setup instructions |

The Section Mapper is the reliability anchor -- it must NEVER require an API call for known mappings.

### Semantic chunking (section-aware, NOT naive character splitting)
- **Individual section PDFs**: Each section = one chunk. Split at sub-section boundaries (`\(\d+\)`) if > 3000 chars.
- **Full Act PDF**: Detect section boundaries via regex (`^Section\s+\d+`, chapter headers). Keep sections intact.
- **Rules PDF**: Split at Rule boundaries.
- **Finance Bill**: Larger chunks (~2000 chars) at clause boundaries.
- **Overlap**: 200 chars between sub-chunks within the same parent section.
- **Short sections**: Sections under 200 chars (e.g., single-line definitions) should be grouped with related short sections in the same sub-chapter to avoid retrieval misses.
- **Proviso rule**: Indian tax sections have a hierarchy: Section > Sub-section (1), (2) > Clause (a), (b) > Proviso ("Provided that...") > Explanation. Provisos and Explanations must always be chunked with their parent sub-section, never split from them.

**Deduplication**: Individual section PDFs overlap with full Act PDF. Priority: section PDFs win (cleaner metadata). For each full-Act chunk, compute text overlap with existing section chunks. If overlap > 80%, skip the full-Act chunk. Keep non-overlapping full-Act chunks (chapter intros, preamble, transitional provisions).

### Retrieval pipeline
1. **Old section detection**: Check if query contains old 1961 section references (regex). If found, augment query with the new section number from the mapping before embedding.
2. **FAISS search**: Embed query via `gemini-embedding-001`, search for top 8 chunks (`RETRIEVAL_TOP_K = 8`).
3. **Parent enrichment**: For each returned chunk, also fetch its parent chunk (chapter context) if not already in results.
4. **Dedup results**: Same section appearing from multiple sources (section PDF + full Act) → keep the one with richer metadata.
5. **Reorder**: Direct section matches first, then related sections, then parent context.

**Context window budget for Gemini prompt (~4500 tokens max):**
| Slot | Budget |
|------|--------|
| Parent context | ~500 tokens (1 chunk) |
| Direct matches | ~2000 tokens (3-4 chunks) |
| Related sections | ~1500 tokens (2-3 chunks) |
| Chat history | ~500 tokens (last 3 turns) |

### Chat history
- Last 3 Q&A turns are passed as context to Gemini for follow-up understanding
- Stored in `st.session_state["chat_history"]` (max 5 turns kept, last 3 sent to prompt)
- **Clears on tab switch.** A "Clear Chat" button resets `st.session_state["chat_history"]`.
- Session-only in v1; persistent across sessions in v2 (via `chat_storage.py`).

### Streamlit caching
- `@st.cache_resource`: FAISS index loading, Gemini client initialization
- `@st.cache_data`: `section_mapping.json` loading
- Profile analysis results: cache after first generation per profile in session state (only 5 profiles)

### Cost awareness
- `gemini-2.0-flash` costs ~$0.001-0.003 per query
- Batch embeddings at batch size 20 to minimize API calls during ingestion
- At 1K queries/day: ~$2-3/day. At 10K: ~$20-30/day
- Avoid unnecessary re-embedding; ingestion is run once

---

## Domain Knowledge

### Critical rule: ALWAYS cite NEW Act 2025 sections
The entire value proposition is citing the correct new sections. If the system outputs old 1961 section numbers, it is useless. Every prompt must instruct Gemini to cite NEW sections only.

**Old section detection in queries**: When a user asks using old section numbers (e.g., "What is Section 80C?"):
1. Recognize the old section reference via regex
2. Look up the corresponding new section from `section_mapping.json`
3. Answer citing the NEW section number
4. Explicitly state: "Note: Section 80C of the 1961 Act corresponds to Section 123 of the new Income Tax Act, 2025."

### Section mapping edge cases
| Scenario | Display approach |
|----------|-----------------|
| One-to-one (80C → 123) | Standard mapping card |
| One-to-many split (80CCD → 124 and 125) | Show multiple new sections, explain what went where |
| Many-to-one merge (192-194T → 393) | Show single new section, note what was consolidated |
| Section deleted (e.g., 10A) | Show "Removed" with explanation |
| Concept change (Assessment Year → Tax Year) | Different card style for concepts |
| Form mapping (Form 16 → Form 130) | Different card style for forms |

### Key terminology changes
| Old (1961 Act) | New (2025 Act) |
|----------------|----------------|
| Assessment Year / Financial Year / Previous Year | Tax Year (Section 3) |
| Form 16 | Form 130 |
| Form 26AS | Form 168 |
| Section 80C (deductions) | Section 123 |
| Section 80D (health insurance) | Section 126 |
| Sections 192-194T (TDS, scattered) | Section 393 (single consolidated table) |
| Section 139 (return filing) | Section 263 |
| Section 143(1) (intimation) | Section 270 |
| Section 148 (reassessment) | Section 279 |
| Section 87A (rebate) | Section 156 |
| Section 115BAC (new tax regime) | Section 202 |

### Section mapping JSON structure
```json
{
  "old_to_new": {
    "80C": {
      "new_section": "123",
      "title_old": "Deduction in respect of life insurance premia, etc.",
      "title_new": "...",
      "change_summary": "...",
      "category": "deductions"
    }
  },
  "concepts": {
    "Assessment Year": { "new_concept": "Tax Year", "new_section": "3", ... }
  },
  "forms": {
    "Form 16": { "new_form": "Form 130", "purpose": "TDS Certificate for Salary", ... }
  }
}
```

### Taxpayer profiles (for Profile Analyzer)
- `salaried` -- Tax Year, standard deduction, HRA 8-city expansion, NPS 14%, Form 130
- `business` -- ITR deadline Aug 31, TDS consolidation (Sec 393), MAT 14%, presumptive taxation
- `investor` -- STT increase on F&O, buyback taxation, LTCG/STCG changes
- `nri` -- Foreign asset disclosure, TAN removal, residential status, DTAA
- `freelancer` -- Presumptive taxation thresholds, TDS, advance tax, ITR deadlines

### Hindi language detection
```python
import re
is_hindi = bool(re.search(r'[\u0900-\u097F]', query_text))
```

---

## Common Tasks

### Add a new section mapping
Edit `data/section_mapping.json`. Add entry under `old_to_new`, `concepts`, or `forms` as appropriate. No code changes needed -- `SectionMapper` loads this file at init.

### Add a new taxpayer profile
In `src/profile_analyzer.py`, add a new entry to the `PROFILES` dict with `label`, `focus_sections`, and `rag_queries`. Add the corresponding radio button label in `src/app.py` Tab 3. Add a static fallback summary in the same class.

### Update a prompt
Edit the string constant in `src/prompts.py`. All prompts are centralized there. No logic in this file -- just template strings. **After modifying a prompt**, test with at least 3 queries: one English, one Hindi, and one that references an old section number. Verify citations are correct and the disclaimer is present.

### Add a new data source (PDF)
1. Place PDF in `data/pdfs/`
2. Re-run `python src/ingest.py` (it processes all PDFs and rebuilds the index)
3. The RAG engine picks up the new index on next app restart

### Change the embedding or generation model
Update the model name constants in `src/config.py`. The embedding dimension may change -- if so, rebuild the FAISS index.

### Add a new UI tab
In `src/app.py`, add a new tab in the `st.tabs()` call. Create a new module class following the pattern of existing ones (self-contained class with a single public method, graceful fallback).

---

## Coding Conventions

- **All constants in `config.py`** -- no magic numbers or strings in other files
- **All prompts in `prompts.py`** -- no prompt text in logic files
- **Every API call wrapped in try/except** -- return graceful error messages, never crash
- **Type hints on public method signatures**
- **Chunk metadata always includes**: `id`, `text`, `source`, `source_file`, `section_number`, `chapter`, `parent_id`, `chunk_index`, `total_chunks`
- **Input normalization in section mapper**: strip whitespace, remove "Section" prefix, case-insensitive matching before exact lookup
- **Disclaimer on every response** -- Tax Q&A, Section Mapper results, Profile Analysis, AND Notice Decoder. No exceptions.
- **Privacy notice on Notice Decoder**: Must display: "Your notice text is processed by Google's Gemini AI and is subject to Google's data policies." (in addition to standard disclaimer)
- **Batch embeddings**: batch size 20, exponential backoff (1s to 60s)
- **Generation retry**: Single call per user query, retry once on transient failure, then return graceful error
- **Session state keys**: `chat_history`, `current_tab`, `mapper_result`, `profile_result`, `notice_result`
- **Input validation**: Tax Q&A: min 10 chars, max 2000 chars. Notice Decoder: min 50 chars, max 10000 chars. Disable submit button on invalid input.

### Config constants reference
All in `src/config.py`:
```
GEMINI_API_KEY, EMBEDDING_MODEL ("gemini-embedding-001"), GENERATION_MODEL ("gemini-2.0-flash"),
RETRIEVAL_TOP_K (8), MAX_CHUNK_SIZE (3000), CHUNK_OVERLAP (200), EMBEDDING_BATCH_SIZE (20),
CONTEXT_TOKEN_BUDGET (4500), CHAT_HISTORY_MAX (5), CHAT_HISTORY_CONTEXT (3)
```

---

## Testing

No automated test suite (v1). Verify manually:

1. **Ingestion**: `python src/ingest.py` -- all 536 section PDFs + 16 schedules + 4 main PDFs processed, dedup works, FAISS index saved
2. **RAG queries**: "What is the new section for 80C?" should cite Section 123. Hindi query should get Hindi response.
3. **Section Mapper**: "80C" -> Section 123 instantly from JSON. Unknown section falls back to RAG. Invalid API key -> still works from JSON.
4. **Profile Analyzer**: Each profile returns structured output. API failure -> static fallback displayed.
5. **Notice Decoder**: Pasted 143(1) intimation -> identifies as Section 270 of new Act with severity badge.
6. **Graceful degradation**: Set invalid API key, verify Section Mapper still works, other features show friendly errors.

---

## What NOT to Do

### Python/Backend
- **Do NOT use `google-generativeai` package.** The correct package is `google-genai`. They have different APIs.
- **Do NOT cite old 1961 Act section numbers in answers.** Always map to new 2025 sections.
- **Do NOT use naive character splitting for chunking.** Use section-aware boundaries.
- **Do NOT make Section Mapper depend on the API.** JSON lookups must work fully offline.
- **Do NOT put prompts inline in logic files.** All prompts go in `prompts.py`.
- **Do NOT put magic numbers in source files.** All constants go in `config.py`.
- **Do NOT skip the disclaimer** on any tax-related response.
- **Do NOT use `load_dotenv()` without `encoding="utf-8-sig"`.** Will silently fail on Windows.
- **Do NOT hardcode file paths with backslashes.** Use `os.path.join()` or `pathlib.Path` for cross-platform compatibility.
- **Do NOT store PDFs or FAISS index in git.** They are gitignored. Only `section_mapping.json` is committed.
- **Do NOT break module interfaces.** Each module's public method signature is its contract. Add parameters with defaults, don't change existing signatures.
- **Do NOT return any tax-related response without the disclaimer.** This includes Section Mapper results, profile analysis, notice decoding, AND Q&A answers. No exceptions.
- **Do NOT send notice text to Gemini without displaying the privacy notice** about data being processed by Google's AI.

### Frontend/React
- **Do NOT hardcode API URLs.** Use environment variables or the `api.ts` utility.
- **Do NOT make synchronous API calls.** Use React Query (`useQuery`, `useMutation`) for all server communication.
- **Do NOT store sensitive data in Zustand.** API keys are OK (user-provided); session tokens are NOT.
- **Do NOT bypass TypeScript.** All API responses must have type-safe schemas in `lib/types.ts`.
- **Do NOT fetch inside components.** Use custom hooks (`useQA`, `useMapper`, etc.) in `hooks/`.
- **Do NOT render without error boundaries.** Components must gracefully handle API failures.
- **Do NOT hardcode Tailwind breakpoints.** Use responsive classes (`sm:`, `md:`, `lg:`).

### FastAPI/Backend
- **Do NOT expose raw Python errors.** All exceptions must return structured JSON error responses.
- **Do NOT skip CORS configuration.** Requests from React (localhost:5173) must be allowed.
- **Do NOT use `GET` for mutations.** Searches are OK, but any write operation must be `POST`.
- **Do NOT store state in global variables.** Use FastAPI's dependency injection or state management.
- **Do NOT start heavy operations in request handlers.** Use background tasks or startup events (e.g., section mapper warmup).
- **Do NOT return raw FAISS results.** Always format as JSON with metadata and citations.

---

## Performance Targets

| Feature | Target |
|---------|--------|
| Tax Q&A response | < 8 seconds |
| Section Mapper (JSON hit) | < 0.5 seconds |
| Section Mapper (RAG fallback) | < 6 seconds |
| Profile Analysis | < 12 seconds |
| Notice Decoding | < 10 seconds |
| Page load (cold start) | < 5 seconds |
| Full ingestion pipeline | < 30 minutes |

---

## UI Reference

### Sidebar content
- "About TaxGPT India" (2-line description)
- Key stats: "536 sections | 333 rules | 80M taxpayers affected"
- Popular Questions (clickable, populate Tab 1 input): "What happened to Section 80C?", "Is income up to 12 lakh still tax-free?", "What is Tax Year?", "New HRA rules for Bangalore and Pune", "STT increase on F&O trading"
- "Built by Ayush Yuvraj" with portfolio/LinkedIn/GitHub links

---

## Git Workflow

**Committed:** All `src/` files, `data/section_mapping.json`, `data/dropdown_options_raw.json`, config files (`.streamlit/`, `.gitignore`, `.env.example`), `requirements.txt`, `Dockerfile`, `README.md`, docs (`CLAUDE.md`, `plan.md`, `PRD.md`, `IDEA.md`).

**Gitignored:** `data/pdfs/`, `data/faiss_index/`, `.env`, `venv/`, `__pycache__/`, IDE folders.

---

## Tooling

### Playwright scraper (`tools/scrape_mapping.py`)
Standalone script to scrape the government mapping utility (v2/v3). **Not a production dependency.** Install separately:
```bash
pip install playwright && playwright install chromium
```

### Ingestion checkpoint (`data/faiss_index/checkpoint.json`)
Tracks `{last_processed_file, last_batch_index, total_chunks_so_far}`. Enables safe interrupt/resume of multi-hour ingestion runs.

---

## Environment Setup

### requirements.txt
```
streamlit>=1.30.0
google-genai>=1.0.0
faiss-cpu>=1.7.4
numpy>=1.24.0
PyPDF2>=3.0.0
python-dotenv>=1.0.0
```

### .env
```
GEMINI_API_KEY=your-gemini-api-key-here
```

### .streamlit/config.toml
```toml
[theme]
primaryColor = "#1B5E20"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#E8F5E9"
textColor = "#1B1B1B"
font = "sans serif"

[server]
headless = true
```

---

## Data Inventory

| Source | Location | Notes |
|--------|----------|-------|
| Income Tax Act 2025 (amended) | `data/pdfs/Income_Tax_Act_2025_as_amended_by_FA_Act_2026.pdf` | Primary source, 3.2MB |
| Income Tax Bill 2025 (original) | `data/pdfs/The_Income-tax_Bill,_2025.pdf` | 8.7MB |
| Income Tax Rules 2026 | `data/pdfs/Income Tax Rules 2026.pdf` | 9.1MB |
| Finance Bill 2026 | `data/pdfs/Finance Bill 2026.pdf` | 1.7MB |
| Individual section PDFs (536) | `data/pdfs/Income Tax Act 2025/Section-*.pdf` | ~130MB total |
| Schedule PDFs (16) | `data/pdfs/Income Tax Act 2025/Schedule-*.pdf` | ~7MB total |
| Section mapping | `data/section_mapping.json` | Compiled from TaxHeal, EzTax, ClearTax |
| Raw scrape data | `data/dropdown_options_raw.json` | Scraped mapping utility data |
