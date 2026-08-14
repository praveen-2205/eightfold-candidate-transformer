from candidate_transformer.sources.csv_source import CsvSource

def test_csv_happy_path():
    source = CsvSource()
    records = source.load("sample_data/recruiter_export.csv")
    assert len(records) >= 3
    
    jane = next(r for r in records if any(f.value == "Jane Doe" for f in r.fields))
    assert jane.source_type == "recruiter_csv"
    
    phones = [f for f in jane.fields if f.field == "phones"]
    assert len(phones) == 0

def test_csv_messy_row():
    source = CsvSource()
    records = source.load("sample_data/recruiter_export.csv")
    
    messy = next(r for r in records if any(f.value == "Messy Person" for f in r.fields))
    # Should have no phone field because it was empty/invalid
    assert not any(f.field == "phones" for f in messy.fields)

def test_csv_missing_file(caplog):
    source = CsvSource()
    records = source.load("does_not_exist.csv")
    assert records == []
    assert "File not found" in caplog.text