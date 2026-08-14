import os
import re

# 1. Update skills.py (Skill Canonicalization & Confidence Link)
skills_path = 'src/candidate_transformer/normalize/skills.py'
skills_content = '''
SKILL_ALIASES = {
    "tensorflow": "TensorFlow", "tf": "TensorFlow",
    "pytorch": "PyTorch", "opencv": "OpenCV",
    "fastapi": "FastAPI", "langgraph": "LangGraph",
    "langchain": "LangChain", "github": "GitHub",
    "neo4j": "Neo4j", "sql": "SQL", "nlp": "NLP",
    "spacy": "spaCy", "scipy": "SciPy", "numpy": "NumPy",
    "pandas": "pandas", "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn", "llm": "LLM", "llms": "LLMs",
    "python": "Python", "java": "Java", "c++": "C++", "c": "C"
}

def canonical_skill(raw_skill: str) -> str | None:
    if not raw_skill:
        return None
    cleaned = raw_skill.strip().lower()
    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]
    return raw_skill.strip().title()

def is_known(raw_skill: str) -> bool:
    if not raw_skill:
        return False
    return raw_skill.strip().lower() in SKILL_ALIASES
'''
with open(skills_path, 'w', encoding='utf-8') as f:
    f.write(skills_content)

# 2. Update deterministic.py (URL Classification Fixes)
det_path = 'src/candidate_transformer/extraction/deterministic.py'
with open(det_path, 'r', encoding='utf-8') as f:
    det_code = f.read()

new_url_logic = '''
        url_lower = raw_url.lower()
        
        # Explicitly reject common email domains from being treated as bare URLs
        if url_lower in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
            continue
            
        if "linkedin.com" in url_lower:
            field_name = "links.linkedin"
        elif "github.com" in url_lower:
            # Distinguish between profile (1 slash) and repo (multiple slashes)
            path = url_lower.split("github.com/")[-1].strip("/")
            if "/" in path:
                field_name = "links.other"
            else:
                field_name = "links.github"
        elif "scholar.google.com" in url_lower:
            field_name = "links.other"
        else:
            field_name = "links.portfolio"
'''
# Inject the new logic over the old block
det_code = re.sub(r'url_lower = raw_url\.lower\(\).*?field_name = "links\.portfolio"', new_url_logic.strip(), det_code, flags=re.DOTALL)
with open(det_path, 'w', encoding='utf-8') as f:
    f.write(det_code)

# 3. Update semantic.py (Education Degree/Field Split)
sem_path = 'src/candidate_transformer/extraction/semantic.py'
with open(sem_path, 'r', encoding='utf-8') as f:
    sem_code = f.read()

old_edu = '''        if not edu.institution and not edu.degree:
            continue
            
        norm_edu = {
            "institution": edu.institution.strip() if edu.institution else None,
            "degree": edu.degree.strip() if edu.degree else None,
            "field": edu.field.strip() if edu.field else None,
            "end_year": to_year(str(edu.end_year)) if edu.end_year else None
        }'''
        
new_edu = '''        if not edu.institution and not edu.degree:
            continue
            
        degree = edu.degree.strip() if edu.degree else None
        field = edu.field.strip() if edu.field else None
        
        # Deterministic split for "Degree in Field"
        if degree and not field and " in " in degree.lower():
            import re as regex
            parts = regex.split(r'\s+in\s+', degree, maxsplit=1, flags=regex.IGNORECASE)
            if len(parts) == 2:
                degree = parts[0].strip()
                field = parts[1].strip()
                
        norm_edu = {
            "institution": edu.institution.strip() if edu.institution else None,
            "degree": degree,
            "field": field,
            "end_year": to_year(str(edu.end_year)) if edu.end_year else None
        }'''

sem_code = sem_code.replace(old_edu, new_edu)
with open(sem_path, 'w', encoding='utf-8') as f:
    f.write(sem_code)

# 4. Write Regression Tests
test_path = 'tests/test_fixes.py'
test_code = '''
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
'''
with open(test_path, 'w', encoding='utf-8') as f:
    f.write(test_code)

print("Pipeline fixes applied and test suite generated.")
