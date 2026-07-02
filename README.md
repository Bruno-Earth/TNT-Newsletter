# TNT Capital Vietnam Market Newsletter Agent Setup

This starter setup defines the manual draft generator workflow for a bilingual TNT Capital newsletter covering Vietnamese stock markets, market-moving news, and selected macro context.

## Current Decision

- Workflow mode: manual draft generator first
- Publishing status: draft-only, no automatic sending
- Review destination: Google Drive for work
- Brand name: TNT Capital
- Old brand name: Thebes Capital should not appear in final newsletter copy
- Typography: Rockwell for display headings, with Georgia and Times New Roman fallbacks
- Primary palette from supplied assets:
  - Deep green: `#07300e`
  - Pale mint: `#f5fff9`
  - White: `#ffffff`
  - Accent mint: `#74f1be`
  - Accent lavender: `#b7b4f0`
  - Accent muted violet: `#6e5c7b`

## Recommended Daily Timing

- Vietnamese draft: 7:30 AM Vietnam time
- English draft: 7:30 AM Boston time, aimed at overseas and global readers interested in Vietnam

## Review Folder

Recommended Google Drive structure:

```text
TNT Capital/
  Newsletter Drafts/
    YYYY-MM-DD - Vietnam Market Brief/
      VN - Vietnam Market Brief.html
      EN - Vietnam Market Brief.html
      VN - Vietnam Market Brief.pdf
      EN - Vietnam Market Brief.pdf
      sources.md
      quality-check.md
      assets/
```

For phase 1, generate files locally and upload or sync them to Google Drive manually. After the format is proven, connect Google Drive for Desktop or the Google Drive API.

## Agent Roles

1. Source & Data Agent
2. Analysis Agent
3. Newsletter Production Agent
4. Review & Compliance Agent

Each role has its own instruction file in `agents/`.

## Daily Output Standard

Every completed package must include:

- Vietnamese HTML email draft
- English HTML email draft
- Vietnamese PDF
- English PDF
- Source list with URLs and access times
- Quality and compliance checklist
- Any charts or images used

## Non-Negotiable Editorial Rules

- No buy, sell, hold, target price, or personalized investment recommendation.
- Market views are allowed when framed as scenarios, risks, and possible direction.
- Every factual claim must be source-backed.
- Use TNT Capital only as the brand name.
- Always include the disclaimer in PDFs and preferably in email footer drafts.

