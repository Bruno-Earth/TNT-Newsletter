# T&T Capital — Collector Setup, Shared Format & Merge Guide

Version: 1.0 | Updated: 2026-08-28

## What this package does

Three manually triggered collectors gather source material for T&T research and Weekend T&T. They do not write the newsletter or make investment judgments. These are instruction documents, not installed agents, a scheduler, or a tested live data pipeline.

| Collector | Instruction file | Output within a run |
| --- | --- | --- |
| VN — Vietnam Public Markets & Economy | `tnt_vietnam_public_market_data_collector.md` | `vietnam_source_inbox.md` |
| US — U.S. Public Markets | `tnt_us_public_market_data_collector.md` | `us_source_inbox.md` |
| MACRO — Global Macro & Policy | `tnt_global_macro_data_collector.md` | `global_macro_source_inbox.md` |

Each collector file contains the same execution/evidence/output contract plus its own remit. It can be used independently; this guide is for the person or parent workflow coordinating the three. Update the shared contract consistently if you later change it. No fourth collector is included.

## Start manually

1. Use a research-capable environment with web search/source reading and, preferably, file writing. Attach or load the relevant instruction file for each agent or session. A Markdown file alone cannot grant tools or start a process.
2. Give all three the same explicit collection interval, timezone, and run ID. They can run independently and write separate files. Start with 20 items maximum per collector, fewer when warranted. Do not load the other collectors' full instructions into each one's context unnecessarily.
3. Inspect each run status and coverage table before merging. Missing access, unread sources, or a failed collector must remain visible.
4. Merge only after the available collectors finish. You can perform this step manually or give the merge instructions below to the parent assistant. It is not another autonomous collector.
5. Review the combined inbox. Analysis, editorial selection, drafting, and publication are separate future steps with human review.

Use this prompt after loading the selected collector file. Replace all bracketed fields before running:

```text
Run the attached T&T [VN / US / MACRO] collector instructions.
Start: [ISO timestamp with offset, inclusive]
End: [ISO timestamp with offset, exclusive]
Timezone: Asia/Ho_Chi_Minh
Run ID: [one unique label shared by all three collectors]
Max items: 20
Previous inbox: [path or None]
Search both collection streams. Save only this collector's own inbox.
Report access and coverage gaps, and stop after collection.
Do not write the newsletter or conduct investment analysis.
```

If no dates are supplied, a collector defaults to the preceding seven days through trigger time, but explicit shared dates prevent slightly different windows across independent runs. Start/end select publication time; the record separately retains the underlying event date or reporting period. The default language is concise English, with original source titles preserved.

## Ownership decisions

| Underlying event | Owner | Treatment |
| --- | --- | --- |
| Vietnam GDP, CPI, domestic rate/credit decision, or Vietnam-only macro report | VN | Keep domestic macro with the existing collector |
| U.S. earnings/filings, ETF, equity-market, or corporate-credit event | US | Vietnam relevance optional; include U.S.-listed foreign issuers, except VN-listed overlap owned by VN |
| U.S. CPI/payrolls, Fed decision, Treasury yields/auction | MACRO | U.S. macro belongs with global macro |
| Foreign tariff naming Vietnam | MACRO | Direct Vietnam tag; no duplicate VN entry for the same announcement |
| Vietnamese government or company response to that tariff | VN | Separate, sourced follow-up; link the international event |
| Global commodity supply disruption or benchmark release | MACRO | Corporate earnings in that sector remain with the relevant company collector |
| Stock-market reaction reported separately from a policy announcement | US or VN | Keep only substantive new observations; link the policy event without inventing causation |
| Multi-country report containing a Vietnam section | MACRO | Keep one report record; a genuinely separate Vietnam-only release belongs to VN |
| Japanese/European company earnings without U.S. listing or a distinct covered event | Unassigned | Record a handoff/gap; global macro is not a catch-all company collector |

When ownership is unclear, use the main factual event and its originating release, not the media outlet's location. Keep distinct events separate even when one article covers several; split only when each event has independent material facts and a clear owner. Scope handoffs do not mean another agent actually processed the item.

## Shared record and evidence contract

All three collector files carry an identical record template. Required fields are: ID; event key; owner; source/language; direct URL; publication date/time; event date/reporting period; geography; category; verified tickers or N/A; source tier; verification label; evidence checked; Vietnam relevance; relevance score; related/supporting references; and a maximum two-sentence factual description.

Use **Primary checked**, **Secondary checked**, **Discovery only**, or **Unverified claim**, never a vague blanket “Confirmed.” Primary and secondary checked entries belong in the main streams. Discovery-only and unverified entries remain in a separate leads section. A publisher's reputation, a copied URL, or repeated syndicated stories cannot substitute for reading the evidence.

