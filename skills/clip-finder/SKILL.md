---
name: clip-finder
description: Scan an episode transcript for short-form clip candidates suitable for Instagram Reels, TikTok, and YouTube Shorts. Targets punchy openers, contrarian takes, surprising stats, emotional beats, and complete narrative arcs that stand alone without surrounding context. Produces 8–12 candidates per episode with start and end timestamps, a transcript excerpt, a suggested hook caption, a platform recommendation, and a why-this-clips note. Outputs a markdown file for the host to scan and a JSON file an editor can import. Run this skill when the user says "find clips for EP042", "what's clippable", "pull clips from the recording", "find shareable moments", "build the clip list", "clip finder", or any equivalent ask for short-form moments. Run after show-notes (the cleaned transcript is the preferred input).
version: 0.1.0
---

## Purpose

Short-form clips drive 10–30% of new podcast listeners according to recent industry reporting, and that share skews higher for shows with a deliberate clip strategy. The constraint is finding the right moments fast. This skill reads a full episode transcript and surfaces the 8–12 best candidates — each one is a complete idea that lands in 30–90 seconds without setup.

The skill ranks. The host picks. Editor imports the JSON, applies captions and visual polish in their tool of choice.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `episode_number` | string | latest | Auto-detects the most recent `outbox/episodes/EP###/` folder. Override with explicit `EP042`. |
| `target_count` | int | from config (`distribution.default_clip_count_target`, fallback 10) | Target number of candidates. The skill aims for this number; it returns fewer if quality is thin and never pads with weak clips. |
| `min_seconds` | int | from config (`distribution.clip_length_seconds.min`, fallback 30) | Minimum clip length. |
| `max_seconds` | int | from config (`distribution.clip_length_seconds.max`, fallback 90) | Maximum clip length. |
| `categories` | string | all | Comma-separated subset of `openers,contrarian,stats,emotional,arcs`. Restricts the scan if the host wants only certain types. |

## Outputs

| Output | Path | Notes |
|---|---|---|
| Clip list (markdown) | `outbox/episodes/EP###/clips.md` | Human-scannable list, ranked. |
| Clip list (JSON) | `outbox/episodes/EP###/clips.json` | Editor-importable. Each clip has start, end, excerpt, caption, platform, rationale, and a stable id. |

## Process

When this skill activates, follow these steps in order.

1. **Verify config and episode folder.**
   - If `config/podcast.yaml` is missing, redirect to `podcast-init`.
   - If the episode folder is missing or has no transcript, stop and direct the user to run `show-notes` first.

2. **Load the transcript.**
   - Prefer `transcript-clean.md`. Fall back to `transcript-raw.md`. Fall back to any `.txt`, `.srt`, or `.vtt` file in the folder.
   - Preserve timestamps. If the transcript has no timestamps, warn in the run summary — the JSON output will use word-index ranges instead of seconds.

