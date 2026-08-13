from candidate_transformer.normalize import to_iso_alpha2

def test_country_happy():
    assert to_iso_alpha2("United States") == "US"
    assert to_iso_alpha2("USA") == "US"
    assert to_iso_alpha2("Canada") == "CA"

def test_country_failure():
    assert to_iso_alpha2("Freedonia") is None
    assert to_iso_alpha2("") is None