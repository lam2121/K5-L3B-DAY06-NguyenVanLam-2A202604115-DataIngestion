# Day 06 · Data Ingestion Engineering

**Lab cá nhân** · **4 giờ** · **Dữ liệu tự chọn**

Biến tài liệu thành kho tri thức có thể truy xuất cho AI agent, rồi đo xem cách chuẩn bị dữ liệu nào hiệu quả nhất.

| 📄 Dữ liệu | 🧩 Chiến lược | 🎯 Benchmark |
|---|---|---|
| Tối thiểu **30 trang nội dung** | Tối thiểu **3 cấu hình** | Tối thiểu **20 câu hỏi** |

## Bắt đầu nhanh

Dùng [starter PostgreSQL + pgvector](starter/README.md) để dựng database và hoàn thiện các hàm TODO, hoặc tự chọn vector store tương đương. Starter chỉ là khung: **bạn tự hiện thực pipeline và benchmark**.

## 1. Xây pipeline

![Đọc tài liệu, chuẩn hóa, chia chunk, tạo vector, lưu và kiểm tra](assets/ingestion-pipeline.svg)

Chọn tài liệu được phép sử dụng; giữ **ID tài liệu, nguồn, trang/vị trí** và metadata phù hợp. Dùng embedding model thật qua API hoặc chạy local; lưu và truy xuất bằng pgvector, Qdrant, Chroma hoặc một store tương đương.

## 2. So sánh và đánh giá

![Ba chiến lược được đánh giá trên cùng corpus và benchmark dev/test](assets/benchmark-workflow.svg)

Dùng cùng dữ liệu, model và câu hỏi cho cả ba cấu hình. Tách **15 câu dev / 5 câu test** trước khi chạy; chọn cấu hình trên dev, rồi đánh giá test sau khi cố định. Mỗi câu hỏi cần có đoạn bằng chứng và trang nguồn; thiết kế bộ câu hỏi và đánh giá theo [BENCHMARK.md](BENCHMARK.md).

Đánh giá theo năm khía cạnh: **độ chính xác truy xuất**, **tính mạch lạc của chunk**, **tính hữu dụng của metadata**, **chất lượng grounding** và **tác động của chiến lược dữ liệu**. Giải thích lựa chọn bằng kết quả, ví dụ lỗi và các đánh đổi.

## 3. Chuẩn bị bài nộp

1. Chạy pipeline và lưu cấu hình, kết quả top-3, trace cùng nhãn đánh giá thủ công.
2. Điền [thông tin học viên](STUDENT.md), [nhật ký thí nghiệm](artifacts/experiment_log.csv) và bản sao [mẫu báo cáo cá nhân](report/individual/MSSV_HoTen.md).
3. Kiểm tra mã nguồn, cách chạy, manifest dữ liệu và checklist trong [SUBMISSION.md](SUBMISSION.md).

## Tài liệu hướng dẫn

| Bạn cần tìm | Tài liệu |
|---|---|
| Setup baseline PostgreSQL + pgvector | [starter/README.md](starter/README.md) |
| Các bước làm và cách tính chỉ số | [GUIDE.md](GUIDE.md) |
| Tiến độ trong 4 giờ | [CHECKPOINTS.md](CHECKPOINTS.md) |
| Năm tiêu chí benchmark và bộ câu hỏi | [BENCHMARK.md](BENCHMARK.md) |
| Tiêu chí chấm điểm | [RUBRIC.md](RUBRIC.md) |
| Quy tắc sử dụng dữ liệu, AI và API | [RULES.md](RULES.md) |
| Cách nộp bài | [SUBMISSION.md](SUBMISSION.md) |


## Hướng dẫn tái lập thực nghiệm (Setup & Run Guide)

### 1. Yêu cầu môi trường
- Python 3.11 – 3.14
- Docker Desktop hoặc Docker Engine + Compose
- Hệ điều hành: Windows / Linux / macOS

### 2. Cài đặt và kích hoạt môi trường
```bash
cd starter
# Tạo và kích hoạt virtual environment
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# Cài đặt thư viện:
pip install -r requirements.txt
```

### 3. Khởi động PostgreSQL + pgvector
```bash
# Bật database local (cổng 55433)
docker compose -p day6_student_starter up -d --wait

# Kiểm tra kết nối:
python scripts/check_setup.py
```

### 4. Chạy toàn bộ Pipeline thực nghiệm
```bash
# Chạy nạp dữ liệu, sinh vector, đánh chỉ mục và chạy benchmark 25 câu hỏi:
python -m src.run
```
Lệnh trên sẽ tự động:
1. Đọc và chuẩn hóa dữ liệu từ `starter/data/College_Success_web.pdf`.
2. Tạo chunks cho Strategy A (`fixed_size`), Strategy B (`by_paragraph`), và Strategy C (`by_paragraph` + `metadata filter`).
3. Mã hóa vector 384 chiều bằng mô hình local `all-MiniLM-L6-v2`.
4. Lưu và đánh chỉ mục trên PostgreSQL + pgvector.
5. Chạy đánh giá Top-3 trên bộ 25 câu hỏi benchmark (`starter/data/benchmark.json`).
6. Xuất traces ra `starter/results/traces.json` và cập nhật `artifacts/experiment_log.csv`.

### 5. Cấu trúc bài nộp
- `STUDENT.md`: Thông tin học viên (Nguyễn Văn Lâm - 2A202604115 - L3B).
- `data/manifest.json`: Manifest toàn bộ 465 trang sách *College Success* (CC BY 4.0).
- `benchmark/benchmark.json`: Bộ 25 câu hỏi benchmark (19 dev / 6 test).
- `starter/src/`: Toàn bộ mã nguồn hoàn chỉnh của pipeline (`ingestion.py`, `chunking.py`, `embeddings.py`, `store.py`, `evaluation.py`, `run.py`).
- `results/`: Kết quả traces (`traces.json`), chỉ số (`metrics.json`), và nhãn audit thủ công (`audit_labels.json`).
- `benchmark_viewer.html`: Giao diện web HTML tra cứu toàn bộ 25 câu hỏi benchmark, so sánh đồng thời 3 chiến lược truy xuất và tô màu vàng dẫn chứng thực tế trong file PDF.
- `artifacts/experiment_log.csv`: Nhật ký thực nghiệm 3 chiến lược.
- `report/individual/2A202604115_NguyenVanLam.md`: Báo cáo cá nhân chi tiết theo chuẩn mẫu.
