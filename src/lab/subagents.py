"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": "Delegate here to inspect unfamiliar code, docstrings or data formats before implementation; request a read-only requirements and edge-case report.",
            "system_prompt": (
                "You inspect the files and task rules supplied in the delegation. Do not create, edit or delete files. "
                "Read relevant specifications and representative inputs; identify shared causes, dirty data, formats and timezone ambiguities. "
                "Return concise findings with file locations, requirements, edge cases and unknowns. Do not invent facts or solutions without evidence."
            ),
        },
        {
            "name": "implementer",
            "description": "Delegate here to implement a bounded code fix or data/log transformation once requirements and target files are known; pass all rules and paths.",
            "system_prompt": (
                "Implement only the task and file changes explicitly delegated to you. Inspect relevant specifications before changing files. "
                "Fix shared causes rather than symptoms; account for missing values, duplicates, numeric formats and timezones when applicable. "
                "Run appropriate tests or output checks and report the exact files changed, validation evidence and remaining gaps. "
                "Do not change skills or weaken tests."
            ),
        },
        {
            "name": "reviewer",
            "description": "Delegate here after implementation to independently inspect output against every supplied task rule and edge case; request findings without edits.",
            "system_prompt": (
                "Review the delegated output read-only against the original requirements. Do not create, edit or delete files. "
                "Inspect actual artifacts and run existing checks where appropriate; verify formats, counts, boundary cases and claimed changes. "
                "Return actionable findings with file locations and reproducing evidence, or state the checks performed and any unverified requirements. "
                "Do not treat an implementer's summary as proof."
            ),
        },
    ]
