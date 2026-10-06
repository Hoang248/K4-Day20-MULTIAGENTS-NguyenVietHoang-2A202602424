# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Việt Hoàng | 2A202602424 | Chủ project, cấu hình API, chọn model; Codex hỗ trợ code, thí nghiệm, phân tích và tự review. |

Trong bài lab này, tôi hoàn thiện bộ khung Deep Agents và so sánh ba cách thực hiện cùng một nhóm tác vụ: tác tử mặc định, tác tử có subagent và tác tử sử dụng skill do curator tự viết. Mục tiêu là tìm hiểu việc chia vai trò và học từ phản hồi có giúp cải thiện kết quả hay không, đồng thời xem phần cải thiện đó phải trả bằng bao nhiêu token. Bài làm bám theo [repo GitHub](https://github.com/Hoang248/K4-Day20-MULTIAGENTS-NguyenVietHoang-2A202602424), từ commit gốc d982034811dae6e0e42d0698131a9f33972a0bed.

Tôi sử dụng gpt-6-luna qua OpenAI Responses API với reasoning ở mức medium. Cả ba điều kiện dùng cùng cấu hình: không truyền temperature, recursion_limit 60, tối đa 8192 output token mỗi request, timeout 120 giây và API retry tối đa 1. Môi trường chạy là Python 3.12 trong Docker/Linux, với Deep Agents 0.7.21, langchain-openai 1.6.7, langchain-core 1.6.6 và OpenAI SDK 3.24.0. Phiên bản và cấu hình thực tế được lưu trong các receipt tại report/evidence/.

Để dùng mô hình đã chọn mà vẫn giữ nguyên model.py của đề, launcher truyền mô hình vào các hàm run_task và curate_skills. output_version v0 giúp kết quả tương thích với hàm hiển thị trace gốc; giá trị LAB_TEMPERATURE trong .env không được áp dụng cho launcher này. Bộ test trên Linux đạt 29/29. Tổng cộng có 27 lần chạy tác vụ: 18 lần chính thức, 3 lần thử skill và 6 lần gặp lỗi hạ tầng CRLF được lưu riêng. Curator được gọi một lần, cùng một lần kiểm tra kết nối API.

Tổng lượng token ghi nhận là 1,715,889, gồm 1,293,854 cho kết quả chính thức, 179,360 cho thử skill, 234,404 cho các lần lỗi hạ tầng, 8,255 cho curator và 16 cho kiểm tra kết nối. Con số này có tính cả cached input nên không thể quy trực tiếp thành tiền hóa đơn. Commit freeze là 6ece8b423bc0f40a3c2fcce954cee0d191caa48d; chi tiết môi trường được trình bày trong [SETUP_NOTES.md](SETUP_NOTES.md).

## 2. Giả thuyết (commit TRƯỚC tag freeze)

- H1 (subagents so với baseline): mean score eval của subagents không tăng quá 0.10 so với baseline, nhưng mean token cao hơn baseline. Baseline learn đã đạt 18/18 check kỹ thuật, chỉ thiếu 9 quy ước; chia vai trò không tự cung cấp quy ước vắng trong đề. Anthropic ghi nhận multi-agent tăng chi phí token trong hệ nghiên cứu riêng [1]; không ngoại suy tỷ lệ 15× cho lab.
- H2 (skills-auto so với baseline): mean score eval của skills-auto tăng ít nhất 0.10 so với baseline nhờ các quy ước chung học qua feedback learn, nhưng không đạt toàn bộ check trên cả 3 eval tasks do có quy ước mới. Đây là dự đoán cho lab có shared conventions, không khẳng định self-generated skills luôn tốt; SkillsBench v1 ghi nhận không có lợi ích trung bình của skill tự sinh [2].
- H3 (tác vụ học so với tác vụ đánh giá): mean score skills-auto trên learn cao hơn eval ít nhất 0.05; quy ước chung có thể chuyển giao nhưng skill thiếu quy ước mới hoặc biên dữ liệu mới. SkillEvolBench ghi nhận cải thiện tại chỗ thường không ổn định ở frozen deployment [3]. So sánh thử học trước và sau freeze để nhận diện nhiễu.

Viết trước khi chạy hoặc đọc điểm eval. Các ngưỡng là dự đoán của nhóm, không phải effect size lấy từ tài liệu tham khảo. Không dùng dữ liệu/đáp án eval để viết skill.

Hypotheses commit: 9c5f0aed. Freeze commit/tag: 6ece8b4 / freeze, 2026-10-06 12:30:19 +07:00. Cả hai được tạo trước mọi eval run; xem report/FREEZE_READY.md. Không sửa skill từ freeze.

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

Trích nguyên văn ngắn từ feedback: code `rule_type_hints`: “every public function”; `rule_regression_tests`: “one test function per bug you fixed (at least 3)”; data `rule_money_in_cents`: “money values in answer.json are integer cents”; logs `rule_sorted_errors`: “sorted by service, then by timestamp_utc, ascending.” Mỗi detail đều bắt đầu `RULE:`; đường dẫn cặp kết quả tương ứng là bằng chứng đầy đủ cho từng dòng.

Baseline đạt 7/10 ở code, 5/8 ở data và 6/9 ở logs, tương ứng điểm trung bình 0.6639. Điều đáng chú ý là cả 18 check kỹ thuật đều đạt, trong khi cả 9 check quy ước đều thất bại. Trace cho thấy tác tử đã đọc docstring, sửa hàm parse_price dùng chung và nơi gọi hàm, rồi chạy lại visible suite với 6 test đạt. Ở hai bài còn lại, tác tử xử lý được dòng trùng, giá trị thiếu, múi giờ, exception và dòng log lặp. Những kết quả này không cho thấy lỗi thuộc nhóm A–D; cũng không thấy bằng chứng của nhóm F trong ba baseline learn runs. Nguyên nhân chung là tác tử chưa biết các quy ước tổ chức không xuất hiện trong đề. Vì vậy, skill có thể giúp bổ sung phần kiến thức này, nhưng vẫn cần kiểm tra xem tác tử có đọc và làm theo hay không.

## 5. Điều kiện subagents (Phần 2.3)

Tôi chia subagent thành ba vai trò. Explorer đọc đặc tả và dữ liệu để nhận diện trường hợp dễ bỏ sót. Implementer thực hiện phần sửa đã được giao và kiểm tra lại. Reviewer đối chiếu kết quả với yêu cầu mà không sửa file. Mỗi vai trò có mô tả tình huống nên được gọi và nhận quy ước đường dẫn qua PATHS_NOTE. Tuy nhiên, quyền chỉ đọc của explorer và reviewer được hướng dẫn bằng prompt, chưa được cưỡng chế ở mức quyền truy cập tool.

| Learn task | Calls | Subagent thực sự gọi | Baseline tokens | Subagents tokens | Baseline / subagents giây |
|---|---|---|---|---|---|
| code-learn | 3 | explorer ×1, reviewer ×2 | 45,777 | 235,290 | 58.4 / 287.6 |
| data-learn | 1 | explorer | 24,419 | 50,928 | 23.2 / 69.5 |
| logs-learn | 1 | explorer | 37,821 | 76,257 | 32.3 / 73.7 |

Implementer không được gọi ở ba learn runs; tác tử chính tự sửa/tạo output. Mean token learn tăng từ 36,005.7 lên 120,825.0 (3.36×), mean thời gian từ 38.0 lên 143.6 giây; mean score giữ 0.6639, technical 18/18, conventions 0/9. Code delegation chỉ nêu scope/docstrings và “Acme conventions where apparent”, không đưa đầy đủ đề nguyên văn; reviewer được gọi cả trước và sau sửa, tạo thêm trao đổi về edge cases ngoài visible tests. Data delegation chỉ nêu paths và “requested metrics” thay vì liệt kê đủ các metric, nên có rủi ro context thiếu; agent chính đọc lại data dictionary, tự tính bằng float rồi Decimal và kiểm JSON. Logs delegation nêu rõ filters, UTC, message/exception/repeat/counts nên đầy đủ hơn. Agent chính kiểm chứng báo cáo bằng đọc files, chạy visible suite hoặc JSON checks; không biết conventions ẩn nên nhiều review vẫn không sửa 9 lỗi E. Bằng chứng ở results/subagents/<task>/trace.md, tool call task và execute; không suy đoán hành vi bên trong subagent từ trace luồng chính.

| Eval task | Calls và vai trò | Baseline / subagents score | Baseline / subagents tokens | Baseline / subagents giây |
|---|---|---|---|---|
| code-eval | 3: explorer, implementer, reviewer | 1/11 / 7/11 | 27,112 / 300,959 | 74.0 / 331.6 |
| data-eval | 1: explorer | 5/9 / 5/9 | 23,567 / 66,165 | 29.0 / 55.1 |
| logs-eval | 2: explorer, reviewer | 6/10 / 6/10 | 25,197 / 72,187 | 20.4 / 85.0 |

Code eval thực sự dùng implementer và agent chính chạy kiểm tra sau báo cáo; data delegation liệt kê đầy đủ first-event/id, missing total, normalization và metrics; logs giao các parser rules và reviewer kiểm output. Eval mean token 146,437 so với 25,292 (5.79×), thời gian 157.2 so với 41.1 giây. Điểm tăng chỉ ở code, nơi baseline kết thúc không sửa gì; không thể gán toàn bộ mức tăng cho ưu thế phối hợp. Receipt subagents ghi 78 LLM responses có status completed; baseline batch chưa có instrumentation này.

## 6. Self-evolving: skill do curator sinh (Phần 3)

Sau khi phân tích lỗi baseline learn, tôi chạy curator một lần và nhận được ba skill. Tôi giữ nguyên nội dung được sinh ra, không sửa tay, không xóa skill và không gọi curator lại. Curator chỉ nhận ba baseline learn runs hợp lệ; các lần lỗi CRLF và dữ liệu eval không được đưa vào đầu vào. Cả ba skill đều đạt bộ kiểm tra định dạng gốc. Prompt, phản hồi nguyên bản và lượng token của lần sinh skill được lưu tại report/evidence/curate-20261006T052322503892Z.json.

| Skill | Tổng quát | Đúng/sai và giới hạn | Độ dài và trigger |
|---|---|---|---|
| python-package-bugfixes | Quy trình sửa package, tests/changelog dùng tên theo conventions, không lặp input/function cụ thể. | Phần type annotations chỉ áp dụng public function được sửa, hẹp hơn feedback yêu cầu mọi public function. Có thể bỏ sót hàm không sửa. Không phải hướng dẫn phá hoại nên giữ để đo hiệu quả/giới hạn. | 10 dòng toàn file, 6 bước body; description nêu Python bugfix với regression/tests/annotations/changelog. |
| cleaned-data-deliverables | Đọc data dictionary, dedup, UTC, schema; clean.csv/answer.json và các khóa thuộc convention được phép. | Phù hợp feedback money/meta/clean CSV. “Exclude unknown” cần hiểu cho revenue/clean deliverable, không được mất thống kê missing của đề; chưa hướng dẫn Decimal cụ thể. | 13 dòng, 9 bước body; trigger tabular → clean CSV/JSON, dates/money. |
| log-triage-json | Quy trình parser/normalize/sort/schema, không nêu file log hoặc service riêng của learn. | Giữ đúng naming/sort/header theo feedback; continuation phải ánh xạ đúng field theo task spec, không đưa cả stack trace vào first-line message. | 13 dòng, 9 bước body; trigger application logs → JSON error records. |

Không có định danh eval theo validator; tên output/schema là shared conventions, không phải bằng chứng leakage. Tính đúng mới được kiểm thêm qua runs; format hợp lệ không tự chứng minh nội dung đủ. Kết quả thử học lưu riêng results/skills-auto-dev trước freeze. Không skill nào bị xóa; không có curator rerun.

Kết quả Phần 3.4 đã hoàn tất và sao lưu ở results/skills-auto-dev, cùng bộ skill không chỉnh sửa:

| Task | Score thử học | Tokens | Skills read | Giây |
|---|---|---|---|---|
| code-learn | 10/10 | 107,610 | 1 | 94.5 |
| data-learn | 8/8 | 33,840 | 1 | 35.5 |
| logs-learn | 9/9 | 37,910 | 1 | 31.3 |

Mean score 1.00; technical 18/18, rules 9/9. Không có error hay skills_modified. Code agent đọc python-package-bugfixes và thực tế bổ sung annotations đủ mọi public functions, nên hạn chế câu chữ đã nêu không làm fail lần này. Data và logs đọc đúng skill tương ứng, tạo schema/clean CSV/naming/sort/header đạt grader; điều này chứng minh hiệu quả trong 3 trial learn runs, không chứng minh transfer eval. Không chạy lại curator.

Cả 6 run chính thức đọc đúng 1 skill tương ứng (skills_read=1), không sửa skill. Code/logs áp dụng annotations/regressions/changelog hoặc naming/sort/schema; data learn sau freeze chỉ áp dụng cents ở CSV nhưng answer.json còn revenue 3130.24 USD. Data eval áp dụng cents đúng nhưng ghi meta.source="workspace/orders.json" thay vì basename và giữ header region trong khi task dùng category. Hai lỗi này cho thấy skill vừa thiếu độ rõ vừa mang schema cụ thể của learn. Ba quy ước mới (version bump, sorted JSON keys, source_line) không có trong skill; chúng đều thất bại. Phân tích eval này thực hiện sau freeze và chạy chính thức, không dùng để sửa skill.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Nội dung dưới đây dán nguyên bảng do native lab.compare sinh từ 18 run.json; bản riêng tại [table.md](table.md).

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 10/10 |
| data-learn | 5/8 | 5/8 | 7/8 |
| logs-learn | 6/9 | 6/9 | 9/9 |
| code-eval | 1/11 | 7/11 | 10/11 |
| data-eval | 5/9 | 5/9 | 6/9 |
| logs-eval | 6/10 | 6/10 | 9/10 |
| **Mean score - learning tasks** | 0.66 | 0.66 | 0.96 |
| **Mean score - evaluation tasks** | 0.42 | 0.60 | 0.83 |
| **Mean tokens per run** | 30,648 | 133,631 | 51,362 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |

Native check_breakdown.py (số token trung bình làm tròn xuống theo script):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     12/18         0/12          25,292      0/3
baseline      learn    18/18         0/9           36,005      0/3
subagents     eval     18/18         0/12         146,437      0/3
subagents     learn    18/18         0/9          120,825      0/3
skills-auto   eval     18/18         7/12          50,900      3/3
skills-auto   learn    18/18         8/9           51,825      3/3
```

Không run chính thức nào có error hoặc skills_modified=true. Native verifier: `checked 6 runs of skill conditions: OK`, log evidence/verify-20261006T055226032Z.log. Baseline code-eval final_message rỗng và trace chỉ đọc files, điểm 1/11; giữ nguyên thay vì rerun theo điểm. Hai batch CRLF chỉ là lỗi hạ tầng đã loại và bảo toàn; startup failure của launcher sau thêm callback xảy ra trước API/run_task, đã sửa import trùng rồi chạy batch một lần. Các log và receipt ghi rõ lịch sử này. Receipt batch skills chính thức ghi 51 responses, tất cả status completed.

## 8. Phân tích

1. **Learn và eval.** Subagents không tăng learn (0.6639 → 0.6639), tăng eval 0.4155 → 0.5973 (+0.1818). Skills-auto tăng learn lên 0.9583 (+0.2944), eval lên 0.8253 (+0.4098); không có điều kiện chỉ tăng learn mà không tăng eval trong bảng này. Skills vẫn có khoảng cách learn–eval 0.1331 và không task eval nào đạt đầy đủ. Các mean là tỷ lệ check đạt theo task, không phải tỷ lệ task thành công hoàn toàn; skills đạt đầy đủ 2/3 learn và 0/3 eval.

2. **Kỹ thuật và quy ước.** Learn technical cả ba điều kiện đều 18/18; lợi ích skill nằm ở conventions, 0/9 → 8/9. Eval subagents và skills đều 18/18 technical so với baseline 12/18, nhưng chỉ skills đạt 7/12 conventions. Tách 9 conventions tương ứng learn, skill đạt 7/9 ở eval; 3 quy ước mới đều 0/3. Thiếu version bump ở code, sort_keys/format ở data, source_line ở logs; curator không nhận feedback về chúng nên không có cơ sở học. Hai convention còn thiếu trong 9 shared checks là data meta và clean CSV; tên check giống nhau nhưng schema category thay region cần thích nghi.

3. **Cơ chế từ trace.** logs-eval đọc log-triage-json ở trace dòng 28, code parser normalize `service.lower().replace('-', '_')`, sort theo service/timestamp và tạo schema_version/generated_by; rule_service_names và rule_sorted_errors từ fail baseline trở thành pass. code-eval đọc python-package-bugfixes ở dòng 13, viết regression tests/changelog ở dòng 275–278 nên pass 3 conventions cũ, nhưng không đổi __version__=1.4.2 đã đọc ở dòng 89: rule_version_bump fail do skill thiếu. data-learn sau freeze đọc skill nhưng tool output revenue vẫn 3130.24 (trace cuối), nên rule_money_in_cents fail: đã đọc không đồng nghĩa làm theo. Data eval còn dùng header region đúng theo skill nhưng sai theo schema eval; đây là counterexample về mức tổng quát.

4. **Chi phí và hiệu quả.** Tổng token chính thức baseline 183,893; subagents 801,786; skills 308,175. Subagents tốn 4.36× baseline trên 6 tasks; skills tốn 1.68×. Định nghĩa hiệu quả là mean score / mean token ×1,000, dùng số không làm tròn: overall baseline 0.01761, subagents 0.00472, skills 0.01736; learn lần lượt 0.01844/0.00549/0.01849, eval 0.01643/0.00408/0.01621. Baseline nhỉnh nhất theo proxy overall, skills có chất lượng cao nhất và hiệu quả token gần baseline; chênh lệch nhỏ không đủ chứng minh ưu thế ổn định. Tỷ lệ này chưa cộng 8,255 token curator và chi phí thử skill, cũng không định giá cached/input/output. Subagents cải thiện code eval nhưng không đáng chi phí theo proxy này: data/logs không tăng điểm, learn không tăng, token và thời gian tăng mạnh. Cùng cap mỗi request không tạo cùng tổng ngân sách, nên đây chưa là phép so sánh ở cùng budget.

5. **Leakage và quá khớp.** Curator chỉ dùng 3 baseline learn hợp lệ; raw prompt/response được lưu, validator không nhận eval identifiers; H1–H3 commit trước freeze, mọi eval bắt đầu sau tag và native hash check OK. Không phát hiện bằng chứng rò rỉ đáp án eval vào skill; validator không phải chứng minh tuyệt đối không leakage. Header region cứng và thiếu source basename là dấu hiệu chuyển giao kém từ conventions của learn. Shared conventions do đề thiết kế giúp skill có lợi thế; kết quả 7/12 eval rules không cho phép kết luận tiến hóa năng lực tổng quát. Chỉ đọc grader eval để giải thích sau freeze và sau run eval tương ứng, không sửa skill hay task.

6. **Nhiễu trước/sau freeze.** Cùng hash skill, code-learn 10/10 → 10/10, data-learn 8/8 → 7/8, logs-learn 9/9 → 9/9; mean 1.0000 → 0.9583, giảm 0.0417. Chênh lệch duy nhất là data money convention dù input/skill không đổi; token mean 59,786.7 → 51,825.0, thời gian 53.8 → 84.7 giây. Hai mẫu learn cho thấy độ không ổn định thực tế, không đo được phân phối nhiễu hay khoảng tin cậy eval. Do vậy +0.1818/+0.4098 là chênh lệch quan sát, chưa là effect ổn định.

Đối chiếu giả thuyết đã đăng ký: **H1 không được hỗ trợ toàn bộ** vì eval tăng 0.1818 >0.10; phần dự đoán token tăng đúng, nhưng baseline code termination là yếu tố gây nhiễu. **H2 được dữ liệu lần chạy này hỗ trợ**: +0.4098 ≥0.10 và 0/3 eval đạt toàn bộ. **H3 được dữ liệu lần chạy này hỗ trợ**: learn–eval 0.1331 ≥0.05; vẫn giữ cảnh báo nhiễu 0.0417 trên learn. Không sửa ngưỡng giả thuyết sau khi biết kết quả.

## 9. Hạn chế và tính hợp lệ

1. Chỉ 3 task mỗi role, thiết kế sẵn theo 3 họ; mean score không đại diện tác vụ sản xuất đa dạng.
2. Mỗi condition/task chính thức một lần; chênh lệch có thể là nhiễu. So sánh trước/sau freeze trên learn không phải khoảng tin cậy eval.
3. Một model/effort và một thiết kế subagents/curator; chưa tách được ảnh hưởng model, prompt và dữ liệu.
4. Shared conventions cố ý xuất hiện trong learn/eval; học conventions không đồng nghĩa tăng năng lực giải quyết vấn đề tổng quát.
5. Trace chỉ luồng chính, cắt mỗi content 1500 ký tự; tool_calls/subagent_calls/skills_read không nhìn bên trong subagent, còn usage cộng mọi LLM call.
6. Hai batch CRLF loại khỏi phân tích nhưng vẫn tiêu token; báo chi phí cả chúng. Tiền hóa đơn chưa đo, không đồng nhất token với tiền.
7. Baseline code-eval kết thúc final rỗng; giới hạn 8192 output/request có thể góp phần, nhưng không lưu response status ở batch đó nên nguyên nhân chưa xác nhận. Điều này làm baseline eval thấp và phóng đại chênh lệch nếu dùng để khẳng định lợi ích kiến trúc.
8. Cùng cấu hình mỗi request nhưng số LLM calls và tổng budget khác nhau, đặc biệt subagents; chưa so sánh ở cùng ngân sách. Logs instrumentation bổ sung sau baseline chỉ để quan sát status, không đổi model/prompt/effort/cap.

## 10. Kết luận

Triển khai đạt 29/29 test gốc Linux, đủ 18 run chính thức và native freeze verification OK. Skill tự sinh nâng mean score learn từ 0.6639 lên 0.9583 và eval từ 0.4155 lên 0.8253, chủ yếu nhờ conventions đã học. Subagents không tăng learn và tốn nhiều token; lợi ích eval chỉ xuất hiện ở code, có yếu tố baseline kết thúc sớm. Skills vẫn bỏ sót quy ước mới và có một lỗi learn lặp lại, nên chưa chứng minh tiến hóa năng lực tổng quát hoặc hiệu quả ổn định. Bước tiếp theo nên lặp eval ở cùng tổng budget, lưu response status từ đầu và báo khoảng dao động mà vẫn giữ snapshot submission hiện tại.

## Phụ lục

Lệnh/log/receipts tại report/evidence/; tái lập từ report/reproduce/README.md. Không làm thử thách mở rộng tùy chọn; batch CRLF không phải phép lặp đo nhiễu có kiểm soát. Giữ provided code và task nguồn; Docker dùng exact Git bytes theo SETUP_NOTES. Review là self-review Codex, chưa có review độc lập Claude Code; người dùng sẽ cung cấp bản đối chiếu sau.

Thứ tự thực thi: provided tests → tour/probe → triển khai và full tests → hai baseline learn lỗi CRLF được bảo toàn → baseline learn hợp lệ → subagents learn → curator → skills-auto learn thử ở results/dev rồi chuyển sang skills-auto-dev → viết H1–H3 và commit hypotheses → commit/tag freeze → baseline eval → subagents eval → skills-auto all → verify → compare → breakdown → tự review/audit. Lệnh Linux/Docker tương ứng được ghi trong report/reproduce/README.md; lịch sử Git và receipts UTC lưu thời điểm. Các lượt test/guard offline không là task API runs. Xem [REVIEW.md](REVIEW.md) và snapshot evidence/publish-audit.json để đối chiếu sau.

### Tài liệu tham khảo

[1] Anthropic (2025). [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system). Hệ nghiên cứu của tác giả, không phải tỷ lệ chi phí đảm bảo cho lab.

[2] Li et al. (2026). [SkillsBench, v1](https://arxiv.org/abs/2602.12670v1). Dùng v1 cho căn cứ 16.2 pp của GUIDE; v4 có thống kê và tập đánh giá cập nhật.

[3] Lei et al. (2026). [SkillEvolBench](https://arxiv.org/abs/2605.24117). Căn cứ rủi ro chuyển giao và procedural clutter.

[4] OpenAI (truy cập 2026-10-06). [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [Using GPT-6](https://developers.openai.com/api/docs/guides/latest-model). Căn cứ Responses API và bỏ temperature khi reasoning khác none.


### Lịch sử bản nộp

Bản GitHub chỉ giữ sản phẩm của bài và tài liệu tái lập, loại các file harness phối hợp khỏi toàn bộ lịch sử bổ sung. Commit hypotheses local c7e9b9d2 tương ứng 9c5f0aed trong bản nộp; freeze local 2a282723 tương ứng 6ece8b42. Hai commit được tạo lại với nguyên ngày giờ, giả thuyết và bytes skill; kết quả và trace không sửa. Đây là bước đóng gói sau thí nghiệm, không phải thí nghiệm mới.
