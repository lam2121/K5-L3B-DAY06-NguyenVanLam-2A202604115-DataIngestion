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

questions = [
    # Dev (q01 - q15)
    {
        "id": "q01",
        "type": "truc_tiep",
        "split": "dev",
        "question": "What license is the textbook College Success published under, and what does it permit?",
        "expected_answer": "It is published under a Creative Commons Attribution 4.0 International (CC BY) license, permitting users to distribute, remix, and build upon the content with proper attribution to OpenStax.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 11,
        "evidence_quote": "College Success is licensed under a Creative Commons Attribution 4.0 International (CC BY) license, which means that you can distribute, remix, and build upon the content, as long as you provide attribution to OpenStax and its content contributors.",
        "filter": None
    },
    {
        "id": "q02",
        "type": "truc_tiep",
        "split": "dev",
        "question": "What is a syllabus commonly referred to as in college courses?",
        "expected_answer": "A syllabus is often called the 'contract of the course' because it sets expectations for both professor and student.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 29,
        "evidence_quote": "A syllabus is often called the “contract of the course” because it contains information about what to expect—from the professor and the student.",
        "filter": None
    },
    {
        "id": "q03",
        "type": "dien_dat_lai",
        "split": "dev",
        "question": "How do instructional qualifications and teaching preparation differ between secondary school educators and university professors?",
        "expected_answer": "High school faculty typically hold teaching certificates or education degrees, whereas college faculty usually have advanced subject degrees but often have not taken pedagogical training courses.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 31,
        "evidence_quote": "High School Faculty College Faculty Often have degrees or certifications in teaching in addition to degrees in subject matter Most likely have not even taken a course in teaching as part of their graduate program",
        "filter": None
    },
    {
        "id": "q04",
        "type": "dieu_kien_ngoai_le",
        "split": "dev",
        "question": "Under what condition can an individual exhibit both fixed and growth mindsets simultaneously?",
        "expected_answer": "People often experience intersections of both mindsets across different domains—feeling high growth potential in areas like art or communication, but feeling fixed or limited in planning or financials.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 60,
        "evidence_quote": "People may feel great ability to grow and learn in some areas, like art and communication, but feel more limited in others, such as planning and financials. Recognizing these intersections will help you approach new topics and tasks.",
        "filter": None
    },
    {
        "id": "q05",
        "type": "loc_metadata",
        "split": "dev",
        "question": "In Chapter 1, what document serves as a roadmap and contract of expectations between instructor and student?",
        "expected_answer": "The syllabus serves as the roadmap and contract of the course.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 29,
        "evidence_quote": "A syllabus is often called the “contract of the course” because it contains information about what to expect—from the professor and the student. It is meant to be a roadmap for succeeding in the class.",
        "filter": {"chapter": 1}
    },
    {
        "id": "q06",
        "type": "truc_tiep",
        "split": "dev",
        "question": "How does the textbook define procrastination?",
        "expected_answer": "Procrastination is defined simply as the act of delaying some task that needs to be completed.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 92,
        "evidence_quote": "Simply put, procrastination is the act of delaying some task that needs to be completed. It is something we all do to greater and lesser degrees.",
        "filter": None
    },
    {
        "id": "q07",
        "type": "truc_tiep",
        "split": "dev",
        "question": "What five steps does the SQ3R reading strategy title stand for?",
        "expected_answer": "The SQ3R reading strategy stands for Survey, Question, Read, Recite, Review.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 173,
        "evidence_quote": "The title stands for Survey, Question, Read, Recite, Review, and you can use the steps on virtually any assigned passage.",
        "filter": None
    },
    {
        "id": "q08",
        "type": "truc_tiep",
        "split": "dev",
        "question": "Who created the Cornell Method of notetaking and during which decade was it developed?",
        "expected_answer": "The Cornell Method was devised by Cornell University education professor Dr. Walter Pauk in the 1940s.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 183,
        "evidence_quote": "One of the most recognizable notetaking systems is called the Cornell Method, a relatively simple way to take effective notes devised by Cornell University education professor Dr. Walter Pauk in the 1940s.",
        "filter": None
    },
    {
        "id": "q09",
        "type": "dien_dat_lai",
        "split": "dev",
        "question": "Why is attempting to record every word spoken by an instructor during lectures discouraged?",
        "expected_answer": "Students lack court-reporter speed and trying to write everything causes them to miss key concepts and main ideas.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 180,
        "evidence_quote": "It is not a good habit to transcribe every single word a speaker utters—even if you have an amazing ability to do that. Most of us don’t have that court-reporter-esque skill level anyway, and if we try, we would end up missing valuable information.",
        "filter": None
    },
    {
        "id": "q10",
        "type": "loc_metadata",
        "split": "dev",
        "question": "According to Chapter 3 on time management, what is the definition and common nature of procrastination?",
        "expected_answer": "Procrastination is delaying tasks that must be finished, a habit practiced to varying extents by everyone.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 92,
        "evidence_quote": "Simply put, procrastination is the act of delaying some task that needs to be completed. It is something we all do to greater and lesser degrees.",
        "filter": {"chapter": 3}
    },
    {
        "id": "q11",
        "type": "dien_dat_lai",
        "split": "dev",
        "question": "How much dedicated time on average is estimated for studying for an exam according to college activity guidelines?",
        "expected_answer": "The average estimated time on task is 90 minutes (or 1 to 2 hours depending on material complexity).",
        "gold_source_id": "openstax-college-success",
        "gold_page": 101,
        "evidence_quote": "Study for exam Per exam 90 minutes 1–2 hours, depending upon complexity of material Table 3.5 Time on task for common college activities.",
        "filter": None
    },
    {
        "id": "q12",
        "type": "dieu_kien_ngoai_le",
        "split": "dev",
        "question": "When does minor procrastination become a serious concern for students?",
        "expected_answer": "While minor procrastination is normal, it becomes a problem when it leads to chronic delay, severe anxiety, and missed obligations.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 92,
        "evidence_quote": "For most people, a little minor procrastination is not a cause for great concern. But there are situations where procrastination can become a serious problem with a lot of risk.",
        "filter": None
    },
    {
        "id": "q13",
        "type": "dieu_kien_ngoai_le",
        "split": "dev",
        "question": "In what pedagogical context is Bloom's Taxonomy utilized by educators?",
        "expected_answer": "Bloom's Taxonomy is used as a guide by teachers when defining what learning goals and skills students should acquire in a course.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 47,
        "evidence_quote": "Bloom’s Taxonomy, and it is often used as a guide for educators when they are determining what students should learn within a course.",
        "filter": None
    },
    {
        "id": "q14",
        "type": "loc_metadata",
        "split": "dev",
        "question": "In Chapter 5 on reading strategies, what does the acronym SQ3R represent?",
        "expected_answer": "SQ3R stands for Survey, Question, Read, Recite, Review.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 173,
        "evidence_quote": "The title stands for Survey, Question, Read, Recite, Review, and you can use the steps on virtually any assigned passage.",
        "filter": {"chapter": 5}
    },
    {
        "id": "q15",
        "type": "loc_metadata",
        "split": "dev",
        "question": "In Chapter 5, what listening advice is given to avoid transcription traps in lectures?",
        "expected_answer": "Students should learn to focus on main ideas and distinctions rather than writing down every utterance.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 180,
        "evidence_quote": "Learn to listen for main ideas and distinguish between these main ideas and details that typically support the ideas.",
        "filter": {"chapter": 5}
    },

    # Test (q16 - q20)
    {
        "id": "q16",
        "type": "truc_tiep",
        "split": "test",
        "question": "What is working memory and when is it utilized according to Chapter 6?",
        "expected_answer": "Working memory is a type of short-term memory that is actively used when performing an active cognitive task.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 204,
        "evidence_quote": "Working memory is a type of short-term memory, but we use it when we are actively performing a task.",
        "filter": None
    },
    {
        "id": "q17",
        "type": "dien_dat_lai",
        "split": "test",
        "question": "What two core methods are described for improving concentration and effectiveness while studying?",
        "expected_answer": "The two connected techniques are eliminating distractions and establishing a conducive study setting.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 212,
        "evidence_quote": "Two major and interrelated techniques involve avoiding distractions to the best of your ability and creating a study environment that works to help you concentrate.",
        "filter": None
    },
    {
        "id": "q18",
        "type": "dien_dat_lai",
        "split": "test",
        "question": "How has technological advancement impacted interpersonal interaction rules and protocols?",
        "expected_answer": "Technology has reshaped communication rules through emoji conventions, abbreviation patterns, and digital etiquette.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 268,
        "evidence_quote": "Technology has created new rules for communication because of the different structures of communication, everything from emoji protocols, to truncated words and spelling, to etiquette and how we form communication networks.",
        "filter": None
    },
    {
        "id": "q19",
        "type": "dieu_kien_ngoai_le",
        "split": "test",
        "question": "Under what condition does OpenStax permit remixing and distributing the textbook material?",
        "expected_answer": "Anyone may distribute or remix the content provided that proper attribution is given to OpenStax and contributors.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 11,
        "evidence_quote": "which means that you can distribute, remix, and build upon the content, as long as you provide attribution to OpenStax and its content contributors.",
        "filter": None
    },
    {
        "id": "q20",
        "type": "loc_metadata",
        "split": "test",
        "question": "In Chapter 6 on studying and memory, what two interrelated techniques help students become more effective learners?",
        "expected_answer": "Avoiding distractions and creating an optimal study environment.",
        "gold_source_id": "openstax-college-success",
        "gold_page": 212,
        "evidence_quote": "Two major and interrelated techniques involve avoiding distractions to the best of your ability and creating a study environment that works to help you concentrate.",
        "filter": {"chapter": 6}
    }
]

