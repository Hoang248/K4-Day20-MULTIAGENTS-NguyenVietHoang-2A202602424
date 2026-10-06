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
