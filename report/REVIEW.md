# Tự review submission Day20

Reviewer: Codex, ngày 2026-10-06. Đây là self-review; chưa có review độc lập của Claude Code. Bản đối chiếu bổ sung từ người dùng sẽ là vòng review tiếp theo.

| Yêu cầu theo GUIDE/RUBRIC | Bằng chứng để kiểm tra |
|---|---|
| Triển khai đúng phạm vi TODO | `publish-audit.json`: đối chiếu 49 file protected và AST ngoài các hàm TODO/imports với base d982034 |
| Test gốc hoạt động | `evidence/tests-20261006T052844615Z.log`: 29 passed trên Linux |
| Baseline và subagents đủ learn/eval | `results/baseline/`, `results/subagents/`: mỗi điều kiện 6 cặp run.json/trace.md |
| Curator tự sinh skill từ learn | Receipt `evidence/curate-20261006T052322503892Z.json` lưu prompt, response và usage; 3 skill hợp lệ, không sửa tay |
| Hypotheses trước freeze | Commit 9c5f0aed trước tag freeze tại 6ece8b4; `FREEZE_READY.md` |
| Skill đóng băng và 6 run chính thức | Native `verify_freeze.py`, hash skill trong từng run.json, skills_modified=false |
| Bảng và số liệu khớp nguồn | `table.md` từ native lab.compare, breakdown từ script gốc; audit đối chiếu bảng và check counts |
| Báo cáo đủ nội dung | REPORT.md mục 1–10: taxonomy 9 lỗi, thiết kế subagents, chất lượng 3 skill, 6 câu phân tích, giả thuyết và hạn chế |
| Giữ dữ liệu nhiễu và lỗi hạ tầng | `results/skills-auto-dev/` và 2 thư mục baseline CRLF tách khỏi bảng chính |
| Key và phối hợp | Audit tìm chuỗi credential trong artifacts; .env ignored, không mount; một writer, Claude mặc định chỉ đọc |

Các vấn đề đã xử lý: CRLF làm lệch hash test mẫu được sửa bằng archive Git giữ nguyên bytes; GPT-6 Luna dùng Responses và không truyền temperature; launcher ghi lại startup failure trước API, từ chối ghi đè kết quả, kiểm freeze trước eval. Raw log/trace giữ nguyên dù có trailing whitespace từ stdout; code và tài liệu được kiểm riêng.

Các giới hạn giữ nguyên trong báo cáo: baseline code-eval kết thúc với final rỗng (1/11), nguyên nhân chưa xác nhận; mỗi điều kiện chỉ một lần chạy chính thức; skill data chứa header region của learn và thiếu cách ghi source basename; skill không học các quy ước mới ở eval. Không sửa skill sau freeze hoặc rerun vì điểm thấp. Không suy luận điểm chấm cuối cùng từ điểm của task agent.

Snapshot máy kiểm tra là `evidence/publish-audit.json`, gồm SHA256 của 18 cặp kết quả, source TODO, báo cáo, launcher và skill. Khi nhận bản đối chiếu, reviewer cần đọc snapshot và lịch sử Git trước, chỉ chạy offline và không thay tag freeze hoặc kết quả thật. Các findings phải có vị trí, tác động và bằng chứng tái hiện; Codex vẫn là writer cho tới khi bàn giao rõ với người dùng.

Kết quả audit cuối: 49 protected files kiểm tra, 18 official runs, findings rỗng; bảng riêng và bảng dán trong REPORT đều khớp native compare. Native verify checked 6 runs OK; skill diff với freeze rỗng. Không tìm thấy chuỗi credential theo bộ dò trong results/report/skills (bộ dò không phải bảo đảm tuyệt đối). Không còn finding cần sửa trong phạm vi kiểm tra này; các hạn chế thí nghiệm vẫn được giữ công khai ở REPORT mục 9.

Bản nộp giữ reviewer là self-review. File publish-audit.json kiểm tra trực tiếp nội dung được công bố; tài liệu phối hợp và helper audit local không được nộp.
