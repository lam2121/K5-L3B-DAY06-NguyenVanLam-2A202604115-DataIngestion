import pypdf
import re
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
pdf_path = base_dir / "data" / "College_Success_web.pdf"
reader = pypdf.PdfReader(str(pdf_path))

def get_page_text(p_num: int) -> str:
    text = reader.pages[p_num - 1].extract_text() or ""
    return re.sub(r"\s+", " ", text).strip()

def print_page_snippet(p: int, keyword: str):
    txt = get_page_text(p)
    pos = txt.lower().find(keyword.lower())
    if pos != -1:
        print(f"=== Page {p} (keyword: {keyword}) ===")
        print(txt[max(0, pos-20):min(len(txt), pos+300)])
        print()

print_page_snippet(11, "Creative Commons Attribution")
print_page_snippet(29, "syllabus")
print_page_snippet(31, "High School Faculty")
print_page_snippet(47, "Bloom")
print_page_snippet(60, "growth and fixed mindset")
print_page_snippet(66, "Learning Styles")
print_page_snippet(92, "procrastination is the act")
print_page_snippet(101, "Study for exam")
print_page_snippet(111, "SMART")
print_page_snippet(126, "values")
print_page_snippet(173, "SQ3R")
print_page_snippet(180, "transcribe every single word")
print_page_snippet(183, "Cornell")
print_page_snippet(204, "Working memory is a type")
print_page_snippet(209, "mnemonic")
print_page_snippet(212, "Two major and interrelated techniques")
print_page_snippet(234, "creative thinking")
print_page_snippet(268, "communication")
print_page_snippet(300, "diversity")
print_page_snippet(330, "financial")

