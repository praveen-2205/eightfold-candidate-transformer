import csv
import json
import os
from pypdf import PdfReader

def test_csv_fixture():
    path = "sample_data/recruiter_export.csv"
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) >= 3
        assert "name" in reader.fieldnames
        assert any(row["name"] == "Jane Doe" for row in rows)

def test_pdf_fixture():
    path = "sample_data/resume_jane_doe.pdf"
    assert os.path.exists(path)
    reader = PdfReader(path)
    text = reader.pages[0].extract_text()
    assert "Jane Doe" in text
    assert "jane@x.com" in text
    assert "Skills" in text

def test_configs_exist_and_load():
    for cfg in ["configs/default.json", "configs/custom_recruiter_view.json"]:
        assert os.path.exists(cfg)
        with open(cfg, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "fields" in data