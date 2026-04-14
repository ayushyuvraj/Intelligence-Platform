# TaxGPT India — Implementation Plan

## Context

India replaced its Income Tax Act (1961) with the Income Tax Act, 2025, effective April 1, 2026. 80M+ taxpayers are confused — every section number, form number, and terminology has changed. TaxGPT India is a RAG-powered AI tool that answers tax questions citing the NEW Act, maps old sections to new ones, provides personalized impact analysis, and decodes tax notices. This positions the user (Ayush Yuvraj) as a strong Google L6 candidate and serves a massive real-world need.

**Key design principle:** Every feature is modular and self-contained. New features in v2/v3 either add new modules or cleanly replace existing ones without breaking existing functionality.

---

## Data Inventory (Already Available)

| Source | Location | Size |
|--------|----------|------|
| Income Tax Act 2025 (amended by FA 2026) | `data/pdfs/Income_Tax_Act_2025_as_amended_by_FA_Act_2026.pdf` | 3.2MB |
| Income Tax Bill 2025 (original) | `data/pdfs/The_Income-tax_Bill,_2025.pdf` | 8.7MB |
| Income Tax Rules 2026 | `data/pdfs/Income Tax Rules 2026.pdf` | 9.1MB |
| Finance Bill 2026 | `data/pdfs/Finance Bill 2026.pdf` | 1.7MB |
| Individual Section PDFs (536) | `data/pdfs/Income Tax Act 2025/Section-*.pdf` | ~130MB |
| Schedule PDFs (16) | `data/pdfs/Income Tax Act 2025/Schedule-*.pdf` | ~7MB |
| **Section mapping data** | Scraped from TaxHeal (200+), EzTax (39), ClearTax (~15) | In-memory (to be compiled) |

---

## Project Structure

```
taxgpt-india/
├── data/
│   ├── pdfs/                           # Source PDFs (gitignored)
│   │   ├── Income Tax Act 2025/        # 536 section + 16 schedule PDFs
│   │   ├── Income_Tax_Act_2025_as_amended_by_FA_Act_2026.pdf
│   │   ├── Income Tax Rules 2026.pdf
│   │   ├── Finance Bill 2026.pdf
│   │   └── The_Income-tax_Bill,_2025.pdf
│   ├── faiss_index/                    # Generated FAISS index (gitignored)
│   │   ├── index.faiss
│   │   └── chunks.json
│   └── section_mapping.json            # Old-to-New section mapping (committed)
├── src/
│   ├── app.py                          # Streamlit main app (entry point)
│   ├── config.py                       # Configuration, API keys, constants
│   ├── ingest.py                       # PDF ingestion → semantic chunks → embeddings → FAISS
│   ├── rag_engine.py                   # RAG pipeline: retrieve + generate with citations
│   ├── section_mapper.py               # Old-to-new section mapping logic
│   ├── profile_analyzer.py             # "What Changed For Me?" personalized analysis
│   ├── notice_decoder.py               # Tax notice decoder
│   └── prompts.py                      # All Gemini prompts centralized
├── tools/
│   └── scrape_mapping.py              # Playwright scraper for govt mapping utility (v2/v3)
├── requirements.txt
├── .env.example
├── .gitignore
├── .streamlit/
│   └── config.toml
├── Dockerfile
└── README.md
```

---

## Phase 1: Foundation (config, data, ingestion)

### Step 1.1 — Project scaffolding
Create all directories, `.gitignore`, `.env.example`, `requirements.txt`, `.streamlit/config.toml`.

**requirements.txt:**
```
streamlit>=1.30.0
google-genai>=1.0.0
faiss-cpu>=1.7.4
numpy>=1.24.0
PyPDF2>=3.0.0
python-dotenv>=1.0.0
```

### Step 1.2 — `src/config.py`
- Load `.env` with BOM handling (`encoding="utf-8-sig"`)
- Export `GEMINI_API_KEY`, model names, chunk sizes, retrieval params
- All constants in one place — no magic numbers elsewhere

### Step 1.3 — `data/section_mapping.json`
Compile the scraped mapping data into a structured JSON file:
- **~120+ unique verified mappings** from TaxHeal, EzTax, ClearTax
- Structure:
```json
{
  "old_to_new": {
    "80C": {
      "new_section": "123",
      "title_old": "Deduction in respect of life insurance premia, etc.",
      "title_new": "Deduction in respect of life insurance premia, etc.",
      "change_summary": "Available only under old tax regime. Overall limit of Rs 1.5 lakh unchanged.",
      "category": "deductions"
    }
  },
  "concepts": {
    "Assessment Year": {
      "new_concept": "Tax Year",
      "new_section": "3",
      "change_summary": "Assessment Year and Financial Year/Previous Year abolished. Replaced by single Tax Year concept."
    }
  },
  "forms": {
    "Form 16": {
      "new_form": "Form 130",
      "purpose": "TDS Certificate for Salary",
      "status": "draft"
    }
  }
}
```

