---
name: episode-program
description: Build a run-of-show for the next episode from two or three selected topics. Reads the most recent topic-radar shortlist (or accepts free-form topic descriptions if topic-radar has not been run), allocates time across recurring segments and topic segments using the show's configured runtime, and drafts a structured rundown with cold-open hook candidates, host talking-point bullets, co-host setup lines, follow-up questions, transitions, and a closing call-to-action. Writes a markdown file locally and creates a shareable Google Doc when the Drive connector is available. Run this skill when the user says "build a run-of-show", "create the rundown", "plan the next episode", "draft an episode outline", "make a run of show", "rundown for episode X", "episode-program", or any equivalent request to structure the next recording. This is the upstream input for research-brief and cohost-brief.
version: 0.1.0
---

## Purpose

This skill turns a small set of selected topics into a running document the host can record from. The host should be able to glance down the page during recording and see exactly which beat is next, what the time target is, and what ammunition is available — without ever reading prose aloud.

The output is a structured rundown, not a script. Every host-facing item is a bullet. Every co-host-facing item is a short throw or a question. Time targets are explicit. Recurring segments from the show's config slot in automatically. The doc is the source of truth for both research-brief and cohost-brief downstream.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `topics` | string | (required) | Either comma-separated topic IDs from a `topic-radar` output (`T-20260501-01,T-20260501-02`), or a free-form list of `title: description` pairs separated by `;` for ad-hoc rundowns. |
| `episode_number` | string | auto | Auto-detected from the highest existing `outbox/episodes/EP###/` folder plus one. Override with explicit `EP042`-style string. |
| `target_runtime` | int | from config (`show.target_runtime_minutes`) | Total target episode length in minutes. |
| `topics_file` | string | `latest` | Which `outbox/topics/YYYY-MM-DD.md` to source IDs from. `latest` picks the most recent file. |
| `segment_overrides` | string | none | Optional comma-separated segment IDs to include or exclude this episode (e.g., `+earnings-watch,-founder-of-the-week`). Defaults to the full recurring set from config. |

## Outputs

| Output | Path | Notes |
|---|---|---|
| Run-of-show (markdown) | `outbox/episodes/EP###/run-of-show.md` | Local source of truth. Always written. |
| Run-of-show (Google Doc) | URL stored in run summary | Created in the Drive folder configured at `output_targets.google_drive.run_of_show_folder_id`. Skipped if Drive connector unavailable. |
| Episode folder | `outbox/episodes/EP###/` | Created if missing; `briefs/` subfolder created for research-brief outputs. |

## Process

When this skill activates, follow these steps in order.

1. **Verify config exists.**
   - If `config/podcast.yaml` is missing, stop and direct the user to run `podcast-init` first.

2. **Load context from config.**
   - `show.audience`, `show.description`, `show.target_runtime_minutes`, `show.episode_number_format`
   - `cohost.name`, `cohost.question_density_default`
   - `segments` list (recurring segment definitions)
   - `host.newsletter_tie_in` (informs the closing CTA)
   - `output_targets.google_drive`
   - `voice` extensions
   - Load `style/voice.md` for the banned-word check.

3. **Resolve the episode number.**
   - If `episode_number` is provided, use it.
   - Otherwise scan `outbox/episodes/` for the highest `EP###` folder and increment. If none exist, start at `EP001`.

4. **Resolve topics.**
   - If `topics` looks like topic IDs: locate `outbox/topics/<topics_file>.md` (or the most recent file if `latest`), grep for each ID, and lift the title, hook, source, and URL into a topic record.
   - If `topics` looks like `title: description; title: description`: parse those into ad-hoc topic records with no source URL.
   - If neither resolves, stop and ask the user to clarify.
   - Reject if fewer than 2 topics or more than 3. The format does not support 1-topic or 4+-topic rundowns without explicit override.

5. **Resolve recurring segments for this episode.**
   - Start with the full `segments` list from config in their configured order.
   - Apply `segment_overrides`: `+id` adds, `-id` removes.
   - Always include `cold-open` and `closing-cta` if defined; warn if either is missing from config.

6. **Allocate the time budget.**
   - Sum the `target_seconds` of all recurring segments (cold open, closing CTA, named segments).
   - Remaining seconds = `target_runtime` × 60 − sum of recurring.
   - Split remaining seconds across topic segments. Default is equal split. If topic scores are available from topic-radar, weight slightly toward the higher-scored topic (60/40 for 2 topics, 40/35/25 for 3 topics).
   - Round to the nearest 30 seconds. If the remaining budget goes negative (recurring segments exceed runtime), warn and ask the user to drop a segment or extend runtime.

