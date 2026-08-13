import re

def normalize_name(raw: str) -> str | None:
    if not raw or not isinstance(raw, str):
        return None
    # Collapse whitespace and strip punctuation
    cleaned = re.sub(r"\s+", " ", raw).strip(" ,.-_")
    if not cleaned:
        return None
        
    # Title case only if all caps or all lower to preserve intended casing (e.g., McDowell)
    if cleaned.isupper() or cleaned.islower():
        return cleaned.title()
    return cleaned