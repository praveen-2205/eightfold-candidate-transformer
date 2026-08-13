from candidate_transformer.models import FieldValue
from candidate_transformer.engine.confidence import (
    calculate_confidence, get_base_confidence, compute_overall_confidence
)

def test_corroboration_noisy_or():
    # Two agreeing sources: CSV and Resume
    fv1 = FieldValue(field="emails", value="jane@x.com", source="recruiter_csv", method="csv_field")
    fv2 = FieldValue(field="emails", value="jane@x.com", source="resume:1.pdf", method="resume_regex")
    
    base1 = get_base_confidence(fv1)  # 1.0 * 0.90 = 0.90
    base2 = get_base_confidence(fv2)  # 0.90 * 0.85 = 0.765
    
    conf = calculate_confidence(fv1, [fv1, fv2], is_union=False)
    
    # Noisy-OR should yield 0.9765
    expected = 1.0 - ((1.0 - base1) * (1.0 - base2)) 
    assert abs(conf - expected) < 0.001
    assert conf > base1 # Corroboration increases confidence

def test_conflict_penalty():
    fv_win = FieldValue(field="current_title", value="Senior Engineer", source="recruiter_csv", method="csv_field")
    fv_lose = FieldValue(field="current_title", value="ML Engineer", source="resume", method="resume_llm")
    
    # Base of winner = 0.90. Conflict penalty = 0.90 * 0.85 = 0.765
    conf = calculate_confidence(fv_win, [fv_win, fv_lose], is_union=False)
    assert abs(conf - 0.765) < 0.001
    
def test_compute_overall():
    confs = {
        "full_name": 0.90,
        "emails": 0.97,
        "phones": 0.0, # missing/null field
        "experience": 0.80,
        "skills": 0.90,
        "education": 0.0 # missing/null field
    }
    
    overall = compute_overall_confidence(confs)
    # 0.9*0.2 + 0.97*0.25 + 0.8*0.2 + 0.9*0.1 = 0.18 + 0.2425 + 0.16 + 0.09 = 0.6725
    assert abs(overall - 0.6725) < 0.001
    
    # Empty profile
    assert compute_overall_confidence({}) == 0.0