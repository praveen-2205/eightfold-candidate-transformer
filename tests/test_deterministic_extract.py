from candidate_transformer.extraction.deterministic import extract_contacts

def test_extract_contacts_happy():
    text = """
    Jane Doe
    Software Engineer
    jane.doe@example.com
    Call me: +1 (415) 555-0123
    Code: https://github.com/janedoe
    """
    fields = extract_contacts(text, "resume:test.pdf")
    
    assert any(f.field == "full_name" and f.value == "Jane Doe" for f in fields)
    assert any(f.field == "emails" and f.value == "jane.doe@example.com" for f in fields)
    assert any(f.field == "phones" and f.value == "+14155550123" for f in fields)
    assert any(f.field == "links.github" and f.value == "https://github.com/janedoe" for f in fields)

def test_extract_contacts_edge_cases():
    text = """
    Not A Name 123
    jane@x.com
    Fake phone: 999-999-9999999
    """
    fields = extract_contacts(text, "resume:test2.pdf")
    
    # 123 prevents it from being picked up as a name
    assert not any(f.field == "full_name" for f in fields)
    
    # Fake phone should fail E164 normalization and not be emitted
    assert not any(f.field == "phones" for f in fields)
    
    # Email should still be caught
    assert any(f.field == "emails" and f.value == "jane@x.com" for f in fields)

def test_extract_contacts_empty():
    assert extract_contacts("", "resume:empty") == []
    assert extract_contacts(None, "resume:none") == []