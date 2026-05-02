---
name: topic-radar
description: Scan configured sources for episode-worthy material and produce a ranked topic shortlist for an upcoming podcast episode. Pulls from the show's configured RSS feeds, websites, earnings calendars, newsletters, and X/Twitter lists, scores each candidate against the show's audience, and writes a markdown table with hooks and "why this matters now" notes. Run this skill when the user says "find topics", "what should we cover", "topic ideas", "what's worth talking about this week", "scan the sources", "run topic radar", "what's in the news for the show", or any equivalent prompt asking what the next episode could be about. This skill is the upstream input to episode-program.
version: 0.1.0
---

## Purpose

This is the editorial scanner. It replaces the executive producer task of waking up Monday morning, opening fifteen tabs, and trying to figure out what is worth covering this week.

The skill reads the show's configured sources, pulls items from a recent window, deduplicates, scores each item against the show's audience and tone, and hands back a ranked shortlist with one-line hooks and a "why this matters now" note per item. The host scans the table, picks two or three, and feeds those IDs into `episode-program`.

The output is ammunition for a human editorial decision, not a final pick. The model ranks; the host chooses.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `theme` | string | none | Free-form filter ("earnings", "AI safety", "leadership transitions", "antitrust"). Matching items get a relevance boost; non-matching items can still appear if their score is high. |
| `lookback_days` | int | from config (`topic_sources.default_lookback_days`, fallback 7) | Window to scan back from today. |
| `max_items` | int | 20 | Maximum number of items in the output table. |
| `min_score` | float | 5.0 | Items below this score are dropped from the main table and listed in a "Below threshold" section with a one-line reason. |

## Outputs

| Output | Path | Notes |
|---|---|---|
| Topic shortlist | `outbox/topics/YYYY-MM-DD.md` | Markdown table with stable IDs the user passes to `episode-program`. Date stamp is the run date; running twice in one day overwrites. |
| Run summary | stdout | Sources scanned, items returned, top 3 by name. |

## Process

When this skill activates, follow these steps in order.

1. **Verify config exists.**
   - If `config/podcast.yaml` is missing, stop and tell the user to run `podcast-init` first. Do not fabricate sources.

2. **Load context.**
   - Read `show.audience`, `show.description`, and `show.cadence` from the config. These calibrate scoring.
   - Read `topic_sources` from the config: RSS feeds, websites, earnings calendars, newsletters, X/Twitter lists.
   - Read any existing `outbox/episodes/EP*/debrief.md` files. The most recent debrief notes inform scoring (what worked, what to avoid covering again soon).

3. **Resolve inputs.**
   - Apply the theme filter, lookback window, and limits from inputs or config defaults.

4. **Fetch from each source category.**
   - **RSS feeds:** fetch each feed, parse entries, keep entries within the lookback window.
   - **Websites:** fetch the homepage or section page, extract headline + link + date.
   - **Earnings calendars:** pull companies reporting in the next 7 days plus those that reported in the lookback window.
   - **Newsletters:** if Gmail connector is available, pull recent issues from the configured senders. Otherwise skip and note in summary.
   - **X/Twitter lists:** if a Twitter/X connector is available, pull top items from the configured lists. Otherwise skip.
   - For any source that fails (timeout, 404, auth error), log the failure and continue.

5. **Normalize and deduplicate.**
   - Convert each item to a common shape: `{ id, title, url, source, published_at, summary }`.
   - Dedupe by URL. Then by near-duplicate title (same story from multiple outlets) — keep the best-sourced version.

6. **Score each item (0–10).**
   - **Audience fit (0–4):** how well the item lands with the configured audience. A founder-story for a founder show scores high; a celebrity gossip item scores low.
   - **Public-perception angle (0–2):** is this something people are talking about, or that the host can have an opinion on? Pure technical news without a stakeholder lens scores lower.
   - **Surface area for analysis (0–2):** named characters, real numbers, contrarian read available, historical parallel reachable.
   - **Timeliness (0–1):** newer is better, but evergreen depth can offset.
   - **Theme match (0–1):** if `theme` was passed and the item matches.
   - **Recency penalty (–0..–3):** if recent debriefs covered the same company, story, or theme, deduct.

7. **Generate per-item copy.**
   - **Hook:** one sentence under 20 words that frames the angle, written in the show's voice (active, no banned words, no clichés).
   - **Why this matters now:** one sentence on the time pressure or the public-attention reason.

8. **Rank and slice.**
   - Sort by score, descending.
   - Keep the top `max_items` for the main table. Items between `min_score` and the cutoff go in a "Below threshold" section so the host can spot something the model underrated.

9. **Write the markdown file.**
   - Path: `outbox/topics/YYYY-MM-DD.md` using today's date.
   - Format:

     ```markdown
     # Topic Shortlist — YYYY-MM-DD

     Lookback: 7 days. Theme filter: none. Sources scanned: 4 RSS, 2 sites, 1 earnings calendar.

     ## Shortlist

     | ID | Topic | Hook | Why now | Score | Source |
     |----|-------|------|---------|-------|--------|
     | T-YYYYMMDD-01 | ... | ... | ... | 9.2 | TechCrunch |

     ## Below threshold

     - T-YYYYMMDD-21 — [Title](url) — score 4.8 — covered similar story in EP012
     ```

   - Use stable IDs in the format `T-YYYYMMDD-NN`. These are what the host passes to `episode-program`.

10. **Print summary.**
    - Sources scanned, items fetched, items kept, items below threshold, top 3 by name and score.
    - Suggested next command: `episode-program` with two or three IDs from the shortlist.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| WebFetch / HTTP | Pull RSS feeds, websites, earnings pages | Source skipped with a logged error; other sources continue. |
| Gmail | Pull newsletter issues from configured senders | Skip newsletter sources; note in summary. |
| X / Twitter API | Pull top items from configured lists | Skip those lists; note in summary. |
| Filesystem read | Load past debriefs from `outbox/episodes/EP*/debrief.md` for the recency penalty | If no debriefs exist, skip the penalty and proceed with raw scoring. |

The skill never blocks because of a missing connector. Each missing source is logged in the run summary so the host knows the picture is incomplete.

## Examples

### Example 1: Default run

User: *"what's worth covering this week"*

```
Topic shortlist for 2026-05-01 written to outbox/topics/2026-05-01.md.
Sources: 4 RSS, 2 websites, 1 earnings calendar (Twitter list skipped — no connector).
20 items kept, 6 below threshold.
Top 3:
  T-20260501-01  Anthropic Opus 5 launch — 9.4
  T-20260501-02  Spotify earnings beat, podcast ad revenue up 28% — 9.1
  T-20260501-03  OpenAI cuts Plus pricing — 8.8
Pick two or three and run: episode-program --topics T-20260501-01,T-20260501-02
```

### Example 2: Theme filter

User: *"find topics about earnings this week"*

Skill applies `theme: earnings`, boosts earnings calendar and finance-source items, and weights the table accordingly. Output table leads with earnings stories; non-earnings items still appear if they scored highly on their own.

### Example 3: Empty week

User runs the skill on a slow news week. Output:

```
Topic shortlist for 2026-05-01 written to outbox/topics/2026-05-01.md.
14 items below threshold, 6 in the shortlist. Top score 7.1.
This is a thin week. Consider widening lookback_days, adding a theme,
or running an evergreen segment from past show prep.
```

The skill is honest when material is thin rather than fluffing the list.
