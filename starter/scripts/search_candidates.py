import pypdf
import re
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
pdf_path = base_dir / "data" / "College_Success_web.pdf"
reader = pypdf.PdfReader(str(pdf_path))

def get_page_text(p_num: int) -> str:
    text = reader.pages[p_num - 1].extract_text() or ""
    return re.sub(r"\s+", " ", text).strip()

# Let's inspect pages from various chapters to get rich quotes:
# Chapter 1: pages 17-42
# Chapter 2: pages 43-82
# Chapter 3: pages 83-124
# Chapter 4: pages 125-160
# Chapter 5: pages 161-200
# Chapter 6: pages 201-230
# Chapter 7: pages 231-264
# Chapter 8: pages 265-292
# Chapter 10: pages 329-374

queries = [
    (11, "Preface", ["license", "OpenStax"]),
    (19, "Ch1", ["hidden curriculum", "syllabus", "degree", "first-generation"]),
    (27, "Ch1", ["grades", "attendance", "plagiarism", "academic integrity"]),
    (31, "Ch1", ["High School Faculty", "College Faculty", "degrees or certifications"]),
    (38, "Ch1", ["office hours", "FERPA", "Family Educational Rights and Privacy Act"]),
    (45, "Ch2", ["Bloom", "Taxonomy", "remember", "understand", "apply"]),
    (54, "Ch2", ["neuroplasticity", "brain", "growth mindset"]),
    (60, "Ch2", ["growth and fixed mindset", "intersections"]),
    (67, "Ch2", ["VARK", "visual", "auditory", "kinesthetic"]),
    (85, "Ch3", ["prioritization", "urgent", "important", "Eisenhower"]),
    (92, "Ch3", ["procrastination", "delaying some task"]),
    (101, "Ch3", ["Table 3.5", "Time on task", "Study for exam"]),
    (111, "Ch3", ["SMART", "Specific", "Measurable", "Attainable"]),
    (130, "Ch4", ["major", "prerequisite", "elective", "credit hours"]),
    (165, "Ch5", ["skimming", "active reading", "comprehension"]),
    (178, "Ch5", ["Cornell", "notetaking", "cue", "summary"]),
    (180, "Ch5", ["court-reporter", "transcribe every single word"]),
    (203, "Ch6", ["short-term memory", "long-term memory", "Working memory"]),
    (212, "Ch6", ["Avoiding Distractions", "study environment", "concentrate"]),
    (220, "Ch6", ["multiple choice", "test anxiety", "cramming", "essay"]),
    (234, "Ch7", ["critical thinking", "creative thinking", "analytical thinking"]),
    (335, "Ch10", ["FAFSA", "grant", "loan", "scholarship", "financial aid"])
]

for p, label, words in queries:
    txt = get_page_text(p)
    matches = [w for w in words if w.lower() in txt.lower()]
    print(f"Page {p} ({label}): matched {matches}")

