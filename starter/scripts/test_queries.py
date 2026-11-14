import pypdf
import re
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
pdf_path = base_dir / "data" / "College_Success_web.pdf"
reader = pypdf.PdfReader(str(pdf_path))

def get_page_text(p_num: int) -> str:
    text = reader.pages[p_num - 1].extract_text() or ""
    return re.sub(r"\s+", " ", text).strip()

def search_text(keywords: list[str], start_p: int, end_p: int):
    results = []
    for p in range(start_p, end_p + 1):
        txt = get_page_text(p)
        if all(k.lower() in txt.lower() for k in keywords):
            results.append((p, txt))
    return results

print("=== Checking queries ===")
for kw, sp, ep in [
    (["Creative Commons Attribution", "license"], 10, 15),
    (["High School Faculty", "College Faculty"], 30, 33),
    (["procrastination is the act"], 90, 95),
    (["Table 3.5", "Time on task"], 100, 103),
    (["SMART", "Specific"], 110, 114),
    (["transcribe every single word"], 179, 183),
    (["Working memory is a type of short-term memory"], 203, 206),
    (["Two major and interrelated techniques involve avoiding distractions"], 211, 214),
    (["Personal Zen", "anxiety"], 223, 226),
    (["intersections of growth and fixed mindset"], 59, 62),
    (["Bloom", "Taxonomy"], 43, 47),
    (["VARK"], 66, 68),
    (["syllabus"], 27, 35),
    (["FERPA"], 35, 40),
    (["Cornell"], 177, 185),
    (["SQ3R"], 165, 175),
    (["mnemonic"], 205, 215),
    (["Pomodoro"], 95, 100)
]:
    res = search_text(kw, sp, ep)
    if res:
        print(f"Keywords {kw} found on pages: {[r[0] for r in res]}")
    else:
        print(f"Keywords {kw} NOT found between {sp} and {ep}")

