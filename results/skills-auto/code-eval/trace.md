### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: read_file
{"file_path": "skills/python-package-bugfixes/SKILL.md", "offset": 0, "limit": 1000}

### Tool call: ls
{"path": "workspace"}

### Tool result
@@ lines 1-10 of 10 @@
---
name: python-package-bugfixes
description: Use when fixing bugs in an existing Python package and the repository expects regression tests, type annotations, and changelog entries.
---
1. Inspect the package structure, project guidance, and existing test and changelog conventions before editing.
2. Add type annotations for every parameter and return value of each public function you modify.
3. Add `tests/test_regressions.py` with a separate test for each fixed bug; include at least three tests.
4. Add a `CHANGELOG.md` bullet under `## Unreleased` for each fix, using `- fix(<function name>): <short description>`.
5. Run the documented test command and confirm the regression tests pass.
6. Review the changed files and verify the required annotations, tests, and changelog bullets are present.

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: ls
{"path": "workspace/bookings"}

### Tool call: ls
{"path": "workspace/tests"}

### Tool call: read_file
{"file_path": "workspace/README.md", "offset": 0, "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/CHANGELOG.md", "offset": 0, "limit": 1000}

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py']

### Tool result
['/workspace/tests/test_bookings.py']

### Tool result
@@ lines 1-5 of 5 @@
# bookings

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 1.4.2
- initial import

### Tool call: read_file
{"file_path": "workspace/bookings/__init__.py", "offset": 0, "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py", "offset": 0, "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/bookings/calendar_export.py", "offset": 0, "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py", "offset": 0, "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py", "offset": 0, "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py", "offset": 0, "limit": 1000}

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Tool call: glob
{"pattern": "*", "path": "workspace"}

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 120000}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/__init__.py', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/test_bookings.py']

### Tool result
Error: timeout 120000s exceeds maximum allowed (3600s).

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 120000}

### Tool result
Error: timeout 120000s exceeds maximum allowed (3600s).

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 60}

### Tool result
FF.                                                                      [100%]
=================================== FAILURES ===================================
_______________________ test_total_minutes_mixed_formats _______________________

    def test_total_minutes_mixed_formats():
>       assert total_minutes(["1h30m", "2h"]) == 210
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_bookings.py:6: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
bookings/schedule.py:7: in total_minutes
    return sum(parse_duration(d) for d in durations)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
bookings/schedule.py:7: in <genexpr>
    return sum(parse_duration(d) for d in durations)
               ^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

text = '2h'

    def parse_duration(text):
        """Convert a duration string to whole minutes (int).
    
        Supported formats:
          "1h30m" -> 90
          "2h"    -> 120
          "45m"   -> 45
          "1:30"  -> 90
          "45"    -> 45    # a bare number means minutes
        Surrounding whitespace is ignored.
        """
        m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
        if not m:
>           raise ValueError(f"bad duration: {text!r}")
E           ValueError: bad duration: '2h'

bookings/timeutil.py:18: ValueError
________________________ test_billable_blocks_rounds_up ________________________

    def test_bil

### Tool call: write_file
{"file_path": "workspace/bookings/timeutil.py", "content": "\"\"\"Time helpers for the bookings package.\"\"\"\nimport re\n\n\n_DURATION_PATTERNS = (\n    re.compile(r\"(\\d+)h(\\d+)m\"),\n    re.compile(r\"(\\d+)h\"),\n    re.compile(r\"(\\d+)m\"),\n    re.compile(r\"(\\d+):(\\d+)\"),\n    re.compile(r\"(\\d+)\"),\n)\n\n\ndef parse_duration(text: str) -> int:\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    if not isinstance(text, str):\n        raise ValueError(f\"bad duration: {text!r}\")\n\n    value = text.strip()\n    for index, pattern in enumerate(_DURATION_PATTERNS):\n        match = pattern.fullmatch(value)\n        if match is None:\n            continue\n        if index == 0:\n            return int(match.group(1)) * 60 + int(match.group(2))\n        if index == 1:\n            return int(match.group(1)) * 60\n        if index == 2:\n            return int(match.group(1))\n        if index == 3:\n            hours, minutes = map(int, match.groups())\n            if minutes >= 60:\n                break\n            return hours * 60 + minutes\n        return int(match.group(1))\n\n    raise ValueError(f\"bad duration: {text!r}\")\n"}

### Tool result
Updated file /workspace/bookings/timeutil.py

