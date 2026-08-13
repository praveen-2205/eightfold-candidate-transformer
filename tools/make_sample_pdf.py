import os
from fpdf import FPDF

def make_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Disable metadata for deterministic output
    pdf.set_creator("")
    pdf.set_author("")
    
    # Header
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Jane Doe", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, "jane@x.com | (415) 555-0123", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "https://github.com/janedoe | https://linkedin.com/in/janedoe", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Summary
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 8, "Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, "Experienced software engineer specializing in scalable backend systems.")
    pdf.ln(5)
    
    # Skills
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 8, "Skills:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, "ReactJS, python, AWS, k8s", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Experience
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 8, "Experience", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "Senior Engineer at Acme", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "I", 12)
    pdf.cell(0, 8, "Jan 2021 - Present", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, "Led backend development using Python and AWS.")
    pdf.ln(2)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "Software Engineer at TechCorp", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "I", 12)
    pdf.cell(0, 8, "Jun 2018 - Dec 2020", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 12)
    pdf.multi_cell(0, 8, "Developed user interfaces using ReactJS.")
    pdf.ln(5)
    
    # Education
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 8, "Education", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, "B.S. Computer Science, State University, 2018", new_x="LMARGIN", new_y="NEXT")
    
    out_path = os.path.join("sample_data", "resume_jane_doe.pdf")
    os.makedirs("sample_data", exist_ok=True)
    pdf.output(out_path)
    print(f"Wrote {out_path} (1 page)")

if __name__ == "__main__":
    make_pdf()