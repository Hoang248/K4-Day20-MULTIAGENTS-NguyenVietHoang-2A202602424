---
name: log-triage-json
description: Use when parsing application logs into structured JSON error records with normalized timestamps and service names.
---
1. Inspect the log format and identify entry lines, continuation lines, and repeat-count lines before parsing.
2. Parse timestamps and normalize them to UTC.
3. Normalize service names to lowercase and replace hyphens with underscores.
4. Attach continuation text, including terminal exception lines, to the preceding entry rather than rejecting it as an unknown line.
5. Apply repeat counts to the preceding entry and preserve the resulting count in the structured record.
6. Select the error levels required by the output specification.
7. Sort `errors` by service and then by `timestamp_utc`, both ascending.
8. Set the top-level `schema_version` to `2` and `generated_by` to `log-triage`.
9. Validate that the output parses as JSON and that its required keys, normalized values, and ordering are correct.
