# Eightfold Multi-Source Candidate Data Transformer

## 1. Project Overview
This project is a robust data transformer designed to ingest noisy candidate information from diverse, conflicting sources. It normalizes fields, deterministically merges identical candidates, resolves field-level conflicts, and outputs a clean, canonical JSON profile with configurable schemas. Currently, the pipeline fully implements and extracts from **Recruiter CSV exports** (structured) and **Resume PDF files** (unstructured).

## 2. Architecture / Pipeline Summary
The system strictly separates internal canonical generation from external schema projection:
- **Detect & Extract**: Parses Recruiter CSV rows and parses Resume PDFs (using hybrid LLM/Regex).
- **Normalize**: Standardizes critical identity signals early (e.g., stripping emails, enforcing E.164 for phones).
- **Merge (Cluster)**: Deterministically groups records into candidates using a threshold-based identity scoring system.
- **Conflict Resolution**: Resolves intra-candidate conflicting values by deferring to a strict source-reliability hierarchy.
- **Confidence & Provenance**: Computes mathematical confidence scores and tracks the exact source origin (and discarded conflicts) for every field.
- **Project & Validate**: Reshapes the canonical internal profile into the requested JSON schema via a dynamic runtime config.

## 3. Prerequisites
- **Python:** 3.11+
- **Packages:** Defined in `requirements.txt` / `pyproject.toml` (e.g., pydantic, pypdf, phonenumbers, pycountry).

## 4. Installation
```bash
git clone <repo-url>
cd eightfold-candidate-transformer
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## 5. API Key Setup — NVIDIA NIM (Llama 3.1 70B Instruct)
Unstructured extraction for Resume PDFs relies on the hosted NVIDIA NIM endpoint for `meta/llama-3.1-70b-instruct` to perform high-accuracy semantic entity extraction.

1. Go to [NVIDIA NIM Llama 3.1 70B Instruct](https://build.nvidia.com/meta/llama-3_1-70b-instruct?nim=hosted)
2. Sign in or create a free NVIDIA developer account.
3. Click **"Get API Key"** on the model page.
4. Copy the generated key (it starts with `nvapi-...`).
5. Set it as an environment variable or add it to a `.env` file at the root of the repository:
   ```bash
   NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxx
   ```
*(Note: Do not commit your `.env` file to version control. The free tier may have rate limits depending on usage volume).*

## 6. Running the Pipeline
You can run the pipeline directly via the installed CLI:

**Default schema run:**
```bash
candidate-transformer --input sample_data/recruiter_export.csv --input sample_data/resume_jane_doe.pdf --out final_merged_profile.json --pretty
```

**Custom config run (if custom config is provided):**
```bash
candidate-transformer --input sample_data/recruiter_export.csv --config configs/my_custom_config.json --out custom_output.json --pretty
```

**CLI Flags:**
- `--input`: Path to input files (can be repeated for multiple files).
- `--config`: (Optional) Path to a custom output projection config JSON. If omitted, the default canonical schema is used.
- `--out`: Output JSON file path.
- `--no-llm`: Disables the LLM extraction path and uses a deterministic regex stub instead.
- `--pretty`: Pretty-prints the resulting JSON output.

## 7. Sample Output
*Example of the default output (truncated):*
```json
[
  {
    "candidate_id": "c_b3122f55ed",
    "full_name": "Praveen Kumar S",
    "emails": [
      "spraveenkumar2205@gmail.com"
    ],
    "phones": null,
    "location": {
      "city": null,
      "region": null,
      "country": null
    },
    "links": {
      "linkedin": "https://www.linkedin.com/in/spraveenkumar2205",
      "github": "https://github.com/praveen-2205",
      "portfolio": null,
      "other": [
        "https://scholar.google.com/citations?hl=en&user=WqhsL7cAAAAJ",
        "https://github.com/praveen-2205/indic-voice-assistant"
      ]
    },
    "headline": null,
    "years_experience": 0.9,
    "skills": [
      {
        "name": "python",
        "confidence": 0.85,
        "sources": [
          "resume:test1.pdf"
        ]
      }
    ],
    "experience": [
      {
        "company": "Granville Tech",
        "title": "Generative AI Intern",
        "start": "2025-07",
        "end": "2025-10",
        "summary": "Built a multi-agent RAG system to automate professional proposal generation..."
      }
    ],
    "overall_confidence": 0.61
  }
]
```
*(Full file typically generated at the specified `--out` path).*

## 8. Running Tests
The suite contains robust edge-case validation and gold-profile end-to-end checks.
```bash
pytest tests/ -v
```
**Test Coverage Includes:**
- **Ambiguous Matching:** Proving that candidates with the same name but different employment histories are not incorrectly merged.
- **Experience Conflicts:** Ensuring overlapping roles at the same company resolve correctly using source priority.
- **Malformed Data:** Normalizing broken phone formats or dropping them if country codes cannot be deterministically inferred.

## 9. Assumptions & Descoped Items
**Assumptions:**
- Phone numbers without explicit country codes are assumed to be un-normalizable and are dropped rather than having country codes guessed.
- E.164 normalization logic has been primarily validated against standard lengths (e.g. US/IN formats).
- Overlapping employment dates at the identical normalized company name are treated as conflicting reports of the same job rather than two separate concurrent jobs.

**Descoped Items (Under Time Pressure):**
- **ATS JSON / LinkedIn / GitHub:** Excluded in favor of prioritizing the core merge, normalization, and provenance engine against CSVs and Resumes.
- **Web UI:** Excluded; a clean, deterministic CLI is provided instead.

## 10. Demo Video
[Demo video (~2 min)](#) *(TODO: Insert link here)*