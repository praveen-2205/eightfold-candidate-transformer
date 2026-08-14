
from candidate_transformer.extraction.deterministic import extract_contacts
from candidate_transformer.normalize.skills import canonical_skill, is_known
from candidate_transformer.extraction.semantic import _post_process_llm_data, LLMOutput, LLMEducation

def test_portfolio_rejects_email_domain():
    text = "My email is test@gmail.com and domain is gmail.com"
    fields = extract_contacts(text, "test")
    portfolios = [f.value for f in fields if f.field == "links.portfolio"]
    assert "gmail.com" not in portfolios

def test_github_repo_is_other():
    text = "Code: https://github.com/user/repo-name"
    fields = extract_contacts(text, "test")
    githubs = [f for f in fields if f.field == "links.github"]
    others = [f for f in fields if f.field == "links.other"]
    assert len(githubs) == 0
    assert len(others) == 1
    assert others[0].value == "https://github.com/user/repo-name"
    
def test_github_profile_is_github():
    text = "Profile: https://github.com/username"
    fields = extract_contacts(text, "test")
    githubs = [f for f in fields if f.field == "links.github"]
    assert len(githubs) == 1
    
def test_skill_canonicalization():
    assert canonical_skill("tensorflow") == "TensorFlow"
    assert canonical_skill("Opencv") == "OpenCV"
    assert is_known("tensorflow") == True
    assert canonical_skill("UnknownSkill123") == "Unknownskill123"
    assert is_known("UnknownSkill123") == False

def test_education_split():
    output = LLMOutput(education=[
        LLMEducation(institution="IIIT", degree="Bachelor of Technology in Computer Science Engineering")
    ])
    fields = _post_process_llm_data(output, "test")
    edu_field = next(f for f in fields if f.field == "education")
    assert edu_field.value["degree"] == "Bachelor of Technology"
    assert edu_field.value["field"] == "Computer Science Engineering"
