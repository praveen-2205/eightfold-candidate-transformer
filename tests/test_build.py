from candidate_transformer.pipeline import run

def test_pipeline_happy_path():
    # Use the stub LLM for deterministic offline testing
    profiles = run([
        "sample_data/recruiter_export.csv",
        "sample_data/resume_jane_doe.pdf"
    ], use_llm=False)
    
    assert len(profiles) >= 2
    
    # Jane should be merged
    jane = next(p for p in profiles if p.full_name == "Jane Doe")
    assert jane.candidate_id.startswith("c_")
    
    # Check deduplication / union
    assert len(jane.emails) == 1
    assert jane.emails[0] == "jane@x.com"
    
    # Check skills propagated
    skill_names = [s.name for s in jane.skills]
    assert "React" in skill_names
    
    # Check years_experience computed
    assert jane.years_experience is not None
    assert jane.years_experience > 0
    
    # Check provenance
    prov_fields = {p.field for p in jane.provenance}
    assert "emails" in prov_fields
    assert "years_experience" in prov_fields

def test_pipeline_determinism():
    run_1 = run(["sample_data/recruiter_export.csv", "sample_data/resume_jane_doe.pdf"], use_llm=False)
    run_2 = run(["sample_data/recruiter_export.csv", "sample_data/resume_jane_doe.pdf"], use_llm=False)
    
    # Assert byte-for-byte identical output
    assert [p.model_dump() for p in run_1] == [p.model_dump() for p in run_2]