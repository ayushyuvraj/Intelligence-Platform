# BUILD PROMPT: TaxGPT India — AI That Understands India's Entire New Tax Code

## CRITICAL CONTEXT: WHY THIS MATTERS RIGHT NOW

India just replaced its entire Income Tax Act. The Income Tax Act, 2025 came into effect on April 1, 2026 — DAYS AGO. It replaces the 1961 Act that governed India's tax system for 63 years. The old Act had 819 sections and 47 chapters. The new one has 536 sections. The Income Tax Rules 1962 (500+ rules) are replaced by Income Tax Rules 2026 (333 rules). Every section number has changed. Every form number has changed (Form 16 → Form 130, Form 26AS → Form 168). The terms "Financial Year" and "Assessment Year" no longer exist — replaced by a single "Tax Year" concept.

Right now, 80 million Indian taxpayers, 300,000+ Chartered Accountants, every HR department, and every financial advisor in India are confused. Their muscle memory is wrong. Their textbooks are outdated. Their software references obsolete sections.

You are building the AI tool that solves this confusion. Ship it NOW.

## WHAT YOU ARE BUILDING

TaxGPT India is a web application with four core features:

1. **Tax Q&A** — Ask any tax question in English or Hindi, get an answer citing the NEW Income Tax Act 2025 sections (not the old 1961 sections that everyone still accidentally references)

2. **Section Mapper** — Type an old section number (e.g., "80C") and instantly see the corresponding new section, what changed, and what stayed the same

3. **"What Changed For Me?"** — Select your taxpayer profile (salaried/business/investor/NRI/freelancer) and get a personalized summary of how the new Act affects YOU specifically

4. **Tax Notice Decoder** — Paste or describe a tax notice and get a plain-English (or Hindi) explanation of what it means, what action to take, and the deadline

## TECH STACK

- **Frontend:** Streamlit (for speed of shipping — we need this live THIS WEEKEND)
- **Backend:** Python
- **AI:** Google Gemini API (`google-genai` package, model: `gemini-2.0-flash`)
- **RAG:** FAISS vector store + `gemini-embedding-001` for embeddings
- **Deployment:** Google Cloud Run (demonstrates GCP skills) OR Streamlit Community Cloud (for speed)
- **Source data:** Income Tax Act 2025 PDF + Income Tax Rules 2026 + Finance Act 2026 + Section mapping utility

### CRITICAL API USAGE (google-genai, NOT google-generativeai):
```python
from google import genai

client = genai.Client(api_key=GEMINI_API_KEY)

# Embeddings:
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=["text1", "text2"],
)
# Access: result.embeddings[0].values

# Generation:
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="your prompt here",
)
# Access: response.text
```

### .env handling for Windows:
```python
try:
    from dotenv import load_dotenv
    load_dotenv(encoding="utf-8-sig")
except Exception:
    pass
```

## SOURCE DOCUMENTS TO INGEST

Download these PDFs and place them in `data/` directory:

1. **Income Tax Act, 2025 (as amended by Finance Act, 2026)**
   - URL: https://www.incometaxindia.gov.in/documents/d/guest/income_tax_act_2025_as_amended_by_fa_act_2026-pdf
   - This is the PRIMARY source. The entire new Act.

2. **Income Tax Act, 2025 (original)**
   - URL: https://incometaxindia.gov.in/Documents/Act/Income-tax-Act-2025.pdf

3. **Income Tax Rules, 2026**
   - URL: https://www.incometaxindia.gov.in/income-tax-rule-2026
   - Download the full rules PDF from this page

4. **Finance Bill 2026**
   - URL: https://www.indiabudget.gov.in/doc/Finance_Bill.pdf

5. **Section Mapping Utility Data**
   - The Income Tax Department published a utility to map old 1961 sections to new 2025 sections
   - URL: https://incometaxindia.gov.in/Pages/income-tax-bill-2025.aspx
   - Extract this mapping data and store as a structured JSON file

6. **Executive Summary / FAQs on the new Act**
   - Available at the same page: General FAQs on the broad scope of the new Income-tax Bill

## PROJECT STRUCTURE