3. **Load context.**
   - Read `run-of-show.md` if present (helps locate segment boundaries and identify which topic each clip belongs to).
   - Read briefs for sourced numbers (helps verify "surprising stats" candidates against the brief's source URLs).
   - Read `style/voice.md` for caption writing.

4. **Scan the transcript by category.**

   For each category, look for these patterns:

   - **Punchy openers**: definitive statements at the top of a thought ("Here's what most people miss about X"), short declarations that hook in under 5 seconds, contrarian setups ("Everyone is saying Y. They're wrong.").
   - **Contrarian takes**: "actually", "the truth is", "people don't realize", followed by a counter-position with a fact or a number behind it. Reject empty contrarianism — every candidate must have a backed claim.
   - **Surprising stats**: a number the host lands on, with enough context that the listener understands why it matters. Cross-check against the briefs' sourced numbers when possible.
   - **Emotional beats**: laughs, candid admissions, audible surprise, frustration, a moment where the host or co-host drops the host-voice and speaks plainly.
   - **Standalone arcs**: a 30–90 second window that has setup, tension, and payoff without depending on what came before. The hardest category to find and the most valuable.

5. **Filter by length.**
   - For each candidate, identify the natural start (a complete thought beginning) and natural end (a complete thought ending). Drop candidates that cannot fit cleanly within `min_seconds` and `max_seconds`.

6. **Score each candidate.**

   Score on five factors, each 0–2, total 0–10:

   - **Standalone-ness**: does it make sense without the rest of the episode?
   - **Hook strength**: does the first 5 seconds make a viewer stop scrolling?
   - **Payoff**: does the clip end on a landing, not a fade?
   - **One clear idea**: a single point, not three half-points.
   - **Quotability**: does a line in the clip work as a text overlay or pull quote?

7. **Rank and slice.**
   - Sort by score, descending.
   - Take the top `target_count`. If fewer candidates score above 6.0, return only those — never pad below threshold.
   - Aim for category mix: not all "stats", not all "contrarian". If the top 10 are all the same category, drop the lowest-scoring of that category until variety is restored.

8. **For each kept candidate, generate the clip metadata.**

   - **Stable id**: `C-EP###-NN` (e.g., `C-EP042-03`).
   - **Start and end timestamps**: in `MM:SS` or `HH:MM:SS` format. Pulled from the transcript.
   - **Transcript excerpt**: the verbatim text of the clip, with speaker labels.
   - **Hook caption**: a one-line text overlay the editor can use, under 80 characters, voice-checked. The caption is the hook, not a summary.
   - **Platform recommendation**: TikTok, Reels, Shorts, or all three. Recommend specific platforms only when there's a real reason: heavy comedic timing leans TikTok; B2B insight with named companies leans Shorts; visual or emotional moments lean Reels. Default to all three.
   - **Why-this-clips note**: one sentence on what makes this moment work.

9. **Voice check on captions.**
   - Captions pass `style/voice.md` rules. No banned words, no clichés, no hashtags in the caption itself (the editor adds platform-appropriate tags downstream).

10. **Write the markdown file.**
    - Path: `outbox/episodes/EP###/clips.md`.
    - Format:

      ```markdown
      # EP### — Clip Candidates

      Target: 10. Returned: 9 (one category-thin week).

      ## Top picks

      ### C-EP042-01 — 04:32 to 05:18 (46s) — TikTok, Reels, Shorts — Score 9.4
      Category: contrarian
      Caption: "Everyone's wrong about why Spotify is winning ads."
      Why: clean setup, named number, definitive payoff.
      Excerpt:
      > HOST: Everyone keeps saying Spotify is winning podcast ads because of exclusives. That's wrong. The exclusives are mostly losing money. The real story is the ad load — they doubled it in twelve months and nobody noticed because the music side absorbed the noise.

      ### C-EP042-02 — ...
      ```

11. **Write the JSON file.**
    - Path: `outbox/episodes/EP###/clips.json`.
    - Schema:

      ```json
      {
        "episode": "EP042",
        "clips": [
          {
            "id": "C-EP042-01",
            "start": "00:04:32",
            "end": "00:05:18",
            "duration_seconds": 46,
            "category": "contrarian",
            "score": 9.4,
            "platforms": ["tiktok", "reels", "shorts"],
            "caption": "Everyone's wrong about why Spotify is winning ads.",
            "rationale": "clean setup, named number, definitive payoff",
            "excerpt": "HOST: Everyone keeps saying Spotify..."
          }
        ]
      }
      ```

12. **Print summary.**
    - Episode number, target vs returned, category breakdown, top 3 by score with captions.
    - If the count is below target, name the reason (transcript thin, all candidates clustered in one category, length window too tight).
    - Suggested next: `distribution-pack EP###`.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| Filesystem read | Load transcript, run-of-show, briefs | Required. |
| Filesystem write | Write clips.md and clips.json | Required. |

The skill is local-only. It does not upload, schedule, or post — `distribution-pack` handles posting via Blotato when the host is ready.

## Examples

### Example 1: Default run

User: *"find clips for EP042"*

```
EP042 — clip candidates returned: 10 of 10 target.
Categories: contrarian (3), stats (3), arcs (2), openers (1), emotional (1).
Top 3:
  C-EP042-01  9.4  contrarian  Everyone's wrong about why Spotify is winning ads.
  C-EP042-04  9.1  arcs        The two minutes where I almost killed the company.
  C-EP042-07  8.8  stats       28% growth in twelve months. Nobody talks about it.

Outputs:
  outbox/episodes/EP042/clips.md
  outbox/episodes/EP042/clips.json

Next: distribution-pack EP042.
```

### Example 2: Category restriction

User: *"give me only contrarian clips and standalone arcs from EP042"*

Skill runs with `categories: contrarian,arcs`, scans only those, and returns whatever passes the score threshold within those two categories. May return fewer than 8 — the run summary notes the restriction.

### Example 3: Thin episode

User runs clip-finder on a low-energy episode. Output:

```
EP044 — clip candidates returned: 6 of 10 target.
Reason: most stat-heavy moments lacked a payoff line; three "contrarian" candidates
were too dependent on prior segment context to stand alone. Returned only the
candidates that scored above 6.0.
```

The skill never pads. Six strong clips beats ten weak ones.