### Tool call: write_file
{"file_path": "workspace/bookings/billing.py", "content": "\"\"\"Billing rules.\"\"\"\nfrom math import ceil\n\n\ndef billable_blocks(minutes: int, block: int = 15) -> int:\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n    \"\"\"\n    if minutes < 0:\n        raise ValueError(\"minutes must be non-negative\")\n    if block <= 0:\n        raise ValueError(\"block must be positive\")\n    return ceil(minutes / block)\n"}

### Tool call: write_file
{"file_path": "workspace/bookings/schedule.py", "content": "\"\"\"Schedule helpers.\"\"\"\nfrom collections.abc import Iterable, Sequence\nfrom typing import TypeVar\n\nfrom .timeutil import parse_duration\n\n\nSlot = TypeVar(\"Slot\")\n\n\ndef total_minutes(durations: Iterable[str]) -> int:\n    \"\"\"Total minutes of a list of duration strings.\"\"\"\n    return sum(parse_duration(duration) for duration in durations)\n\n\ndef add_slot(slot: Slot, slots: Sequence[Slot] = ()) -> list[Slot]:\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    return [*slots, slot]\n"}

### Tool call: write_file
{"file_path": "workspace/bookings/calendar_export.py", "content": "\"\"\"Calendar export.\"\"\"\nfrom .timeutil import parse_duration\n\n\ndef slot_end(start_minute: int, duration_text: str) -> int:\n    \"\"\"Minute of the day at which a slot ends.\"\"\"\n    return start_minute + parse_duration(duration_text)\n"}

### Tool result
Updated file /workspace/bookings/billing.py

### Tool result
Updated file /workspace/bookings/schedule.py

### Tool result
Updated file /workspace/bookings/calendar_export.py

### Tool call: edit_file
{"file_path": "workspace/bookings/billing.py", "old_string": "from math import ceil\n\n\n", "new_string": "", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: edit_file
{"file_path": "workspace/bookings/billing.py", "old_string": "    return ceil(minutes / block)\n", "new_string": "    return (minutes + block - 1) // block\n", "replace_all": false}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: write_file
{"file_path": "workspace/tests/test_regressions.py", "content": "import pytest\n\nfrom bookings.billing import billable_blocks\nfrom bookings.schedule import add_slot\nfrom bookings.timeutil import parse_duration\n\n\ndef test_parse_duration_supports_all_documented_formats():\n    assert parse_duration(\" 1h30m \") == 90\n    assert parse_duration(\"2h\") == 120\n    assert parse_duration(\"45m\") == 45\n    assert parse_duration(\"1:30\") == 90\n    assert parse_duration(\"45\") == 45\n\n\ndef test_billable_blocks_rounds_up_and_rejects_negative_minutes():\n    assert billable_blocks(0) == 0\n    assert billable_blocks(15) == 1\n    assert billable_blocks(16) == 2\n    assert billable_blocks(20, block=10) == 2\n    with pytest.raises(ValueError):\n        billable_blocks(-1)\n\n\ndef test_add_slot_returns_a_new_list_without_mutating_input():\n    original = [\"existing\"]\n    assert add_slot(\"new\", original) == [\"existing\", \"new\"]\n    assert original == [\"existing\"]\n    assert add_slot(\"a\") == [\"a\"]\n    assert add_slot(\"b\") == [\"b\"]\n\n\ndef test_parse_duration_rejects_unsupported_or_malformed_values():\n    for value in (\"\", \"1d\", \"one hour\", \"1:60\"):\n        with pytest.raises(ValueError):\n            parse_duration(value)\n"}

### Tool call: edit_file
{"file_path": "workspace/CHANGELOG.md", "old_string": "## Unreleased\n\n", "new_string": "## Unreleased\n\n- fix(parse_duration): support all documented duration formats and reject malformed values.\n- fix(billable_blocks): round partial blocks up and reject negative minutes.\n- fix(add_slot): return a fresh list without mutating shared or caller-owned state.\n\n", "replace_all": false}

### Tool result
Updated file /workspace/tests/test_regressions.py

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/CHANGELOG.md'

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q", "timeout": 60}

### Tool result
.......                                                                  [100%]
7 passed in 0.01s

[Command succeeded with exit code 0]

### Assistant
[{'type': 'text', 'text': 'Fixed duration parsing for all documented formats, corrected billable-block rounding and negative-minute validation, and made `add_slot` return a fresh list. Added regression tests and Unreleased changelog entries. The full test suite passes.\n\nChanged: `bookings/timeutil.py`, `bookings/billing.py`, `bookings/schedule.py`, `bookings/calendar_export.py`, `tests/test_regressions.py`, and `CHANGELOG.md`.', 'annotations': [], 'phase': 'final_answer'}]