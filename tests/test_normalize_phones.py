
from candidate_transformer.normalize import to_e164

def test_phones_strict_no_guess():
    # Should NOT guess +1 when country code is missing
    assert to_e164("(415) 555-0123") is None
    assert to_e164("6369821425") is None

def test_phones_with_country_code():
    # Should work when country code is explicit
    assert to_e164("+1 (415) 555-0123") == "+14155550123"
    assert to_e164("+91 98765 43210") == "+919876543210"