print(f"Total questions: {len(questions)}")
dev_q = [q for q in questions if q["split"] == "dev"]
test_q = [q for q in questions if q["split"] == "test"]
filter_q = [q for q in questions if q["filter"] is not None]
filter_test_q = [q for q in test_q if q["filter"] is not None]

print(f"Dev count: {len(dev_q)}, Test count: {len(test_q)}")
print(f"Filter count: {len(filter_q)}, Filter in Test: {len(filter_test_q)}")

# Verify all quotes strictly exist in page text
all_verified = True
for q in questions:
    p_text = get_page_text(q["gold_page"])
    if q["evidence_quote"] not in p_text:
        print(f"FAIL: {q['id']} on page {q['gold_page']}")
        print(f"Expected quote: '{q['evidence_quote']}'")
        all_verified = False
    else:
        print(f"PASS: {q['id']} (page {q['gold_page']}, split: {q['split']}, type: {q['type']}, filter: {q['filter']})")

if all_verified:
    print("\nALL 20 QUOTES PERFECTLY VERIFIED!")
    
    # Write to target locations
    out_paths = [
        base_dir / "data" / "benchmark.json",
        base_dir.parent / "data" / "benchmark.json",
        base_dir.parent / "benchmark" / "benchmark.json"
    ]
    for p in out_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print(f"Saved benchmark to {p}")
