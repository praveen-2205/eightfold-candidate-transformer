from candidate_transformer.models import Provenance
from candidate_transformer.engine.conflict import ResolvedField, _dates_overlap, _normalize_name

def _val_key(v) -> str:
    if isinstance(v, dict):
        return str(sorted((k, val) for k, val in v.items() if val))
    return str(v).lower().strip() if v else ""

def build_provenance(resolved: dict[str, ResolvedField]) -> list[Provenance]:
    prov_list = []
    
    for field_name, resolved_field in resolved.items():
        if not resolved_field.winners:
            continue
            
        for winner in resolved_field.winners:
            # 1. Record the winner
            prov_list.append(Provenance(
                field=field_name,
                source=winner.source,
                method=winner.method
            ))
            
            # 2. Record conflicts for dictionary fields like experience
            if field_name in {"experience", "education"} and isinstance(winner.value, dict):
                w_key = _normalize_name(winner.value.get("company") or winner.value.get("institution") or "")
                
                for loser in resolved_field.losers:
                    if not isinstance(loser.value, dict):
                        continue
                    l_key = _normalize_name(loser.value.get("company") or loser.value.get("institution") or "")
                    
                    if l_key == w_key and _dates_overlap(winner.value, loser.value):
                        # They belong to the same cluster. Find field-level conflicts.
                        for k, l_val in loser.value.items():
                            w_val = winner.value.get(k)
                            if l_val and w_val and l_val != w_val:
                                prov_list.append(Provenance(
                                    field=f"{field_name}.{k}",
                                    source=loser.source,
                                    method=loser.method,
                                    value=str(l_val),
                                    is_conflict=True
                                ))
                        
            # 3. Record any corroborating sources (multiple agreeing)
            win_key = _val_key(winner.value)
            for loser in resolved_field.losers:
                if _val_key(loser.value) == win_key:
                    prov_list.append(Provenance(
                        field=field_name,
                        source=loser.source,
                        method=loser.method
                    ))
                    
    # Sort deterministically by field, then source, then method
    return sorted(prov_list, key=lambda p: (p.field, p.source, p.method))