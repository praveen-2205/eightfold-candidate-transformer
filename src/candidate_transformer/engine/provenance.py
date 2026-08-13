from candidate_transformer.models import Provenance
from candidate_transformer.engine.conflict import ResolvedField

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
            
            # 2. Record any corroborating sources (multiple agreeing)
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