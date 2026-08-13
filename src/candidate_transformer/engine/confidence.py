from candidate_transformer.models import FieldValue

METHOD_RELIABILITY = {
    "csv_field": 0.90,
    "resume_regex": 0.85,
    "normalized:E164": 0.85,
    "derived": 0.70,
    "resume_llm": 0.60,
}

SOURCE_RELIABILITY = {
    "recruiter_csv": 1.00,
    "ats_json": 0.95,
    "resume": 0.90,
    "github": 0.80,
    "notes": 0.70
}

def _get_source_rel(source_str: str) -> float:
    # Handle "resume:jane.pdf" -> "resume"
    base = source_str.split(":")[0]
    return SOURCE_RELIABILITY.get(base, 0.50)

def _get_method_rel(method_str: str) -> float:
    best = 0.50
    for k, v in METHOD_RELIABILITY.items():
        if k in method_str and v > best:
            best = v
    return best

def get_base_confidence(fv: FieldValue) -> float:
    return _get_source_rel(fv.source) * _get_method_rel(fv.method)

def calculate_confidence(winner: FieldValue, all_candidates: list[FieldValue], is_union: bool = False) -> float:
    def _val_key(v):
        if isinstance(v, dict):
            # dicts to strings for comparison
            return str(sorted((k, val) for k, val in v.items() if val))
        return str(v).lower().strip() if v else ""
        
    win_key = _val_key(winner.value)
    corroborators = [c for c in all_candidates if _val_key(c.value) == win_key]
    
    # 1. Corroboration via noisy-OR: 1 - Π(1 - base_i)
    prod = 1.0
    for c in corroborators:
        prod *= (1.0 - get_base_confidence(c))
    conf = 1.0 - prod
    
    # 2. Conflict penalty if non-union and sources disagreed
    if not is_union:
        if any(_val_key(c.value) != win_key for c in all_candidates if c.value):
            conf *= 0.85
            
    # 3. Clamp
    return max(0.0, min(1.0, conf))

def compute_overall_confidence(field_confidences: dict[str, float]) -> float:
    weights = {
        "full_name": 0.20,
        "emails": 0.25,
        "phones": 0.15,
        "experience": 0.20,
        "skills": 0.10,
        "education": 0.10
    }
    
    score = 0.0
    for field, weight in weights.items():
        score += field_confidences.get(field, 0.0) * weight
        
    total_weight = sum(weights.values())
    return max(0.0, min(1.0, score / total_weight))