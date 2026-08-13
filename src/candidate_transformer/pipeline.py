import os
from candidate_transformer.models import CanonicalProfile
from candidate_transformer.sources.csv_source import CsvSource
from candidate_transformer.sources.resume_source import ResumeSource
from candidate_transformer.engine.build import build_profiles
from candidate_transformer.util.logging import get_logger

logger = get_logger(__name__)

def run(input_paths: list[str], use_llm: bool = False) -> list[CanonicalProfile]:
    all_records = []
    
    csv_adapter = CsvSource()
    resume_adapter = ResumeSource(use_llm=use_llm)
    
    for path in input_paths:
        if not os.path.exists(path):
            logger.warning(f"Input path does not exist: {path}")
            continue
            
        ext = os.path.splitext(path)[1].lower()
        if ext == ".csv":
            records = csv_adapter.load(path)
            all_records.extend(records)
            logger.info(f"Loaded {len(records)} records from {path}")
        elif ext in [".pdf", ".txt", ".docx"]:
            records = resume_adapter.load(path)
            all_records.extend(records)
            logger.info(f"Loaded {len(records)} records from {path}")
        else:
            logger.warning(f"No adapter available for file type '{ext}' ({path})")
            
    if not all_records:
        logger.warning("No records extracted from any inputs.")
        return []
        
    profiles = build_profiles(all_records)
    logger.info(f"Built {len(profiles)} canonical profiles from {len(all_records)} source records.")
    return profiles