```
taxgpt-india/
├── data/
│   ├── pdfs/                     # Downloaded source PDFs
│   ├── faiss_index/              # Generated FAISS index
│   ├── chunks.json               # Chunk metadata
│   └── section_mapping.json      # Old section → New section mapping
├── src/
│   ├── app.py                    # Streamlit main app (entry point)
│   ├── config.py                 # Configuration, API keys, constants
│   ├── ingest.py                 # PDF ingestion → chunks → embeddings → FAISS
│   ├── rag_engine.py             # RAG pipeline: retrieve + generate with citations
│   ├── section_mapper.py         # Old-to-new section mapping logic
│   ├── profile_analyzer.py       # "What Changed For Me?" personalized analysis
│   ├── notice_decoder.py         # Tax notice decoder
│   └── prompts.py                # All Gemini prompts centralized
├── requirements.txt
├── .env.example
├── .gitignore
├── .streamlit/
│   └── config.toml
├── Dockerfile                    # For Cloud Run deployment
└── README.md
```

## DOCUMENT INGESTION (src/ingest.py)

### What it does:
1. Reads all PDFs from `data/pdfs/`
2. Extracts text using PyPDF2
3. Chunks into ~1200 character segments with 200 character overlap
4. Breaks at sentence boundaries (look for periods and newlines)
5. Each chunk stores: id, text, source_filename, page_number (if extractable), section_reference (if detectable)
6. Generates embeddings using `gemini-embedding-001` (batch size 20)
7. Builds FAISS IndexFlatIP with L2 normalization for cosine similarity
8. Saves index + chunks.json to `data/faiss_index/`

### Section detection in chunks:
When chunking the Income Tax Act, try to detect section numbers in the text. Regex patterns like:
- `Section \d+` or `section \d+`
- `\d+\.\s` at the start of a paragraph (section numbering)
This metadata helps the section mapper and improves retrieval quality.

### Run once:
```bash
python src/ingest.py
```
Should print progress: which PDF, how many chunks, total chunks, index saved.

## RAG ENGINE (src/rag_engine.py)

### Core function: `answer_tax_question(question, language="english")`

1. Generate query embedding using `gemini-embedding-001`
2. Search FAISS index for top 8 relevant chunks
3. Construct a prompt with the retrieved chunks as context
4. Send to Gemini for answer generation
5. Return: answer text, list of source citations (section numbers + source document)

### The Gemini prompt for Tax Q&A:

```python
TAX_QA_PROMPT = """You are TaxGPT India, an expert AI assistant specializing in the NEW Income Tax Act, 2025 which came into effect on April 1, 2026, replacing the Income Tax Act, 1961.

CRITICAL RULES:
1. ALWAYS cite the NEW Act's section numbers (Income Tax Act, 2025), NOT the old 1961 Act sections
2. If the user asks using an old section number (like "80C" or "10(13A)"), first identify the corresponding NEW section, then answer citing the new section
3. Every factual claim must reference a specific section from the retrieved context
4. If you cannot find the answer in the provided context, say "I couldn't find specific guidance on this in the Income Tax Act, 2025. Please consult a Chartered Accountant for this query."
5. Use simple, clear language. Avoid legal jargon. Explain as if speaking to someone with no tax background.
6. If the user asks in Hindi, respond in Hindi. If in English, respond in English.
7. ALWAYS end with a disclaimer: "This is AI-generated information for educational purposes. Please verify with a qualified CA before making tax decisions."

CONTEXT FROM INCOME TAX ACT, 2025:
{context}

USER QUESTION: {question}

Provide a clear, cited answer:"""
```

### Hindi support:
Detect language of the query (simple heuristic: check for Devanagari characters using regex `[\u0900-\u097F]`). If Hindi, add instruction to respond in Hindi to the prompt.

## SECTION MAPPER (src/section_mapper.py)

### Data source:
The Income Tax Department published a mapping utility. Create a `section_mapping.json` with entries like:

