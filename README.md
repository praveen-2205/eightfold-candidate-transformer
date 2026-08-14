# Eightfold Candidate Transformer

A robust, multi-source data pipeline that ingests messy, unstructured (PDF/TXT resumes) and structured (CSV) recruiter data to produce highly confident, deterministic, and canonically merged candidate profiles.

## Architecture & Design Philosophy

This pipeline employs a **Hybrid Extraction Strategy** designed to eliminate LLM hallucinations and enforce deterministic, testable outputs:

1. **Deterministic First:** Phones, emails, links, and structured CSV fields are extracted using strict regular expressions and heuristics.
2. **Boxed LLM Semantic Extraction:** We only use LLMs for inherently semantic fields (skills, experience summaries). The LLM output is strictly validated against a Pydantic schema, mapped back to deterministic enums/canonicals, and cached.
3. **Graph-Based Matching:** Candidate deduplication utilizes a Union-Find (Disjoint Set) algorithm with a deterministic scoring threshold. It employs blocking (grouping by emails, phones, or last name initials) to scale efficiently and avoid O(N²) comparisons.
4. **Weighted Conflict Resolution:** When sources disagree, the engine picks the winner based on source reliability (e.g., CSV > Resume) and extraction method (e.g., Regex > LLM).
5. **Noisy-OR Confidence & Provenance:** Corroborating sources boost a field's confidence using a noisy-OR calculation. Every emitted field includes a transparent audit trail (`provenance`) detailing exactly which source and method produced it.
6. **Configurable Projection Layer:** The core engine is decoupled from the output schema. A JSON-driven projection layer dynamically reshapes the profile, handling missing-value policies and array indexing on the fly.

## Project Structure

```text
src/candidate_transformer/
├── engine/         # Matching, Conflict Resolution, Confidence, Provenance
├── extraction/     # PDF parsing, Regex rules, and LLM semantic extraction
├── models/         # Pydantic schemas (SourceRecord, CanonicalProfile, Config)
├── normalize/      # Deterministic standardizers (E.164, ISO Countries, Canonical Skills)
├── projection/     # Dynamic output formatting & JSON schema validation
├── sources/        # Input adapters (CsvSource, ResumeSource)
├── cli.py          # Command-line interface
└── pipeline.py     # Main engine orchestration
```

## Setup Instructions

This project requires Python 3.10+.

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Install the package locally (optional but recommended)

```bash
pip install -e .
```

## Usage

Use the CLI to process candidate data. You can chain as many `--input` flags as needed.

### Basic Run (Offline/Deterministic Stub)

```bash
candidate-transformer \
  --input sample_data/recruiter_export.csv \
  --input sample_data/resume_jane_doe.pdf \
  --out final_candidates.json \
  --pretty \
  --no-llm
```

### Custom Output View

The projection layer allows you to reshape the JSON without changing Python code.

```bash
candidate-transformer \
  --input sample_data/recruiter_export.csv \
  --input sample_data/resume_jane_doe.pdf \
  --config configs/custom_recruiter_view.json \
  --pretty \
  --no-llm
```

## Testing

The project maintains a strict deterministic test suite, including a "Gold Profile" end-to-end test that prevents regressions.

```bash
# Run all tests
pytest -q

# Run with coverage report
pytest --cov=candidate_transformer --cov-report=term-missing
```