import pypdf
import re
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
pdf_path = base_dir / "data" / "College_Success_web.pdf"
reader = pypdf.PdfReader(str(pdf_path))

def get_page_text(p_num: int) -> str:
    text = reader.pages[p_num - 1].extract_text() or ""
    return re.sub(r"\s+", " ", text).strip()

new_candidates = [
    (233, "metacognition, the practice of thinking about your thinking."),
    (131, "short-term goals can absolutely look like a checklist of tasks because their purpose is to keep you moving forward toward your larger goals."),
    (216, "You can certainly make up your own mnemonics, but be careful that your reminder isn’t so complex and convoluted that it is more"),
    (183, "three sections by drawing a horizontal line across your paper about one to two inches from the bottom of the page (the summary area) and then drawing a vertical line to separate the rest of the page above this bottom area, making the left side about two inches wide (the recall column) and leaving the biggest area to the right of the vertical line (the notes column)."),
    (112, "Measurable, Attainable, Relevant, and Time-bound. The reason these are all desirable traits for your goals is because they not only help you plan how to meet the goal, but they can also contribute to your decision-making processes during the planning stage.")
]

for p, quote in new_candidates:
    p_text = get_page_text(p)
    if quote in p_text:
        print(f"Page {p}: PASS exact match!")
    else:
        print(f"Page {p}: FAIL!")
        # Find where it diverges
        words = quote.split()[:5]
        first_few = " ".join(words)
        pos = p_text.find(first_few)
        if pos != -1:
            print("  Actual text snippet:", repr(p_text[pos:pos+len(quote)+30]))

