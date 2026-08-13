import re
import phonenumbers
from candidate_transformer.models import FieldValue
from candidate_transformer.normalize import normalize_email, to_e164, classify_url

# Standard regex patterns
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
URL_REGEX = re.compile(r"(?:https?://)?(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)")

def extract_contacts(text: str, source_id: str) -> list[FieldValue]:
    if not text or not isinstance(text, str):
        return []
        
    fields = []
    
    # 1. Name Heuristic: Look at the first few lines for a valid name
    # Criteria: 1-4 tokens, alpha characters and spaces only, no digits/emails
    for line in text.split("\n")[:10]:
        clean_line = line.strip()
        if not clean_line:
            continue
            
        # Reject if contains digits or @
        if any(char.isdigit() or char == '@' for char in clean_line):
            continue
            
        tokens = clean_line.split()
        if 1 <= len(tokens) <= 4:
            # Check if tokens are primarily alphabetic
            if all(re.match(r"^[A-Za-z\.\-]+$", t) for t in tokens):
                fields.append(FieldValue(
                    field="full_name",
                    value=clean_line,
                    source=source_id,
                    method="resume_regex",
                    raw=clean_line,
                    extraction_confidence=0.80  # Lower than CSV's 0.9
                ))
                break # Only take the first matching line as the name
                
    # 2. Emails
    for match in EMAIL_REGEX.finditer(text):
        raw_email = match.group(0)
        norm_email = normalize_email(raw_email)
        if norm_email:
            fields.append(FieldValue(
                field="emails",
                value=norm_email,
                source=source_id,
                method="resume_regex",
                raw=raw_email,
                extraction_confidence=0.85
            ))
            
    # 3. Phones (using phonenumbers Matcher for robustness)
    for match in phonenumbers.PhoneNumberMatcher(text, "US"):
        raw_phone = match.raw_string
        norm_phone = to_e164(raw_phone)
        if norm_phone:
            fields.append(FieldValue(
                field="phones",
                value=norm_phone,
                source=source_id,
                method="normalized:E164",
                raw=raw_phone,
                extraction_confidence=0.85
            ))
            
    # 4. URLs (LinkedIn, GitHub, Portfolio)
    for match in URL_REGEX.finditer(text):
        raw_url = match.group(0)
        url_tuple = classify_url(raw_url)
        if url_tuple:
            kind, norm_url = url_tuple
            fields.append(FieldValue(
                field=f"links.{kind}",
                value=norm_url,
                source=source_id,
                method="resume_regex",
                raw=raw_url,
                extraction_confidence=0.85
            ))
            
    return fields