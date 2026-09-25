#!/usr/bin/env python3
""".venv/bin/python scripts/md_to_pdf.py"""
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
pdf.add_font("DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
pdf.set_font("DejaVu", "", 9)
pdf.set_auto_page_break(auto=True, margin=15)
epw = pdf.w - 2*pdf.l_margin

with open("../INSTRUCTIONS.md") as f:
    md = f.read()

for line in md.split("\n"):
    if line.startswith("# "):
        pdf.set_font("DejaVu", "B", 14)
        pdf.multi_cell(epw, 8, line.strip("# "))
        pdf.ln(2)
        pdf.set_font("DejaVu", "", 9)
    elif line.startswith("## "):
        pdf.set_font("DejaVu", "B", 12)
        pdf.multi_cell(epw, 7, line.strip("# "))
        pdf.ln(1)
        pdf.set_font("DejaVu", "", 9)
    elif line.startswith("### "):
        pdf.set_font("DejaVu", "B", 10)
        pdf.multi_cell(epw, 6, line.strip("# "))
        pdf.ln(1)
        pdf.set_font("DejaVu", "", 9)
    elif line.startswith("```"):
        continue
    elif line.strip() == "":
        pdf.ln(2)
    elif line.strip().startswith("- "):
        pdf.multi_cell(epw, 4.5, f"  \u2022 {line.strip('- ')}")
    elif line.strip().startswith("| "):
        cells = [c.strip() for c in line.strip().split("|")[1:-1]]
        pdf.set_font("DejaVu", "", 7)
        pdf.cell(epw, 4, " | ".join(cells))
        pdf.ln()
        pdf.set_font("DejaVu", "", 9)
    else:
        pdf.multi_cell(epw, 4.5, line)

pdf.output("INSTRUCTIONS.pdf")
print(f"OK: INSTRUCTIONS.pdf created, {pdf.pages_count} pages")