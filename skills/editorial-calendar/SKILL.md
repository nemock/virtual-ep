---
name: editorial-calendar
description: Maintain the show's editorial calendar in the configured Google Sheet (or local CSV fallback) and sync recording and publish dates to the configured Google Calendar so the co-host sees the schedule. Supports adding new episodes, updating status and metadata (recorded, edited, published, downloads, top clip), querying single episodes, and a "what's on deck" report that lists upcoming episodes and what's missing for each. Run this skill when the user says "update the editorial calendar", "what's on deck", "next episode status", "mark EP042 as published", "schedule EP043 recording", "what's missing for EP043", "sync the calendar", "add EP043 to the calendar", or any equivalent ask about episode status, scheduling, or the calendar pipeline. The default action with no arguments is the next-episode report.
version: 0.1.0
---

## Purpose

The editorial calendar is the production pipeline view. It says what is recorded, what is edited, what is published, and what is on deck. It also carries the post-show numbers — runtime, downloads, top-performing clip — so the host can see episode-over-episode performance in one row.

The Google Sheet is the source of truth when connected. A local CSV at `outbox/editorial-calendar.csv` is the fallback. Either way the schema is identical so a host can switch between them later without losing data.

This skill also writes recording and publish dates to the configured Google Calendar so the co-host can see the schedule from their own calendar app without having to open a sheet.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `action` | string | `next` | One of `add`, `update`, `get`, `list`, `next`, `sync-calendar`. |
| `episode_number` | string | (required for add, update, get) | Episode identifier (`EP042`). |
| `fields` | object | none | Map of field updates for `update` action. Examples: `{"status": "published", "actual_publish_date": "2026-05-01", "runtime_minutes": 47}`. |
| `lookahead_episodes` | int | 3 | For `next` and `list` actions. How many upcoming episodes to include. |

## Schema

Every row in the calendar carries these fields. Order matters when writing the CSV.

| Field | Type | Notes |
|---|---|---|
| episode_number | string | `EP042` |
| working_title | string | From episode-program output |
| status | enum | `idea`, `scheduled`, `recorded`, `edited`, `published` |
| topics | string | Comma-separated topic IDs or short titles |
| segments | string | Comma-separated segment IDs run this episode |
| target_publish_date | date | YYYY-MM-DD |
| recording_date | date | YYYY-MM-DD |
| actual_publish_date | date | YYYY-MM-DD |
| runtime_minutes | int | from show-notes |
| downloads | int | from `post-show-debrief` analytics pull |
| views | int | from YouTube Studio pull |
| top_clip_id | string | from clip-finder + post-show-debrief |
| notes | string | freeform |

## Outputs

| Output | Path | Notes |
|---|---|---|
| Updated row | Google Sheet (`output_targets.google_sheets.editorial_calendar_id`) | Or `outbox/editorial-calendar.csv` if Sheets unavailable. |
| Calendar events | Google Calendar (`output_targets.google_calendar.calendar_id`) | Recording event + publish event per episode. Created/updated by `add`, `update`, and `sync-calendar` actions. |
| Status report | stdout | Printed for `next`, `list`, and `get` actions. |

## Process

1. **Verify config exists.**
   - If `config/podcast.yaml` is missing, redirect to `podcast-init`.

2. **Resolve the calendar backend.**
   - If `output_targets.google_sheets.editorial_calendar_id` is set and the Sheets connector is available, use Sheets.
   - Otherwise fall back to `outbox/editorial-calendar.csv`. Create it with headers if missing.

