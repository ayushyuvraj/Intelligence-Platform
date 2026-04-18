# TaxGPT India

RAG-powered AI tool helping 80M+ Indian taxpayers navigate the Income Tax Act 2025 (effective April 1, 2026), which replaced the 1961 Act. Every section number, form number, and core terminology changed. This tool answers tax questions citing NEW Act sections, maps old-to-new sections, provides personalized impact analysis, and decodes tax notices.

**Author:** Ayush Yuvraj
**Platform:** Windows (bash shell in Claude Code, but Python paths must handle Windows)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| AI/LLM | Google Gemini (`gemini-2.0-flash` for generation, `gemini-embedding-001` for embeddings) |
| Vector Store | FAISS (`faiss-cpu`, `IndexFlatIP` with L2 normalization for cosine similarity) |
| PDF Parsing | PyPDF2 |
| Language | Python 3.11+ |
| Deployment | Google Cloud Run or Streamlit Community Cloud |

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
├── data/
│   ├── pdfs/                           # Source PDFs (gitignored)
│   │   ├── Income Tax Act 2025/        # 536 individual section PDFs + 16 schedule PDFs
│   │   ├── Income_Tax_Act_2025_as_amended_by_FA_Act_2026.pdf
│   │   ├── Income Tax Rules 2026.pdf
│   │   ├── Finance Bill 2026.pdf
│   │   └── The_Income-tax_Bill,_2025.pdf
│   ├── faiss_index/                    # Generated FAISS index (gitignored)
│   │   ├── index.faiss
│   │   ├── chunks.json
│   │   └── checkpoint.json             # Ingestion progress checkpoint
│   ├── section_mapping.json            # Old-to-new section mapping (COMMITTED, offline backbone)
│   └── dropdown_options_raw.json       # Raw scraped mapping data
├── src/
│   ├── app.py                          # Streamlit entry point (4 tabs UI)
│   ├── config.py                       # All configuration, API keys, constants
│   ├── ingest.py                       # PDF ingestion -> semantic chunks -> embeddings -> FAISS
│   ├── rag_engine.py                   # RAG pipeline: embed query -> FAISS search -> Gemini generate
│   ├── section_mapper.py               # Old-to-new section mapping (JSON-first, RAG fallback)
│   ├── profile_analyzer.py             # Personalized impact analysis by taxpayer profile
│   ├── notice_decoder.py               # Tax notice decoder with severity rating
│   └── prompts.py                      # ALL Gemini prompt templates (centralized)
├── tools/
│   └── scrape_mapping.py               # Playwright scraper for govt mapping utility (v2/v3)
├── .streamlit/
│   └── config.toml                     # Green/white theme, headless server config
├── requirements.txt
├── .env.example                        # GEMINI_API_KEY=your-key-here
├── .gitignore
├── Dockerfile
├── CLAUDE.md                           # This file
├── plan.md                             # Implementation plan
├── PRD.md                              # Product requirements document
├── IDEA.md                             # Original build prompt
└── README.md
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
python -m venv venv
source venv/Scripts/activate  # Windows bash
# PowerShell: .\venv\Scripts\Activate.ps1
# CMD: venv\Scripts\activate.bat
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Ingestion (run once, or when PDFs change)
```bash
python src/ingest.py
```
Reads all PDFs from `data/pdfs/` (recursive), creates semantic chunks, generates embeddings via `gemini-embedding-001`, builds FAISS index. Saves to `data/faiss_index/`. Checkpoints after every batch -- safe to interrupt and resume.

### Run the app
```bash
streamlit run src/app.py
# Opens at http://localhost:8501
```

### Docker deployment
Base image: `python:3.11-slim`. FAISS index is baked into the image (not generated at runtime). Port 8080.
```bash
docker build -t taxgpt-india .
docker run -p 8080:8080 -e GEMINI_API_KEY=your-key taxgpt-india
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
