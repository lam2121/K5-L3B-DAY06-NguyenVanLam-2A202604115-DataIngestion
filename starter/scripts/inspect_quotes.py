import pypdf
import re
import json
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
pdf_path = base_dir / "data" / "College_Success_web.pdf"
reader = pypdf.PdfReader(str(pdf_path))

def get_page_text(p_num: int) -> str:
    text = reader.pages[p_num - 1].extract_text() or ""
    return re.sub(r"\s+", " ", text).strip()

# Let's inspect some pages to find exact text quotes
def find_quotes_in_page(p_num: int, search_words: list[str]):
    text = get_page_text(p_num)
    print(f"=== Page {p_num} ===")
    for w in search_words:
        pos = text.lower().find(w.lower())
        if pos != -1:
            snippet = text[max(0, pos-40):min(len(text), pos+160)]
            print(f"Match for '{w}': {snippet}\n")
        else:
            print(f"NOT found: '{w}'")

# Inspection
find_quotes_in_page(11, ["Welcome to College Success", "Creative Commons"])
find_quotes_in_page(31, ["Differences between High School", "High School Faculty", "College Faculty"])
find_quotes_in_page(92, ["procrastination is the act", "chronic procrastinators"])
find_quotes_in_page(97, ["Pomodoro Technique", "twenty-five minutes"])
find_quotes_in_page(101, ["Time on task for common college activities", "Study for exam"])
find_quotes_in_page(165, ["skimming", "scanning", "active reading"])
find_quotes_in_page(180, ["transcribe every single word", "court-reporter"])
find_quotes_in_page(204, ["Working memory is a type of short-term memory", "Marilyn"])
find_quotes_in_page(212, ["Avoiding Distractions", "Two major and interrelated techniques"])
find_quotes_in_page(224, ["test anxiety", "cramming"])
