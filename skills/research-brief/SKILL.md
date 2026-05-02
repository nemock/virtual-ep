---
name: research-brief
description: Build a one-page research brief on a single topic for an upcoming podcast episode. Produces fact-cited bullets the host can pull from extemporaneously — never paragraphs of prepared remarks. Each brief includes key facts with working source URLs, three contrarian or non-obvious angles, surprising stats, historical parallels, and named characters with quotes the host can reference. Cites every claim with a verified URL. Run this skill when the user says "research this topic", "build a brief on X", "research brief", "background for the segment on X", "give me ammunition on X", "go deep on T-20260501-01", or any equivalent ask for per-topic prep material. Run once per topic on the rundown.
version: 0.1.0
---

## Purpose

This skill is the research desk. The host speaks extemporaneously and does not want to read prose. The brief gives them facts and angles in scannable form — anything paragraph-shaped gets converted to bullets. Three contrarian or non-obvious angles per topic is a hard floor: if the model can only find two, it goes back and works harder. Every factual claim has a working URL the host can click during the recording session if a co-host pushes back.

The brief is per topic, not per episode. A two-topic episode produces two briefs. A three-topic episode produces three.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `topic` | string | (required) | Either a topic ID (`T-20260501-01`) that resolves through topic-radar and the run-of-show, or free-form topic text for ad-hoc research. |
| `episode_number` | string | auto | Episode folder for output. Auto-detected from the most recent `outbox/episodes/EP###/run-of-show.md` that references the topic. Override with explicit `EP042`. |
| `topic_index` | int | auto | Which topic slot in the rundown this is (1, 2, or 3). Used in the output filename. Auto-detected from the run-of-show order. |
| `depth` | string | `standard` | `light`, `standard`, or `deep`. Drives length, fact count, source count, and historical context depth. |

## Outputs

| Output | Path | Notes |
|---|---|---|
| Brief (markdown) | `outbox/episodes/EP###/briefs/topic-N.md` | Local source of truth. Always written. |
| Brief (Google Doc) | URL printed in run summary | Optional. Created in `output_targets.google_drive.briefs_folder_id` when Drive connector is available. |

## Process

When this skill activates, follow these steps in order.

1. **Verify config and episode folder exist.**
   - If `config/podcast.yaml` is missing, redirect to `podcast-init`.
   - If the episode folder does not exist, run `episode-program` first or accept ad-hoc mode (no run-of-show context).

2. **Resolve the topic.**
   - If `topic` looks like a topic ID, load the topic record from the most recent `outbox/topics/*.md` and the run-of-show. Pull title, hook, source URL, and existing one-line context.
   - If `topic` is free-form text, treat it as the topic title and proceed without prior context.

3. **Set depth parameters.**

   | Depth | Fact bullets | Contrarian angles | Surprising stats | Historical parallels | Named characters | Source URLs |
   |---|---|---|---|---|---|---|
   | light | 5–7 | 2–3 | 1–2 | 0–1 | 1–2 | 3–5 |
   | standard | 10–12 | 3 | 2–3 | 1–2 | 2–3 | 5–8 |
   | deep | 15+ | 4–5 | 4+ | 2–3 | 3–5 | 8–12 |

4. **Gather material.**
   - Search the open web for current reporting on the topic.
   - Fetch primary sources where available: company filings, official press releases, founder posts, regulatory documents, transcripts.
   - Pull at least one source on the human side: named executives, founders, analysts, public reactions.
   - Pull at least one historical parallel: a comparable past event, deal, launch, or failure with named participants.

5. **Verify every URL.**
   - Hit each source URL to confirm it returns 200 and that the page contains the cited claim.
   - If a URL is broken, replace it with a working alternative or drop the claim. Never include a claim with a dead link.

6. **Build the brief.**

   Required sections in this order:

   - **The angle** (1 line): the non-obvious lens the host should bring to this topic. Not a summary — a take.
   - **Key facts** (depth-dependent count): one bullet per fact, each ending with `[Source](url)`. No filler.
   - **Three (or more) contrarian or non-obvious angles**: each is a one-paragraph bullet — the conventional read, then the counter-read with a fact or two backing it. These are the bullets that earn the host's respect.
   - **Surprising stats**: numbers the host can drop in. Each cited.
   - **Historical parallels**: 1–3 past events that rhyme. Named, dated, sourced.
   - **Named characters and quotes**: the people involved, their public position, one to two quotable lines per person, sourced.
   - **What the co-host might ask**: 3–5 follow-up questions the co-host could lob in. These are not the same as the run-of-show questions — these go deeper and assume the brief has been read.
   - **One thing to avoid saying**: optional but useful — a known minefield (legal, factual, or reputational) the host should sidestep.

7. **Voice check.**
   - Run the generated copy (angles, hooks, framing lines) through `style/voice.md` plus `voice.banned_words_extra` from config. Replace banned words. Rewrite passive voice.
   - Factual claims and direct quotes from sources are not rewritten — quotes stay verbatim, attributed.

8. **Write the markdown file.**
   - Path: `outbox/episodes/EP###/briefs/topic-N.md` where N is the segment slot.
   - Format follows the section order above. Every fact carries an inline `[Source](url)` link.

9. **Create the Google Doc.**
   - If `output_targets.google_drive.enabled` is true and Drive connector is available, create a doc in `briefs_folder_id` named `EP### — Topic N — <Title>`. Mirror markdown content.
   - Optionally share with co-host if the run-of-show is shared with them.
   - Skip if Drive unavailable.

10. **Print summary.**
    - Topic title, depth, fact count, angle count, source count, broken-link count (always 0 if the skill ran correctly), output paths.
    - Suggested next: run `research-brief` for the remaining topics on the rundown, then `cohost-brief`.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| WebSearch / WebFetch | Pull and verify sources | Required. If unavailable, the skill cannot run; tell the user to enable web access. |
| Google Drive | Create the brief doc | Skip; markdown file only. |
| Filesystem read | Load topic-radar output and run-of-show | Required for ID-based input. Free-form topic input bypasses. |

## Examples

### Example 1: Standard-depth brief from a topic ID

User: *"research T-20260501-02 for EP042"*

```
Topic: Spotify earnings beat, podcast ad revenue up 28%
Depth: standard
Facts: 11 bullets, all sourced
Angles: 3 contrarian reads
Surprising stats: 3 (ad load %, MAU growth slowdown, exclusive-deal write-off)
Historical parallels: 2 (Pandora 2014, SiriusXM 2019)
Named characters: 3 (Daniel Ek, Dawn Ostroff, Bill Simmons)
Source URLs: 7 verified

Brief written to outbox/episodes/EP042/briefs/topic-2.md.
Google Doc: https://docs.google.com/document/d/xyz789

Next: research-brief T-20260501-01 for the other topic, then cohost-brief EP042.
```

### Example 2: Deep brief on free-form topic

User: *"go deep on the WeWork comeback story for the next episode"*

Skill accepts the free-form topic, runs at deep depth, builds 15+ facts with 4 angles and 3 historical parallels (1980s real estate flips, Theranos, Yahoo at $5B). Writes to `outbox/episodes/EP###/briefs/topic-N.md` based on the next available slot in the most recent run-of-show, or asks for the episode number if there is none.

### Example 3: Light brief

User: *"give me a quick brief on T-20260501-03"*

Skill runs at `light` depth, produces 6 facts, 2 angles, 4 sources. Total length under half a page. Useful for the third or fourth topic in a packed week.
