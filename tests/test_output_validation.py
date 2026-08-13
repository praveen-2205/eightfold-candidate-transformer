import pytest
from candidate_transformer.models.config import OutputConfig, FieldSpec
from candidate_transformer.projection.validate import validate_output, SchemaValidationError

def test_validate_happy_path():
    config = OutputConfig(
        fields=[
            FieldSpec(path="name", type="string", required=True),
            FieldSpec(path="skills", type="string[]"),
            FieldSpec(path="years", type="number")
        ]
    )
    
    valid_output = {
        "name": "Jane",
        "skills": ["React", "Python"],
        "years": 5.5
    }
    
    # Should not raise
    validate_output(valid_output, config)

def test_validate_missing_required():
    config = OutputConfig(fields=[FieldSpec(path="name", type="string", required=True)])
    
    with pytest.raises(SchemaValidationError, match="required but got null/missing"):
        validate_output({"name": None}, config)
        
    with pytest.raises(SchemaValidationError, match="required but got null/missing"):
        validate_output({}, config)

def test_validate_type_mismatch():
    config = OutputConfig(fields=[FieldSpec(path="skills", type="string[]")])
    
    # Passing a string instead of string[]
    with pytest.raises(SchemaValidationError, match="expected type 'string\\[\\]'"):
        validate_output({"skills": "React"}, config)
        
    # Passing a list of dicts instead of string[]
    with pytest.raises(SchemaValidationError, match="expected type 'string\\[\\]'"):
        validate_output({"skills": [{"name": "React"}]}, config)