import json
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
bench_path = base_dir / "data" / "benchmark.json"

with open(bench_path, "r", encoding="utf-8") as f:
    questions = json.load(f)

# The 5 new questions
new_5 = [
    {
        "id": "q21",
        "type": "truc_tiep",
        "split": "dev",
        "question": "How is metacognition simply defined in the context of cognitive skills?",
        "expected_answer": "Metacognition is defined as the practice of thinking about your thinking.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 233,
        "evidence_quote": "metacognition, the practice of thinking about your thinking.",
        "filter": None
    },
    {
        "id": "q22",
        "type": "dien_dat_lai",
        "split": "dev",
        "question": "Why is it appropriate for an undergraduate's near-term academic targets to resemble an itemized checklist?",
        "expected_answer": "Short-term goals function to break down broader long-term goals into smaller, manageable chunks that are easier to focus on.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 131,
        "evidence_quote": "short-term goals can absolutely look like a checklist of tasks because their purpose is to break the long-term goal down into manageable chunks that are easier to focus on",
        "filter": None
    },
    {
        "id": "q23",
        "type": "dieu_kien_ngoai_le",
        "split": "dev",
        "question": "What potential pitfall must learners avoid when creating personalized mnemonic devices?",
        "expected_answer": "They must be cautious not to make the reminder so complex and convoluted that it is harder to recall than the original information.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 216,
        "evidence_quote": "You can certainly make up your own mnemonics, but be careful that your reminder isn’t so complex and convoluted that it is more difficult to remember than the information you were relating it to!",
        "filter": None
    },
    {
        "id": "q24",
        "type": "loc_metadata",
        "split": "dev",
        "question": "In Chapter 5 on notetaking, what three distinct layout sections are created on a page when utilizing the Cornell Method?",
        "expected_answer": "The summary area at the bottom, the recall column on the left, and the notes column on the right.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 183,
        "evidence_quote": "three sections by drawing a horizontal line across your paper about one to two inches from the bottom of the page (the summary area) and then drawing a vertical line to separate the rest of the page above this bottom area, making the left side about two inches (the recall column) and leaving the biggest area to the right of your vertical line (the notes column).",
        "filter": {"chapter": 5}
    },
    {
        "id": "q25",
        "type": "loc_metadata",
        "split": "test",
        "question": "In Chapter 3 on time management, what do the five SMART goal attributes represent, and why are they considered desirable?",
        "expected_answer": "SMART represents Specific, Measurable, Attainable, Relevant, and Time-bound; they are desirable because they guide execution planning and aid decision-making.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 112,
        "evidence_quote": "Measurable, Attainable, Relevant, and Time-bound. The reason these are all desirable traits for your goals is because they not only help you plan how to meet the goal, but they can also contribute to your decision-making processes during the planning stage.",
        "filter": {"chapter": 3}
    }
]

# Avoid duplicate IDs
existing_ids = {q["id"] for q in questions}
for nq in new_5:
    if nq["id"] not in existing_ids:
        questions.append(nq)

print(f"Total questions now: {len(questions)}")
dev_cnt = sum(1 for q in questions if q["split"] == "dev")
test_cnt = sum(1 for q in questions if q["split"] == "test")
filter_cnt = sum(1 for q in questions if q["filter"] is not None)
filter_test_cnt = sum(1 for q in questions if q["split"] == "test" and q["filter"] is not None)

print(f"Dev: {dev_cnt}, Test: {test_cnt}, Filter total: {filter_cnt}, Filter in Test: {filter_test_cnt}")

targets = [
    base_dir / "data" / "benchmark.json",
    base_dir.parent / "data" / "benchmark.json",
    base_dir.parent / "benchmark" / "benchmark.json"
]

for t in targets:
    t.parent.mkdir(parents=True, exist_ok=True)
    with open(t, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"Updated {t}")

