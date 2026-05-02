---
name: recurring-segment
description: Define, manage, and populate the show's recurring named segments — beats like "Earnings Watch", "Founder of the Week", "Mailbag", or any custom segment that appears in most episodes. Adds richer per-segment configuration on top of the basic segments list in config/podcast.yaml — including which sources feed each segment, how many ammunition bullets to generate, and what the populate strategy is. Also runs the per-episode populate step that episode-program reads when slotting a recurring segment into a run-of-show. Run this skill when the user says "add a recurring segment", "define a new segment", "set up earnings watch", "populate the segments for EP043", "manage recurring segments", "list segments", "remove the founder segment", "configure my segments", or any equivalent ask about the show's named beats.
version: 0.1.0
---

## Purpose

The base `config/podcast.yaml` carries a flat list of segments with id, name, target seconds, and a one-line description. That is enough to slot a segment into a run-of-show but not enough to *populate* it automatically with this week's material.

This skill upgrades the segments block. Each segment gets a populate strategy: where the material comes from (topic-radar categories, specific RSS feeds, the earnings calendar, a Gmail label, or a custom prompt against the latest topic shortlist), how many ammunition bullets to generate, how many co-host questions to attach, and any voice modifier the segment uses (e.g., a "Mailbag" segment might want a less formal tone than the rest of the show).

The skill is also the runtime helper that `episode-program` calls when it slots a segment in. Given an episode number, it generates the segment's bullets and questions for that specific recording. If this skill has not been run, `episode-program` falls back to the segment's static description and produces generic ammunition — fine but flatter.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `action` | string | `list` | One of `add`, `update`, `remove`, `list`, `populate`. |
| `segment_id` | string | (required for add, update, remove, populate) | The id of the segment, e.g. `earnings-watch`. |
| `episode_number` | string | latest | Episode to populate when `action: populate`. Auto-detects the most recent in the editorial calendar. |
| `fields` | object | none | Field updates for `add` and `update`. Schema below. |

## Segment schema (extended)

The base schema in `config/podcast.yaml` carries `id`, `name`, `target_seconds`, `description`. This skill writes additional optional fields under each segment's `populate:` block.

| Field | Type | Notes |
|---|---|---|
| `populate.strategy` | enum | One of `topic-radar-category`, `rss-feed`, `earnings-calendar`, `gmail-label`, `custom-prompt`. Drives how material is sourced for the segment. |
| `populate.source` | string | The category, feed URL, label name, or prompt template that the strategy reads. |
| `populate.ammunition_count` | int | Default 3–5. How many bullets to generate per episode. |
| `populate.question_count` | int | Default 2. How many co-host follow-up questions to attach. |
| `populate.voice_modifier` | string | Optional override of voice rules for this segment, e.g. `looser` or `more-formal`. Applied only within the segment's bullets and questions. |
| `populate.lookback_days` | int | Default `topic_sources.default_lookback_days`. How far back the source is scanned. |

## Outputs

| Output | Path | Notes |
|---|---|---|
| Updated config | `config/podcast.yaml` | Modifies the `segments` block. Always preserves comments and ordering. |
| Populated segment file | `outbox/episodes/EP###/segments/<segment-id>.md` | Created by `populate` action. Contains the segment's bullets, questions, and source links for this episode. Read by `episode-program`. |
| Run summary | stdout | Per action. |

## Process

When this skill activates, follow these steps in order.

1. **Verify config exists.**
   - If `config/podcast.yaml` is missing, redirect to `podcast-init`.

