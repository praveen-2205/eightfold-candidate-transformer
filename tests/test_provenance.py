from candidate_transformer.models import FieldValue, Provenance
from candidate_transformer.engine.conflict import ResolvedField
from candidate_transformer.engine.provenance import build_provenance

def test_provenance_corroboration():
    # Two sources agree on the email
    fv_win = FieldValue(field="emails", value="jane@x.com", source="recruiter_csv", method="csv_field")
    fv_corroborator = FieldValue(field="emails", value="jane@x.com", source="resume", method="resume_regex")
    
    resolved = {
        "emails": ResolvedField(winners=[fv_win], losers=[fv_corroborator])
    }
    
    provs = build_provenance(resolved)
    
    assert len(provs) == 2
    assert all(p.field == "emails" for p in provs)
    sources = {p.source for p in provs}
    assert sources == {"recruiter_csv", "resume"}

def test_provenance_conflict():
    # Two sources disagree on title. Loser should NOT get standard provenance for the winning value.
    fv_win = FieldValue(field="current_title", value="Senior Engineer", source="recruiter_csv", method="csv_field")
    fv_loser = FieldValue(field="current_title", value="ML Engineer", source="resume", method="resume_llm")
    
    resolved = {
        "current_title": ResolvedField(winners=[fv_win], losers=[fv_loser])
    }
    
    provs = build_provenance(resolved)
    
    assert len(provs) == 1
    assert provs[0].source == "recruiter_csv"
    assert provs[0].method == "csv_field"

def test_provenance_missing_field():
    resolved = {
        "phones": ResolvedField(winners=[], losers=[])
    }
    
    provs = build_provenance(resolved)
    assert len(provs) == 0

def test_provenance_derived():
    fv_derived = FieldValue(field="years_experience", value=4.5, source="system", method="derived:from_experience_dates")
    resolved = {
        "years_experience": ResolvedField(winners=[fv_derived], losers=[])
    }
    
    provs = build_provenance(resolved)
    assert len(provs) == 1
    assert provs[0].source == "system"
    assert "derived" in provs[0].method