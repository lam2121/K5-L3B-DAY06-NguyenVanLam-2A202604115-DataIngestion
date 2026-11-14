# Báo cáo cá nhân — Day 6: Data Ingestion Engineering

- **Họ và tên**: Nguyễn Văn Lâm
- **MSSV**: 2A202604115
- **Lớp**: L3B
- **Chủ đề**: Kỹ thuật nạp và truy xuất dữ liệu giáo trình đại học (*College Success*, OpenStax)

---

## Dữ liệu và pipeline

- **Chủ đề, nguồn/quyền, số trang và quy tắc tính trang**:
  - **Tài liệu sử dụng**: Giáo trình *College Success* do tổ chức OpenStax (Rice University) xuất bản.
  - **Giấy phép bản quyền**: Creative Commons Attribution 4.0 International (CC BY 4.0), cho phép phân phối và tái sử dụng có ghi công.
  - **Số trang vật lý**: `465 trang`.
  - **Số trang nội dung hữu ích trong manifest**: `443 trang` (đạt yêu cầu $\ge 30$ trang).
  - **Số trang được nạp trong pipeline thực nghiệm**: `282 trang` (từ Preface đến hết Chapter 8, trang 11 đến trang 292), bao quát toàn bộ 25 câu hỏi benchmark.
  - **Quy tắc tính trang**: Trang nội dung được tính từ Preface (trang 11) đến hết Chapter 12 (trang 456) có độ dài ký tự sau chuẩn hóa $\ge 100$; loại bỏ trang bìa, thông tin xuất bản, mục lục (trang 1–10) và phụ lục đáp án/index (trang 457–465).
- **Chuẩn hóa, lỗi và giới hạn**:
  - **Chuẩn hóa Unicode & khoảng trắng**: Áp dụng chuẩn hóa Unicode NFC (`unicodedata.normalize('NFC')`), chuyển đổi ngắt dòng Windows `\r\n` thành `\n`, chuẩn hóa khoảng trắng ngang và gộp các dòng trống liên tiếp thành `\n\n` để bảo tồn cấu trúc đoạn văn cho chiến lược `by_paragraph`.
  - **Phát hiện trang rỗng**: Tự động phát hiện 8 trang không có nội dung văn bản hữu ích (<50 ký tự, chủ yếu là các trang chuyển mục rỗng).
  - **Giới hạn**: Các bảng biểu nhiều cột trong PDF gốc khi chuyển sang text thuần bị mất định dạng gióng hàng cột, gây khó khăn cho việc truy xuất bảng số liệu phức tạp.
- **Embedding model, vector store, metric, lệnh chạy và chi phí**:
  - **Embedding Model**: `all-MiniLM-L6-v2` (`sentence-transformers` phiên bản `6.3.0`, PyTorch `2.15.0+cpu`).
  - **Số chiều (Dimensions)**: `384` chiều vector.
  - **Vector Store**: PostgreSQL 16 + pgvector `0.8.7` (chạy local qua Docker Compose tại cổng `127.0.0.1:55433`).
  - **Metric tìm kiếm**: Cosine Distance (`<=>` trong pgvector) với embedding vector được chuẩn hóa $L_2$ (`normalize_embeddings=True`).
  - **Thư viện phụ thuộc (Ghi nhận đầy đủ trong requirements.txt)**:
    - `psycopg[binary]==3.3.8`: Driver kết nối PostgreSQL và pgvector.
    - `pypdf>=5,<7`: Đọc và trích xuất dữ liệu trang PDF giáo trình gốc.
    - `python-dotenv>=1,<2`: Đọc biến môi trường `.env`.
    - `sentence-transformers==6.3.0`: Mã hóa vector ngữ nghĩa cục bộ `all-MiniLM-L6-v2` ($0 chi phí).
    - `rank-bm25==0.2.2`: Tìm kiếm từ khóa Sparse BM25 phục vụ phần mở rộng Hybrid Retrieval.
    - `pymupdf>=2.1`: Render trang sách PDF chuẩn xác và tính tọa độ bounding box tô màu vàng cho `benchmark_viewer.html`.
  - **Lệnh chạy tái lập**:
    ```bash
    cd starter
    docker compose -p day6_student_starter up -d --wait
    .venv\Scripts\python.exe -m src.run
    ```
  - **Chi phí**: `0 USD` (chạy hoàn toàn offline cục bộ trên CPU, không tiêu tốn API token trả phí).
