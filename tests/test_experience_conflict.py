import pytest
from candidate_transformer.models import FieldValue
from candidate_transformer.engine.conflict import resolve_field
from candidate_transformer.engine.provenance import build_provenance

def test_experience_conflict_merging():
    # Setup two FieldValues with the same company and overlapping dates
    csv_fv = FieldValue(
        field="experience",
        value={
            "company": "Granville Tech",
            "title": "AI Engineer",
            "start": "2025-07",
            "end": "2025-10",
            "summary": None
        },
        source="recruiter_csv",
        method="csv_field",
        raw="...",
        extraction_confidence=0.9
    )
    
    pdf_fv = FieldValue(
        field="experience",
        value={
            "company": "Granville Tech",
            "title": "Generative AI Intern",
            "start": "2025-07",
            "end": "2025-10",
            "summary": "Worked on AI models"
        },
        source="resume:test1.pdf",
        method="resume_llm",
        raw="...",
        extraction_confidence=0.8
    )
    
    # Resolve
    resolved = resolve_field("experience", [csv_fv, pdf_fv])
    
    # We should have ONE winner
    assert len(resolved.winners) == 1
    winner_val = resolved.winners[0].value
    
    # The title should be from CSV (higher reliability)
    assert winner_val["title"] == "AI Engineer"
    
    # The summary should be from PDF (enriched)
    assert winner_val["summary"] == "Worked on AI models"
    
    # The loser should still be recorded
    assert len(resolved.losers) == 1
    
    # Now let's test provenance conflict tracking
    prov = build_provenance({"experience": resolved})
    
    # We should have a conflict provenance record for experience.title
    conflict_prov = [p for p in prov if getattr(p, "is_conflict", False) and p.field == "experience.title"]
    assert len(conflict_prov) == 1
    assert conflict_prov[0].value == "Generative AI Intern"
    assert conflict_prov[0].source == "resume:test1.pdf"

def test_experience_different_jobs():
    csv_fv = FieldValue(
        field="experience",
        value={
            "company": "Granville Tech",
            "title": "Software Engineer",
            "start": "2026-01",
            "end": "present",
            "summary": None
        },
        source="recruiter_csv",
        method="csv_field",
        raw="...",
        extraction_confidence=0.9
    )
    
    pdf_fv = FieldValue(
        field="experience",
        value={
            "company": "Granville Tech",
            "title": "Generative AI Intern",
            "start": "2025-07",
            "end": "2025-10",
            "summary": "Worked on AI models"
        },
        source="resume:test1.pdf",
        method="resume_llm",
        raw="...",
        extraction_confidence=0.8
    )
    
    # Resolve
    resolved = resolve_field("experience", [csv_fv, pdf_fv])
    
    # We should have TWO winners because the dates don't overlap
    assert len(resolved.winners) == 2
