---
name: hot-sheet
description: Build a glanceable, browser-based hot sheet for a solo riff-to-camera episode and open it in a browser tab. Reads topic candidates from configured local inboxes (research-ingest nodes, voice-library positions) and/or the latest topic-radar shortlist, picks a themed set of riffable items, drafts a cold-open intro and per-topic cards with context, source links, the host's pre-loaded angle, and riff prompts, then renders a single self-contained HTML page via scripts/render_hotsheet.py. Run this skill when the user says "let's do an episode", "build a hot sheet", "hot sheet", "set up a riff session", "I want to record", "what am I riffing on today", or any equivalent request to get camera-ready fast. This is the solo-format counterpart to episode-program; riff-capture closes the loop afterward.
version: 0.1.0
---

## Purpose

This is the "let's do an episode" button. The host says one sentence and gets a Chrome tab they can record from: a memorable cold-open line, a scrollable stack of topic cards with just enough context to riff, and a sign-off. No hunting through markdown files, no script to read — ammunition at a glance.

Unlike `episode-program` (structured run-of-show, co-host throws, time budgets), the hot sheet is built for a solo host doing an unedited or lightly edited talking-head session. Cards are ordered around a common thread so the episode hangs together, but nothing on the page is meant to be read aloud except the intro and sign-off candidates — and those are short enough to glance at, look up, and deliver.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `theme` | string | auto | Free-form filter ("FDA", "AI hype", "fundraising"). If omitted, the skill finds the strongest common thread in the candidate pool and names it. |
| `card_count` | int | 6 | Target number of topic cards. Acceptable range 4–10. If the pool can't support the target at quality, produce fewer and say so. |
| `episode_number` | string | auto | Auto-detected from the highest existing `outbox/episodes/EP###/` folder plus one. |
| `sources` | string | all configured | Restrict to a subset of `topic_sources.local_inboxes` by name, e.g. `external-voices`. |

## Outputs

| Output | Path | Notes |
|---|---|---|
| Hot sheet data | `outbox/episodes/EP###/hotsheet.json` | Structured episode data. Schema documented in `scripts/render_hotsheet.py`. |
| Hot sheet page | `outbox/episodes/EP###/hotsheet.html` | Self-contained HTML, rendered by the script, served + opened in the browser. |
| Riffed state | `outbox/episodes/EP###/riffed.json` | Written live by `scripts/hotsheet_server.py` as the host checks cards off. Input to `riff-capture`. |
| Run summary | stdout | Cards chosen, theme, pool stats, the page URL. |

## Process

When this skill activates, follow these steps in order.

1. **Verify config exists.**
   - If `config/podcast.yaml` is missing, stop and tell the user to run `podcast-init` first.

2. **Load context.**
   - `show.audience`, `show.description` — calibrate topic selection and voice.
   - `topic_sources.local_inboxes` — the list of local inbox files/directories to read (see schema in `config/podcast.yaml.example`). Each entry has a `name`, `path`, and optional `filters`.
   - `style/voice.md` plus `voice.*_extra` config — for the banned-word check on intro and sign-off.
   - If `topic_sources.local_inboxes` is empty, fall back to the most recent `outbox/topics/*.md` shortlist from topic-radar. If neither exists, stop and say which one to set up.

3. **Read the candidate pool.**
   - For each configured local inbox, read the index file at `path`. Apply the entry's `filters` (e.g. `status: new`, `purpose_tags` containing `riff_prompt`, `brand_tags` overlapping the configured list, minimum heat score).
   - For each surviving candidate, follow its node link and read the node file. Lift: title, source name, source URL, summary/context, any pre-written angle, any voice-library position slugs.
   - Respect the inbox's own ranking (heat score or table order). Do not re-score what an upstream pipeline already scored — select, don't re-rank.

4. **Pick the themed set.**
   - If `theme` was given, filter to matching candidates first.
   - Otherwise look for the strongest common thread across the top of the pool — shared position slugs, shared subject, shared tension. Name the thread in one sentence; it becomes the episode's `theme` line and informs the intro.
   - Select `card_count` items: lead with the strongest hook, alternate heavy/light where possible, end on the most forward-looking item.
   - Honesty rule: if the pool is thin or no thread exists, build the best mixed-bag sheet you can and say plainly in the summary that it's a grab bag.

