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

print("=== Metacognition on Page 233 ===")
check_phrase(233, "metacognition")

print("=== Office hours on Page 36-40 ===")
for p in range(35, 41):
    check_phrase(p, "office hours")

print("=== Academic Advisor / Major on Page 130-145 ===")
for p in range(130, 145):
    check_phrase(p, "advisor")

print("=== Active listening on Page 270-285 ===")
for p in range(270, 285):
    check_phrase(p, "active listening")

print("=== Note-taking / Cornell on Page 183-185 ===")
for p in range(183, 186):
    check_phrase(p, "cue column")
    check_phrase(p, "three sections")

