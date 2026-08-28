# Manual Collection, Merge & Google Drive Runbook

One user request starts collection, merging, and saving. The user does not need
to prompt the stages separately. Nothing runs on a schedule. No Google Sheet,
review-status tracker, investment analysis, or newsletter writing is included.

## 1. Check the destination before collecting

Read the local `storage_config.json`. If it is missing, use the user's supplied
folder URL with `python scripts/tnt_run.py configure --folder-url "FOLDER_URL"`.
If no URL was supplied, ask for it. This saves the destination locally without
granting access. Use the configured ID, not a folder-name search, when saving.

- Confirm that this Codex environment exposes authenticated Google Drive
  folder creation, file upload/import, and metadata read tools. Use the Google
  Drive plugin/skills where available. If tools are missing, stop and explain
  that this environment needs its own Google connection. Do not invent a tool
  name, request pasted credentials, or assume another ChatGPT session's access.
- Read destination metadata and confirm it is the expected folder. A successful
  read is not proof of write access.
- Sharing status is not a collection blocker. Do not inspect, change, add, or
  remove Drive permissions as part of this workflow.
- If a saving dependency is blocked, stop before collection and explain what is
  unavailable. Do not spend a full collection run expecting an unconfigured
  upload to work.

## 2. Initialize one shared run

From the repository directory:

```bash
python scripts/tnt_run.py init
```

This creates a unique `runs/<run_id>/run.json`. Defaults are all three
collectors, the past seven days, Asia/Ho_Chi_Minh, and up to 20 items per
collector. It also records `drive_week`, the Monday-to-Sunday date range and
exact Drive folder name for the run's end date. It makes no network calls and
does not start collection.

For an explicit period, use:

```bash
python scripts/tnt_run.py init --start 2026-08-21T00:00:00+07:00 --end 2026-08-28T00:00:00+07:00
```

The dates above are an example, not a permanent collection period. Options also
include `--timezone`, `--run-id`, `--max-items`, and `--collectors VN US MACRO`.
Both dates must be provided or neither. Existing runs are never overwritten by
initialization. On Windows, install `tzdata` if the helper reports missing time
zone data. Python 3.10 or later is required.

Pass the exact values in `run.json` to each requested collector. This avoids
three different interpretations of “the last seven days.”

## 3. Collect into separate local files

| Collector | Instruction | Output under the run folder |
| --- | --- | --- |
| VN | `tnt_vietnam_public_market_data_collector.md` | `vietnam_source_inbox.md` |
| US | `tnt_us_public_market_data_collector.md` | `us_source_inbox.md` |
| MACRO | `tnt_global_macro_data_collector.md` | `global_macro_source_inbox.md` |

Each collector performs its own filtering and evidence checks. It saves only its
own inbox and stops. The main coordinator continues the remaining steps. When
subagents are unavailable, run scopes sequentially and disclose that execution
mode. A failed collector must be marked Missing or produce a Blocked inbox;
never substitute invented records or silently call it Complete.

Use this header, replacing placeholders with actual values copied from
`run.json`. `Collected` is the actual collection timestamp with an offset:

```text
# [Collector title]
Collector ID: [VN / US / MACRO]
Instruction version: [version from the assigned collector file]
Run ID: [run_id]
Start: [start]
End: [end]
Timezone: [timezone]
Collected: [ISO timestamp with offset]
Run status: [Complete / Partial / Blocked]
```

Use these exact level-two headings: `Stream A — Data / Reports`,
`Stream B — News / Events`, `Leads / Unverified`, `Handoffs`, and
`Coverage and gaps`. Collector entries use level-three headings and the fields
in their existing template. Keep every field value on its own labeled line;
`Description` contains at most two short sentences. Do not wrap the completed
inbox in a code fence. Empty sections state that nothing was found or explain
the gap. Date uncertainty and evidence labels remain governed by the collector file.

## 4. Merge automatically within the same Codex task

The main coordinator follows `tnt_collectors_shared_guide.md`, then writes
`source_inbox.md`. This is semantic event deduplication by the coordinator;
the Python helper does not perform research or decide that two events match.

- Preserve distinct releases, material updates, evidence limitations, and all
  unresolved conflicts. Keep original collector files unchanged.