```json
{
  "old_to_new": {
    "10": {"new_section": "11", "title": "Income not included in total income", "change_summary": "Restructured and simplified. Key exemptions retained with clearer language."},
    "10(13A)": {"new_section": "Covered under Section 17 read with Rules", "title": "House Rent Allowance", "change_summary": "HRA exemption now extended to 8 cities at 50% rate including Bangalore, Pune, Hyderabad, Ahmedabad. Relationship disclosure with landlord now required."},
    "80C": {"new_section": "123", "title": "Deduction in respect of life insurance premia, etc.", "change_summary": "Available only under old tax regime. Overall limit of Rs 1.5 lakh unchanged. Consolidated under new section."},
    "80D": {"new_section": "126", "title": "Deduction in respect of health insurance premia", "change_summary": "Limits unchanged. Now under Section 126 of the new Act."},
    "80CCD": {"new_section": "124 and 125", "title": "NPS contributions", "change_summary": "Split into two sections. Employer contribution deduction enhanced to 14% for all employers."},
    "194": {"new_section": "393(1) [Table entries]", "title": "TDS provisions", "change_summary": "ALL TDS provisions consolidated under a single Section 393 with a master table. No more scattered sections."},
    "139": {"new_section": "263", "title": "Return of income", "change_summary": "Filing provisions restructured. ITR-3/4 deadline extended to August 31. Revised return window extended to 12 months."},
    "148": {"new_section": "279", "title": "Income escaping assessment / Reassessment", "change_summary": "Provisions simplified. Focus shifted to substance over procedural technicalities."},
    "Assessment Year": {"new_section": "Tax Year (Section 3)", "title": "Tax Year concept", "change_summary": "Assessment Year and Financial Year/Previous Year abolished. Replaced by single 'Tax Year' concept. Tax Year 2026-27 = April 1, 2026 to March 31, 2027."},
    "Form 16": {"new_section": "Form 130 (draft)", "title": "TDS Certificate for Salary", "change_summary": "Same purpose, new form number under draft Income Tax Rules 2026."},
    "Form 26AS": {"new_section": "Form 168 (draft)", "title": "Annual Tax Statement", "change_summary": "Same purpose, new form number under draft Income Tax Rules 2026."}
  }
}
```

IMPORTANT: This is a SEED mapping. You should include at least 30-50 of the most commonly referenced sections. The user will also be able to ask the RAG system about any section not in this mapping, and the RAG will search the full Act text.

### Function: `map_section(old_section)`
1. Check the mapping JSON first for exact match
2. If not found, search the RAG knowledge base for the old section reference
3. Return: old section, new section, title, what changed

### Streamlit UI for mapper:
- Text input: "Enter old section number (e.g., 80C, 10(13A), 194)"
- Display: Card showing old → new mapping with change summary
- Below: "Ask a follow-up question about this section" input

## PROFILE ANALYZER (src/profile_analyzer.py)

### Function: `analyze_impact(profile_type)`

Profile types:
- **Salaried Employee** — Focus on: Tax Year concept, HRA changes (8 cities now), standard deduction, Form 16 → Form 130, ITR filing deadlines, NPS deduction enhancement
- **Business/Professional** — Focus on: ITR-3 deadline extension to Aug 31, presumptive taxation changes, TDS consolidation under Section 393, MAT reduction to 14%, revised return window extension
- **Investor/Trader** — Focus on: STT rate increase on F&O, buyback taxation change (now capital gains, not dividend), interest deduction removal on dividend income, LTCG/STCG holding period for converted securities
- **NRI** — Focus on: Foreign asset disclosure one-time window, TDS on property purchase (TAN removal), global income taxation rules, residential status determination
- **Freelancer/Gig Worker** — Focus on: Presumptive taxation thresholds, TDS provisions, advance tax requirements, ITR filing deadlines

### Implementation:
For each profile, create a curated prompt that pulls relevant sections from the RAG knowledge base and generates a personalized summary. The summary should be structured as:

```
## What Changed For You as a [Profile Type]

### 🔴 Action Required (Do This Now)
1. [Most urgent change with deadline]
2. [Second most urgent]

### 🟡 Important Changes (Understand This)
1. [Key change with impact explanation]
2. [Key change with impact explanation]

### 🟢 Good News (Benefits)
1. [Positive change]
2. [Positive change]

### ℹ️ No Change (Stays the Same)
1. [Thing people are worried about but hasn't changed]
```

## TAX NOTICE DECODER (src/notice_decoder.py)

### Function: `decode_notice(notice_text)`

