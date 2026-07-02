# Manual Draft Generator Specification

## Purpose

The manual draft generator creates the full newsletter review package on demand. It does not send emails, publish posts, or upload files automatically during phase 1.

## Inputs

- Approved source list
- Any additional user-provided sources
- Daily market data
- Daily news links
- TNT Capital brand assets
- Newsletter date
- Target languages: Vietnamese and English

## Outputs

```text
YYYY-MM-DD - Vietnam Market Brief/
  VN - Vietnam Market Brief.html
  EN - Vietnam Market Brief.html
  VN - Vietnam Market Brief.pdf
  EN - Vietnam Market Brief.pdf
  sources.md
  quality-check.md
  assets/
```

## Phase 1 Execution

1. Source & Data Agent prepares the source pack.
2. Analysis Agent ranks what matters and drafts the market view.
3. Newsletter Production Agent writes and formats the bilingual drafts.
4. Review & Compliance Agent checks factual support, tone, and no-recommendation rules.
5. User reviews the package in Google Drive.

## Later Automation

After approval of format and sources:

- Schedule Vietnamese draft for 7:30 AM Vietnam time.
- Schedule English draft for 7:30 AM Boston time.
- Sync or upload to Google Drive.
- Optionally create email-platform drafts after manual approval.

