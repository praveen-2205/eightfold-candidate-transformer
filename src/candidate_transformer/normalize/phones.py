import phonenumbers

def to_e164(phone_str: str, default_region: str | None = None) -> str | None:
    """
    Normalizes a phone number to E.164 format.
    If no country code is present and no default region is explicitly provided,
    it returns None (Do not guess policy).
    """
    if not phone_str:
        return None
        
    try:
        # Parse the number. If default_region is None, it requires an explicit country code (+).
        parsed = phonenumbers.parse(phone_str, default_region)
        
        # Check if it's actually a valid number for that region
        if not phonenumbers.is_valid_number(parsed):
            return None
            
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return None