Takes the text of a tax notice (user pastes it) and:
1. Identifies the notice type (Section 143(1) intimation, Section 148 reassessment, Section 245 refund adjustment, etc.) — mapping to NEW section numbers
2. Explains in plain English/Hindi what the notice means
3. Lists the specific action required
4. Identifies the deadline for response
5. Rates the severity: 🟢 Routine (e.g., ITR processed), 🟡 Attention Needed (e.g., mismatch found), 🔴 Urgent (e.g., reassessment, demand)

### The Gemini prompt:

```python
NOTICE_DECODER_PROMPT = """You are an expert Indian tax advisor. A taxpayer has received the following tax notice and needs help understanding it.

Analyze the notice and provide:

1. **Notice Type:** Identify the section and type (e.g., "This is an intimation under Section 270 of the Income Tax Act, 2025 (previously Section 143(1) of the 1961 Act)")
2. **What It Means:** Explain in simple language what the Income Tax Department is telling the taxpayer
3. **Why You Got This:** Common reasons this notice is issued
4. **Action Required:** Specific steps the taxpayer should take
5. **Deadline:** When they need to respond (extract from the notice if mentioned)
6. **Severity:** 🟢 Routine / 🟡 Attention Needed / 🔴 Urgent
7. **Should You Worry?** Honest assessment

IMPORTANT: Map any old section references in the notice to the new Income Tax Act 2025 sections.

End with: "⚠️ This is AI-generated guidance. For notices with tax demands or reassessment proceedings, please consult a Chartered Accountant immediately."

NOTICE TEXT:
{notice_text}

Analysis:"""
```

## STREAMLIT APP (src/app.py)

### Page Layout:

```python
st.set_page_config(
    page_title="TaxGPT India — AI for India's New Tax Code",
    page_icon="🇮🇳",
    layout="wide",
)
```

### Header:
```
🇮🇳 TaxGPT India
India's Income Tax Act just changed after 63 years. Ask me anything about the new law.
```

Subtitle stat: "The new Income Tax Act, 2025 went live on April 1, 2026. 536 new sections. 333 new rules. Every section number changed. TaxGPT India helps you navigate the transition."

### Navigation:
Four tabs (use `st.tabs`):

**Tab 1: 💬 Ask a Tax Question**
- Text area for question (placeholder: "e.g., What is the new section for 80C deductions? / HRA exemption rules for Pune? / क्या NPS में employer contribution की limit बढ़ी है?")
- Language toggle: English / Hindi
- "Ask TaxGPT" button
- Response area showing the answer with section citations
- "Sources" expandable section showing retrieved chunks
- Disclaimer at bottom

**Tab 2: 🔄 Section Mapper**
- Text input: "Enter old section number"
- Common section quick-access buttons: "80C", "80D", "10(13A)", "194", "148", "139", "Assessment Year"
- Result card showing old → new mapping with change summary
- "Ask a follow-up about this section" input

**Tab 3: 👤 What Changed For Me?**
- Radio buttons: Salaried Employee / Business Owner / Investor & Trader / NRI / Freelancer
- "Analyze My Impact" button
- Personalized impact summary with color-coded sections (Action Required / Important / Good News / No Change)

**Tab 4: 📋 Decode a Tax Notice**
- Text area: "Paste your tax notice text here"
- "Decode This Notice" button
- Structured analysis with severity badge
- Warning disclaimer

### Sidebar:
- "About TaxGPT India" section
- Key stats: "536 sections in new Act", "333 new rules", "80M taxpayers affected"
- "Built by Ayush Yuvraj" with links
- "Open Source — Star us on GitHub" link
- "Popular Questions" quick-access list:
  - "What happened to Section 80C?"
  - "Is income up to 12 lakh still tax-free?"
  - "What is Tax Year?"
  - "New HRA rules for Bangalore and Pune"
  - "STT increase on F&O trading"

### Styling (.streamlit/config.toml):
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

Use a green/white theme (associated with Indian government / money / tax). Keep it clean and professional — CAs and tax professionals are the early adopters.

## REQUIREMENTS.TXT

```
streamlit>=1.30.0
google-genai>=1.0.0
faiss-cpu>=1.7.4
numpy>=1.24.0
PyPDF2>=3.0.0
python-dotenv>=1.0.0
```

## .GITIGNORE

```
.env
venv/
__pycache__/
*.pyc
data/pdfs/*.pdf
data/faiss_index/
.vscode/
.idea/
.DS_Store
Thumbs.db
```

