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

print("=== Mnemonics on Page 214-218 ===")
for p in range(214, 219):
    check_phrase(p, "mnemonic")

print("=== Skimming / Reading on Page 164-167 ===")
for p in range(164, 168):
    check_phrase(p, "skimming")

