# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Việt Hoàng (theo tên repo) | 2A202602424 (theo tên repo) | Chủ project, cấu hình API, chọn model; Codex hỗ trợ code, thí nghiệm, phân tích và tự review. |

Nguồn đề: [GitHub](https://github.com/Hoang248/K4-Day20-MULTIAGENTS-NguyenVietHoang-2A202602424), base d982034811dae6e0e42d0698131a9f33972a0bed. Model gpt-6-luna, OpenAI Responses API, reasoning medium, không truyền temperature, recursion_limit 60, max output 8192/request, timeout 120 giây, API retry tối đa 1. Tất cả điều kiện cùng cấu hình. Python 3.12, Docker/Linux, Deep Agents 0.7.21, langchain-openai 1.6.7, langchain-core 1.6.6, OpenAI SDK 3.24.0; phiên bản thực lưu trong report/evidence/*.json.

Launcher report/reproduce/run_model.py inject model qua tham số native run_task/curate_skills; giữ nguyên model.py. output_version v0 để tương thích renderer gốc. LAB_TEMPERATURE=0 trong .env không áp dụng launcher reasoning. Test Linux đạt 29/29. Kế hoạch 21 task runs, 1 curator, 1 probe; thêm 6 run hạ tầng CRLF lưu riêng và loại khỏi phân tích. Tổng token và freeze commit sẽ cập nhật khi hoàn tất. Xem [SETUP_NOTES.md](SETUP_NOTES.md).

## 2. Giả thuyết (commit TRƯỚC tag freeze)

- H1 (subagents so với baseline): mean score eval của subagents không tăng quá 0.10 so với baseline, nhưng mean token cao hơn baseline. Baseline learn đã đạt 18/18 check kỹ thuật, chỉ thiếu 9 quy ước; chia vai trò không tự cung cấp quy ước vắng trong đề. Anthropic ghi nhận multi-agent tăng chi phí token trong hệ nghiên cứu riêng [1]; không ngoại suy tỷ lệ 15× cho lab.
- H2 (skills-auto so với baseline): mean score eval của skills-auto tăng ít nhất 0.10 so với baseline nhờ các quy ước chung học qua feedback learn, nhưng không đạt toàn bộ check trên cả 3 eval tasks do có quy ước mới. Đây là dự đoán cho lab có shared conventions, không khẳng định self-generated skills luôn tốt; SkillsBench v1 ghi nhận không có lợi ích trung bình của skill tự sinh [2].
- H3 (tác vụ học so với tác vụ đánh giá): mean score skills-auto trên learn cao hơn eval ít nhất 0.05; quy ước chung có thể chuyển giao nhưng skill thiếu quy ước mới hoặc biên dữ liệu mới. SkillEvolBench ghi nhận cải thiện tại chỗ thường không ổn định ở frozen deployment [3]. So sánh thử học trước và sau freeze để nhận diện nhiễu.

Viết trước khi chạy hoặc đọc điểm eval. Các ngưỡng là dự đoán của nhóm, không phải effect size lấy từ tài liệu tham khảo. Không dùng dữ liệu/đáp án eval để viết skill.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tour offline: ls, read_file, write_file, edit_file, delete, glob, grep, execute, task; execute chạy shell. write_todos không xuất hiện trong danh sách model thấy ở phiên bản này.
2. general-purpose mặc định có cùng tools với agent chính; invocation mặc định stateless, chỉ thấy prompt được giao và trả một báo cáo cuối. Phải truyền đủ rules, paths và output.
3. Mô tả task: “Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report.” Mô tả execute: “You MUST avoid using search commands like find and grep.” Đây là chỉ dẫn hành vi trong tool descriptions dù system prompt riêng mặc định rỗng. Log: report/evidence/tour-20261006T050646153Z.log.

Mô tả execute dùng chữ isolated sandbox; LocalShellBackend thực tế chạy trên host của container. Thư mục tạm và env sạch không tự tạo OS isolation; Docker tạo ranh giới ngoài host Windows.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Chỉ dùng baseline learn hợp lệ. Cả 9 check thất bại thuộc E; CRLF là hạ tầng, loại khỏi taxonomy.

| Task | Check thất bại | Nhóm | Bằng chứng detail trong results/baseline/<task>/run.json |
|---|---|---|---|
| code-learn | rule_type_hints | E | Mọi public function cần annotations cho parameters và return. |
| code-learn | rule_regression_tests | E | tests/test_regressions.py có ít nhất 3 test cho bugs sửa và phải pass. |
| code-learn | rule_changelog | E | CHANGELOG.md dưới ## Unreleased có ít nhất 3 bullets dạng - fix(<function name>): ... |
| data-learn | rule_money_in_cents | E | Tiền trong answer.json phải là integer cents. |
| data-learn | rule_meta_block | E | meta gồm source, rows_in gồm duplicates, rows_used gồm distinct orders known amount. |
| data-learn | rule_clean_csv | E | clean.csv đúng header, UTC timestamp, canonical region và amount_cents. |
| logs-learn | rule_service_names | E | Service lowercase, thay hyphen bằng underscore. |
| logs-learn | rule_sorted_errors | E | errors sort theo service rồi timestamp_utc, tăng dần. |
| logs-learn | rule_schema_header | E | schema_version=2 và generated_by=log-triage. |

Code 7/10, data 5/8, logs 6/9, mean score 0.6639. Technical 18/18, rules 0/9. Bằng chứng phủ định A–D: code đọc docstrings, sửa shared parse_price và caller, chạy visible suite 6 passed; data xử lý duplicates/sentinel/timezone; logs đạt UTC/exception/repeat/count checks. Không có bằng chứng lỗi F; final summaries khớp artifact được grader kiểm tra. Visible suite pass không chứng minh conventions pass. Skill có thể bổ sung quy ước thiếu, nhưng lợi ích còn phụ thuộc agent đọc và thực thi.

## 5. Điều kiện subagents (Phần 2.3)

Ba vai trò: explorer đọc specifications/data và báo edge cases; implementer sửa phạm vi rõ rồi kiểm tra; reviewer kiểm chứng output chỉ đọc. Description nêu khi nào gọi; build_agent nối PATHS_NOTE cho mỗi subagent. Giới hạn read-only bằng prompt, không enforce bằng quyền tool.

| Learn task | Calls | Subagent thực sự gọi | Baseline tokens | Subagents tokens | Baseline / subagents giây |
|---|---|---|---|---|---|
| code-learn | 3 | explorer ×1, reviewer ×2 | 45,777 | 235,290 | 58.4 / 287.6 |
| data-learn | 1 | explorer | 24,419 | 50,928 | 23.2 / 69.5 |
| logs-learn | 1 | explorer | 37,821 | 76,257 | 32.3 / 73.7 |

Implementer không được gọi ở ba learn runs; tác tử chính tự sửa/tạo output. Mean token learn tăng từ 36,005.7 lên 120,825.0 (3.36×), mean thời gian từ 38.0 lên 143.6 giây; mean score giữ 0.6639, technical 18/18, conventions 0/9. Code delegation chỉ nêu scope/docstrings và “Acme conventions where apparent”, không đưa đầy đủ đề nguyên văn; reviewer được gọi cả trước và sau sửa, tạo thêm trao đổi về edge cases ngoài visible tests. Data delegation chỉ nêu paths và “requested metrics” thay vì liệt kê đủ các metric, nên có rủi ro context thiếu; agent chính đọc lại data dictionary, tự tính bằng float rồi Decimal và kiểm JSON. Logs delegation nêu rõ filters, UTC, message/exception/repeat/counts nên đầy đủ hơn. Agent chính kiểm chứng báo cáo bằng đọc files, chạy visible suite hoặc JSON checks; không biết conventions ẩn nên nhiều review vẫn không sửa 9 lỗi E. Bằng chứng ở results/subagents/<task>/trace.md, tool call task và execute; không suy đoán hành vi bên trong subagent từ trace luồng chính.

## 6. Self-evolving: skill do curator sinh (Phần 3)

Curator chạy một lần, sinh 3 skill; không xóa hoặc sửa tay, không chạy lại. Receipt gốc gồm prompt, raw response và usage tại report/evidence/curate-20261006T052322503892Z.json. Chỉ nhận baseline learn hợp lệ; không dùng hai batch CRLF hoặc eval. Validator gốc trả danh sách vấn đề rỗng cho cả 3 skill.

| Skill | Tổng quát | Đúng/sai và giới hạn | Độ dài và trigger |
|---|---|---|---|
| python-package-bugfixes | Quy trình sửa package, tests/changelog dùng tên theo conventions, không lặp input/function cụ thể. | Phần type annotations chỉ áp dụng public function được sửa, hẹp hơn feedback yêu cầu mọi public function. Có thể bỏ sót hàm không sửa. Không phải hướng dẫn phá hoại nên giữ để đo hiệu quả/giới hạn. | 10 dòng toàn file, 6 bước body; description nêu Python bugfix với regression/tests/annotations/changelog. |
| cleaned-data-deliverables | Đọc data dictionary, dedup, UTC, schema; clean.csv/answer.json và các khóa thuộc convention được phép. | Phù hợp feedback money/meta/clean CSV. “Exclude unknown” cần hiểu cho revenue/clean deliverable, không được mất thống kê missing của đề; chưa hướng dẫn Decimal cụ thể. | 13 dòng, 9 bước body; trigger tabular → clean CSV/JSON, dates/money. |
| log-triage-json | Quy trình parser/normalize/sort/schema, không nêu file log hoặc service riêng của learn. | Giữ đúng naming/sort/header theo feedback; continuation phải ánh xạ đúng field theo task spec, không đưa cả stack trace vào first-line message. | 13 dòng, 9 bước body; trigger application logs → JSON error records. |

Không có định danh eval theo validator; tên output/schema là shared conventions, không phải bằng chứng leakage. Tính đúng mới được kiểm thêm qua runs; format hợp lệ không tự chứng minh nội dung đủ. Kết quả thử học lưu riêng results/skills-auto-dev trước freeze; skills_read và hành vi trong trace sẽ bổ sung sau batch.

Kết quả Phần 3.4 đã hoàn tất và sao lưu ở results/skills-auto-dev, cùng bộ skill không chỉnh sửa:

| Task | Score thử học | Tokens | Skills read | Giây |
|---|---|---|---|---|
| code-learn | 10/10 | 107,610 | 1 | 94.5 |
| data-learn | 8/8 | 33,840 | 1 | 35.5 |
| logs-learn | 9/9 | 37,910 | 1 | 31.3 |

Mean score 1.00; technical 18/18, rules 9/9. Không có error hay skills_modified. Code agent đọc python-package-bugfixes và thực tế bổ sung annotations đủ mọi public functions, nên hạn chế câu chữ đã nêu không làm fail lần này. Data và logs đọc đúng skill tương ứng, tạo schema/clean CSV/naming/sort/header đạt grader; điều này chứng minh hiệu quả trong 3 trial learn runs, không chứng minh transfer eval. Không chạy lại curator.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Chưa chạy eval trước hypotheses/freeze. Bảng cuối phải do lab.compare sinh từ 18 run.json. Kết quả skills thử học giữ riêng results/skills-auto-dev để so với lần chính thức sau freeze.

## 8. Phân tích

Chưa kết luận eval ở checkpoint này. Sẽ trả lời đủ sáu câu hỏi mẫu bằng số liệu và trace: learn/eval, technical/rules, cơ chế dùng skill, token efficiency, leakage/overfitting và nhiễu trước/sau freeze.

## 9. Hạn chế và tính hợp lệ

1. Chỉ 3 task mỗi role, thiết kế sẵn theo 3 họ; mean score không đại diện tác vụ sản xuất đa dạng.
2. Mỗi condition/task chính thức một lần; chênh lệch có thể là nhiễu. So sánh trước/sau freeze trên learn không phải khoảng tin cậy eval.
3. Một model/effort và một thiết kế subagents/curator; chưa tách được ảnh hưởng model, prompt và dữ liệu.
4. Shared conventions cố ý xuất hiện trong learn/eval; học conventions không đồng nghĩa tăng năng lực giải quyết vấn đề tổng quát.
5. Trace chỉ luồng chính, cắt mỗi content 1500 ký tự; tool_calls/subagent_calls/skills_read không nhìn bên trong subagent, còn usage cộng mọi LLM call.
6. Hai batch CRLF loại khỏi phân tích nhưng vẫn tiêu token; báo chi phí cả chúng. Tiền hóa đơn chưa đo, không đồng nhất token với tiền.

## 10. Kết luận

Triển khai đạt 29/29 test gốc Linux. Baseline learn đạt mọi check kỹ thuật, thiếu conventions. Chưa kết luận lợi ích subagents/skills đến khi hoàn tất dữ liệu chính thức sau freeze.

## Phụ lục

Lệnh/log/receipts tại report/evidence/; tái lập từ report/reproduce/README.md. Không làm thử thách mở rộng tùy chọn; batch CRLF không phải phép lặp đo nhiễu có kiểm soát. Giữ provided code và task nguồn; Docker dùng exact Git bytes theo SETUP_NOTES. Review là self-review Codex, chưa có review độc lập Claude Code; người dùng sẽ cung cấp bản đối chiếu sau.

### Tài liệu tham khảo

[1] Anthropic (2025). [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system). Hệ nghiên cứu của tác giả, không phải tỷ lệ chi phí đảm bảo cho lab.

[2] Li et al. (2026). [SkillsBench, v1](https://arxiv.org/abs/2602.12670v1). Dùng v1 cho căn cứ 16.2 pp của GUIDE; v4 có thống kê và tập đánh giá cập nhật.

[3] Lei et al. (2026). [SkillEvolBench](https://arxiv.org/abs/2605.24117). Căn cứ rủi ro chuyển giao và procedural clutter.

[4] OpenAI (truy cập 2026-10-06). [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [Using GPT-6](https://developers.openai.com/api/docs/guides/latest-model). Căn cứ Responses API và bỏ temperature khi reasoning khác none.
