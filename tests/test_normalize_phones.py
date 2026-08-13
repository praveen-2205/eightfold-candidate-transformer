from candidate_transformer.normalize import to_e164

def test_phones_happy():
    assert to_e164("(415) 555-0123") == "+14155550123"
    assert to_e164("+44 20 7123 1234", "GB") == "+442071231234"

def test_phones_edge():
    assert to_e164("not a phone") is None
    assert to_e164("") is None
    assert to_e164(None) is None