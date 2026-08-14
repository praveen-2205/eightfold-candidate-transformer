import json
import os
import re
from rapidfuzz import process, fuzz

# Load dictionary once at module level
_DICT_PATH = os.path.join(os.path.dirname(__file__), "skills_dictionary.json")
try:
    with open(_DICT_PATH, "r", encoding="utf-8") as f:
        _SKILL_MAP = json.load(f)
except Exception:
    _SKILL_MAP = {}

_KNOWN_CANONICAL = set(_SKILL_MAP.values())

def canonical_skill(raw: str) -> str | None:
    if not raw or not isinstance(raw, str):
        return None
        
    cleaned = re.sub(r"\s+", " ", raw).strip()
    if not cleaned:
        return None
        
    query = cleaned.lower()
    
    # 1. Exact alias hit
    if query in _SKILL_MAP:
        return _SKILL_MAP[query]  # type: ignore
        
    # 2. Fuzzy match against canonicals
    if _KNOWN_CANONICAL:
        best_match = process.extractOne(
            cleaned, 
            list(_KNOWN_CANONICAL), 
            scorer=fuzz.WRatio
        )
        if best_match and best_match[1] >= 92:
            return best_match[0]  # type: ignore
            
    # 3. Fallback: preserve cleaned title-cased
    return cleaned.title()

def is_known(raw: str) -> bool:
    if not raw or not isinstance(raw, str):
        return False
    canon = canonical_skill(raw)
    return canon in _KNOWN_CANONICAL