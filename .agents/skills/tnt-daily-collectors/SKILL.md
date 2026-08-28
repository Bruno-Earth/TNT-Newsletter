---
name: tnt-daily-collectors
description: Manually run the T&T VN, US, and global macro collectors, merge and validate their source inboxes, and save one dated run to the configured private Google Drive folder. Use only when explicitly invoked for a current or demo collection run; never schedule it or continue into analysis or newsletter creation.
---

# Run T&T Daily Collectors

An explicit invocation authorizes one current collection, merge, validation, and
save operation in the configured Drive destination. It does not authorize a
schedule, sharing change, analysis, newsletter writing, publication, or trading.

## Load The Repository Workflow

Locate the repository root, then read and follow these files in order:

1. [`AGENTS.md`](../../../AGENTS.md)
2. [`README.md`](../../../README.md)
3. [`runbook.md`](../../../runbook.md)
4. [`tnt_collectors_shared_guide.md`](../../../tnt_collectors_shared_guide.md)
5. The three collector instruction files referenced by the runbook

These files own collection scope, evidence rules, merge behavior, validation,
Drive saving, and failure handling. Do not replace them with abbreviated rules
from this skill.

## Resolve The Daily Window

Use an interval explicitly supplied by the user. Otherwise:

1. Set `end` to the current trigger time with an explicit timezone offset.
2. Inspect the configured Drive destination for the latest successfully saved
   run. Verify its `run.json`, `validation.json`, and `save_receipt.json`; do not
   infer success from a folder name alone.
3. If a valid prior run exists, set `start` to that run's exact `end`. This
   avoids routine gaps and seven-day overlap.
4. If no valid prior run exists, use the preceding seven days as the bootstrap
   interval.
5. Use `Asia/Ho_Chi_Minh` unless the user specifies another timezone. Give all
   collectors the same resolved interval and run ID.

If the latest run is ambiguous, its receipt is partial, its end is later than
the current trigger, or the resulting interval is invalid, stop and ask for the
window. Never guess across a possible collection gap.

## Run Once

1. Complete the Drive access and privacy preflight in the runbook. Codex uses
   the user's connected Google account and needs no separate share invitation.
   Do not change folder permissions.
2. Initialize one run with explicit `start` and `end` values.
3. Run VN, US, and MACRO collectors using their authoritative instruction files.
4. Merge semantically, preserve evidence limitations, and account for every
   original item ID.
5. Validate with `scripts/tnt_run.py` and correct only structural problems that
   the evidence supports.
6. Save the requested artifacts to one new date-sortable run folder in the
   configured Drive destination, verify every write by metadata readback, and
   preserve all prior runs.
7. Return the verified Google Docs inbox link, run-folder link, interval,
   retained counts, duplicates removed, coverage gaps, and save failures.
8. Stop.

If Drive access, privacy, collection, validation, or saving is blocked, preserve
completed work, report the exact state, and do not present a partial result as a
successful daily run.
