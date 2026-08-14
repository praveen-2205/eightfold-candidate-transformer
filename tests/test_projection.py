import pytest
from candidate_transformer.models.canonical import CanonicalProfile
from candidate_transformer.models.config import OutputConfig, FieldSpec
from candidate_transformer.projection.config_loader import load_config
from candidate_transformer.projection.project import project, ProjectionError

def test_default_config_loads():
    config = load_config("configs/default.json")
    assert len(config.fields) > 0

def test_project_custom_config():
    profile = CanonicalProfile(
        candidate_id="c_123",
        full_name="Jane Doe",
        emails=["jane@x.com", "other@y.com"],
        phones=["+14155550123"],
        skills=[
            {"name": "reactjs", "confidence": 0.9, "sources": []},
            {"name": "python", "confidence": 0.9, "sources": []}
        ]
    )
    
    config = OutputConfig(
        fields=[
            FieldSpec(path="name", from_="full_name", type="string"),
            FieldSpec(path="primary_email", from_="emails[0]", type="string"),
            FieldSpec(path="phone", from_="phones[0]", type="string", normalize="E164"),
            FieldSpec(path="skills", from_="skills[].name", type="string[]", normalize="canonical")
        ],
        include_confidence=True
    )
    
    out = project(profile, config)
    assert out["name"] == "Jane Doe"
    assert out["primary_email"] == "jane@x.com" # Picks index 0
    assert out["phone"] == "+14155550123" # Normalized
    assert out["skills"] == ["React", "Python"] # Mapped array + Normalized
    assert out["overall_confidence"] == 0.0

def test_on_missing_policies():
    profile = CanonicalProfile(candidate_id="c_123")
    
    # 1. Policy: null (default)
    cfg_null = OutputConfig(fields=[FieldSpec(path="full_name", type="string")], on_missing="null")
    assert project(profile, cfg_null) == {"full_name": None}
    
    # 2. Policy: omit
    cfg_omit = OutputConfig(fields=[FieldSpec(path="full_name", type="string")], on_missing="omit")
    assert project(profile, cfg_omit) == {}
    
    # 3. Policy: error
    cfg_error = OutputConfig(fields=[FieldSpec(path="full_name", type="string")], on_missing="error")
    with pytest.raises(ProjectionError):
        project(profile, cfg_error)
        
    # 4. Required field acts like 'error' if it's missing
    cfg_req = OutputConfig(fields=[FieldSpec(path="full_name", type="string", required=True)], on_missing="null")
    with pytest.raises(ProjectionError):
        project(profile, cfg_req)