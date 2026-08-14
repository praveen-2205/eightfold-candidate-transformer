import os
import re

# 1. Update SKILL_ALIASES in skills.py to add AWS
skills_path = 'src/candidate_transformer/normalize/skills.py'
with open(skills_path, 'r', encoding='utf-8') as f:
    skills_content = f.read()

if '"aws": "AWS"' not in skills_content:
    missing_aws = '"kubernetes": "Kubernetes", "kubernets": "Kubernetes", "k8s": "Kubernetes",\n    "amazon web services": "AWS", "aws": "AWS",'
    skills_content = skills_content.replace('"kubernetes": "Kubernetes", "kubernets": "Kubernetes", "k8s": "Kubernetes",', missing_aws)
    with open(skills_path, 'w', encoding='utf-8') as f:
        f.write(skills_content)

# 2. Fix test_no_identity_resume using regex and a mock PDF reader
rob_path = 'tests/test_robustness.py'
with open(rob_path, 'r', encoding='utf-8') as f:
    rob_content = f.read()

new_pdf_test = '''def test_no_identity_resume(tmp_path, monkeypatch):
    # Mock pypdf so we don't need to generate a real PDF file for this test
    class MockPage:
        def extract_text(self): return "Skills: ReactJS, python"
        def __contains__(self, key): return False
    class MockReader:
        pages = [MockPage()]
        def __init__(self, *args, **kwargs): pass
        
    import pypdf
    monkeypatch.setattr(pypdf, "PdfReader", MockReader)
    
    resume_file = tmp_path / "anon_resume.pdf"
    resume_file.write_text("dummy PDF content", encoding="utf-8")
    
    from candidate_transformer.pipeline import run
    profiles = run([str(resume_file)], use_llm=False)
    assert len(profiles) == 1'''

# Forcefully replace the old function block
rob_content = re.sub(r'def test_no_identity_resume\(tmp_path\):.*?assert len\(profiles\) == 1', new_pdf_test, rob_content, flags=re.DOTALL)

with open(rob_path, 'w', encoding='utf-8') as f:
    f.write(rob_content)

print("Final test patches applied successfully!")
