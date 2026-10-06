# Tái lập và kiểm tra bài nộp

Chạy trên Linux với Python >=3.11 hoặc Docker Desktop. Các file của đề, prompt cố định và bộ chấm được giữ nguyên. .gitattributes giữ nguyên bytes Git của tasks/tests và LF cho skill; không dùng checkout bị chuyển đổi CRLF làm đầu vào grader.

```bash
pip install -e .
pytest
python scripts/verify_freeze.py
python -m lab.compare
python scripts/check_breakdown.py
```

Model thực nghiệm là gpt-6-luna, Responses API, reasoning medium, không truyền temperature, cap 8192 output/request, timeout 120 giây, retry 1, recursion_limit 60. Launcher run_model.py truyền ChatOpenAI vào các hàm native, không sửa model.py. Chỉ cấu hình OPENAI_API_KEY và LAB_MODEL=openai:gpt-6-luna trong .env; để trống Azure. Không gửi hoặc commit key.

Không chạy lại vào kết quả có sẵn. Các lệnh dưới minh họa thứ tự thí nghiệm đã thực hiện, cần một thư mục kết quả mới nếu muốn lặp:

```bash
python scripts/tour.py
python report/reproduce/run_model.py probe
python report/reproduce/run_model.py run --condition baseline --tasks learn --results results/repeat
python report/reproduce/run_model.py run --condition subagents --tasks learn --results results/repeat
# Curator ban đầu đã sinh 3 skill; không sinh lại hoặc sửa skill đóng băng của submission.
# Với thí nghiệm mới, tách repo/namespace, chạy curator rồi thử learn và đăng ký hypotheses trước freeze mới.
python report/reproduce/run_model.py run --condition baseline --tasks eval --results results/repeat
python report/reproduce/run_model.py run --condition subagents --tasks eval --results results/repeat
python report/reproduce/run_model.py run --condition skills-auto --tasks all --results results/repeat
```

Launcher từ chối ghi đè và kiểm verifier gốc trước eval. Bộ kết quả chính thức tại results/baseline, subagents, skills-auto; trials tại skills-auto-dev và hai batch CRLF là bằng chứng loại khỏi phân tích. Không chuyển tag freeze khi lặp.

Docker offline:

```bash
docker build -t day20-lab:local .
docker build -f report/reproduce/Dockerfile -t day20-lab:runtime .
docker run --rm -v "$PWD:/lab:ro" -e PYTHONDONTWRITEBYTECODE=1 -e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0=/lab day20-lab:runtime python scripts/verify_freeze.py
```

Lệnh mount toàn repo ở trên chỉ dành cho kiểm tra offline, không chạy tác tử với key. Khi chạy API trong Docker, dùng --env-file .env và chỉ mount src/tests/scripts/tasks/skills/.git readonly cùng results/report writable theo từng thư mục; không mount .env hoặc toàn workspace chứa secrets. Backend shell của tác tử nhận env whitelist; container là lớp cô lập ngoài host. Read-only theo vai trò subagent vẫn là quy tắc prompt, không phải quyền OS.
