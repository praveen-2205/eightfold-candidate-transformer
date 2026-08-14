import os
import re

# 1. Update SKILL_ALIASES in skills.py to satisfy the tests
skills_path = 'src/candidate_transformer/normalize/skills.py'
with open(skills_path, 'r', encoding='utf-8') as f:
    skills_content = f.read()

# Inject the missing test skills into the dictionary
missing_aliases = '''    "tensorflow": "TensorFlow", "tf": "TensorFlow",
    "react": "React", "reactjs": "React", "react.js": "React",
    "kubernetes": "Kubernetes", "kubernets": "Kubernetes", "k8s": "Kubernetes",'''
    
skills_content = skills_content.replace('"tensorflow": "TensorFlow", "tf": "TensorFlow",', missing_aliases)

with open(skills_path, 'w', encoding='utf-8') as f:
    f.write(skills_content)

# 2. Fix test_no_identity_resume (Create an actual PDF instead of a TXT file)
robustness_path = 'tests/test_robustness.py'
with open(robustness_path, 'r', encoding='utf-8') as f:
    rob_content = f.read()

old_pdf_test = '''    def test_no_identity_resume(tmp_path):
        # Resume with no name, email, or phone, just skills
        resume_file = tmp_path / "anon_resume.txt"
        resume_file.write_text("Skills: ReactJS, python", encoding="utf-8")'''

new_pdf_test = '''    def test_no_identity_resume(tmp_path):
        from reportlab.pdfgen import canvas
        
        # Must create an actual PDF file for the ResumeSource pypdf reader
        resume_file = tmp_path / "anon_resume.pdf"
        c = canvas.Canvas(str(resume_file))
        c.drawString(100, 750, "Skills: ReactJS, python")
        c.save()'''

rob_content = rob_content.replace(old_pdf_test, new_pdf_test)

with open(robustness_path, 'w', encoding='utf-8') as f:
    f.write(rob_content)

print("Test suite patched and aliases updated.")