Use **Direct**, **Potential**, or **Not identified** for Vietnam relevance. A Potential basis must start `Inference:` and stay brief. It is a routing aid, not an investment conclusion. U.S./global scores prioritize their own remits; absence of a Vietnam connection must not lower eligibility.

Tier and verification are separate: a primary source can be discovered but unread, while a media article can be read without the original filing being checked. Correctly attribute company assertions, forecasts, allegations, and proposed policies. Keep source figures in their published units and distinguish revised data from the original vintage.

## Merge instructions — one coordination step

**Inputs:** The three inboxes for the same run, any prior combined inbox supplied for comparison, and explicit collector statuses. Do not browse for fresh news or start another collection run during merging.

**Output:** `runs/<run_id>/source_inbox.md`. Keep every original collector inbox unchanged. If that output already exists, ask before replacing it or create a new revision filename; do not overwrite history silently.

1. **Validate inputs.** Check run ID, timezone, interval, required fields, evidence labels, and scope. Do not silently combine mismatched windows. If an inbox is missing or blocked, merge only the available material and mark the result Partial. A failed input is not an empty-news result.
2. **Find duplicate events.** Compare event keys and normalized URLs, then entity/dataset, event type, period/date, and substantive facts. Remove tracking parameters only; preserve meaningful document/version parameters. URL matches alone are insufficient: one page may host multiple releases. Similar headlines alone are also insufficient.
3. **Select the canonical record.** Prefer evidence actually checked, then the strongest original source for the specific claim. Do not replace a checked secondary record with an unread primary link. Keep secondary/primary supporting links and original IDs as aliases. Preserve unresolved contradictions visibly; do not silently settle them.
4. **Preserve meaningful updates.** Link corrections, revisions, later filings, and separately observed market responses. Do not collapse different data vintages or reporting periods. A summary article adding no new evidence is a duplicate, not an update.
5. **Assign one owner.** Apply the ownership table; retain contributing collector IDs as provenance. Place each item in one stream only: original data/report releases in A, substantive event reporting in B. Do not duplicate an item across streams or countries.
6. **Keep uncertain material separate.** Preserve Leads / Unverified and Handoffs without promoting their status. Resolve references to canonical IDs when possible; leave unknown IDs unresolved rather than inventing matches. Log unresolved handoffs as gaps.
7. **Retain qualified records without imposing another quota.** Sort within each owner group by relevance and recency. Do not add the three scores or compare them as precise numerical measurements. The merger organizes collection; it does not make an editorial selection or discard an entire market to create a short newsletter.
8. **Report the result.** Include input files/statuses, collection period, total retained counts by owner/stream, duplicate count, partial coverage, missing sources, unresolved conflicts, and handoffs. Stop without analysis or newsletter text.

Suggested combined headings:

```markdown
# T&T Combined Source Inbox
Run ID:
Period / timezone:
Input statuses:
Merge status: Complete / Partial / Blocked

## Stream A — Data / Reports
### Vietnam
### U.S. Public Markets
### Global Macro

## Stream B — News / Events
### Vietnam
### U.S. Public Markets
### Global Macro

## Leads / Unverified
## Handoffs and unresolved routing
## Coverage, gaps, and duplicate counts
```

Place retained item headings one level below each owner subsection. Add `Contributors / original IDs` to merged records. If no usable input is available, report Blocked, not Complete.

## Changes from the original Vietnam instructions

- Preserved Vietnam macro, market data, company financial releases, the two collection streams, manual triggering, and the collection-only boundary.
- Moved standalone global/commodity collection into MACRO and U.S. market events into US; added explicit handoffs so discoveries are not silently lost.
- Replaced the shared output filename with separate per-collector files and an explicit merge step.
- Replaced binary Confirmed/Unverified with evidence-access labels; added date/period precision, coverage gaps, Vietnam tags, and event deduplication.
- Kept public signal discovery optional. Private broker-room access is not assumed; potentially confidential information stays outside the shared inbox for human review.

## First-run acceptance check

After a real manual run, check that Vietnam macro stayed in VN, U.S. macro stayed in MACRO, repeated events merged, U.S. collection extended beyond mega-cap technology, and global coverage included non-U.S. sources. Spot-check retained descriptions against their actual URLs and verify that unread snippets were not promoted. Review access failures and adjust source choices or limits before adding another collector.

Source entry points are suggestions, not proof of a working connection or complete coverage. Availability must be checked on each run. This package has not itself collected live news or validated a deployed agent runtime.