## .ENV.EXAMPLE

```
GEMINI_API_KEY=your-gemini-api-key-here
```

## DOCKERFILE (for Cloud Run deployment)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-build the FAISS index if data/pdfs/ contains files
# RUN python src/ingest.py

EXPOSE 8080

CMD ["streamlit", "run", "src/app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true"]
```

## SEED DATA FOR SECTION MAPPING

Create a comprehensive `section_mapping.json` with AT LEAST these mappings. Research the correct new section numbers from the Income Tax Act, 2025:

### Individual/Salary related:
- 10 (Exemptions) → Section 11
- 10(13A) (HRA) → Covered under Section 17/Rules
- 10(14) (Special allowances) → Covered under Section 17/Rules
- 16 (Standard deduction) → Section 19
- 17 (Salary definition) → Section 15
- 80C (Investments deduction) → Section 123
- 80CCC (Pension fund) → Merged into Section 123
- 80CCD (NPS) → Sections 124, 125
- 80D (Health insurance) → Section 126
- 80E (Education loan interest) → Section 127 (check)
- 80G (Donations) → Section 133 (check)
- 80TTA (Savings interest) → Section 129 (check)
- 87A (Rebate) → Section 207 (check)

### Business related:
- 44AD (Presumptive taxation) → Check new section
- 44ADA (Professional presumptive) → Check new section
- 115BAC (New tax regime) → Section 202
- 115JB (MAT) → Check new section (rate reduced to 14%)

### Capital gains:
- 111A (STCG on equity) → Check new section
- 112A (LTCG on equity) → Check new section
- 54 (Exemption on house property sale) → Check new section

### TDS:
- 192 (Salary TDS) → All consolidated under Section 393
- 194A (Interest TDS) → Section 393 table
- 194C (Contractor TDS) → Section 393 table
- 194H (Commission TDS) → Section 393 table
- 194I (Rent TDS) → Section 393 table
- 194IA (Property TDS) → Section 393 table

### Filing:
- 139 (Return filing) → Section 263
- 148 (Reassessment) → Section 279
- 143(1) (Intimation) → Section 270
- Assessment Year → Tax Year (Section 3)
- Previous Year → Tax Year (Section 3)

### Forms:
- Form 16 → Form 130 (draft)
- Form 16A → Form 131 (draft)
- Form 26AS → Form 168 (draft)
- ITR-1 (Sahaj) → Check if name changes
- ITR-4 (Sugam) → Check if name changes

NOTE: Some of these new section numbers may be approximate. The builder should verify against the actual Act PDF during ingestion. The RAG system will handle queries about sections not in this mapping by searching the full Act text.

## README.md

```markdown
# 🇮🇳 TaxGPT India

## AI That Understands India's New Tax Code — Before Your CA Does

India just replaced its entire Income Tax Act after 63 years. The Income Tax Act, 2025 went live on April 1, 2026, with 536 new sections replacing 819 old ones. Every section number changed. Every form changed. The concepts of "Assessment Year" and "Financial Year" no longer exist.

**80 million taxpayers are confused. TaxGPT India fixes that.**

### What It Does

- 💬 **Ask any tax question** — Get answers citing the NEW Act sections, not the old ones
- 🔄 **Section Mapper** — Instantly find what happened to Section 80C, 10(13A), 194, or any old section
- 👤 **Personal Impact Analysis** — See exactly what changed for YOUR taxpayer profile
- 📋 **Tax Notice Decoder** — Paste any notice, get a plain-English explanation with action items

### Built With

- Google Gemini AI (gemini-2.0-flash) for intelligent analysis
- RAG architecture over the complete Income Tax Act, 2025 + Rules 2026
- FAISS vector search for accurate section retrieval
- Streamlit for the interface
- Deployed on Google Cloud Run

### Why This Isn't ChatGPT

ChatGPT's training data is primarily based on the old Income Tax Act, 1961. When you ask "What section covers HRA?" it gives you Section 10(13A) — which no longer exists. TaxGPT India is built on a RAG pipeline over the actual new legislation, so every answer cites the correct new sections.

### Setup

[Standard setup instructions: clone, venv, pip install, .env, download PDFs, run ingest, run app]

### Architecture

[ASCII diagram of RAG pipeline]

