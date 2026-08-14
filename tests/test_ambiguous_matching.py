import pytest
from candidate_transformer.models import FieldValue, SourceRecord
from candidate_transformer.engine.build import build_profiles

def test_ambiguous_candidate_different_ids():
    # Praveen at Backspace Tech
    fv_name_1 = FieldValue(field="full_name", value="Praveen Kumar", source="csv", method="csv")
    fv_exp_1 = FieldValue(
        field="experience", 
        value={"company": "Backspace Tech", "title": "AI Intern", "start": None, "end": None, "summary": None}, 
        source="csv", 
        method="csv"
    )
    rec1 = SourceRecord(source_id="csv_0", source_type="csv", fields=[fv_name_1, fv_exp_1])
    
    # Praveen at Unrelated Company
    fv_name_2 = FieldValue(field="full_name", value="Praveen Kumar", source="csv", method="csv")
    fv_exp_2 = FieldValue(
        field="experience", 
        value={"company": "Unrelated Company", "title": "Software Engineer", "start": None, "end": None, "summary": None}, 
        source="csv", 
        method="csv"
    )
    rec2 = SourceRecord(source_id="csv_1", source_type="csv", fields=[fv_name_2, fv_exp_2])
    
    # Run through build_profiles
    profiles = build_profiles([rec1, rec2])
    
    # They shouldn't merge (no strong identifier, different company) -> 2 profiles
    assert len(profiles) == 2
    
    # Their candidate IDs MUST be different
    id1 = profiles[0].candidate_id
    id2 = profiles[1].candidate_id
    
    assert id1 != id2
    assert id1.startswith("c_")
    assert id2.startswith("c_")
    
def test_same_name_and_company_same_id():
    # If they are exactly the same (name + company) but don't merge (because score = 0.30)
    # But they SHOULD get the same candidate ID as a deterministic fallback.
    fv_name_1 = FieldValue(field="full_name", value="Praveen Kumar", source="csv", method="csv")
    fv_exp_1 = FieldValue(
        field="experience", 
        value={"company": "Backspace Tech", "title": "AI Intern", "start": None, "end": None, "summary": None}, 
        source="csv", 
        method="csv"
    )
    rec1 = SourceRecord(source_id="csv_0", source_type="csv", fields=[fv_name_1, fv_exp_1])
    
    fv_name_2 = FieldValue(field="full_name", value="Praveen Kumar", source="csv", method="csv")
    fv_exp_2 = FieldValue(
        field="experience", 
        value={"company": "Backspace Tech", "title": "AI Intern", "start": None, "end": None, "summary": None}, 
        source="csv", 
        method="csv"
    )
    rec2 = SourceRecord(source_id="csv_1", source_type="csv", fields=[fv_name_2, fv_exp_2])
    
    profiles = build_profiles([rec1, rec2])
    
    # Still 2 profiles because they don't merge via matching.py
    assert len(profiles) == 2
    
    # But since their name and employment signature are identical, they get the SAME candidate ID
    assert profiles[0].candidate_id == profiles[1].candidate_id
