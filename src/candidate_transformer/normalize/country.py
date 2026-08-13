import pycountry

def to_iso_alpha2(raw: str) -> str | None:
    if not raw or not isinstance(raw, str):
        return None
    cleaned = raw.strip()
    try:
        # Try exact lookup first
        result = pycountry.countries.lookup(cleaned)
        return result.alpha_2
    except LookupError:
        # Try fuzzy search as fallback
        try:
            results = pycountry.countries.search_fuzzy(cleaned)
            if results:
                return results[0].alpha_2
        except Exception:
            pass
    return None