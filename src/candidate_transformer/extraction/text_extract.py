import os
import re
from pypdf import PdfReader
from candidate_transformer.util.logging import get_logger

logger = get_logger(__name__)

def extract_text(path: str) -> str:
    if not os.path.exists(path):
        logger.warning(f"File not found: {path}")
        return ""
        
    ext = os.path.splitext(path)[1].lower()
    text = ""
    
    try:
        if ext == ".pdf":
            reader = PdfReader(path)
            pages_text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            text = "\n".join(pages_text)
            
        elif ext == ".txt":
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
                
        elif ext == ".docx":
            # Optional stub for DOCX
            logger.warning(f"DOCX support not yet implemented. Skipping: {path}")
            return ""
            
        else:
            logger.warning(f"Unsupported file extension '{ext}' for file: {path}")
            return ""
            
    except Exception as e:
        logger.warning(f"Failed to extract text from {path}: {e}")
        return ""
        
    # Collapse excessive blank lines to a maximum of two
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()