5. **Draft the sheet content.**
   - **Intro candidates (2–3):** each under 25 words, in the show's voice, framing the thread. These are the only lines on the page meant to be spoken close to verbatim — make them memorable enough to deliver after one glance, not teleprompter prose.
   - **Per card:**
     - `headline` — the topic in the host's framing, not the source's headline.
     - `context` — a 15-second setup: who, what number, what happened. One or two sentences.
     - `angle` — the host's pre-loaded take. If the node already carries one (e.g. a "potential angle" section naming voice-library positions), use it as the basis; otherwise draft one from the show's point of view.
     - `riffs` — 2–3 open prompts that point at where the riff can go ("What does this mean for the founder who…", "The historical parallel here is…"). Prompts, not sentences to read.
     - `positions` — voice-library position slugs this card reinforces, if any.
     - `source`, `url` — where the host can click for the full story mid-session.
     - `node` — the relative path of the source node file, so `riff-capture` can find it later.
   - **Sign-off candidates (2):** one or two sentences each, with one specific ask (subscribe, share, reply — pick one per episode). Include the newsletter mention if `host.newsletter_tie_in.enabled` is true.

6. **Voice check.**
   - Scan every generated line against `style/voice.md` plus config extras. Replace hits.

7. **Write and render.**
   - Resolve the episode number, create `outbox/episodes/EP###/` if missing.
   - Write `hotsheet.json` per the schema in `scripts/render_hotsheet.py`.
   - Run: `python3 <abs path>/scripts/render_hotsheet.py <abs path>/outbox/episodes/EP###/hotsheet.json`
   - The script validates required fields and writes `hotsheet.html` alongside the JSON.

8. **Start the state server and open the tab.**
   - Run in the background: `python3 <abs path>/scripts/hotsheet_server.py <abs path>/outbox/episodes/EP###`
   - It prints the URL it settled on (`http://127.0.0.1:<port>/hotsheet.html`). Open that URL — macOS: `open <url>` (add `-a "Google Chrome"` if the default browser isn't the right one).
   - Served this way, every checkbox toggle on the page writes `riffed.json` into the episode folder, so `riff-capture` needs no input from the host. The server exits on its own after 4 idle hours.
   - If the server can't start, fall back to `open <abs path>/.../hotsheet.html` — the page degrades to localStorage plus the "Copy riff summary" button.

9. **Print summary.**
   - Episode number, theme line, cards chosen (title + source), pool stats (candidates read, filtered, picked), the page URL, and the reminder: after recording, just say "capture EP###" — the checkboxes already recorded which cards were riffed.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| Filesystem read | Local inbox indexes and node files (may live outside this repo — paths come from config) | Required for inbox mode. Fall back to topic-radar shortlists if no inbox is configured. |
| Filesystem write | `hotsheet.json` + `hotsheet.html` in the episode folder | Required. |
| Shell | Run the render script; open the browser tab | If `open` fails, print the file path for manual opening. |

No network access is needed — the hot sheet is built entirely from material upstream pipelines already collected. That keeps "let's do an episode" fast.

## Examples

### Example 1: Default run

User: *"let's do an episode"*

```
EP007 — The confirmatory stage
Theme: early green lights keep dying in the confirmatory round — in trials, in AI budgets, in robotics.

6 cards from external-voices (54 candidates read, 19 passed filters):
  1. ADC Therapeutics: 27 deaths in the confirmatory trial   r/biotech
  2. Measured AI productivity gain: 7.8%, not 10x            r/artificial
  ...

Serving at http://127.0.0.1:8765/hotsheet.html — opened in the browser.
Check cards off as you riff. After recording, just say: capture EP007.
```

### Example 2: Themed run

User: *"build a hot sheet about fundraising"*

Skill applies `theme: fundraising`, pulls the raise-related candidates from the pool, and notes in the summary if it had to reach below the usual heat threshold to fill the sheet.

### Example 3: Thin pool

User runs the skill when the inbox has been mostly worked through. Output names the shortfall — "4 cards, not 6; the pool under your filters is thin this week" — rather than padding with off-brand items.
