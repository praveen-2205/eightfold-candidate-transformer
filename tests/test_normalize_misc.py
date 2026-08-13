from candidate_transformer.normalize import normalize_email, normalize_name, classify_url

def test_emails():
    assert normalize_email(" Jane@X.COM ") == "jane@x.com"
    assert normalize_email("invalid email") is None

def test_names():
    assert normalize_name("jane doe") == "Jane Doe"
    assert normalize_name("JANE DOE") == "Jane Doe"
    assert normalize_name("de la Cruz") == "de la Cruz"
    assert normalize_name("  Jane   Doe. ") == "Jane Doe"

def test_urls():
    assert classify_url("github.com/janedoe?ref=123") == ("github", "https://github.com/janedoe")
    assert classify_url("https://www.linkedin.com/in/jane") == ("linkedin", "https://linkedin.com/in/jane")
    assert classify_url("myportfolio.com/work") == ("portfolio", "https://myportfolio.com/work")
    assert classify_url("not a url") is None