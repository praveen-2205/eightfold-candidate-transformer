from candidate_transformer.normalize import canonical_skill, is_known

def test_skills_happy():
    assert canonical_skill("reactjs") == "React"
    assert canonical_skill("  amazon web services ") == "AWS"

def test_skills_fuzzy():
    assert canonical_skill("Kubernets") == "Kubernetes" # typo

def test_skills_unknown():
    assert canonical_skill("Some New Framework") == "Some New Framework"
    assert not is_known("Some New Framework")
    assert is_known("react")