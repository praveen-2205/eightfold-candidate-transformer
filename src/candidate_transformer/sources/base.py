from typing import Protocol
from candidate_transformer.models import SourceRecord

class SourceAdapter(Protocol):
    source_type: str
    
    def load(self, path: str) -> list[SourceRecord]:
        ...