### Author

Built by **Ayush Yuvraj** — AI Product Leader building decision intelligence systems for financial services.

🌐 [Portfolio](https://ayushyuvraj.com) | 💼 [LinkedIn](https://linkedin.com/in/ayushyuvraj) | 💻 [GitHub](https://github.com/ayushyuvraj)

*"I've spent 3 years building AI compliance systems for India's largest banks. When the new Income Tax Act dropped, I realized 80 million taxpayers needed the same AI-powered guidance that banking compliance teams have. So I built TaxGPT India in a weekend."*

### License

MIT — Use it, fork it, improve it.
```

## CRITICAL REQUIREMENTS

1. **Use `google-genai` package ONLY.** NOT `google-generativeai`. Import: `from google import genai`. Client: `genai.Client(api_key=KEY)`.
2. **Embedding model: `gemini-embedding-001`**. Generation model: `gemini-2.0-flash`.
3. **Handle .env BOM:** `load_dotenv(encoding="utf-8-sig")` in try/except.
4. **Every answer must cite NEW Act sections.** This is the entire value proposition. If the system cites old 1961 sections, it's useless.
5. **Include the disclaimer on every response.** This is tax advice territory — legal protection matters.
6. **Hindi support must work.** Detect Devanagari script and respond in Hindi when asked in Hindi.
7. **The section mapper must be fast and accurate.** This is the feature people will use most in the first weeks. Pre-compute the mapping, don't rely on RAG for known mappings.
8. **All files must be complete.** No placeholders, no TODOs. This ships this weekend.

## LINKEDIN LAUNCH POST

```
India just did something historic.

After 63 years, the entire Income Tax Act has been replaced. The Income Tax Act, 2025 went live on April 1, 2026.

536 new sections. 333 new rules. Every section number changed. "Assessment Year" and "Financial Year" no longer exist.

80 million taxpayers. 300,000 CAs. Every HR department in India.
All confused. All searching for answers.

I built TaxGPT India this weekend:
→ Ask any tax question, get answers citing the NEW Act (not the old one)
→ Instant old-to-new section mapper (What happened to 80C? 80D? 194?)
→ Personalized impact analysis based on your taxpayer profile
→ Tax notice decoder that explains notices in plain English and Hindi

Built on the same RAG architecture I use for enterprise compliance AI at scale. Deployed on Google Cloud.

Free. Open source. No login. Hindi supported.

🔗 Try it: [link]
💻 GitHub: [link]

The old Act served us for 63 years. Let's make sure the new one is understood by everyone, not just CAs.

Tag a friend who needs this right now 👇

#IncomeTax #TaxGPTIndia #AI #NewTaxAct2025 #CA #TaxFiling #India #OpenSource
```

## POST-LAUNCH METRICS TO TRACK

- Total queries per day
- Most asked questions (cluster by topic)
- Section mapper usage (which old sections are most queried)
- Profile distribution (which taxpayer type uses it most)
- Language split (English vs Hindi)
- Notice decoder usage
- Return visits (session-based)
- Geographic distribution (if detectable from Cloud Run logs)

These become your interview talking points: "I discovered that 40% of queries were about the old-to-new section mapping, which told me the transition confusion was the primary pain point. I iterated the UI to make the mapper the default tab."

## AFTER BUILDING

1. Download the Income Tax Act 2025 PDF from the government website
2. Download the Rules 2026 and Finance Bill 2026
3. Place in `data/pdfs/`
4. Run `python src/ingest.py`
5. Run `streamlit run src/app.py`
6. Test with these queries:
   - "What is the new section for 80C?"
   - "Am I eligible for HRA exemption in Pune?"
   - "What is Tax Year?"
   - "क्या 12 लाख तक की इनकम अभी भी टैक्स फ्री है?"
   - "What changed for salaried employees?"
   - "STT on options trading in 2026"
7. Deploy to Cloud Run or Streamlit Cloud
8. Post on LinkedIn
9. Share in every CA group, tax professional group, and student group you can find
10. Watch it spread

## TIME IS EVERYTHING

Every day you wait, the confusion decreases as people figure out the new Act on their own. The window for maximum impact is RIGHT NOW — the first 2-4 weeks after April 1, 2026. Ship this weekend. Polish later. Users first.
