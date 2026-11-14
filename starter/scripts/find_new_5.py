import pypdf
import re
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
pdf_path = base_dir / "data" / "College_Success_web.pdf"
reader = pypdf.PdfReader(str(pdf_path))

def check_phrase(p_num, phrase):
    txt = re.sub(r"\s+", " ", reader.pages[p_num - 1].extract_text() or "")
    pos = txt.lower().find(phrase.lower())
    if pos != -1:
        print(f"Page {p_num}: FOUND '{phrase}'")
        print("  Snippet:", repr(txt[pos:pos+250]))
        print()
        return True
    return False

print("=== Checking SMART goals ===")
for p in range(110, 115):
    check_phrase(p, "Specific")
    check_phrase(p, "Measurable")
    check_phrase(p, "Attainable")

print("=== Checking Critical thinking ===")
for p in range(231, 236):
    check_phrase(p, "Critical thinking")

print("=== Checking Academic prerequisites / Degree plan ===")
for p in range(130, 137):
    check_phrase(p, "prerequisite")

print("=== Checking Mindset / Brain plasticity ===")
for p in range(50, 58):
    check_phrase(p, "plasticity")
    check_phrase(p, "neuron")

