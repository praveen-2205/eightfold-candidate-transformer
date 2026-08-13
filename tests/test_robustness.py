import os
import json
from candidate_transformer.pipeline import run
from candidate_transformer.sources.csv_source import CsvSource

def test_missing_source_degrades_gracefully():
    # Valid resume + missing CSV -> should still produce a profile
    profiles = run(["does_not_exist.csv", "sample_data/resume_jane_doe.pdf"], use_llm=False)
    assert len(profiles) > 0
    assert any(p.full_name == "Jane Doe" for p in profiles)

def test_garbage_binary_source_tolerated(tmp_path):
    # Valid CSV + garbage binary file -> should still produce profiles from CSV, no crash
    bad_file = tmp_path / "garbage.bin"
    bad_file.write_bytes(b"\x00\xFF\xFE\x01\x02")
    
    profiles = run(["sample_data/recruiter_export.csv", str(bad_file)], use_llm=False)
    assert len(profiles) > 0
    
def test_invalid_values_become_null(tmp_path):
    # Create a CSV with a bad phone number
    csv_file = tmp_path / "bad_data.csv"
    csv_file.write_text("name,email,phone,current_company,title\nBad Phone,bp@x.com,not_a_phone,Acme,Dev", encoding="utf-8")
    
    profiles = run([str(csv_file)], use_llm=False)
    assert len(profiles) == 1
    
    # The invalid phone should be dropped entirely, leaving the phones array empty (null equivalent)
    assert profiles[0].phones == []
    assert profiles[0].emails == ["bp@x.com"]

def test_no_identity_resume(tmp_path):
    # Resume with no name, email, or phone, just skills
    resume_file = tmp_path / "anon_resume.txt"
    resume_file.write_text("Skills: ReactJS, python", encoding="utf-8")
    
    profiles = run([str(resume_file)], use_llm=False)
    assert len(profiles) == 1
    
    p = profiles[0]
    # Should still get a deterministic candidate_id (from hash of "unknown")
    assert p.candidate_id.startswith("c_")
    
    # Should extract skills
    assert len(p.skills) == 2
    
    # Confidence should be relatively low since there is no identity info
    assert p.overall_confidence < 0.5