import os
from candidate_transformer.models import SourceRecord
from candidate_transformer.extraction.text_extract import extract_text
from candidate_transformer.extraction.deterministic import extract_contacts
from candidate_transformer.extraction.semantic import get_extractor
from candidate_transformer.util.logging import get_logger

logger = get_logger(__name__)

class ResumeSource:
    source_type = "resume"
    
    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        self.semantic_extractor = get_extractor(use_llm=self.use_llm)
        
    def load(self, path: str) -> list[SourceRecord]:
        source_id = f"resume:{os.path.basename(path)}"
        text = extract_text(path)
        
        if not text:
            return []
            
        fields = []
        try:
            fields.extend(extract_contacts(text, source_id))
            fields.extend(self.semantic_extractor.extract(text, source_id))
        except Exception as e:
            logger.error(f"Extraction failed for {path}: {e}")
            
        if not fields:
            return []
            
        return [SourceRecord(
            source_id=source_id,
            source_type=self.source_type,
            fields=fields
        )]