- **Metadata bắt buộc, trường lọc bổ sung, nguồn giá trị và lý do chọn**:
  - **Metadata bắt buộc**: `document_id` (`openstax-college-success`), `source` (`starter/data/College_Success_web.pdf`), `page` (số trang vật lý thực tế).
  - **Trường lọc bổ sung**: `chapter` (số thứ tự chương từ 0 đến 14) và `chapter_title` (tiêu đề chương tương ứng).
  - **Nguồn giá trị**: Trích xuất tự động từ ranh giới các chương dựa trên cấu trúc bookmark/outline của file PDF chuẩn hóa.
  - **Lý do chọn**: Giáo trình có dung lượng lớn và chia theo nhiều chủ đề độc lập (ví dụ quản lý thời gian, đọc và ghi chú, trí nhớ và thi cử). Trường `chapter` cho phép người dùng hoặc AI Agent khoanh vùng chính xác phạm vi ngữ cảnh khi đặt câu hỏi chuyên đề, loại trừ nhiễu từ các chương khác.

---

## Cấu hình và benchmark

- **Mô tả 3 Chiến lược (A / B / C)**:
  - **Chiến lược A (Fixed-size)**: Cắt chunk kích thước cố định `500 ký tự`, độ gối đầu (`overlap`) `50 ký tự`. Gắn metadata (`source`, `page`, `chapter`). Truy xuất Top-3 Cosine similarity, **không lọc**.
  - **Chiến lược B (By-paragraph)**: Cắt chunk theo cấu trúc đoạn văn ngữ nghĩa (`by_paragraph`, giới hạn `max_size=800 ký tự`), tôn trọng ranh giới đoạn văn và câu. Cùng metadata, truy xuất Top-3, **không lọc**.
  - **Chiến lược C (Metadata Filtering)**: Sử dụng chính xác tập chunk và vector của Chiến lược B (cùng `by_paragraph`), nhưng áp dụng **bộ lọc SQL metadata (`chapter`)** khi câu hỏi có điều kiện ngữ cảnh filter. Khác biệt duy nhất giữa B và C là việc áp dụng filter metadata.
- **Bộ benchmark 25 câu đa dạng**:
  - **Tổng số câu**: 25 câu hỏi có bằng chứng kiểm chứng.
  - **Phân chia cố định**: 19 câu Dev (`q01`–`q15`, `q21`–`q24`) và 6 câu Test (`q16`–`q20`, `q25`).
  - **Đa dạng phân loại**:
    - `truc_tiep` (Direct factual): 7 câu (`q01`, `q02`, `q06`, `q07`, `q08`, `q16`, `q21`).
    - `dien_dat_lai` (Rephrased): 6 câu (`q03`, `q09`, `q11`, `q17`, `q18`, `q22`).
    - `dieu_kien_ngoai_le` (Conditional / Exception): 5 câu (`q04`, `q12`, `q13`, `q19`, `q23`).
    - `loc_metadata` (Metadata Filter): 7 câu (`q05`, `q10`, `q14`, `q15`, `q24` trong Dev; `q20`, `q25` trong Test).
  - **Kiểm chứng evidence**: 100% `evidence_quote` được kiểm tra tự động bằng code xác nhận tồn tại chính xác nguyên vẹn từng ký tự trong văn bản đã chuẩn hóa của trang `gold_page`.
- **Tiêu chí chọn chiến lược đã chốt trước khi xem test**:
  1. *Tiêu chí 1*: Evidence Hit@3 trên tập Dev phải đạt mức cao nhất.
  2. *Tiêu chí 2*: Tính mạch lạc của chunk (Chunk Coherence) phải giữ trọn vẹn ngữ nghĩa để giảm thiểu hiện tượng ảo giác (hallucination) khi chuyển cho LLM sinh câu trả lời.
  3. *Tiêu chí 3*: Tiết kiệm tài nguyên lưu trữ (số lượng chunk ít hơn mà vẫn duy trì hoặc tăng độ chính xác).

