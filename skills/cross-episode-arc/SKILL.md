---
name: cross-episode-arc
description: Surface themes that span multiple past episodes and suggest concrete callback opportunities for the next episode. Reads cleaned transcripts and topic shortlists across the recent run, clusters recurring themes (e.g., "AI commoditization", "Spotify ad strategy", "founder talent flight"), and produces a callbacks document that names the theme, when it last came up, what was said, and a suggested phrasing the host can drop in. Also writes a longer themes map that catalogs every running thread across the lookback window. Run this skill when the user says "what arcs are running across episodes", "find callbacks for EP043", "cross-episode themes", "what should I call back to", "callback opportunities", "what are the running threads", or any equivalent ask about story continuity. Run after episode-program for the next episode is drafted but before recording, so the host can absorb the callbacks during prep.
version: 0.1.0
---

## Purpose

A solo show with a recurring host gains depth when threads from past episodes get called back. "Three weeks ago I said X. Look what happened." That kind of self-reference is what listeners reward — it signals the show is paying attention to the world over time, not reading new headlines each week.

Doing this manually is hard. The host would have to remember every take they made and which episode it was in. This skill does that work: it reads the past N episodes, identifies recurring themes (named entities and recurring frames), and for an upcoming episode whose run-of-show is drafted, suggests specific callbacks that fit the planned topics.

The output is two files: a focused callbacks document for the upcoming episode, and a broader themes map the host can browse to spot connections.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `target_episode` | string | latest with run-of-show but not yet recorded | Episode to suggest callbacks for. |
| `lookback_episodes` | int | 10 | How many published episodes to scan back. |
| `min_theme_episodes` | int | 2 | A theme must appear in at least this many episodes to surface as a callback candidate. |
| `theme_categories` | string | all | Comma-separated subset: `companies`, `people`, `frames`, `predictions`. Restrict the scan if useful. |

## Outputs

| Output | Path | Notes |
|---|---|---|
| Callbacks for upcoming episode | `outbox/episodes/EP###/callbacks.md` | Focused on what the host should reference in the next recording. |
| Themes map | `outbox/themes/themes-YYYY-MM-DD.md` | Broader catalog of running threads across the lookback window. Overwritten each run with today's date. |

## Process

When this skill activates, follow these steps in order.

1. **Verify config and resolve the target episode.**
   - If `config/podcast.yaml` is missing, redirect to `podcast-init`.
   - Resolve `target_episode`. The default is the most recent episode in the editorial calendar that has a `run-of-show.md` and is not yet `recorded`.
   - If the target has no run-of-show, stop and direct the user to run `episode-program` first.

2. **Load the lookback set.**
   - Pull the last `lookback_episodes` published episodes from the editorial calendar.
   - For each, load `transcript-clean.md` (preferred), `run-of-show.md`, and any `briefs/topic-N.md`. Skip episodes missing all three.

3. **Extract candidate theme units per episode.**

   - **Companies** — named companies that appeared (Anthropic, Spotify, OpenAI, etc.). Track every mention plus the host's stance ("bullish", "skeptical", "neutral").
   - **People** — named operators, founders, executives. Track stance and the specific take.
   - **Frames** — recurring framings the host applied ("commoditization", "routing business", "churn defense", "platform-vs-product"). These are the host's mental models.
   - **Predictions** — explicit calls the host made ("Apple is two quarters away from copying this", "OpenAI will respond on price within a week"). Tag with the episode and the time horizon.

4. **Cluster and score.**
   - Cluster theme units across episodes. A "company" appearing in three episodes counts as one thread with three data points.
   - Score each thread for callback value: recency-weighted frequency, prediction-resolution opportunities (a prediction that has now come true or failed gets a high score), and stance-shift detection (the host changed their mind — that is callback gold).
   - Drop threads that appear in fewer than `min_theme_episodes` episodes.

5. **Match against the target episode's run-of-show.**
   - Read the target episode's `run-of-show.md` and topic IDs.
   - For each thread, check whether it intersects with any topic on the target rundown. Examples of intersection: same company, same frame, related industry, prediction maturity.
   - Surface the highest-scoring intersections as callback candidates.

