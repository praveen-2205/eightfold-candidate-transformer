from candidate_transformer.models.config import OutputConfig

class SchemaValidationError(Exception):
    pass

def _check_type(value: any, expected_type: str) -> bool:
    if expected_type == "string":
        return isinstance(value, str)
    elif expected_type == "string[]":
        return isinstance(value, list) and all(isinstance(x, str) for x in value)
    elif expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    elif expected_type == "boolean":
        return isinstance(value, bool)
    elif expected_type == "object":
        return isinstance(value, dict)
    elif expected_type == "object[]":
        return isinstance(value, list) and all(isinstance(x, dict) for x in value)
    return True # If unknown type, let it pass or handle as needed

def validate_output(output: dict, config: OutputConfig) -> None:
    for spec in config.fields:
        val = output.get(spec.path)
        
        # 1. Check requirement
        if val is None:
            if spec.required:
                raise SchemaValidationError(f"Field '{spec.path}' is required but got null/missing.")
            continue # If not required and missing, it's valid
            
        # 2. Check type
        if not _check_type(val, spec.type):
            raise SchemaValidationError(f"Field '{spec.path}' expected type '{spec.type}', got {type(val).__name__}.")