7. **Draft the rundown.**

   For the cold open:
   - Generate 3 candidate hooks. Each is one sentence, under 25 words, in the show's voice. The host picks one at recording.

   For each topic segment:
   - Title and time target.
   - Co-host throw (1 line): how the co-host sets up the segment.
   - Host ammunition (5–10 bullets): facts, contrarian angles, surprising numbers, named characters, public-perception read. Bullets only — never prose paragraphs. Each bullet stands alone.
   - Suggested follow-up questions for the co-host (2–4 lines): questions the co-host can drop in to keep pacing if the host's run thins out.
   - Quotable item to drop in (1 line, optional): a number or quote the host might want to land on.
   - Transition out (1 line): how the segment hands off to the next.

   For each recurring named segment:
   - Pull the description from config.
   - Generate 3–5 ammunition bullets relevant to this week's material (e.g., for "Earnings Watch", surface the most-talked-about earnings report from the topic-radar window).
   - One co-host throw line and 2 follow-up questions.

   For the closing CTA:
   - 2 candidate sign-offs the host can pick from. Each is one or two sentences.
   - If `host.newsletter_tie_in.enabled` is true, include a one-line newsletter mention.
   - Always include a single specific ask (subscribe, share with one operator, leave a review — pick one per episode, not all three).

8. **Voice check.**
   - Scan every generated line against `style/voice.md` plus `voice.banned_words_extra` and `voice.banned_phrases_extra` from config.
   - Replace any hits. If a banned word is the only honest way to say it, leave one occurrence and note it in the run summary.
   - Check for passive voice patterns ("is being [verb]ed by", "there is", "it is important to note"). Rewrite.

9. **Write the markdown file.**
   - Path: `outbox/episodes/EP###/run-of-show.md`. Create the folder and `briefs/` subfolder if missing.
   - Format:

     ```markdown
     # EP### — <Working Title>

     Target runtime: 45 min. Topics: T-20260501-01, T-20260501-02.

     ## Cold Open (60s)

     Hook candidates:
     - ...
     - ...
     - ...

     ## Segment 1: <Topic Title> (12 min)

     Co-host throw:
     - "..."

     Host ammunition:
     - ...
     - ...

     Follow-up questions:
     - ...

     Quotable: "..."

     Transition: "..."

     ## Segment 2: ...

     ## Earnings Watch (8 min)

     ...

     ## Closing CTA (45s)

     Sign-off candidates:
     - ...
     - ...
     ```

   - Generate a working title from the highest-scored topic. The host can rename later.

10. **Create the Google Doc.**
    - If `output_targets.google_drive.enabled` is true and the Drive connector is available, create a doc named `EP### — <Working Title>` in the configured run-of-show folder. Mirror the markdown structure.
    - Set sharing so the co-host (per `cohost.email`) has comment access.
    - Capture the doc URL.
    - If Drive is unavailable, skip and note in the summary.

11. **Print summary.**
    - Episode number, working title, time budget breakdown by segment, doc URL or local-only path, banned-word warnings if any.
    - Suggested next commands: `research-brief` for each topic ID, then `cohost-brief` for the episode.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| Google Drive | Create the run-of-show doc, share with co-host | Skip; markdown file only. Note in summary. |
| Gmail | Optionally email the doc URL to the co-host | Skip; doc URL printed for manual sharing. |
| Filesystem read | Read `outbox/topics/*.md` and existing episode folders | Required. If `outbox/` is missing, the skill creates it. |

## Examples

### Example 1: Two topics from the latest topic-radar output

User: *"build a run of show with T-20260501-01 and T-20260501-02"*

```
EP042 — Anthropic Opus 5 and the Spotify ad business

Time budget:
  Cold open      60s
  Segment 1      12m   Anthropic Opus 5 launch
  Earnings Watch 8m    Spotify Q1
  Segment 2      11m   OpenAI cuts Plus pricing
  Closing CTA    45s

run-of-show.md written to outbox/episodes/EP042/.
Google Doc: https://docs.google.com/document/d/abc123 (shared with cohost@example.com)
Voice check: clean.

Next: research-brief T-20260501-01 (Opus 5)
      research-brief T-20260501-02 (Spotify)
      cohost-brief EP042
```

### Example 2: Ad-hoc topics, no topic-radar run

User: *"plan an episode with these two: 'Tesla deliveries miss: what's actually happening at the showroom level'; 'Why YC's latest batch leans so hard on infra'"*

Skill parses the free-form pairs, creates ad-hoc topic records, and drafts the rundown without sources to cite. Run summary flags that research-brief will need to source these from scratch.

### Example 3: Override segments

User: *"build the rundown for next episode with three topics, drop earnings watch this week"*

Skill applies `segment_overrides: -earnings-watch`, redistributes the freed time across the three topic segments, and drafts accordingly.
