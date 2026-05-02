---
name: post-show-debrief
description: Close the loop on a published episode. Pulls early performance data from configured analytics providers (Spotify for Podcasters, Apple Podcasts Connect, YouTube Studio, Buzzsprout), summarizes listener comments and reviews where available, identifies the top-performing clip, scores the episode against the show's running median, and writes a debrief that updates the editorial calendar entry. The debrief also feeds back into topic-radar's relevance scoring on future runs. Run this skill when the user says "debrief EP042", "post-show debrief", "how did EP042 do", "wrap up EP042", "close the loop on EP042", "analyze the numbers", "performance review for EP042", or any equivalent ask after the episode has been live for at least a few days. Default window is 7 days post-publish.
version: 0.1.0
---

## Purpose

The debrief is the part the host most often skips. Without it the show stops learning. This skill makes the loop closure cheap: pull the numbers, summarize the comments, identify which clip carried, write a one-page debrief that the next topic-radar run reads to calibrate scoring.

The output is a file the host can scan in two minutes plus a handful of structured updates that go back into the editorial calendar and into the system's memory of the show.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `episode_number` | string | most recent published | Auto-detects the most recent episode in the calendar with `status: published`. Override with explicit `EP042`. |
| `window_days` | int | 7 | Days after `actual_publish_date` to pull data for. Use a longer window for an evergreen episode. |
| `compare_to` | string | `running_median` | What to score against. Options: `running_median` (default, the show's median over the last 10 published episodes), `previous_episode`, or `target` (a specific number passed via `target_downloads`). |
| `target_downloads` | int | none | When `compare_to` is `target`, the explicit number to compare against. |

## Outputs

| Output | Path | Notes |
|---|---|---|
| Debrief | `outbox/episodes/EP###/debrief.md` | One-page debrief. Always written. |
| Calendar update | Google Sheet row (or CSV fallback) | Updates `downloads`, `views`, `top_clip_id`, `notes` on the EP### row. |
| Topic-radar feedback | Implicit | The debrief is read by future `topic-radar` runs to inform the recency penalty and audience-fit scoring. No separate file needed. |

## Process

When this skill activates, follow these steps in order.

1. **Verify config and episode state.**
   - If `config/podcast.yaml` is missing, redirect to `podcast-init`.
   - Look up the episode in the editorial calendar. If `status` is not `published`, stop and tell the user the episode must be published before debrief.
   - If `actual_publish_date` is unset, ask the user for it.

2. **Pull analytics from each enabled provider.**
   - For each `analytics.<provider>: true` in config, attempt to pull data for the episode within the window.
   - **Spotify for Podcasters**: streams, listeners, plays, completion rate per episode.
   - **Apple Podcasts Connect**: plays, listeners, follow-through rate.
   - **YouTube Studio**: views, watch time, average view duration, like ratio.
   - **Buzzsprout**: downloads (the closest analog to the IAB metric most podcasters care about).
   - For each provider that fails (auth expired, rate limit, no data yet), log the failure and continue.

3. **Pull comments and reactions.**
   - **YouTube comments**: top 20 by like count + the most recent 20.
   - **Apple Podcasts reviews**: any new reviews in the window.
   - **Spotify Q&A or comments**: any responses in the window if the platform exposes them.
   - **X mentions**: search for the episode URL or the show handle within the window if X access is available.
   - **LinkedIn comments**: pull comments on the distribution-pack LinkedIn post if accessible.
   - For each missing source, log and continue.

4. **Summarize comment sentiment.**
   - Group comments into: positive (specific praise), critical (specific complaints, usefully so), questions, off-topic.
   - Surface the 3 most-substantive comments verbatim — not the most-positive, the most-substantive. A sharp critique often beats six "great episode!" replies for learning value.

5. **Identify the top-performing clip.**
   - For each clip in `clips.json`, look up its performance on the platforms it was posted to (via Blotato API if scheduled there, or via direct platform analytics).
   - Pick the highest-engagement clip and store its ID in the calendar row's `top_clip_id` field.
   - Note in the debrief why the host thinks it worked (drawn from the clip's category, hook, and structure).

6. **Score the episode.**
   - Compute the comparison metric per `compare_to`:
     - `running_median`: median downloads (or the show's primary metric) over the last 10 published episodes excluding this one.
     - `previous_episode`: the immediately previous episode's number.
     - `target`: the explicit `target_downloads` value.
   - Express this episode's number as `X% of comparison` and as an absolute delta.
   - Score 1–5: `5` = top quintile, `4` = above median, `3` = at median, `2` = below median, `1` = bottom quintile of the running 10.

7. **Score against episode-specific goals.**
   - Read the episode's `run-of-show.md` and `cohost-brief.md` to extract any explicit goals the host set (segment time targets, named CTAs, newsletter mentions).
   - Compare actuals from the cleaned transcript and show-notes runtime against those goals. Note any segment that ran significantly long or short.

8. **Build the debrief.**

   Sections in this order:

   - **Headline numbers**: 3–5 lines. Downloads, views, completion, top clip, score.
   - **What worked**: 3 bullets. Specific moments, segments, or framings that drew engagement (drawn from comments and clip performance).
   - **What didn't**: 3 bullets. Specific issues. If a segment ran long, name it. If a topic underperformed expected interest, name it.
   - **Comments worth surfacing**: the 3 most-substantive comments verbatim with attribution.
   - **Goal-tracking**: a short table of planned vs actual on segment runtimes and named goals.
   - **Lessons for next time**: 3 bullets. Concrete adjustments — not platitudes. "Cut earnings watch to 6 minutes" beats "improve pacing".
   - **Topic-radar signal**: 1–2 lines explicitly written for the next topic-radar run to consume — what to over-weight, what to under-weight, what to avoid covering again soon.

9. **Voice check.**
   - All generated copy passes `style/voice.md` plus `voice.banned_words_extra`. Comments quoted verbatim are not rewritten — they are the audience's words.

10. **Update the editorial calendar.**
    - Set `downloads`, `views`, `top_clip_id`, and append a one-line entry to `notes` ("Debrief 2026-05-08: hit 112% of running median; earnings watch ran 4 min long; clip C-EP042-01 carried.").

11. **Print summary.**
    - Episode number, headline numbers, score, top clip, sources successfully pulled, sources that failed, debrief path, calendar update confirmation.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| Spotify for Podcasters API | Pull episode performance | Skip; note in debrief that Spotify data is unavailable. |
| Apple Podcasts Connect API | Pull episode performance | Skip; note. |
| YouTube Data API + YouTube Studio | Pull views, watch time, comments | Skip; note. |
| Buzzsprout API | Pull downloads | Skip; note. |
| Blotato API | Pull clip post engagement | Skip; ask the user to provide top-clip ID manually if known. |
| X / LinkedIn search | Pull mentions and comments | Skip; note. |
| Google Sheets / CSV | Update editorial calendar row | CSV fallback. |
| Filesystem read | Read run-of-show, cohost-brief, clips.json, show-notes | Required. |

The skill is robust to partial-source failures. A debrief with only Buzzsprout and YouTube data is still a useful debrief; the run summary names what was missing so the host can decide whether to wait for more data or ship the loop closure now.

## Examples

### Example 1: Default — recent episode

User: *"debrief EP042"*

```
EP042 — "Anthropic Opus 5 and the Spotify ad business"
Window: 7 days post-publish (2026-05-01 to 2026-05-08).

Headline numbers:
  Downloads: 2,318  (112% of running median)   score 4/5
  YouTube views: 4,210
  YouTube avg view duration: 11:34 (38% of total)
  Top clip: C-EP042-01 — 84,000 views on TikTok, 21,000 on Reels.

What worked: contrarian Spotify ad take landed. C-EP042-01 carried clip distribution.
What didn't: earnings watch ran 4 min long, dropped Apple completion rate.
Sources pulled: Buzzsprout ✓, YouTube ✓, Spotify ✗ (auth expired), Apple ✓.
Comments surfaced: 3.

Debrief written to outbox/episodes/EP042/debrief.md.
Calendar updated: downloads, top_clip_id, notes.
```

### Example 2: Compare to previous episode

User: *"how did EP042 do compared to EP041"*

Skill runs with `compare_to: previous_episode`. Output expresses EP042 as a percentage of EP041's downloads and notes the absolute delta. Useful when running median is skewed by one outlier.

### Example 3: Partial data, run anyway

User runs debrief 48 hours after publish. Some platforms have no data yet. Output:

```
EP042 — partial debrief (window 2 days, recommended 7).

Buzzsprout: 1,140 downloads (data still rolling in).
YouTube: too early — Studio shows insufficient data for this window.
Top clip: not yet calculable; rerun in 5 days.

Debrief written with available data and flagged as partial. Recommend rerunning the
skill in five days for full numbers. Calendar updated with current downloads only.
```

The skill never fabricates a number. Partial data ships as partial.
