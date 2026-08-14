import re
import phonenumbers
from candidate_transformer.models import FieldValue
from candidate_transformer.normalize import to_e164, normalize_email

def extract_contacts(text: str | None, source_id: str) -> list[FieldValue]:
    if not text:
        return []
        
    fields = []
    
    # 0. Name (Basic heuristic: first non-empty line)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        name = lines[0]
        if len(name) < 50 and not any(char.isdigit() for char in name):  # Sanity check to avoid grabbing a whole paragraph
            fields.append(FieldValue(
                field="full_name", value=name, 
                source=source_id, method="resume_regex", 
                raw=name, extraction_confidence=0.80
            ))
    
    # 1. Emails
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    found_emails = set()
    for match in re.finditer(email_pattern, text):
        raw_email = match.group(0)
        norm_email = normalize_email(raw_email)
        if norm_email and norm_email not in found_emails:
            found_emails.add(norm_email)
            fields.append(FieldValue(
                field="emails", value=norm_email, 
                source=source_id, method="resume_regex", 
                raw=raw_email, extraction_confidence=0.95
            ))

    # 2. Phones (Strict: Do not guess country code)
    for phone_match in phonenumbers.PhoneNumberMatcher(text, None):
        raw_phone = phone_match.raw_string
        norm_phone = to_e164(raw_phone)
        if norm_phone:
            fields.append(FieldValue(
                field="phones", value=norm_phone, 
                source=source_id, method="normalized:E164", 
                raw=raw_phone, extraction_confidence=0.90
            ))

    # 3. URLs (Visible in text)
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(com|org|net|io|me|dev)[^\s]*)'
    for match in re.finditer(url_pattern, text):
        raw_url = match.group(0).rstrip('.,;)')
        
        # EXPLICITLY PREVENT EMAILS FROM BEING PARSED AS URLS
        if '@' in raw_url:
            continue
            
        url_lower = raw_url.lower()
        
        # Explicitly reject common email domains from being treated as bare URLs
        if url_lower in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
            continue
            
        if "linkedin.com" in url_lower:
            field_name = "links.linkedin"
        elif "github.com" in url_lower:
            # Distinguish between profile (1 slash) and repo (multiple slashes)
            path = url_lower.split("github.com/")[-1].strip("/")
            if "/" in path:
                field_name = "links.other"
            else:
                field_name = "links.github"
        elif "scholar.google.com" in url_lower:
            field_name = "links.other"
        else:
            field_name = "links.portfolio"
            
        fields.append(FieldValue(
            field=field_name, value=raw_url, 
            source=source_id, method="resume_regex", 
            raw=raw_url, extraction_confidence=0.85
        ))
        
    return fields