### Step 1.4 — `src/ingest.py` (Semantic Chunking + FAISS)

**Ingestion pipeline:**

1. **PDF text extraction** using PyPDF2 from all files in `data/pdfs/` (recursive)
2. **Semantic chunking strategy (section-aware + parent-child):**
   - **For individual section PDFs** (`data/pdfs/Income Tax Act 2025/Section-*.pdf`): Each section PDF becomes one chunk. If section text > 3000 chars, split at sub-section boundaries (`\(\d+\)` patterns). Each chunk gets a `parent_id` = chapter identifier.
   - **For full Act PDF** (`Income_Tax_Act_2025_as_amended_by_FA_Act_2026.pdf`): Detect section boundaries using regex patterns (`^Section\s+\d+`, `^\d+\.\s`, chapter headers). Keep each section as one chunk, split oversized sections at sub-section boundaries.
   - **For Rules PDF**: Similar section-aware splitting at Rule boundaries
   - **For Finance Bill**: Larger chunks (~2000 chars) at clause boundaries
   - **Overlap**: 200-char overlap between split sub-chunks (within the same parent section)

3. **Chunk metadata:**
   ```python
   {
     "id": "act2025_section_80_chunk_0",
     "text": "...",
     "source": "Income Tax Act 2025 (Section 80)",
     "source_file": "Section-80_..._en.pdf",
     "section_number": "80",
     "chapter": "VIII - Deductions",
     "parent_id": "chapter_viii",
     "chunk_index": 0,
     "total_chunks": 1
   }
   ```

4. **Deduplication**: Since we have both individual section PDFs AND the full Act PDF, detect near-duplicate chunks by text similarity and keep the one with better metadata.

5. **Embeddings**: `gemini-embedding-001`, batch size 20, exponential backoff (1s to 60s), checkpoint after every batch (save progress to `data/faiss_index/checkpoint.json`).

6. **FAISS index**: `IndexFlatIP` with L2 normalization for cosine similarity. Save `index.faiss` + `chunks.json`.

**Run:** `python src/ingest.py` — prints progress per PDF, chunk count, dedup stats, total index size.

---

## Phase 2: RAG Engine + Prompts

### Step 2.1 — `src/prompts.py`
Centralized prompt templates:
- `TAX_QA_PROMPT` — Q&A with citations, language awareness, disclaimer
- `SECTION_MAPPER_FOLLOWUP_PROMPT` — Follow-up questions about a mapped section
- `PROFILE_IMPACT_PROMPT` — Personalized impact analysis per taxpayer profile
- `NOTICE_DECODER_PROMPT` — Tax notice analysis with severity rating
- All prompts instruct Gemini to cite NEW Act sections only

### Step 2.2 — `src/rag_engine.py`

**Core class: `TaxRAGEngine`**

```python
class TaxRAGEngine:
    def __init__(self):
        # Load FAISS index + chunks on init
        # Initialize Gemini client
    
    def retrieve(self, query: str, top_k: int = 8) -> list[dict]:
        # Embed query -> search FAISS -> return top_k chunks
        # ALSO retrieve parent chunks for context enrichment
    
    def answer(self, question: str, chat_history: list = None, language: str = "auto") -> dict:
        # 1. Detect language (Devanagari regex for Hindi)
        # 2. Retrieve relevant chunks
        # 3. Include last 3 chat turns as context
        # 4. Construct prompt with chunks + history
        # 5. Generate via gemini-2.0-flash
        # 6. Return: {"answer": str, "sources": list, "language": str}
    
    def answer_with_fallback(self, question: str, ...) -> dict:
        # Try Gemini API. On failure, return graceful error message
        # For section-related queries, try static mapping as fallback
```

**Key features:**
- **Parent-child retrieval**: When a chunk scores high, also pull its parent (chapter context) into the prompt
- **Chat history**: Last 3 Q&A turns included in prompt context via `chat_history` parameter
- **Language detection**: Devanagari character regex `[\u0900-\u097F]`
- **Graceful degradation**: Try/except around all API calls, return helpful error messages

