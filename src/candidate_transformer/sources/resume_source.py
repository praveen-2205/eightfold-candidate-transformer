import os
import pypdf
from candidate_transformer.models import SourceRecord
from candidate_transformer.extraction.deterministic import extract_contacts
from candidate_transformer.extraction.semantic import get_extractor
from candidate_transformer.util.logging import get_logger

logger = get_logger(__name__)

class ResumeSource:
    def __init__(self, use_llm: bool = True):
        self.semantic_extractor = get_extractor(use_llm)

    def load(self, filepath: str) -> list[SourceRecord]:
        if not os.path.exists(filepath):
            logger.warning(f"Input path does not exist: {filepath}")
            return []
            
        source_id = f"resume:{os.path.basename(filepath)}"
        text_chunks = []
        
        try:
            with open(filepath, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    # 1. Extract visible prose text
                    text = page.extract_text()
                    if text:
                        text_chunks.append(text)
                        
                    # 2. Extract hidden hyperlink annotations
                    if "/Annots" in page:
                        for annot_ref in page["/Annots"]:
                            # Resolve the indirect PDF object
                            annot = annot_ref.get_object()
                            if annot.get("/Subtype") == "/Link":
                                action = annot.get("/A")
                                if action and action.get("/S") == "/URI":
                                    uri = action.get("/URI")
                                    if uri:
                                        # Append the hidden URL so the regex engine can find it
                                        text_chunks.append(str(uri))
                                        
        except Exception as e:
            logger.error(f"Failed to read PDF {filepath}: {e}")
            return []

        full_text = "\n".join(text_chunks)
        
        # Extract fields using the newly aggregated text (visible prose + hidden links)
        fields = extract_contacts(full_text, source_id)
        fields.extend(self.semantic_extractor.extract(full_text, source_id))
        
        return [SourceRecord(source_id=source_id, source_type="resume", fields=fields)]