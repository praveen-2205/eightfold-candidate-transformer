import os
import json
from pydantic import ValidationError
from candidate_transformer.extraction.semantic import (
    get_extractor, LLMOutput, _post_process_llm_data
)

def test_stub_extraction_happy():
    extractor = get_extractor(use_llm=False)
    sample_text = "Skills: ReactJS, python\nExperience: Senior Engineer at Acme, Jan 2021 to Present"
    
    fields = extractor.extract(sample_text, "resume:test.pdf")
    
    skills = [f.value for f in fields if f.field == "skills"]
    assert "React" in skills
    assert "Python" in skills
    
    exp = [f.value for f in fields if f.field == "experience"]
    assert len(exp) == 1
    assert exp[0]["company"] == "Acme"
    assert exp[0]["title"] == "Senior Engineer"
    assert exp[0]["start"] == "2021-01"
    assert exp[0]["end"] == "present"

def test_llm_output_validation_post_processing():
    # Simulate a raw JSON blob returned by an LLM
    raw_llm_json = {
        "skills": ["react", "unknown framework", "aws"],
        "headline": "Great dev",
        "experience": [
            {"company": "Beta LLC", "title": "Dev", "start": "2020-05"},
            {"company": None, "title": None} # Unsupported, should be dropped
        ],
        "education": []
    }
    
    # 1. Validate against schema
    validated = LLMOutput.model_validate(raw_llm_json)
    
    # 2. Post-process
    fields = _post_process_llm_data(validated, "resume:test.pdf")
    
    skills = [f for f in fields if f.field == "skills"]
    assert len(skills) == 3
    
    # Check normalized canonicals
    assert any(s.value == "React" for s in skills)
    assert any(s.value == "Unknown Framework" for s in skills)
    
    # Known skill gets higher confidence
    react_field = next(s for s in skills if s.value == "React")
    assert react_field.extraction_confidence == 0.70
    
    # Unknown gets lower confidence
    unknown_field = next(s for s in skills if s.value == "Unknown Framework")
    assert unknown_field.extraction_confidence == 0.60
    
    # Experience should drop the empty one
    exps = [f for f in fields if f.field == "experience"]
    assert len(exps) == 1
    assert exps[0].value["company"] == "Beta LLC"
    assert exps[0].value["start"] == "2020-05"

def test_llm_cache_determinism(tmp_path):
    # Set the cache dir to a temp directory for the test
    extractor = get_extractor(use_llm=True)
    extractor.cache_dir = str(tmp_path)
    
    test_text = "Jane Doe resume text"
    cache_key = extractor._get_cache_key(test_text)
    cache_file = os.path.join(str(tmp_path), f"{cache_key}.json")
    
    # Seed the cache with a fake valid LLM output
    fake_data = {"skills": ["Java"], "experience": [], "education": []}
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(fake_data, f)
        
    # The extractor should hit the cache instead of the network/fallback
    fields = extractor.extract(test_text, "resume:test.pdf")
    assert len(fields) == 1
    assert fields[0].field == "skills"
    assert fields[0].value == "Java"