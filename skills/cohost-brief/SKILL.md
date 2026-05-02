---
name: cohost-brief
description: Build a separate prep document for the remote co-host of an upcoming episode. Reads the run-of-show and any research briefs in the episode folder, then drafts a co-host-facing artifact in the right framing — cold-open setup line, segment-by-segment "throw" lines that hand off to the host, two to four follow-up questions per segment, articles and links the co-host should have queued, pacing notes (when to interject, when to let the host run uninterrupted), and recurring segment cues. Outputs both a local markdown file and a shareable Google Doc when Drive is connected. Run this skill when the user says "build the co-host brief", "prep the co-host", "make the co-host doc", "send the co-host their prep", "cohost brief for EP042", or any equivalent ask for the second-seat prep document. Run after episode-program, ideally after research-brief has been run for each topic.
version: 0.1.0
---

## Purpose

The run-of-show is for the host. The co-host needs a different artifact — same factual grounding, completely different framing.

The co-host's job in this format is to throw articles, news items, and follow-up questions that drive pacing while the host carries the bulk of the talk time. The brief is built around that role: each segment lists the throw line the co-host delivers, the questions they can drop in to keep momentum, and the links they should have queued in another tab. The brief also includes pacing notes — moments where the co-host should interject and moments where they should let the host run uninterrupted.

The brief is one document per episode, not per topic.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `episode_number` | string | latest | Auto-detects the most recent `outbox/episodes/EP###/` folder. Override with explicit `EP042`. |
| `question_density` | string | from config (`cohost.question_density_default`) | `light` (2 per segment), `standard` (3 per segment), `heavy` (4 per segment). |
| `include_briefs` | bool | `true` | Whether to read research briefs for additional questions and links. If false, builds from run-of-show only. |
| `email_to_cohost` | bool | `false` | If true and Gmail connector is available, send the doc URL to `cohost.email` after creation. |

## Outputs

| Output | Path | Notes |
|---|---|---|
| Co-host brief (markdown) | `outbox/episodes/EP###/cohost-brief.md` | Local source of truth. Always written. |
| Co-host brief (Google Doc) | URL printed in run summary | Created in `output_targets.google_drive.cohost_brief_folder_id` when Drive connector is available. Shared with `cohost.email` with comment access. |
| Email | sent via Gmail if `email_to_cohost` is true | Otherwise skipped. |

## Process

When this skill activates, follow these steps in order.

1. **Verify config and episode folder.**
   - If `config/podcast.yaml` is missing, redirect to `podcast-init`.
   - If the episode folder is missing or has no `run-of-show.md`, stop and direct the user to run `episode-program` first.

2. **Load context.**
   - Read `cohost.name`, `cohost.email`, `cohost.contact_preference`, `cohost.question_density_default`.
   - Read the run-of-show from `outbox/episodes/EP###/run-of-show.md`.
   - If `include_briefs` is true, read every `outbox/episodes/EP###/briefs/topic-N.md` that exists.
   - Read `style/voice.md` and `voice.banned_words_extra`.

3. **Resolve question density.**
   - Map `light → 2`, `standard → 3`, `heavy → 4` questions per segment.

4. **Draft the brief.**

   Sections in this order:

   - **Episode header**: episode number, working title, target runtime, recording date if scheduled.
   - **Cold open** — one line the co-host can deliver to open the show. Pulled or adapted from the run-of-show's hook candidates. The co-host throws to the host with this line; the host carries from there.
   - **Pacing principles** (3–5 bullets): when to interject, when to let the host run, what kind of question keeps momentum vs. what kind kills it. These are show-wide, generated from the format and tone in the config.
   - **Per-segment block** (one per topic segment and per recurring named segment in the run-of-show):
     - Segment title and time target.
     - Throw line (1 line): how the co-host introduces this segment to the host.
     - Follow-up questions (count by density): drawn from the run-of-show's question list and supplemented by the research brief's "what the co-host might ask" section if available. Phrased for the co-host's voice.
     - Articles to have queued (1–3 links): URLs the co-host should have open in a tab. Pulled from the research brief's sources or the topic-radar source URL. Each link has a one-line "what's in it" note.
     - Cue (1 line): a specific moment to interject if pacing thins out — e.g., "If the host hasn't mentioned the layoffs by the 6-minute mark, throw the headcount number."
   - **Closing** (1 line): co-host's sign-off cue if the format calls for it.
   - **Quick reference** at the end: full link list and key numbers in a single block the co-host can scroll to during recording.

5. **Voice check.**
   - Run all generated copy (throw lines, framing notes, cue lines) through the voice rules. Replace banned words.
   - Throw lines and questions should sound like the co-host, not like marketing copy. Short, direct, conversational.

6. **Write the markdown file.**
   - Path: `outbox/episodes/EP###/cohost-brief.md`. Always written.

7. **Create the Google Doc.**
   - If `output_targets.google_drive.enabled` is true and Drive is available, create a doc in `cohost_brief_folder_id` named `EP### — Co-host Brief — <Working Title>`.
   - Share with `cohost.email` (comment access).
   - Capture the URL.
   - If Drive unavailable, skip and note in summary.

8. **Optionally email the co-host.**
   - If `email_to_cohost` is true and Gmail connector is available, send a short email to `cohost.email` with the doc URL. Subject line: `Co-host brief: EP### — <Working Title>`. Body is one paragraph.
   - If Gmail unavailable, print the email body to stdout for manual sending.

9. **Print summary.**
   - Episode number, working title, segment count, total questions written, link count, doc URL or fallback path, email status.
   - Suggested next: schedule the recording on the editorial calendar if not already.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| Filesystem read | Read run-of-show and research briefs from the episode folder | Required. |
| Google Drive | Create the co-host doc, share with co-host | Skip; markdown file only. |
| Gmail | Email the doc URL to the co-host | Print email body to stdout for manual sending. |

## Examples

### Example 1: Default run, briefs already written

User: *"build the co-host brief for EP042"*

```
EP042 — Anthropic Opus 5 and the Spotify ad business
Question density: standard (3 per segment)
Segments processed: 4 (cold open, segment 1, earnings watch, segment 2)
Total questions written: 12
Links queued: 9
Pacing principles: 4

Co-host brief written to outbox/episodes/EP042/cohost-brief.md.
Google Doc: https://docs.google.com/document/d/xyz789 (shared with cohost@example.com, comment access)
Email: not sent (email_to_cohost was false)

Next: confirm recording date on the editorial calendar.
```

### Example 2: Heavy question density, send by email

User: *"send the co-host their EP042 prep, give them lots of questions"*

Skill runs with `question_density: heavy` (4 per segment) and `email_to_cohost: true`. Creates the doc, shares with the co-host, sends a short email with the link. Email body is generated in the show's voice — short and direct.

### Example 3: Briefs not written yet

User: *"build the co-host brief for next episode"*

If no `briefs/` folder exists for the latest episode, the skill runs with `include_briefs: false` and notes in the summary that questions are sourced from the run-of-show only. Suggested next: run `research-brief` per topic and rerun `cohost-brief` to enrich with brief-sourced questions and links.