---

## Phase 3: Feature Modules (each self-contained)

### Step 3.1 — `src/section_mapper.py`

**Class: `SectionMapper`**

```python
class SectionMapper:
    def __init__(self, mapping_path, rag_engine=None):
        # Load section_mapping.json
        # Optional RAG engine for unknown sections
    
    def map_section(self, old_section: str) -> dict:
        # 1. Normalize input (strip whitespace, handle "Section 80C" -> "80C")
        # 2. Check static mapping (exact match, then fuzzy)
        # 3. If not found AND rag_engine available, search RAG
        # 4. Return: {old, new, title, change_summary, source: "official"/"rag"}
    
    def get_all_mappings(self) -> dict:
        # Return full mapping for display
    
    def get_popular_sections(self) -> list:
        # Return list of commonly queried sections for quick-access buttons
```

**Graceful degradation**: Works entirely from JSON when Gemini API is down. RAG only used for sections not in the static mapping.

### Step 3.2 — `src/profile_analyzer.py`

**Class: `ProfileAnalyzer`**

```python
class ProfileAnalyzer:
    PROFILES = {
        "salaried": { "label": "Salaried Employee", "focus_sections": [...], "rag_queries": [...] },
        "business": { "label": "Business Owner", ... },
        "investor": { "label": "Investor & Trader", ... },
        "nri": { "label": "NRI", ... },
        "freelancer": { "label": "Freelancer / Gig Worker", ... },
    }
    
    def analyze(self, profile_type: str) -> dict:
        # 1. Get profile config
        # 2. Retrieve relevant chunks via RAG for each focus area
        # 3. Generate personalized impact summary via Gemini
        # 4. Return structured response with Action Required / Important / Good News / No Change
```

**Fallback**: Pre-written static summaries for each profile type, displayed if Gemini API fails.

### Step 3.3 — `src/notice_decoder.py`

**Class: `NoticeDecoder`**

```python
class NoticeDecoder:
    def decode(self, notice_text: str) -> dict:
        # 1. Send notice text + NOTICE_DECODER_PROMPT to Gemini
        # 2. Parse response into structured format
        # 3. Return: {type, meaning, reason, action, deadline, severity, worry_level}
    
    def decode_with_fallback(self, notice_text: str) -> dict:
        # Try Gemini. On failure, return basic regex-based analysis
        # (detect section numbers mentioned, classify as routine/urgent)
```

---

## Phase 4: Streamlit UI

### Step 4.1 — `src/app.py`

**Layout:**
- Page config: title, icon, wide layout
- **Sidebar**: About section, key stats, popular questions (clickable), author info
- **Main area**: 4 tabs using `st.tabs`

**Tab 1: Ask a Tax Question**
- `st.text_area` for question input
- Language toggle (English/Hindi)
- "Ask TaxGPT" button
- Response with section citations rendered in green badges
- Expandable "Sources" section showing retrieved chunks
- Disclaimer at bottom
- **Chat history**: Stored in `st.session_state["chat_history"]` (list of {question, answer} dicts, last 5 kept). Displayed above input as a conversation thread. Cleared on tab switch.

**Tab 2: Section Mapper**
- `st.text_input` for old section number
- Quick-access buttons: 80C, 80D, 10(13A), 194, 148, 139, Assessment Year
- Result card: old → new with arrow, change summary
- "Ask a follow-up" text input below the result
- Works offline (from JSON) — shows "offline mode" badge if API unavailable

**Tab 3: What Changed For Me?**
- Radio buttons for profile selection
- "Analyze My Impact" button
- Color-coded sections with emoji indicators
- Structured output in st.containers

**Tab 4: Decode a Tax Notice**
- `st.text_area` for pasting notice text
- "Decode This Notice" button
- Severity badge (colored)
- Structured analysis output
- Prominent disclaimer

**Styling:**
- Green/white theme (`.streamlit/config.toml`)
- Professional, clean — targeting CAs and tax professionals
- Responsive layout using `st.columns`

### Step 4.2 — Session state management
```python
# In st.session_state:
"chat_history": [],      # Last 5 Q&A turns
"current_tab": str,      # Track active tab
"mapper_result": dict,   # Last section mapping result
"profile_result": dict,  # Last profile analysis
"notice_result": dict,   # Last notice decode
```

---

## Phase 5: Deployment & Polish

### Step 5.1 — Dockerfile
- Python 3.11-slim base
- Install requirements
- Copy source + pre-built FAISS index + section_mapping.json
- Expose 8080, run Streamlit headless
- **Note**: FAISS index baked into image for fast cold starts

