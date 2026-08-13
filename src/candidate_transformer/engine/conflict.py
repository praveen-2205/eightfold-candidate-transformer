from dataclasses import dataclass
from collections import defaultdict
from typing import Any

from candidate_transformer.models import FieldValue
from candidate_transformer.engine.matching import Cluster

SOURCE_RELIABILITY = {
    "recruiter_csv": 1.00,
    "ats_json": 0.95,
    "resume": 0.90,
    "github": 0.80,
    "notes": 0.70
}

# Base method reliability extraction
def _get_method_reliability(method: str) -> float:
    if "csv_field" in method: return 0.90
    if "normalized" in method or "resume_regex" in method: return 0.85
    if "derived" in method: return 0.70
    if "resume_llm" in method: return 0.60
    return 0.50

@dataclass
class ResolvedField:
    winners: list[FieldValue]
    losers: list[FieldValue]

def _get_source_rel(source_str: str) -> float:
    # Handle dynamic sources like "resume:jane.pdf"
    base_source = source_str.split(":")[0]
    return SOURCE_RELIABILITY.get(base_source, 0.50)

def _get_corroboration_count(val: Any, all_candidates: list[FieldValue]) -> int:
    # How many sources agree on this exact value?
    if isinstance(val, dict):
        return sum(1 for c in all_candidates if c.value == val)
    return sum(1 for c in all_candidates if str(c.value).lower() == str(val).lower())

def _score_candidate(fv: FieldValue, all_candidates: list[FieldValue]) -> tuple:
    """Returns a sorting tuple (higher is better)."""
    source_rel = _get_source_rel(fv.source)
    method_rel = _get_method_reliability(fv.method)
    corrob = _get_corroboration_count(fv.value, all_candidates)
    
    # Tie-break string representation
    lexical = str(fv.value) if fv.value is not None else ""
    
    return (source_rel, method_rel, corrob, fv.source, lexical)

def resolve_field(field_name: str, candidates: list[FieldValue]) -> ResolvedField:
    if not candidates:
        return ResolvedField(winners=[], losers=[])
        
    array_fields = {"emails", "phones", "skills", "links.other"}
    
    # Filter out empty values
    valid_candidates = [c for c in candidates if c.value is not None and c.value != ""]
    if not valid_candidates:
         return ResolvedField(winners=[], losers=candidates)

    if field_name in array_fields:
        # Union and dedupe by value
        seen = set()
        winners = []
        losers = []
        
        # Sort so we pick the "best" FieldValue representation of a duplicate
        sorted_cands = sorted(valid_candidates, key=lambda x: _score_candidate(x, valid_candidates), reverse=True)
        
        for c in sorted_cands:
            val_key = str(c.value).lower()
            if val_key not in seen:
                seen.add(val_key)
                winners.append(c)
            else:
                losers.append(c)
        return ResolvedField(winners=winners, losers=losers)
        
    elif field_name in {"experience", "education"}:
        # Specialized array merge by keys (company/institution)
        seen_keys = set()
        winners = []
        losers = []
        
        # Sort by source reliability first
        sorted_cands = sorted(valid_candidates, key=lambda x: _score_candidate(x, valid_candidates), reverse=True)
        for c in sorted_cands:
            if not isinstance(c.value, dict):
                continue
            key = (c.value.get("company") or c.value.get("institution") or "").lower()
            if key and key not in seen_keys:
                seen_keys.add(key)
                winners.append(c)
            else:
                losers.append(c)
        return ResolvedField(winners=winners, losers=losers)

    else:
        # Single-value field -> pick one deterministic winner
        sorted_cands = sorted(valid_candidates, key=lambda x: _score_candidate(x, valid_candidates), reverse=True)
        winner = sorted_cands[0]
        losers = sorted_cands[1:] + [c for c in candidates if c not in valid_candidates]
        return ResolvedField(winners=[winner], losers=losers)

def resolve_cluster(cluster: Cluster) -> dict[str, ResolvedField]:
    fields_map = defaultdict(list)
    for record in cluster.records:
        for fv in record.fields:
            fields_map[fv.field].append(fv)
            
    resolved = {}
    for field_name, fvs in fields_map.items():
        resolved[field_name] = resolve_field(field_name, fvs)
        
    return resolved