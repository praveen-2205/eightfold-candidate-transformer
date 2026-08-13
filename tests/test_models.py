import pytest
from candidate_transformer.models import CanonicalProfile, FieldValue, SourceRecord

def test_canonical_profile_defaults():
    profile = CanonicalProfile(candidate_id="c_123")
    dump = profile.model_dump()
    
    assert dump["candidate_id"] == "c_123"
    assert dump["emails"] == []
    assert dump["location"]["city"] is None
    assert dump["provenance"] == []
    assert dump["overall_confidence"] == 0.0

def test_canonical_profile_full():
    profile = CanonicalProfile(
        candidate_id="c_456",
        full_name="Jane Doe",
        emails=["jane@example.com"],
        overall_confidence=0.82
    )
    dump = profile.model_dump()
    
    assert dump["full_name"] == "Jane Doe"
    assert dump["emails"] == ["jane@example.com"]
    assert dump["overall_confidence"] == 0.82

def test_overall_confidence_validation():
    with pytest.raises(ValueError):
        CanonicalProfile(candidate_id="c_bad", overall_confidence=1.5)
        
    with pytest.raises(ValueError):
        CanonicalProfile(candidate_id="c_bad2", overall_confidence=-0.5)

def test_intermediate_models():
    fv = FieldValue(
        field="full_name",
        value="Jane Doe",
        source="recruiter_csv",
        method="csv_field",
        raw="Jane Doe",
        extraction_confidence=0.9
    )
    assert fv.raw == "Jane Doe"
    
    record = SourceRecord(
        source_id="csv_row_1",
        source_type="recruiter_csv",
        fields=[fv]
    )
    assert len(record.fields) == 1
    assert record.errors == []