3. **Dispatch on action.**

   **`add`**
   - Require `episode_number`. Optional `fields` for any non-default values.
   - Default new row: `status: scheduled` if a `recording_date` is provided, otherwise `status: idea`.
   - Pull `working_title`, `topics`, `segments` from `outbox/episodes/EP###/run-of-show.md` if present.
   - Write the row to the backend.
   - If `recording_date` or `target_publish_date` is set and Google Calendar is connected, create or update the calendar events.

   **`update`**
   - Require `episode_number` and `fields`.
   - Validate field names against the schema. Reject unknown fields.
   - Apply updates. Status transitions are not enforced — the host may move backward (e.g., `published` → `edited`) if a re-edit is needed.
   - If a date field changes, update the corresponding Google Calendar event.

   **`get`**
   - Return the row for the given `episode_number` as a structured printout. Note any missing required fields.

   **`list`**
   - Return all rows from the backend. Include status counts at the top.

   **`next`** (default)
   - Find the next episode that is not yet `published`, sorted by `target_publish_date` then `recording_date` then `episode_number`.
   - Report:
     - Episode number, working title, status.
     - Days until target publish (or days overdue).
     - Checklist of expected artifacts and which ones exist:
       - `run-of-show.md` (required for `scheduled` and beyond)
       - `briefs/topic-N.md` for each topic on the rundown (required for `scheduled` and beyond)
       - `cohost-brief.md` (required for `scheduled` and beyond)
       - Recording event on Google Calendar (required for `scheduled` and beyond)
       - `transcript-clean.md` (required for `recorded` and beyond)
       - `show-notes.md` (required for `edited` and beyond)
       - `clips.md` and `clips.json` (required for `edited` and beyond)
       - `distribution.md` or scheduled Blotato posts (required for `published`)
     - For each missing artifact, the suggested skill to run.
   - Then list the next `lookahead_episodes - 1` upcoming episodes with their status.

   **`sync-calendar`**
   - For every row with `status` in `scheduled` or beyond, ensure the recording event and publish event exist on the configured Google Calendar.
   - Title format: `Record EP042 — <Working Title>` and `Publish EP042 — <Working Title>`.
   - Add the co-host (`cohost.email`) as an attendee on the recording event.
   - Skip if Google Calendar connector is unavailable; note in the run summary.

4. **Voice check on `notes` content the skill writes.**
   - Auto-generated notes (e.g., "Backfilled from EP-folder artifacts") pass `style/voice.md` rules. Host-entered notes are not rewritten.

5. **Print summary.**
   - Action performed, rows changed, calendar events created or updated, fallback path if Sheets/Calendar were unavailable.
   - For `next`, print the on-deck report directly to stdout in scannable form.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| Google Sheets | Read and write rows | `outbox/editorial-calendar.csv` |
| Google Calendar | Create and update recording / publish events | Print event details to stdout, skip creation |
| Filesystem read | Detect existing artifacts in `outbox/episodes/EP###/` for the on-deck checklist | Required |

## Examples

### Example 1: Default — what's on deck

User: *"what's on deck"*

```
EP043 — "When does an open-source model become a moat?" — status: scheduled
Target publish: 2026-05-08 (in 7 days). Recording: 2026-05-05.

Artifact checklist:
  ✓ run-of-show.md
  ✓ briefs/topic-1.md
  ✗ briefs/topic-2.md         → run: research-brief T-20260501-04
  ✗ cohost-brief.md           → run: cohost-brief EP043
  ✓ Calendar event (recording)
  — transcript-clean.md       (required after recording)
  — show-notes.md             (required after editing)
  — clips.md / clips.json     (required after editing)
  — distribution.md           (required at publish)

Upcoming:
  EP044 — "..." — idea — target 2026-05-15
  EP045 — "..." — idea — target 2026-05-22
```

### Example 2: Mark an episode published

User: *"mark EP042 as published, runtime 47 minutes, 2,318 downloads first week"*

Skill updates the EP042 row: `status: published`, `actual_publish_date: <today>`, `runtime_minutes: 47`, `downloads: 2318`. Updates the publish event on the calendar to past. Run summary confirms the changes and reminds the host to run `post-show-debrief EP042` for the loop closure.

### Example 3: Add an episode in idea state

User: *"add EP044 to the calendar, target publish May 15, three topics from the radar, no recording date yet"*

Skill creates a row with `status: idea`, `target_publish_date: 2026-05-15`, the three topic IDs in the `topics` field. No calendar event is created since there's no recording date yet. Notes that recording date should be set before `episode-program` is run.

### Example 4: Sync after manual edits

User: *"sync the calendar, I edited some dates manually"*

Skill walks every row, ensures the corresponding Google Calendar events match. Updates the events that drifted, creates missing ones, and reports any rows that fall outside the configured calendar's allowed range.