### Step 5.2 — README.md
- Professional README with setup instructions, architecture diagram, author section

### Step 5.3 — `tools/scrape_mapping.py`
- Standalone Playwright script to scrape the government mapping utility
- Iterates through all 1019 dropdown options, captures corresponding 2025 sections
- Saves to `data/section_mapping_official.json`
- For v2/v3 use — not needed for v1 launch

---

## Modularity Design (v2/v3 readiness)

Each module is a self-contained class with a clear interface:

| Module | Interface | Can be replaced independently? |
|--------|-----------|-------------------------------|
| `rag_engine.py` | `answer(question, history, lang)` | Yes — swap FAISS for Pinecone, swap Gemini for GPT-4 |
| `section_mapper.py` | `map_section(old)` -> dict | Yes — swap static JSON for live API scraping |
| `profile_analyzer.py` | `analyze(profile)` -> dict | Yes — add new profiles without touching others |
| `notice_decoder.py` | `decode(text)` -> dict | Yes — add OCR (v2) as preprocessing step before decode |
| `prompts.py` | Template strings | Yes — update prompts without touching logic |
| `ingest.py` | Standalone script | Yes — add new data sources, re-run independently |

**v2 additions (no breaking changes):**
- Persistent chat history -> add `chat_storage.py`, wire into `app.py` session init
- OCR for notices -> add `ocr.py` with `extract_text(image)` interface, call before `notice_decoder.decode()`
- Analytics -> add `analytics.py` logging wrapper, instrument in `app.py`

**v3 additions:**
- Live website scraper -> `tools/scrape_guidelines.py` feeds new data into `ingest.py`
- More languages -> update `prompts.py` language detection + prompt templates

---

## Implementation Order

| # | Task | Files | Dependencies |
|---|------|-------|-------------|
| 1 | Project scaffolding | `.gitignore`, `.env.example`, `requirements.txt`, `.streamlit/config.toml` | None |
| 2 | Config module | `src/config.py` | Step 1 |
| 3 | Section mapping JSON | `data/section_mapping.json` | None |
| 4 | Prompts | `src/prompts.py` | None |
| 5 | Ingestion pipeline | `src/ingest.py` | Steps 1, 2 |
| 6 | RAG engine | `src/rag_engine.py` | Steps 2, 4, 5 |
| 7 | Section mapper | `src/section_mapper.py` | Steps 3, 6 |
| 8 | Profile analyzer | `src/profile_analyzer.py` | Steps 4, 6 |
| 9 | Notice decoder | `src/notice_decoder.py` | Steps 4, 6 |
| 10 | Streamlit app | `src/app.py` | Steps 6-9 |
| 11 | Dockerfile | `Dockerfile` | Step 10 |
| 12 | README | `README.md` | Step 10 |
| 13 | Scraper tool | `tools/scrape_mapping.py` | None (standalone) |

---

## Verification Plan

1. **Ingestion test**: Run `python src/ingest.py`, verify:
   - All PDFs read (536 sections + 16 schedules + 4 main PDFs)
   - Deduplication works (chunk count < raw count)
   - FAISS index saved, loadable
   - Checkpoint/resume works (kill mid-run, restart)

2. **RAG test queries** (run via Streamlit):
   - "What is the new section for 80C?" -> Should cite Section 123
   - "Am I eligible for HRA exemption in Pune?" -> Should cite Section 17 + Rules, mention 8-city expansion
   - "What is Tax Year?" -> Should cite Section 3, explain AY/FY replaced
   - Hindi: "क्या 12 लाख तक की इनकम अभी भी टैक्स फ्री है?" -> Should respond in Hindi
   - Follow-up: After asking about 80C, ask "What about for NRIs?" -> Should maintain context

3. **Section mapper tests**:
   - Type "80C" -> Shows Section 123 with change summary
   - Type "Assessment Year" -> Shows Tax Year (Section 3)
   - Type obscure section not in mapping -> Falls back to RAG
   - API offline -> Still shows results from JSON

4. **Profile analyzer**: Select each profile type, verify structured output with correct sections

5. **Notice decoder**: Paste a sample Section 143(1) intimation, verify it identifies as Section 270 of new Act

6. **Graceful degradation**: Set invalid API key, verify section mapper still works, other features show friendly error

7. **Browser test**: Open `http://localhost:8501`, test all 4 tabs, verify responsive layout, Hindi toggle, sidebar links
