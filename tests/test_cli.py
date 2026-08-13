import json
from candidate_transformer.cli import main

def test_cli_happy_path(capsys):
    argv = [
        "--input", "sample_data/recruiter_export.csv",
        "--input", "sample_data/resume_jane_doe.pdf",
        "--config", "configs/default.json",
        "--no-llm"
    ]
    exit_code = main(argv)
    assert exit_code == 0
    
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert isinstance(output, list)
    assert len(output) >= 2

def test_cli_custom_config(capsys):
    argv = [
        "--input", "sample_data/recruiter_export.csv",
        "--input", "sample_data/resume_jane_doe.pdf",
        "--config", "configs/custom_recruiter_view.json",
        "--no-llm"
    ]
    exit_code = main(argv)
    assert exit_code == 0
    
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    # Custom config renames 'full_name' to 'name'
    assert "name" in output[0]

def test_cli_robustness(capsys):
    # One valid input, one garbage input
    argv = [
        "--input", "sample_data/recruiter_export.csv",
        "--input", "does_not_exist.bin",
        "--config", "configs/default.json",
        "--no-llm"
    ]
    exit_code = main(argv)
    assert exit_code == 0
    
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert isinstance(output, list)
    assert len(output) > 0 # Should still process the valid CSV

def test_cli_all_garbage():
    argv = [
        "--input", "does_not_exist.bin",
        "--config", "configs/default.json"
    ]
    exit_code = main(argv)
    assert exit_code == 1 # Exits 1 if all inputs are unusable