2. **Dispatch on action.**

   **`add`**
   - Require `segment_id` and `fields` (at minimum `name`, `target_seconds`, `description`).
   - Walk an interactive prompt for the `populate` block: strategy, source, ammunition count, question count, optional voice modifier.
   - Validate: strategy is one of the enum values; source is consistent with strategy (URL for `rss-feed`, category name for `topic-radar-category`, etc.).
   - Append the new segment to `config/podcast.yaml` under `segments:`.
   - Print confirmation with the new segment's id and where it will sit in the segment order.

   **`update`**
   - Require `segment_id`. Load the existing segment.
   - Walk only the fields the user wants to change. Validate.
   - Write the updated segment back to `config/podcast.yaml`.

   **`remove`**
   - Require `segment_id`. Confirm with the user before deleting (unless `force: true`).
   - Remove the segment from the config.
   - Warn if any past episode's `run-of-show.md` references the segment — they continue to work because the historical files are static, but future runs of `episode-program` will not slot this segment.

   **`list`**
   - Print every segment with its id, name, target seconds, populate strategy, and populate source.
   - Mark which segments have a `populate` block configured and which only have the static description.

   **`populate`**
   - Require `segment_id` and `episode_number`.
   - Load the segment's `populate` block from config.
   - Source material per strategy:
     - `topic-radar-category`: load the most recent `outbox/topics/*.md` and pick items in the named category that did not make the main rundown.
     - `rss-feed`: fetch the configured feed and pull entries within `lookback_days`.
     - `earnings-calendar`: pull companies reporting in the lookback window from the configured earnings source.
     - `gmail-label`: pull recent items from the configured Gmail label (requires Gmail connector).
     - `custom-prompt`: run the prompt template against the latest topic shortlist and the show's audience description from config.
   - Generate ammunition bullets and co-host questions per the configured counts. Apply the voice modifier if set, then run the standard voice check (`style/voice.md` + per-show extensions, with the modifier as a soft override).
   - Cite each bullet with a source URL where the material came from a URL-bearing source. For `custom-prompt` strategies, citations are optional.
   - Write to `outbox/episodes/EP###/segments/<segment-id>.md`.
   - Print summary: segment id, source count, ammunition count, source URLs verified.

3. **For `populate`, signal `episode-program`.**
   - The `episode-program` skill reads `outbox/episodes/EP###/segments/*.md` when slotting recurring segments. If the file exists, it overrides the static description with the populated content. If not, it falls back to static.
   - This skill does not invoke `episode-program`; it just writes the artifact.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| Filesystem read/write | Load and edit `config/podcast.yaml`, write segment artifacts | Required |
| WebFetch | RSS feeds, earnings calendars, custom-prompt source URLs | Skip the source; segment artifact still written with whatever sources resolved. |
| Gmail | `gmail-label` strategy | Skip; segment artifact falls back to topic-radar material. |
| Filesystem read on `outbox/topics/` | `topic-radar-category` strategy | Required for that strategy; if no recent topic-radar output exists, fall back to RSS. |

## Examples

### Example 1: Add an "Earnings Watch" segment

User: *"add a recurring segment called Earnings Watch that pulls from the earnings calendar"*

```
Walking the new segment:
  id: earnings-watch
  name: Earnings Watch
  target_seconds: 480 (8 minutes)
  description: One earnings report, public-perception lens.
  populate.strategy: earnings-calendar
  populate.source: https://www.investing.com/earnings-calendar/
  populate.ammunition_count: 5
  populate.question_count: 2
  populate.voice_modifier: (none)
  populate.lookback_days: 7

Segment added to config/podcast.yaml after "cold-open", before "founder-of-the-week".
Run "recurring-segment populate earnings-watch EP043" to test.
```

### Example 2: Populate for a specific episode

User: *"populate earnings watch for EP043"*

```
Segment: earnings-watch (Earnings Watch, 8 min)
Strategy: earnings-calendar, lookback 7 days.
Companies pulled: 12. Selected: 1 (Spotify Q1 — most cited in topic-radar).
Ammunition bullets: 5 (all sourced).
Co-host questions: 2.
Voice check: clean.

Written to outbox/episodes/EP043/segments/earnings-watch.md.
episode-program will pick this up when slotting the segment.
```

### Example 3: Add a custom-prompt segment

User: *"add a Mailbag segment that pulls from listener questions in our Gmail"*

Skill walks the user through `gmail-label` strategy, asks for the label name, and confirms the segment is added. Notes that the Gmail connector must be wired to populate the segment automatically; without it, the segment falls back to the static description and the host fills it in manually.

### Example 4: List

User: *"list the recurring segments"*

```
Configured recurring segments:
  cold-open               60s   (no populate block — static description only)
  earnings-watch         480s   populate: earnings-calendar, ammo 5, questions 2
  founder-of-the-week    360s   populate: topic-radar-category=founders, ammo 4, questions 2
  closing-cta             45s   (no populate block)

4 segments configured. 2 have populate blocks.
```
