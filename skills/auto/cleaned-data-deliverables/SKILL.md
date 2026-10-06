---
name: cleaned-data-deliverables
description: Use when transforming a tabular file into a cleaned CSV and a JSON summary with deduplication, normalized dates, or monetary values.
---
1. Read the data dictionary and inspect the input rows before choosing parsing and deduplication rules.
2. Count all input data rows, including duplicates, and count distinct records with a known amount separately.
3. Deduplicate by the documented identifier and exclude records whose amount is marked unknown.
4. Normalize dates to UTC and emit timestamps in `YYYY-MM-DDTHH:MM:SSZ` format.
5. Normalize region labels to their canonical spelling.
6. Write `workspace/clean.csv` with the header `order_id,timestamp_utc,region,amount_cents` and one row per distinct record with a known amount.
7. Represent monetary values as integer cents in both deliverables.
8. Write `workspace/answer.json` with a `meta` object containing `source`, `rows_in`, and `rows_used`.
9. Validate that the JSON parses and the CSV header, row count, timestamps, and monetary values match the required schema.
