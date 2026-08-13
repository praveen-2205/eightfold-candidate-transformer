import phonenumbers

def to_e164(raw: str, default_region: str = "US") -> str | None:
    if not raw or not isinstance(raw, str):
        return None
    try:
        parsed = phonenumbers.parse(raw, default_region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        pass
    return None