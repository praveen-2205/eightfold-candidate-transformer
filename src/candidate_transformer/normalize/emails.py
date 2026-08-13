import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def normalize_email(raw: str) -> str | None:
    if not raw or not isinstance(raw, str):
        return None
    cleaned = raw.strip().lower()
    if EMAIL_REGEX.match(cleaned):
        return cleaned
    return None