---

## Kết quả

### Bảng 1: Hiệu năng Truy xuất và Tài nguyên (25 câu benchmark)
| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Thời gian Ingest | Chi phí |
|---|---|---|---|---|---|---|
| **A (Fixed 500)** | dev | 6/19 (31.58%) | 12/19 (63.16%) | 1638 | 87.41s | $0 |
| **A (Fixed 500)** | test | 2/6 (33.33%) | 3/6 (50.00%) | 1638 | ~0.8s | $0 |
| **B (Paragraph 800)** | dev | 7/19 (36.84%) | 13/19 (68.42%) | 1067 | 70.53s | $0 |
| **B (Paragraph 800)** | test | 2/6 (33.33%) | 3/6 (50.00%) | 1067 | ~0.6s | $0 |
| **C (Paragraph + Filter)** | dev | 7/19 (36.84%) | 13/19 (68.42%) | 1067 | 70.53s | $0 |
| **C (Paragraph + Filter)** | test | 2/6 (33.33%) | **4/6 (66.67%)** | 1067 | ~0.6s | $0 |

### Bảng 2: Chấm điểm Thủ công 5 Khía cạnh (Audit)
| Strategy | Coherence trung bình /2 (n=10) | Metadata đủ và đúng (n/N) | Filter tuân thủ (n/N) | Grounding 0/1/2 (số câu) và trung bình /2 |
|---|---|---|---|---|
| **A** | **1.1 / 2.0** (10 mẫu) | 18/18 (100%) | N/A (không có filter) | 0: 1 câu \| 1: 2 câu \| 2: 3 câu -> **1.33 / 2.0** |
| **B** | **1.9 / 2.0** (10 mẫu) | 18/18 (100%) | N/A (không có filter) | 0: 2 câu \| 1: 1 câu \| 2: 3 câu -> **1.17 / 2.0** |
| **C** | **1.9 / 2.0** (10 mẫu) | 18/18 (100%) | **2/2 (100%)** | 0: 1 câu \| 1: 1 câu \| 2: 4 câu -> **1.50 / 2.0** |

