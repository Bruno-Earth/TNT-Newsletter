# Manual Data Collection Runbook

This runbook coordinates the three collection subagents. The process ends when the collector inboxes are saved and checked. It does not continue into analysis or newsletter production.

## 1. Resolve Run Parameters

Confirm or derive:

- `start` and `end` for the half-open interval `[start, end)`
- `timezone`, defaulting to `Asia/Ho_Chi_Minh`
- one shared `run_id`
- optional `max_items`, defaulting to 20 per collector
- any previous inboxes needed for duplicate detection

If both dates are omitted, each collector uses the preceding seven days ending at trigger time. If only one date is supplied or the interval is invalid, ask the user before collecting.

## 2. Run The Collectors

Run only the collectors requested by the user. When all three are requested, they may run independently with the same parameters and shared run ID.

| Collector | Instruction | Required output |
| --- | --- | --- |
| `VN` | [`tnt_vietnam_public_market_data_collector.md`](tnt_vietnam_public_market_data_collector.md) | `runs/<run_id>/vietnam_source_inbox.md` |
| `US` | [`tnt_us_public_market_data_collector.md`](tnt_us_public_market_data_collector.md) | `runs/<run_id>/us_source_inbox.md` |
| `MACRO` | [`tnt_global_macro_data_collector.md`](tnt_global_macro_data_collector.md) | `runs/<run_id>/global_macro_source_inbox.md` |

Each collector writes only its own inbox. Do not overwrite an existing inbox without the user's decision.

## 3. Check Boundaries And Duplicates

Before accepting the run:

- Confirm each retained item belongs to the collector that wrote it.
- Confirm cross-scope items appear as short handoffs rather than duplicate summaries.
- Confirm duplicate events within and across previous inboxes were removed or linked as material updates.
- Confirm Primary checked and Secondary checked items are in the main streams.
- Confirm Discovery only and Unverified claim items are in Leads / Unverified.
- Confirm each inbox states its period, timezone, collected-at time, run status, coverage gaps, and item counts.

If an event is ambiguous, use `Unassigned` and flag it for human review instead of forcing ownership.

## 4. Stop At Collection

A collection run is complete when the requested inbox files exist and pass the checks above. Do not create a combined inbox unless the user explicitly requests one. Do not interpret the collected facts, develop investment theses, draft newsletter sections, create publication assets, or distribute content.

Any later analysis or newsletter phase requires a separate user decision and a separate set of instructions.
