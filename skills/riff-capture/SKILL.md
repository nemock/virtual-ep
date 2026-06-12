---
name: riff-capture
description: Close the loop after a hot-sheet recording session. Takes the episode number and which cards the host actually riffed on (the hot sheet page's "Copy riff summary" button produces the exact command), marks the source inbox nodes as acted on so upstream pipelines stop resurfacing them, and — when a transcript or recording notes are provided — extracts quotable lines, fresh positions, and anecdotes into a handoff file for the voice-library intake. Run this skill when the user says "riff-capture EP### --cards 1,3,5", "capture that session", "I recorded, here's what I covered", "close out the episode", or pastes the copied riff summary. This is the downstream counterpart to hot-sheet.
version: 0.1.0
---

## Purpose

A riff session produces two things worth keeping: a record of which topics are now spent, and the host's own words. This skill banks both. Spent topics get their source nodes flipped to `acted_on` so the research pipeline's inbox stops showing them. The host's words — quotes, takes, anecdotes that surfaced mid-riff — get extracted into a structured handoff the voice-library intake can ingest, so the next piece of content written in the host's voice has more to draw on.

Without this step the system leaks: the same topics resurface, and the best lines from a session evaporate with the recording.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `episode` | string | (required) | `EP###` — must have a `hotsheet.json` in its episode folder. |
| `cards` | string | from `riffed.json` | Comma-separated card numbers the host riffed on (`1,3,5`), or `none`. Usually omitted: when the hot sheet ran with its state server, the page's checkboxes already wrote `riffed.json` and this skill reads it. The explicit form (emitted by the page's "Copy riff summary" button) is the fallback for sheets opened without the server. |
| `transcript` | path | none | Optional path to a transcript, cleaned or raw. Enables the voice-extraction pass. |
| `notes` | string | none | Optional free-form recall ("the bit about residents vs attendings landed") — used the same way as a transcript, lower fidelity. |

## Process

When this skill activates, follow these steps in order.

1. **Load the episode.**
   - Read `outbox/episodes/EP###/hotsheet.json`. If missing, stop and say so.
   - Resolve which cards were riffed: use the `cards` input if given; otherwise read `outbox/episodes/EP###/riffed.json` (written live by the hot sheet's checkboxes) and take the card numbers whose value is true. If neither exists, ask the host which cards they covered.
   - Resolve the card numbers to their `node` paths. Node paths are relative to the inbox they came from — resolve against the matching `topic_sources.local_inboxes` entry's base directory.

2. **Consolidate the recording into the episode folder.**
   - The host records to a flat `recordings/` folder (OBS doesn't know the episode number at record time), so the master lands there with a date name like `recordings/YYYY-MM-DD_riff.mp4`.
   - Move the most recent matching master into `outbox/episodes/EP###/` so everything for the episode lives in one place. Then run the audio-cleanup pass on it (mandatory) and write the cleaned master alongside. Generate the whisper transcript (always) — it can run off the raw in parallel with cleanup.
   - If no master is found in `recordings/`, note it and continue (the host may have filed it manually).

3. **Mark spent nodes.**
   - For each riffed card with a `node` path: open the node file and update its frontmatter `status` from `new` to `acted_on`. Leave every other field untouched. If the node is already `acted_on` or `discarded`, skip and note it.
   - If the upstream pipeline documents a different convention, follow that convention — check the inbox's README or the node's own frontmatter vocabulary before inventing values.
   - Cards without a `node` path (ad-hoc topics) are skipped silently.

4. **Extract voice material (only if `transcript` or `notes` provided).**
   - Read the transcript. For each riffed card's topic, pull:
     - **Quotes** — lines the host said that stand alone: sharp, opinionated, reusable. Verbatim, no cleanup beyond removing filler words.
     - **Positions** — takes that sound like durable stances rather than one-off reactions. Note which existing position slugs they reinforce (the card's `positions` list is the starting point) and flag apparent *new* positions explicitly.
     - **Anecdotes** — any personal story the host told. Capture the story beats, not a paraphrase.
   - Quality bar: 3 strong items beat 15 weak ones. If a card's riff produced nothing worth keeping, say so.

5. **Write the handoff.**
   - Path: `outbox/episodes/EP###/talk-time-handoff.md`.
   - Format: one section per riffed card with topic title, node path, and the extracted quotes/positions/anecdotes, each tagged with its type and any reinforced position slugs. Frontmatter records the episode, date, and transcript source.
   - This file is an *input* for the voice-library intake (e.g. a `/talk-time` session) — it does not write into the voice library directly. Note this in the summary.

6. **Write the debrief stub.**
   - Append to (or create) `outbox/episodes/EP###/debrief.md`: date recorded, cards riffed vs skipped, nodes marked, handoff written or not. The `post-show-debrief` skill extends this file later with performance data if the episode ships publicly.

7. **Print summary.**
   - Nodes flipped to `acted_on` (count + slugs), cards skipped, voice items extracted by type, handoff path. Suggest running the voice-library intake on the handoff if one was written.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| Filesystem read/write | Episode folder, inbox node files (may live outside this repo), handoff + debrief | Required. If a node file is missing (moved/expired upstream), log it and continue with the rest. |

## Examples

### Example 1: Checkbox flow — no arguments needed

User: *"capture EP007"*

```
EP007: 3 of 6 cards riffed (from riffed.json, last updated 2026-06-11T22:40Z).
Marked acted_on:
  biotech-adc-therapeutics-27-deaths-confirmatory-trial
  artificial-25t-ai-spending-95pct-zero-pl-impact
  robotics-china-humanoid-boom-fades-unitree-profit-drop
No transcript provided — skipped voice extraction.
Debrief stub written to outbox/episodes/EP007/debrief.md.
```

### Example 2: With a transcript

User: *"capture EP007, cards 1,3,5, transcript at outbox/episodes/EP007/transcript-raw.md"*

Skill marks the nodes, then extracts: 4 quotes, 1 reinforced position, 1 new position candidate, 1 anecdote → `talk-time-handoff.md`. Summary suggests running the voice-library intake on the handoff.

### Example 3: Nothing landed

User: *"riff-capture EP008 --cards none"*

No nodes are touched. The debrief stub records that the session was scrapped, which tells the next hot-sheet run those topics are still live.