- Use the same header fields, omit `Collector ID` and `Instruction version`, add
  `Collector instruction versions: VN=<version>; US=<version>; MACRO=<version>`
  for the requested collectors, and use `Merge status` instead of `Run status`.
  Use the same five level-two section names as above.
- In each item section, level-three headings identify Vietnam, U.S. Public
  Markets, or Global Macro. Level-four headings identify the merged records.
- Keep an original item's ID as the canonical record ID. Add
  `Contributors / original IDs: ID1, ID2` to every merged item, including its own
  canonical ID. Every input item must appear exactly once in this mapping.
  This makes dropped items and duplicate merges detectable.
- Status is Complete only when all requested inputs are Complete; Partial if
  some are missing, blocked, or partial; Blocked if every input is missing or
  blocked. Do not merge mismatched time intervals.

## 5. Validate and prepare NotebookLM links

```bash
python scripts/tnt_run.py validate --run-id YOUR_RUN_ID
```

The helper checks headers, required fields, evidence sections, item limits,
original-ID accounting, and input/merge statuses. It rejects verification
upgrades unsupported by the input records. It does not fact-check descriptions
or prove that two stories are the same event.

On success it writes `validation.json` and `notebooklm_sources.txt`. The latter
contains unique source URLs from checked main-stream records only. It does not
import sources into NotebookLM, retrieve linked content, or bypass paywalls.
If the combined run is Blocked, report the problem and do not upload it as a
successful collection.

## 6. Save with the authenticated Google Drive tools

Recheck the configured destination. Then:

1. Read `drive_week.name` from `run.json`. It is a Monday-to-Sunday label such
   as `Week 2026-08-24 to 2026-08-30`, calculated in the run timezone.
2. Search for an exact-name child folder directly under the configured T&T
   Newsletter folder ID. If none exists, create it. If exactly one exists,
   reuse it. If multiple exact matches exist, stop and report the ambiguity.
   Never create a second folder for the same week.
3. Upload each existing collector inbox, `source_inbox.md`, `run.json`,
   `validation.json`, and `notebooklm_sources.txt` directly into that weekly
   folder. Use the Drive filename `<run_id> - <local filename>` so later runs in
   the same week do not overwrite or duplicate the current run's artifacts.
   Do not upload credentials, unrelated local files, or raw private signals.
4. Create a simple native Google Docs reading copy of the merged inbox named
   `T&T Source Inbox - <run_id>` in the same folder. Preserve the source links,
   record metadata, descriptions, uncertainty, and grouping. Follow the Google
   Docs authoring/import skill when available; do not invent an unsupported
   conversion. This is a readable copy of the source list, not an article or
   investment report. The Markdown remains the canonical archive.
5. Read metadata back for every written item, checking its actual parent ID,
   name, and MIME type. Keep the URLs and IDs returned by completed operations.
   Never derive or invent a Google Docs URL from an expected title.
6. Save a local `save_receipt.json` containing the run ID, weekly-folder name,
   weekly-folder ID/URL,
   each uploaded item's local filename and returned ID/URL, the reading-copy
   ID/URL, and `Saved` or `Partial` with any errors. Upload this receipt last
   and verify it too. Upload it as `<run_id> - save_receipt.json`. It must
   contain no tokens or account credentials.

If an operation fails or times out, preserve successful uploads and record
what remains. Do not report Saved, restart the entire upload, or create another
weekly folder blindly. On retry, reconcile the destination and existing IDs first;
if content differs, ask before replacing it or use a new run/revision. If only
the reading copy fails, provide the verified Markdown link and explain that
the Google Docs copy is missing.

Original reports may be stored in a `reports` subfolder when actually downloaded
and permitted, but do not download every linked article just to fill that folder.

## 7. Return the result and stop

Return the verified **Google Docs inbox link** and **weekly-folder link**, the
collection period, retained counts, and any missing coverage or save failures.
The user can read the inbox without marking statuses or using a spreadsheet.

Do not automatically create/populate NotebookLM notebooks, draft a newsletter,
publish, analyze investments, or schedule another run. The prepared URL list is
available for the next NotebookLM step. Tool access and source import remain
separate from saving files to Drive.
