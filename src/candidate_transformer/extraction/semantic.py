import json
import hashlib
import os
from typing import Protocol
from pydantic import BaseModel

from candidate_transformer.models import FieldValue
from candidate_transformer.normalize import canonical_skill, is_known, to_year_month, to_year
from candidate_transformer.util.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------
# Strict JSON Schema for LLM Output Validation
# ---------------------------------------------------------
class LLMExperience(BaseModel):
    company: str | None = None
    title: str | None = None
    start: str | None = None
    end: str | None = None
    summary: str | None = None

class LLMEducation(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    end_year: int | None = None

class LLMOutput(BaseModel):
    skills: list[str] = []
    headline: str | None = None
    experience: list[LLMExperience] = []
    education: list[LLMEducation] = []

# ---------------------------------------------------------
# Protocol Interface
# ---------------------------------------------------------
class SemanticExtractor(Protocol):
    def extract(self, resume_text: str, source_id: str) -> list[FieldValue]:
        ...

# ---------------------------------------------------------
# Post-Processing (Deterministic Normalization of LLM Output)
# ---------------------------------------------------------
def _post_process_llm_data(data: LLMOutput, source_id: str) -> list[FieldValue]:
    fields = []
    base_conf = 0.60  # Base confidence for LLM extraction

    if data.headline:
        fields.append(FieldValue(
            field="headline", value=data.headline, source=source_id,
            method="resume_llm", raw=data.headline, extraction_confidence=base_conf
        ))

    for raw_skill in data.skills:
        canon = canonical_skill(raw_skill)
        if canon:
            known = is_known(raw_skill)
            fields.append(FieldValue(
                field="skills", value=canon, source=source_id,
                method="resume_llm+normalized:canonical", raw=raw_skill,
                extraction_confidence=0.70 if known else base_conf
            ))

    for exp in data.experience:
        if not exp.company and not exp.title:
            continue
            
        norm_exp = {
            "company": exp.company.strip() if exp.company else None,
            "title": exp.title.strip() if exp.title else None,
            "start": to_year_month(exp.start) if exp.start else None,
            "end": to_year_month(exp.end) if exp.end else None,
            "summary": exp.summary.strip() if exp.summary else None
        }
        fields.append(FieldValue(
            field="experience", value=norm_exp, source=source_id,
            method="resume_llm", raw=exp.model_dump(), extraction_confidence=base_conf
        ))

    for edu in data.education:
        if not edu.institution and not edu.degree:
            continue
            
        norm_edu = {
            "institution": edu.institution.strip() if edu.institution else None,
            "degree": edu.degree.strip() if edu.degree else None,
            "field": edu.field.strip() if edu.field else None,
            "end_year": to_year(str(edu.end_year)) if edu.end_year else None
        }
        fields.append(FieldValue(
            field="education", value=norm_edu, source=source_id,
            method="resume_llm", raw=edu.model_dump(), extraction_confidence=base_conf
        ))

    return fields

# ---------------------------------------------------------
# Stub Implementation
# ---------------------------------------------------------
class StubSemanticExtractor:
    def extract(self, resume_text: str, source_id: str) -> list[FieldValue]:
        data = LLMOutput()
        if "ReactJS" in resume_text or "React" in resume_text:
            data.skills.append("React")
        if "python" in resume_text.lower():
            data.skills.append("Python")
            
        if "Senior Engineer at Acme" in resume_text:
            data.experience.append(LLMExperience(
                company="Acme", title="Senior Engineer",
                start="Jan 2021", end="Present"
            ))
            
        return _post_process_llm_data(data, source_id)

# ---------------------------------------------------------
# Real LLM Implementation (Cached, Validated)
# ---------------------------------------------------------
class LlmSemanticExtractor:
    def __init__(self):
        self.cache_dir = os.path.join(os.getcwd(), "cache", "llm")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.prompt_version = "v3"
        self.model_id = "meta/llama-3.3-70b-instruct"
        self.stub_fallback = StubSemanticExtractor()
        
        self.api_key = os.environ.get("NVIDIA_API_KEY")
        if self.api_key:
            from openai import OpenAI
            self.client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=self.api_key
            )
        else:
            self.client = None

    def _get_cache_key(self, text: str) -> str:
        content = f"{self.model_id}:{self.prompt_version}:{text}".encode('utf-8')
        return hashlib.sha256(content).hexdigest()

    def extract(self, resume_text: str, source_id: str) -> list[FieldValue]:
        if not resume_text:
            return []

        cache_key = self._get_cache_key(resume_text)
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")

        # 1. Check Cache
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                validated_data = LLMOutput.model_validate(cached_data)
                return _post_process_llm_data(validated_data, source_id)
            except Exception as e:
                logger.debug(f"Cache read failed for {cache_key}: {e}")

        # 2. Check if API is configured
        if not self.client:
            logger.warning("NVIDIA_API_KEY not found in environment. Falling back to Stub.")
            return self.stub_fallback.extract(resume_text, source_id)

        # 3. Call NVIDIA NIM API
        logger.info(f"Calling {self.model_id} via NVIDIA API for {source_id}...")
        
        system_prompt = """You are a highly precise candidate data extraction engine.
Extract the professional data from the provided resume text into a strict JSON object.
Do NOT wrap the output in markdown code blocks. Output RAW JSON only.

Schema:
{
  "skills": ["array of strings (technical and soft skills)"],
  "headline": "string or null (a short professional summary)",
  "experience": [
    {
      "company": "string",
      "title": "string",
      "start": "string (YYYY-MM format) or null",
      "end": "string (YYYY-MM or 'present') or null",
      "summary": "string or null (brief bullet points)"
    }
  ],
  "education": [
    {
      "institution": "string",
      "degree": "string",
      "field": "string or null",
      "end_year": integer or null
    }
  ]
}"""

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Resume Text:\n\n{resume_text}"}
                ],
                temperature=0.1,  # Low temperature for deterministic extraction
                top_p=0.7,
                max_tokens=2048,
                response_format={"type": "json_object"},
                stream=False
            )
            
            raw_content = completion.choices[0].message.content
            
            # Defensive cleaning just in case Llama outputs markdown formatting
            raw_content = raw_content.strip()
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:-3].strip()
            elif raw_content.startswith("```"):
                raw_content = raw_content[3:-3].strip()
                
            parsed_data = json.loads(raw_content)
            
            # Validate against our Pydantic schema
            validated_data = LLMOutput.model_validate(parsed_data)
            
            # Save to Cache
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(parsed_data, f)
                
            return _post_process_llm_data(validated_data, source_id)
            
        except Exception as e:
            logger.error(f"NVIDIA API LLM extraction failed: {e}")
            return self.stub_fallback.extract(resume_text, source_id)

# ---------------------------------------------------------
# Factory
# ---------------------------------------------------------
def get_extractor(use_llm: bool) -> SemanticExtractor:
    if use_llm:
        return LlmSemanticExtractor()
    return StubSemanticExtractor()