from typing import Any
from candidate_transformer.models.canonical import CanonicalProfile
from candidate_transformer.models.config import OutputConfig
from candidate_transformer.normalize import to_e164, to_year_month, to_iso_alpha2, canonical_skill

MISSING = object()

class ProjectionError(Exception):
    pass

def _resolve_path(data: Any, path: str) -> Any:
    if not path:
        return data
        
    # Translate dot notation and bracket notation into a list of keys
    parts = path.replace("[]", "[*]").replace(".", "[").replace("]", "").split("[")
    parts = [p for p in parts if p]
    
    current = data
    for part in parts:
        if current is None or current is MISSING:
            return MISSING
            
        if part == "*":
            if not isinstance(current, list):
                return MISSING
            return current
            
        if isinstance(current, dict):
            current = current.get(part, MISSING)
        elif isinstance(current, list):
            try:
                idx = int(part)
                current = current[idx]
            except (ValueError, IndexError):
                return MISSING
        else:
            return MISSING
    return current

def _resolve_complex_path(data: dict, path: str) -> Any:
    # Handle array mapping, e.g., "skills[].name"
    if "[]" in path:
        base, rest = path.split("[]", 1)
        rest = rest.lstrip(".")
        
        array_val = _resolve_path(data, base)
        if array_val is MISSING or not isinstance(array_val, list):
            return MISSING
            
        if not rest:
            return array_val
            
        result = []
        for item in array_val:
            val = _resolve_path(item, rest)
            if val is not MISSING:
                result.append(val)
        return result if result else MISSING
        
    return _resolve_path(data, path)

def _apply_normalization(value: Any, norm_type: str) -> Any:
    if value is None:
        return None
        
    # Map normalization over arrays
    if isinstance(value, list):
        return [_apply_normalization(v, norm_type) for v in value]
        
    norm_lower = norm_type.lower()
    if norm_lower == "e164":
        return to_e164(str(value))
    elif norm_lower == "canonical":
        return canonical_skill(str(value))
    elif norm_lower == "yyyy-mm":
        return to_year_month(str(value))
    elif norm_lower == "iso_country":
        return to_iso_alpha2(str(value))
        
    return value

def project(profile: CanonicalProfile, config: OutputConfig) -> dict:
    output: dict[str, Any] = {}
    dump = profile.model_dump()
    
    for spec in config.fields:
        source_path = spec.from_ or spec.path
        val = _resolve_complex_path(dump, source_path)
        
        # Determine missing policy (field-level overrides global)
        missing_policy = spec.on_missing or config.on_missing
        
        # Handle Missing/Empty Values
        if val is MISSING or val is None or val == []:
            if missing_policy == "error" or (spec.required and missing_policy != "omit"):
                raise ProjectionError(f"Field '{spec.path}' is missing or null but required.")
            elif missing_policy == "omit":
                continue
            else:
                output[spec.path] = None
                continue
                
        # Handle Normalization
        if spec.normalize:
            val = _apply_normalization(val, spec.normalize)
            if val is None and spec.required:
                 raise ProjectionError(f"Field '{spec.path}' became null after normalization but is required.")
                 
        output[spec.path] = val
        
    # Handle global toggles
    if config.include_confidence:
        output["overall_confidence"] = profile.overall_confidence
    if config.include_provenance:
        output["provenance"] = dump.get("provenance", [])
        
    return output