- **Đường dẫn artifacts và trace**:
  - Dấu vết truy xuất chi tiết từng câu: [starter/results/traces.json](file:///E:/Projects/Lab6Vinuni/K5-L3B-DAY06-NguyenVanLam-2A202604115-DataIngestion/starter/results/traces.json)
  - Số liệu tóm tắt: [starter/results/metrics.json](file:///E:/Projects/Lab6Vinuni/K5-L3B-DAY06-NguyenVanLam-2A202604115-DataIngestion/starter/results/metrics.json)
  - Nhật ký thực nghiệm: [artifacts/experiment_log.csv](file:///E:/Projects/Lab6Vinuni/K5-L3B-DAY06-NguyenVanLam-2A202604115-DataIngestion/artifacts/experiment_log.csv)
  - Cách chọn mẫu chấm Coherence: Lấy chunk chứa 10 vị trí nội dung cố định tại các trang `[11, 29, 31, 47, 60, 92, 101, 173, 180, 204]`.

---

## Phân tích và kết luận

### 1. So sánh Chiến lược A và B (Tác động của kỹ thuật Chunking)
- **Độ chính xác truy xuất**: Trên tập Dev, Strategy B (by-paragraph) đạt **Evidence Hit@3 là 13/19 (68.42%)**, vượt trội hơn Strategy A (12/19 - 63.16%). Hit@1 của B cũng cao hơn (7/19 so với 6/19).
- **Tính mạch lạc của Chunk (Coherence)**: Strategy B vượt trội rõ rệt với điểm trung bình **1.9 / 2.0** so với **1.1 / 2.0** của Strategy A.
  - *Nguyên nhân thất bại của Strategy A*: Chia chunk cố định 500 ký tự thường xuyên cắt ngang giữa câu hoặc thậm chí xẻ đôi từ (ví dụ tại trang 11 từ *Customization* bị cắt thành `'ustomization'`, trang 180 từ *enough* bị cắt thành `'ough'`). Đầu chunk thường xuyên thiếu chủ ngữ hoặc mệnh đề điều kiện đứng trước.
  - *Ưu thế của Strategy B*: Nhóm theo đoạn văn giúp giữ trọn vẹn chủ ngữ, vị ngữ và ngữ cảnh giải thích liền mạch.
- **Tài nguyên**: Strategy B chỉ tạo ra **1.067 chunks**, giảm **35% dung lượng lưu trữ và số vector** so với Strategy A (1.638 chunks).

### 2. So sánh Chiến lược B và C (Tác động của Metadata Filtering)
- Chiến lược C tái sử dụng chính xác các chunk của B nhưng áp dụng lọc trường `chapter` trong câu truy vấn SQL khi câu hỏi có filter.
- **Minh chứng rõ rệt trên tập Test (Câu `q25`)**:
  - Ở câu hỏi `q25` về các đặc tính của mục tiêu SMART trong Chapter 3, Strategy A và Strategy B không có filter đã bị lọt chunk ở trang 129 (thuộc Chapter 4) vào Top-3 vì trang 129 cũng nhắc đến các mục tiêu học tập. Hậu quả là trang chứa bằng chứng gold (trang 112) bị đẩy ra khỏi Top-3 (Hit@3 = False).
  - Trong khi đó, **Strategy C với bộ lọc `chapter: 3` đã loại bỏ hoàn toàn trang 129**, giúp trang gold 112 lọt vào Top-3 với thứ hạng Rank 3 (**Hit@3 = True**).
  - Nhờ đó, Strategy C đạt **Evidence Hit@3 trên tập Test là 4/6 (66.67%)**, cao hơn hẳn mức 3/6 (50.0%) của Strategy B.

### 3. Phân tích 2 trường hợp truy xuất thất bại (Failure Cases)
- **Ví dụ 1 — Câu `q18` (Test set)**:
  - *Câu hỏi*: *"How has technological advancement impacted interpersonal interaction rules and protocols?"*
  - *Trang nguồn gold*: Trang 268 (bàn về các biến số giao tiếp kỹ thuật số: emoji protocols, viết tắt, mạng lưới).
  - *Kết quả thực tế*: Cả 3 chiến lược đều trả về trang 280 (thảo luận về mạng xã hội và điện thoại di động) và trang 271 thay vì trang 268.
  - *Nguyên nhân*: Trang 280 lặp lại từ khóa *"technology"*, *"communication"*, *"socialization"* với tần suất rất dày đặc, khiến embedding dense của `all-MiniLM-L6-v2` cho ra độ tương đồng cosine cao hơn (Score 0.58) so với trang 268 (Score < 0.53).
- **Ví dụ 2 — Câu `q20` (Test set)**:
  - *Câu hỏi*: *"In Chapter 6 on studying and memory, what two interrelated techniques help students become more effective learners?"*
  - *Trang nguồn gold*: Trang 212 (*"Two major and interrelated techniques involve avoiding distractions... and creating a study environment..."*).
  - *Kết quả thực tế*: Top-3 trả về các trang 215, 217, 229 thuộc Chapter 6. Trang 217 xuất hiện tiêu đề lớn *"Three Effective Study Strategies"*, khiến mô hình dense nhầm tưởng trang này trả lời câu hỏi về kỹ thuật học tập hiệu quả hơn là trang 212.

### 4. Chiến lược lựa chọn, đánh đổi và điều kiện áp dụng
- **Chiến lược được chọn**: **Chiến lược C** (By-paragraph kết hợp Metadata Filtering).
- **Đánh đổi (Trade-offs)**:
  - *Được*: Đạt Hit@3 cao nhất trên tập Test (66.67%), chunk mạch lạc cao (1.9/2), điểm Grounding cao nhất (1.50/2), giảm 35% chi phí lưu trữ vector, kiểm soát chính xác phạm vi tìm kiếm theo phân mục.
  - *Mất*: Độ dài các chunk không đồng đều (từ 200 đến 800 ký tự); cần thêm bước tiền xử lý cấu trúc tài liệu và xác định filter từ người dùng trước khi gọi database.

### 5. Hạn chế và hướng mở rộng
- **Hạn chế**: Kích thước tập Test gồm 6 câu là mẫu nhỏ dùng để minh họa quy trình đánh giá nghiêm ngặt, chưa đủ lớn để suy rộng về mặt thống kê. Mô hình dense embedding đôi khi bị thiên lệch bởi tần suất lặp từ khóa chung chung.
- **Hướng cải tiến**: Áp dụng Hybrid Retrieval kết hợp Sparse BM25 với Dense Vector và xếp hạng lại bằng Reranker.

---

## Mở rộng tùy chọn: Thử nghiệm Hybrid Retrieval (Dense Vector + BM25)

Theo hướng dẫn mở rộng trong [GUIDE.md](../../GUIDE.md), ta giữ nguyên các chunk của Chiến lược B & C (by-paragraph) và bộ lọc metadata, kết hợp tìm kiếm ngữ nghĩa Dense Vector (`all-MiniLM-L6-v2`) với tìm kiếm từ khóa Sparse **BM25** (thư viện `rank-bm25`).

### 1. Kiến trúc kết hợp (Fusion Methods)
1. **Weighted Score Fusion**: Chuẩn hóa Min-Max điểm số Dense Cosine và điểm số BM25, sau đó kết hợp theo trọng số $\alpha$:
   $$\text{Score}_{\text{hybrid}} = \alpha \cdot \text{Score}_{\text{dense\_norm}} + (1 - \alpha) \cdot \text{Score}_{\text{bm25\_norm}}$$
2. **Reciprocal Rank Fusion (RRF)**: Phương pháp kết hợp thứ hạng phi tham số chuẩn công nghiệp ($k = 60$):
   $$\text{RRF\_Score}(d) = \frac{1}{60 + \text{rank}_{\text{dense}}(d)} + \frac{1}{60 + \text{rank}_{\text{bm25}}(d)}$$

### 2. Chọn tham số trên tập Dev và Đánh giá trên tập Test
Dưới đây là kết quả điều chỉnh tham số trên 19 câu Dev và đánh giá kiểm chứng độc lập trên 6 câu Test:

| Phương pháp / Cấu hình | Dev Hit@1 (n/N) | Dev Hit@3 (n/N) | Test Hit@1 (n/N) | Test Hit@3 (n/N) | Đánh giá & Nhận xét |
|---|---|---|---|---|---|
| **BM25-only ($\alpha = 0.0$)** | 6/19 (31.58%) | 11/19 (57.89%) | 2/6 (33.33%) | 4/6 (66.67%) | Yếu ở câu diễn đạt lại, bắt tốt từ khóa hiếm. |
| **Dense-only (Strategy C baseline)** | 7/19 (36.84%) | 13/19 (68.42%) | 2/6 (33.33%) | 4/6 (66.67%) | Hiểu ngữ nghĩa tốt nhưng bị bias tần suất từ khóa. |
| **Weighted ($\alpha = 0.3$)** | 6/19 (31.58%) | 13/19 (68.42%) | 3/6 (50.00%) | **5/6 (83.33%)** | Nghiêng về từ khóa, cải thiện Test Hit@3. |
| **Weighted ($\alpha = 0.5$) [Tối ưu]** | 5/19 (26.32%) | **14/19 (73.68%)** | **4/6 (66.67%)** | **5/6 (83.33%)** | **Cấu hình tối ưu nhất trên Dev**, bứt phá mạnh trên Test. |
| **Weighted ($\alpha = 0.7$)** | 7/19 (36.84%) | 13/19 (68.42%) | 2/6 (33.33%) | 4/6 (66.67%) | Nghiêng nhiều về Dense, tương đương baseline. |
| **RRF ($k = 60$)** | 6/19 (31.58%) | **14/19 (73.68%)** | 2/6 (33.33%) | **5/6 (83.33%)** | RRF đạt hiệu năng cao tương đương Weighted $\alpha = 0.5$. |

- **Quyết định chọn tham số trên Dev**: Cấu hình **Weighted ($\alpha = 0.5$)** và **RRF ($k=60$)** đạt kết quả Dev Hit@3 cao nhất (**14/19 - 73.68%**). Khi áp dụng cấu hình $\alpha = 0.5$ lên tập Test chưa từng nhìn thấy, **Test Hit@3 tăng từ 4/6 (66.67%) lên 5/6 (83.33%)**, và **Test Hit@1 tăng vọt từ 2/6 lên 4/6 (66.67%)**!

### 3. Phân tích các trường hợp Hybrid cải thiện vượt bậc
- **Câu `q18` (Test set)**:
  - *Câu hỏi*: *"How has technological advancement impacted interpersonal interaction rules and protocols?"*
  - *Dense-only (Strategy C)*: Thất bại hoàn toàn (Hit@1 = False, Hit@3 = False). Trả về trang 280, 271, 272 do bị bias bởi mật độ từ khóa *"technology"*.
  - *Hybrid ($\alpha = 0.5$)*: **Đạt Hit@1 = True, Hit@3 = True**! Đưa đúng trang **268** lên Rank 1.
  - *Cơ chế giải thích*: BM25 bắt chính xác các thuật ngữ hiếm và cụ thể như *"rules"*, *"protocols"* chỉ xuất hiện tại trang 268 (*"Technology has created new rules for communication... emoji protocols..."*), kéo trang 268 từ ngoài top-10 lên thẳng vị trí số 1.
- **Câu `q20` (Test set)**:
  - *Dense-only (Strategy C)*: Thất bại (Hit@1 = False, Hit@3 = False) do bị tiêu đề lớn *"Three Effective Study Strategies"* ở trang 217 đánh lừa.
  - *Hybrid ($\alpha = 0.5$)*: **Đạt Hit@1 = True, Hit@3 = True**! Đưa đúng trang **212** lên Rank 1.
  - *Cơ chế giải thích*: BM25 bắt trúng cụm từ *"interrelated techniques"* chỉ có tại trang 212 (*"Two major and interrelated techniques involve avoiding distractions..."*).

### 4. Ghi nhận trung thực trường hợp Hybrid LÀM XẤU KẾT QUẢ (Degraded Case)
Theo đúng yêu cầu của GUIDE.md về tính trung thực khoa học, ta ghi nhận trường hợp Hybrid làm giảm độ chính xác:
- **Câu `q17` (Test set)**:
  - *Câu hỏi*: *"What two core methods are described for improving concentration and effectiveness while studying?"*
  - *Gold page*: Trang 212.
  - *Dense-only (Strategy C)*: **Hit@3 = True** (Trang 212 xếp ở Rank 2, điểm Cosine 0.6384).
  - *Hybrid ($\alpha = 0.5$)*: **Hit@3 = False (BỊ RỚT KHỎI TOP-3)**! Top-3 bị thay thế bởi trang 229, 217, 166.
  - *Nguyên nhân thất bại của Hybrid*: Câu hỏi `q17` thuộc dạng **diễn đạt lại (rephrased)**, sử dụng các từ chung chung như *"improving concentration and effectiveness"*. Các từ này xuất hiện lặp lại với tần suất cao ở phần tóm tắt ôn tập cuối chương (trang 229) và phần đọc hiểu (trang 166). BM25 đã cho điểm từ khóa rất cao cho các trang này, làm **pha loãng tín hiệu tương đồng ngữ nghĩa của Dense**, hệ quả là đẩy trang chứa bằng chứng gốc 212 rớt xuống vị trí Rank 4 ngoài Top-3.

---
*Dữ liệu vết truy xuất đầy đủ của thực nghiệm Hybrid được lưu tại: `results/hybrid_traces.json`.*
