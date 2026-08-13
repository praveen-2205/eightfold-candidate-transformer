from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class FieldSpec(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    path: str
    from_: str | None = Field(default=None, alias="from")
    type: str
    required: bool = False
    normalize: str | None = None
    on_missing: Literal["null", "omit", "error"] | None = None

class OutputConfig(BaseModel):
    fields: list[FieldSpec]
    include_confidence: bool = False
    include_provenance: bool = False
    on_missing: Literal["null", "omit", "error"] = "null"