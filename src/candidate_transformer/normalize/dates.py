from dateutil import parser
import re

def _clean_date_str(raw: str) -> str:
    if not raw or not isinstance(raw, str):
        return ""
    return raw.strip().lower()

def to_year_month(raw: str) -> str | None:
    cleaned = _clean_date_str(raw)
    if not cleaned:
        return None
    if cleaned in ["present", "current", "now"]:
        return "present"
    
    # Reject year-only strings (e.g., "2021") for month-precision fields
    if re.fullmatch(r"\d{4}", cleaned):
        return None

    try:
        dt = parser.parse(cleaned, default=None)
        return dt.strftime("%Y-%m")  # type: ignore
    except (ValueError, TypeError, OverflowError):
        return None

def to_year(raw: str) -> int | None:
    cleaned = _clean_date_str(raw)
    if not cleaned:
        return None
    
    # Fast path for explicit year
    match = re.search(r"\b(19|20)\d{2}\b", cleaned)
    if match:
        return int(match.group(0))
        
    try:
        dt = parser.parse(cleaned, default=None)
        return dt.year  # type: ignore
    except (ValueError, TypeError, OverflowError):
        return None