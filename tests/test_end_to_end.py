import os
import json
import pytest
from candidate_transformer.pipeline import run
from candidate_transformer.projection.config_loader import load_config
from candidate_transformer.projection.project import project

def test_gold_profile_end_to_end():
    # Run the pipeline deterministically
    profiles = run([
        "sample_data/recruiter_export.csv", 
        "sample_data/resume_jane_doe.pdf"
    ], use_llm=False)
    
    config = load_config("configs/default.json")
    
    output_data = []
    for p in profiles:
        output_data.append(project(p, config))
        
    gold_path = os.path.join("tests", "gold", "default_gold.json")
    
    # Generate gold file if it doesn't exist or if REGEN=1
    if os.environ.get("REGEN") == "1" or not os.path.exists(gold_path):
        os.makedirs(os.path.dirname(gold_path), exist_ok=True)
        with open(gold_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, default=str)
        pytest.skip("Regenerated gold profile. Run tests again to compare.")
        
    with open(gold_path, "r", encoding="utf-8") as f:
        gold_data = json.load(f)
        
    # Serialize and deserialize current output to ensure types (like tuples) match JSON formats
    current_json = json.loads(json.dumps(output_data, default=str))
    
    # Assert byte-for-byte deterministic equality
    assert current_json == gold_data