6. **Generate suggested phrasings.**
   - For each callback candidate, write a one-line draft of how the host could drop the callback. Voice-checked.
   - Include the source episode, date, and the original language so the host can decide whether the phrasing rings true.
   - Mark predictions that resolved: "EP037 you said Apple was two quarters away from a programmatic audio play. They announced it Monday."

7. **Write the callbacks file.**
   - Path: `outbox/episodes/EP###/callbacks.md`.
   - Format:

     ```markdown
     # EP### — Callback Opportunities

     Lookback: 10 episodes. Themes meeting threshold: 8.

     ## Resolved predictions

     ### EP037 — Apple programmatic audio
     Original take: "Apple is two quarters away from a programmatic audio play."
     What happened: Apple announced Apple Audience Network on Monday.
     Suggested callback: "Three weeks ago I said Apple was two quarters away. They beat me by a quarter."

     ## Stance shifts to acknowledge

     ### Anthropic pricing strategy
     EP032: "Anthropic won't cut prices in 2026."
     EP041: "Sonnet 5 just dropped 40% — they cut."
     Suggested callback: "I was wrong on this in February. Worth saying out loud."

     ## Continuing threads

     ### Spotify routing-business framing
     Established: EP024 ("the routing business").
     Reinforced: EP031, EP041.
     Today's relevance: Spotify Q1 earnings on the rundown.
     Suggested callback: "We've been calling this the routing business since EP024. Today's call confirmed it."

     ## Threads worth not naming this episode

     - "AI commoditization" frame appeared in 6 of last 10 episodes. Host has used the word "commodity" 11 times in those episodes. Consider giving it a rest this week — repetition risks the listener tuning it out.
     ```

8. **Write the themes map.**
   - Path: `outbox/themes/themes-YYYY-MM-DD.md`.
   - Catalog every thread that met the `min_theme_episodes` threshold, grouped by category (companies, people, frames, predictions).
   - For each thread: list every episode it appeared in, the host's stance per episode, and any prediction maturity.
   - This file is the host's reference for "what have I been saying" without having to re-listen.

9. **Voice check.**
   - Generated phrasings pass `style/voice.md`. Direct quotes from past transcripts are not rewritten — they are the host's own past words.

10. **Print summary.**
    - Episodes scanned, threads found, callbacks suggested for the target episode, resolved predictions count, stance shifts count, file paths.
    - Suggested next: skim `callbacks.md` before recording. Decide which to use.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| Filesystem read | Transcripts, run-of-show, briefs, calendar | Required. |
| Filesystem write | callbacks.md and themes-YYYY-MM-DD.md | Required. |

The skill is local-only. No external APIs.

## Examples

### Example 1: Default — find callbacks for the next episode

User: *"find callbacks for EP043"*

```
Episodes scanned: 10. Lookback: EP033 to EP042.
Threads found: 14. Above threshold (>=2 episodes): 8.

Callbacks for EP043:
  Resolved predictions: 1 (Apple programmatic audio)
  Stance shifts: 1 (Anthropic pricing)
  Continuing threads: 3 (Spotify routing, AI commoditization, founder-talent flight)
  Threads to rest: 1 (AI commoditization frame — overused)

Outputs:
  outbox/episodes/EP043/callbacks.md
  outbox/themes/themes-2026-05-08.md

Read callbacks.md before recording. Pick 1–2 to use.
```

### Example 2: Restrict to companies only

User: *"what running threads do we have on specific companies"*

Skill runs with `theme_categories: companies` and produces a themes map filtered to company-level threads. Useful for spotting a company the host has been quiet on for several episodes that may be due for a return.

### Example 3: First-time run, thin lookback

User runs the skill on a brand-new show with only 3 published episodes. Output:

```
Episodes scanned: 3. Threads above threshold: 0 (need 2+ episodes; almost everything is single-mention).

callbacks.md written but mostly empty. Themes map written for the 3 episodes — useful as a baseline for future runs.
Rerun this skill after EP005 publishes to see real patterns.
```

The skill does not pad with weak suggestions when the data is thin.
