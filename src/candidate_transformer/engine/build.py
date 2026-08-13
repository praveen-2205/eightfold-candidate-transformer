import hashlib
from candidate_transformer.models import (
    SourceRecord, CanonicalProfile, Location, Links, 
    Skill, ExperienceItem, EducationItem, FieldValue, Provenance
)
from candidate_transformer.engine.matching import cluster_records
from candidate_transformer.engine.conflict import resolve_cluster
from candidate_transformer.engine.confidence import calculate_confidence, compute_overall_confidence
from candidate_transformer.engine.provenance import build_provenance

def _generate_id(resolved: dict) -> str:
    # Strongest key: email > phone > name+source
    key = ""
    if resolved.get("emails") and resolved["emails"].winners:
        key = f"email:{resolved['emails'].winners[0].value}"
    elif resolved.get("phones") and resolved["phones"].winners:
        key = f"phone:{resolved['phones'].winners[0].value}"
    elif resolved.get("full_name") and resolved["full_name"].winners:
        w = resolved["full_name"].winners[0]
        key = f"name:{w.value}:{w.source}"
    else:
        key = "unknown"
        
    return "c_" + hashlib.sha1(key.encode('utf-8')).hexdigest()[:10]

def _parse_month(ym_str: str) -> int | None:
    if not ym_str:
        return None
    if ym_str.lower() == "present":
        # Deterministic bound for "present" (Locked to August 2026)
        return 2026 * 12 + 8
    try:
        parts = ym_str.split("-")
        return int(parts[0]) * 12 + int(parts[1])
    except:
        return None

def _calculate_years_experience(experiences: list[ExperienceItem]) -> float | None:
    intervals = []
    for exp in experiences:
        start_m = _parse_month(exp.start)
        end_m = _parse_month(exp.end)
        
        if start_m and end_m and start_m <= end_m:
            intervals.append((start_m, end_m))
        elif start_m and not end_m:
            # Assume 1 month if start but no end
            intervals.append((start_m, start_m))
            
    if not intervals:
        return None
        
    # Merge overlapping intervals
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        previous = merged[-1]
        if current[0] <= previous[1]:
            merged[-1] = (previous[0], max(previous[1], current[1]))
        else:
            merged.append(current)
            
    total_months = sum((end - start + 1) for start, end in merged)
    return round(total_months / 12.0, 1)

def _get_single_val(resolved: dict, field_name: str):
    rf = resolved.get(field_name)
    return rf.winners[0].value if rf and rf.winners else None

def _get_list_vals(resolved: dict, field_name: str) -> list[str]:
    rf = resolved.get(field_name)
    return [w.value for w in rf.winners] if rf else []

def build_profiles(records: list[SourceRecord]) -> list[CanonicalProfile]:
    clusters = cluster_records(records)
    profiles = []
    
    for cluster in clusters:
        resolved = resolve_cluster(cluster)
        
        # Calculate confidences
        field_confs = {}
        all_fvs = [fv for r in cluster.records for fv in r.fields]
        
        for fname, rf in resolved.items():
            if not rf.winners:
                continue
            is_union = fname in {"emails", "phones", "skills", "links.other"}
            # Score based on the primary winner
            field_confs[fname] = calculate_confidence(rf.winners[0], all_fvs, is_union)
            
        overall_conf = compute_overall_confidence(field_confs)
        provenance = build_provenance(resolved)
        
        # Build complex objects
        loc = Location(
            city=_get_single_val(resolved, "location.city"),
            region=_get_single_val(resolved, "location.region"),
            country=_get_single_val(resolved, "location.country")
        )
        
        links = Links(
            linkedin=_get_single_val(resolved, "links.linkedin"),
            github=_get_single_val(resolved, "links.github"),
            portfolio=_get_single_val(resolved, "links.portfolio"),
            other=_get_list_vals(resolved, "links.other")
        )
        
        skills = []
        if "skills" in resolved:
            for w in resolved["skills"].winners:
                s_conf = calculate_confidence(w, all_fvs, is_union=True)
                sources = list(set([w.source] + [l.source for l in resolved["skills"].losers if l.value == w.value]))
                skills.append(Skill(name=w.value, confidence=s_conf, sources=sorted(sources)))
                
        experience = []
        if "experience" in resolved:
            for w in resolved["experience"].winners:
                v = w.value
                experience.append(ExperienceItem(
                    company=v.get("company"), title=v.get("title"),
                    start=v.get("start"), end=v.get("end"), summary=v.get("summary")
                ))
                
        education = []
        if "education" in resolved:
            for w in resolved["education"].winners:
                v = w.value
                education.append(EducationItem(
                    institution=v.get("institution"), degree=v.get("degree"),
                    field=v.get("field"), end_year=v.get("end_year")
                ))
                
        # Calculate years experience and add strictly typed Provenance
        years_exp = _calculate_years_experience(experience)
        if years_exp is not None:
            provenance.append(Provenance(
                field="years_experience", 
                source="system", 
                method="derived:from_experience_dates"
            ))

        profile = CanonicalProfile(
            candidate_id=_generate_id(resolved),
            full_name=_get_single_val(resolved, "full_name"),
            emails=_get_list_vals(resolved, "emails"),
            phones=_get_list_vals(resolved, "phones"),
            location=loc,
            links=links,
            headline=_get_single_val(resolved, "headline"),
            years_experience=years_exp,
            skills=skills,
            experience=experience,
            education=education,
            provenance=provenance,
            overall_confidence=overall_conf
        )
        profiles.append(profile)
        
    return sorted(profiles, key=lambda p: p.candidate_id)