from typing import Any
from pydantic import BaseModel

class FieldValue(BaseModel):
    field: str                 
    value: Any                 
    source: str                
    method: str                
    raw: Any | None = None     
    extraction_confidence: float = 0.5   

class SourceRecord(BaseModel):
    source_id: str
    source_type: str           
    fields: list[FieldValue] = []
    errors: list[str] = []