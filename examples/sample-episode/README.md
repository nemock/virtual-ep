# Sample Episode — EP001

This folder shows one complete production cycle from topic shortlist to debrief. Every file is illustrative and uses fictional facts about real companies. Treat it as a shape reference, not a source.

The example covers a single episode of the reference show — a topical business commentary podcast — covering two topics: Anthropic's Opus 5 launch and Spotify's Q1 podcast ad revenue. It walks through the artifacts each skill produces.

## Workflow shown

```
topics.md
   ↓ (host picks T-20260501-01 and T-20260501-02)
EP001/run-of-show.md
   ↓
EP001/briefs/topic-1.md
EP001/briefs/topic-2.md
EP001/cohost-brief.md
   ↓ (record)
EP001/transcript-raw.md
   ↓
EP001/transcript-clean.md
EP001/show-notes.md
EP001/clips.md + clips.json
   ↓ (publish)
EP001/distribution.md
   ↓ (one week later)
EP001/debrief.md
```

## How to read each file

- `topics.md` — `topic-radar` output. The host picks two IDs from this table.
- `EP001/run-of-show.md` — `episode-program` output. The host's recording document.
- `EP001/briefs/topic-N.md` — `research-brief` output. One per topic.
- `EP001/cohost-brief.md` — `cohost-brief` output. The co-host's prep document.
- `EP001/transcript-raw.md` — what the transcription provider returns. Shortened for the example.
- `EP001/transcript-clean.md` — `show-notes` output. Filler removed.
- `EP001/show-notes.md` — `show-notes` output. Titles, descriptions, chapters, takeaways, links.
- `EP001/clips.md` and `EP001/clips.json` — `clip-finder` output.
- `EP001/distribution.md` — `distribution-pack` output. Drafts for every platform.
- `EP001/debrief.md` — `post-show-debrief` output. Numbers, lessons, topic-radar feedback.

## Important note

All numbers, quotes, comments, and links in this example are fabricated to illustrate the shape of each output. Do not cite anything from this folder as a fact about Anthropic, Spotify, or any other company.
