import json
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent

audit_data = {
    "coherence_audit_10_locations": [
        {
            "location_id": "loc_01",
            "page": 11,
            "topic": "OpenStax License & Customization",
            "strategy_A": {
                "score": 1,
                "reason": "Bị cắt đôi từ mở đầu ('ustomization' thay vì 'Customization'), mất tiêu đề mục.",
                "snippet": "ustomization\nCollege Success is licensed under a Creative Commons Attribution 4.0 Internat..."
            },
            "strategy_B": {
                "score": 2,
                "reason": "Mở đầu trọn vẹn ranh giới đoạn văn 'Format\nYou can access this textbook...', đầy đủ ngữ cảnh.",
                "snippet": "Format\nYou can access this textbook for free in web view or PDF through openstax.org..."
            }
        },
        {
            "location_id": "loc_02",
            "page": 29,
            "topic": "Syllabus definition",
            "strategy_A": {
                "score": 1,
                "reason": "Mất chủ ngữ ở đầu câu ('often called the \"contract of the course\"').",
                "snippet": "often called the “contract of the course” because it contains information about what to expect..."
            },
            "strategy_B": {
                "score": 2,
                "reason": "Mở đầu rõ ràng với tiêu đề và định nghĩa hoàn chỉnh của Syllabus.",
                "snippet": "Syllabus The contract of a course that provides information about course expectations..."
            }
        },
        {
            "location_id": "loc_03",
            "page": 31,
            "topic": "High School vs College Faculty",
            "strategy_A": {
                "score": 1,
                "reason": "Cắt ngang giữa bảng so sánh, thiếu phần kết của bảng.",
                "snippet": "Differences between High School and College Faculty\nHigh School Faculty College Faculty\nOften have degrees..."
            },
            "strategy_B": {
                "score": 2,
                "reason": "Bao quát trọn vẹn toàn bộ bảng đối chiếu giữa hai nhóm giảng viên.",
                "snippet": "Differences between High School and College Faculty\nHigh School Faculty College Faculty..."
            }
        },
        {
            "location_id": "loc_04",
            "page": 47,
            "topic": "Bloom's Taxonomy",
            "strategy_A": {
                "score": 1,
                "reason": "Bắt đầu bằng liên từ nối 'and develop the lower thinking skills...', thiếu mệnh đề trước.",
                "snippet": "and develop the lower thinking skills that include remembering, applying, and analyzing..."
            },
            "strategy_B": {
                "score": 2,
                "reason": "Giữ nguyên vẹn đoạn văn thảo luận về các kỹ năng tư duy và ví dụ của Bloom's Taxonomy.",
                "snippet": "Creativity doesn't always present itself in the guise of a chart-topping musical hit or other..."
            }
        },
        {
            "location_id": "loc_05",
            "page": 60,
            "topic": "Growth vs Fixed Mindset Intersections",
            "strategy_A": {
                "score": 2,
                "reason": "Đủ ngữ cảnh giải thích sự giao thoa giữa hai loại tư duy.",
                "snippet": "Figure 2.11 The differences between fixed and growth mindset are clear when aligned to key..."
            },
            "strategy_B": {
                "score": 2,
                "reason": "Trọn vẹn đoạn văn phân tích các giao điểm tư duy theo ngữ cảnh cụ thể.",
                "snippet": "Figure 2.11 The differences between fixed and growth mindset are clear when aligned to key..."
            }
        },
        {
            "location_id": "loc_06",
            "page": 92,
            "topic": "Procrastination Definition",
            "strategy_A": {
                "score": 2,
                "reason": "Bao gồm định nghĩa cốt lõi của sự trì hoãn.",
                "snippet": "Figure 3.6 We can think of many creative ways to procrastinate, but the outcome is often..."
            },
            "strategy_B": {
                "score": 2,
                "reason": "Đoạn văn hoàn chỉnh với định nghĩa và ngữ cảnh mức độ ảnh hưởng của trì hoãn.",
                "snippet": "Figure 3.6 We can think of many creative ways to procrastinate, but the outcome is often..."
            }
        },
        {
            "location_id": "loc_07",
            "page": 101,
            "topic": "Time on task / Study for exam",
            "strategy_A": {
                "score": 1,
                "reason": "Bị cắt giữa phần giới thiệu và bảng thời gian biểu.",
                "snippet": "Below, you will find a table of common college academic activities. This list has been com..."
            },
            "strategy_B": {
                "score": 2,
                "reason": "Bảo tồn đầy đủ cấu trúc bảng thời gian cho bài thi (90 phút, 1-2 giờ).",
                "snippet": "Time on Task\nActivity Unit Time on task Notes\nStudy for exam Per exam 90 minutes 1–2 hours..."
            }
        },
        {
            "location_id": "loc_08",
            "page": 173,
            "topic": "SQ3R Reading Strategy",
            "strategy_A": {
                "score": 1,
                "reason": "Bắt đầu bằng một câu phụ 'assume that it will not take you long...', thiếu tiêu đề chính.",
                "snippet": "assume that it will not take you long to read because it is relatively short compared to..."
            },
            "strategy_B": {
                "score": 2,
                "reason": "Bắt đầu với tiêu đề chính 'The SQ3R Reading Strategy' và giải nghĩa 5 bước rõ ràng.",
                "snippet": "The SQ3R Reading Strategy\nYou may have heard of the SQ3R method for active reading..."
            }
        },
        {
            "location_id": "loc_09",
            "page": 180,
            "topic": "Lecture note transcription warning",
            "strategy_A": {
                "score": 0,
                "reason": "Từ đầu tiên bị cắt đôi ('ough' thay vì 'enough'), làm câu đầu vô nghĩa.",
                "snippet": "ough time for all 100 students to each discuss their thoughts. On the flip side..."
            },
            "strategy_B": {
                "score": 2,
                "reason": "Bảo tồn trọn vẹn câu cảnh báo không nên chép nguyên văn lời giảng viên.",
                "snippet": "On the flip side, most professors who teach lecture classes use technology to give them..."
            }
        },
        {
            "location_id": "loc_10",
            "page": 204,
            "topic": "Working memory definition",
            "strategy_A": {
                "score": 1,
                "reason": "Bị ngắt giữa ví dụ minh họa về sinh viên ngành y Marilyn.",
                "snippet": "Working Memory\nWorking memory is a type of short-term memory, but we use it when we are ac..."
            },
            "strategy_B": {
                "score": 2,
                "reason": "Bao quát trọn vẹn định nghĩa working memory và ví dụ minh họa thực tế.",
                "snippet": "Working Memory\nWorking memory is a type of short-term memory, but we use it when we are ac..."
            }
        }
    ],
    "coherence_summary": {
        "strategy_A_mean": 1.1,
        "strategy_B_mean": 1.9,
        "strategy_C_mean": 1.9
    },
    "grounding_audit_6_test_queries": [
        {
            "question_id": "q16",
            "gold_page": 204,
            "strategy_A": {"score": 2, "reason": "Rank 1 chứa đầy đủ định nghĩa working memory."},
            "strategy_B": {"score": 2, "reason": "Rank 1 chứa trọn vẹn đoạn văn định nghĩa."},
            "strategy_C": {"score": 2, "reason": "Rank 1 chứa trọn vẹn đoạn văn định nghĩa."}
        },
        {
            "question_id": "q17",
            "gold_page": 212,
            "strategy_A": {"score": 2, "reason": "Rank 1 chứa đầy đủ 2 kỹ thuật tránh sao nhãng và tạo môi trường học."},
            "strategy_B": {"score": 2, "reason": "Rank 2 chứa đầy đủ 2 kỹ thuật cốt lõi."},
            "strategy_C": {"score": 2, "reason": "Rank 2 chứa đầy đủ 2 kỹ thuật cốt lõi."}
        },
        {
            "question_id": "q18",
            "gold_page": 268,
            "strategy_A": {"score": 0, "reason": "Top-3 không chứa trang 268 (bị lệch sang trang 280)."},
            "strategy_B": {"score": 0, "reason": "Top-3 không chứa trang 268 (bị lệch sang trang 280, 271)."},
            "strategy_C": {"score": 0, "reason": "Top-3 không chứa trang 268 (bị lệch sang trang 280, 271)."}
        },
        {
            "question_id": "q19",
            "gold_page": 11,
            "strategy_A": {"score": 1, "reason": "Có ngữ cảnh giấy phép nhưng điều kiện ghi công bị cắt sang chunk khác."},
            "strategy_B": {"score": 2, "reason": "Rank 1 có đầy đủ điều kiện ghi công (attribution)."},
            "strategy_C": {"score": 2, "reason": "Rank 1 có đầy đủ điều kiện ghi công (attribution)."}
        },
        {
            "question_id": "q20",
            "gold_page": 212,
            "strategy_A": {"score": 2, "reason": "Rank 2 chứa đầy đủ bằng chứng trang 212."},
            "strategy_B": {"score": 0, "reason": "Trang 212 xếp ở rank 4 ngoài top-3."},
            "strategy_C": {"score": 1, "reason": "Top-3 thuộc chapter 6, bàn về kỹ thuật học nhưng thiếu đoạn chính trang 212."}
        },
        {
            "question_id": "q25",
            "gold_page": 112,
            "strategy_A": {"score": 1, "reason": "Lọt trang 113 nêu ví dụ SMART nhưng thiếu lý do desirable ở trang 112."},
            "strategy_B": {"score": 1, "reason": "Lọt trang 113 và trang 129 ngoài chapter 3, thiếu trang 112."},
            "strategy_C": {"score": 2, "reason": "Nhờ filter chapter 3, trang 112 lọt vào Rank 3 với đầy đủ bằng chứng!"}
        }
    ],
    "grounding_summary": {
        "strategy_A_mean": 1.33,
        "strategy_B_mean": 1.17,
        "strategy_C_mean": 1.50
    },
    "metadata_usefulness": {
        "test_records_checked": 18,
        "test_records_valid_and_complete": 18,
        "valid_percentage": 100.0,
        "filter_compliance": {
            "strategy_A": "N/A (no filter)",
            "strategy_B": "N/A (no filter)",
            "strategy_C": "2/2 (100.0%) - q20 và q25 đều tuân thủ 100% chapter filter"
        }
    }
}

paths = [
    base_dir / "results" / "audit_labels.json",
    base_dir.parent / "results" / "audit_labels.json"
]
for p in paths:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, ensure_ascii=False, indent=2)
    print("Saved audit labels to", p)
