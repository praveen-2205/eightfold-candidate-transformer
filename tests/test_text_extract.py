import os
from candidate_transformer.extraction.text_extract import extract_text

def test_extract_pdf_happy():
    text = extract_text("sample_data/resume_jane_doe.pdf")
    assert "Jane Doe" in text
    assert "Skills" in text
    assert "jane@x.com" in text

def test_extract_txt_happy(tmp_path):
    # Use pytest's tmp_path to create a dummy txt file
    p = tmp_path / "dummy.txt"
    p.write_text("Line 1\n\n\n\nLine 2")
    
    text = extract_text(str(p))
    # Assert excessive newlines were collapsed
    assert text == "Line 1\n\nLine 2"

def test_extract_missing_file(caplog):
    text = extract_text("does_not_exist.pdf")
    assert text == ""
    assert "File not found" in caplog.text

def test_extract_unsupported_file(tmp_path, caplog):
    p = tmp_path / "image.png"
    p.write_bytes(b"fake image data")
    
    text = extract_text(str(p))
    assert text == ""
    assert "Unsupported file extension" in caplog.text