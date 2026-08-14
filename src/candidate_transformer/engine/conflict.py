import re
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
    if "resume_annotation" in method: return 0.88
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

def _normalize_name(name: str) -> str:
    if not name:
        return ""
    name = name.lower()
    # Strip parentheticals
    name = re.sub(r'\(.*?\)', '', name)
    # Strip common suffixes at the end
    suffixes = [r'\binc\.?', r'\bllc\.?', r'\bpvt\.?', r'\bltd\.?', r'\bcorp\.?', r'\bcorporation\b', r'\bco\.?']
    for suffix in suffixes:
        name = re.sub(suffix + r'$', '', name).strip()
        name = re.sub(r'[,.\s]+$', '', name)
    # Collapse spaces
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

def _parse_date(d: str | None, is_end: bool) -> str:
    if not d or d.lower() == "present":
        return "9999-99" if is_end else "0000-00"
    if len(d) == 4 and d.isdigit():
        return f"{d}-12" if is_end else f"{d}-01"
    return str(d)

def _dates_overlap(item1: dict, item2: dict) -> bool:
    if "end_year" in item1 or "end_year" in item2:
        y1 = str(item1.get("end_year") or "")
        y2 = str(item2.get("end_year") or "")
        if not y1 or not y2: return True
        return y1 == y2
        
    if not (item1.get("start") or item1.get("end")): return True
    if not (item2.get("start") or item2.get("end")): return True
    
    start1 = _parse_date(item1.get("start"), False)
    end1 = _parse_date(item1.get("end"), True)
    start2 = _parse_date(item2.get("start"), False)
    end2 = _parse_date(item2.get("end"), True)
    
    return start1 <= end2 and start2 <= end1

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
        winners = []
        losers = []
        
        # Sort by source reliability first
        sorted_cands = sorted(valid_candidates, key=lambda x: _score_candidate(x, valid_candidates), reverse=True)
        for c in sorted_cands:
            if not isinstance(c.value, dict):
                continue
            key = _normalize_name(c.value.get("company") or c.value.get("institution") or "")
            if not key:
                continue
                
            overlapping_winner = None
            for w in winners:
                w_key = _normalize_name(w.value.get("company") or w.value.get("institution") or "")
                if w_key == key and _dates_overlap(w.value, c.value):
                    overlapping_winner = w
                    break
            
            if overlapping_winner:
                for k, v in c.value.items():
                    if not overlapping_winner.value.get(k) and v:
                        overlapping_winner.value[k] = v
                losers.append(c)
            else:
                merged_val = c.value.copy()
                new_fv = FieldValue(
                    field=c.field,
                    value=merged_val,
                    source=c.source,
                    method=c.method,
                    raw=c.raw,
                    extraction_confidence=c.extraction_confidence
                )
                winners.append(new_fv)
                
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