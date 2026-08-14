from candidate_transformer.pipeline import run
from candidate_transformer.models.intermediate import FieldValue
from candidate_transformer.normalize import canonical_skill, is_known
from candidate_transformer.engine.confidence import calculate_confidence

def test_edge_case_conflicting_title_picks_csv(tmp_path):
    # Create a CSV where Jane is a "Chief Engineer"
    csv_path = tmp_path / "rec.csv"
    csv_path.write_text("name,email,phone,latest_company,title\nJane Doe,jane@x.com,,Acme,Chief Engineer", encoding="utf-8")
    
    # Our stub resume extractor hardcodes Jane's experience as "Senior Engineer"
    profiles = run([str(csv_path), "sample_data/resume_jane_doe.pdf"], use_llm=False)
    
    jane = next(p for p in profiles if p.full_name == "Jane Doe")
    
    # CSV source reliability (1.0) beats Resume LLM reliability (0.90)
    assert len(jane.experience) > 0
    assert jane.experience[0].title == "Chief Engineer"
    
    # The WINNER should be captured in provenance; the loser is excluded from the public audit trail
    assert any(p.method == "csv_field" and p.field == "experience" for p in jane.provenance)
    assert not any(p.method == "resume_llm" and p.field == "experience" for p in jane.provenance)

def test_edge_case_missing_csv_yields_resume_only():
    profiles = run(["missing_file.csv", "sample_data/resume_jane_doe.pdf"], use_llm=False)
    
    assert len(profiles) > 0
    jane = next(p for p in profiles if p.full_name == "Jane Doe")
    
    # Resume-only fields should be present
    assert "React" in [s.name for s in jane.skills]
    assert jane.experience[0].title == "Senior Engineer"

def test_edge_case_unknown_skill_preserved_with_lower_confidence():
    # Unknown skills should be title-cased but preserved
    unknown = "Some Brand New Tech"
    canon = canonical_skill(unknown)
    assert canon == "Some Brand New Tech"
    assert not is_known(unknown)
    
    # Simulate extraction
    fv_known = FieldValue(field="skills", value="React", source="resume", method="resume_llm", extraction_confidence=0.70)
    fv_unknown = FieldValue(field="skills", value=canon, source="resume", method="resume_llm", extraction_confidence=0.60)
    
    # Known skill corroboration logic
    conf_known = calculate_confidence(fv_known, [fv_known], is_union=True)
    conf_unknown = calculate_confidence(fv_unknown, [fv_unknown], is_union=True)
    
    assert conf_unknown < conf_known