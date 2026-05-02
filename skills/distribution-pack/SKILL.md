---
name: distribution-pack
description: Build the social distribution package for a published episode. Produces a LinkedIn post in the host's voice (1300–2000 characters), an X/Twitter single post plus a 4-tweet thread option, an Instagram caption built around the featured clip, a YouTube community post, and an optional newsletter tie-in section when the host runs a tie-in newsletter. Voice-checked against banned words and banned phrases. Schedules posts via Blotato when the connector is available; falls back to writing drafts to a local file. Run this skill when the user says "build the distribution pack", "draft the social posts", "social copy for EP042", "promote EP042", "make the LinkedIn post", "schedule the posts", "distribution pack", or any equivalent ask for episode promotion. Run after show-notes and clip-finder.
version: 0.1.0
---

## Purpose

Episode posts have to land in different shapes on different platforms. LinkedIn rewards length and structure. X rewards a sharp single line plus an optional thread. Instagram is built around the clip, not the caption. YouTube community posts are short and link-driven. The newsletter wants a self-contained 200–400 word section that fits the host's normal newsletter rhythm.

This skill drafts all five at once, in the show's voice, with the same factual grounding pulled from show-notes and the top-scoring clip from clip-finder. When Blotato is connected, it schedules. When it isn't, it writes drafts the host can copy and paste. Either way the host approves before anything ships.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `episode_number` | string | latest | Auto-detects the most recent `outbox/episodes/EP###/`. Override with explicit `EP042`. |
| `featured_clip_id` | string | top-scored clip from `clips.json` | Which clip ID to feature in the Instagram and X drafts. Override to choose a different one. |
| `platforms` | string | `linkedin,x,instagram,youtube,newsletter` | Comma-separated subset to generate. Drop any platform the host does not use. The skill reads `host.newsletter_tie_in.enabled` from config and skips the newsletter section if it is false. |
| `schedule_at` | datetime | none | If provided and Blotato is connected, schedule the posts at this time. Otherwise write drafts only. |
| `episode_url` | string | from config or detected | The published episode link. If not provided, the skill checks `publishing.show_urls` and the most recent post on the configured RSS feed. If it can't resolve a URL, it leaves a `[EPISODE URL]` placeholder and flags it in the run summary. |

## Outputs

| Output | Path | Notes |
|---|---|---|
| Distribution pack | `outbox/episodes/EP###/distribution.md` | All drafts in one file. Always written. |
| Scheduled posts | Blotato | Created when `schedule_at` is provided and Blotato is connected. |

## Process

When this skill activates, follow these steps in order.

1. **Verify config and episode folder.**
   - If `config/podcast.yaml` is missing, redirect to `podcast-init`.
   - If the episode folder has no `show-notes.md`, stop and direct the user to run `show-notes` first.

2. **Load context.**
   - Read `show-notes.md` (title options, descriptions, key takeaways, links).
   - Read `clips.json` to pick the featured clip (highest-scoring, or override).
   - Read `run-of-show.md` for the topic context.
   - Read `host`, `cohost`, `distribution`, and `voice` blocks from config.
   - Read `style/voice.md` for the voice check.

3. **Resolve the episode URL.**
   - If `episode_url` is provided, use it.
   - Otherwise, check `publishing.show_urls` for a hosting platform that exposes a permalink and try to detect the latest episode URL.
   - If neither resolves, leave `[EPISODE URL]` as a placeholder and flag it in the run summary so the host fills it in before publishing.

4. **Draft the LinkedIn post.**
   - 1300–2000 characters.
   - Structure: a one-line hook (the strongest take from the episode), a 2–3 line setup, the meat (3–5 short paragraphs or bullets carrying the main insight, named numbers, named people), a one-line landing, and a one-line CTA pointing to the episode.
   - Host voice: first person, active, opinionated. Reads like the host actually wrote it.
   - No hashtags in the body. The post may end with up to 3 relevant tags on a separate line if the host's standard pattern uses them.
   - No emojis (per `style/voice.md`).

5. **Draft the X single post.**
   - Under 280 characters total, including the URL.
   - One sharp line + the episode URL.
   - Should work as a standalone tweet without the thread.

6. **Draft the X thread (4 tweets).**
   - Tweet 1: the hook from the LinkedIn post, adapted for X length. Ends with "🧵" or "Thread:" only if that matches the host's normal pattern (check past episodes if available).
   - Tweets 2–3: two specific points from the episode. Named numbers, named companies, no filler.
   - Tweet 4: the landing + the episode URL.
   - Each tweet under 280 characters, including the URL on tweet 4.

7. **Draft the Instagram caption.**
   - 150–300 characters in the body.
   - Built around the featured clip — the caption should make sense paired with the clip the editor will post.
   - Hook in the first line (Instagram truncates at ~125 chars in feed; the first line has to land alone).
   - One-line description of what the clip is, plus a one-line CTA ("full episode in bio" or similar).
   - Hashtag block at the end on a separate line. Up to 8 platform-relevant tags, drawn from the show's topic area. No banned words. No fake-niche tags.

8. **Draft the YouTube community post.**
   - Under 500 characters.
   - One-line hook + one-line context + the episode URL.
   - This post sits on the channel community tab; it should feel like a heads-up to subscribers, not a paid ad.

9. **Draft the newsletter tie-in section (if enabled).**
   - Skip if `host.newsletter_tie_in.enabled` is false.
   - 200–400 words.
   - Written as a self-contained section the host can drop into the newsletter without rewriting. Carries the angle from the episode in the host's newsletter voice — slightly longer paragraphs than the LinkedIn post, fewer rhetorical hooks, more reasoned.
   - Ends with one line of "if you want to go deeper, the full episode is here: [URL]".

10. **Voice check every draft.**
    - Every piece passes `style/voice.md` plus `voice.banned_words_extra` and `voice.banned_phrases_extra` from config.
    - Required phrases from `voice.required_phrases` are present where natural — the skill does not force them into pieces where they do not fit.
    - Active voice. No semicolons. No emojis (in body copy; platform-appropriate exceptions like the "🧵" thread marker are allowed if the host's pattern uses them).

11. **Schedule via Blotato or write drafts.**
    - If `distribution.blotato.enabled` is true and the Blotato connector is available and `schedule_at` is provided: schedule each post on the corresponding account from `distribution.blotato.accounts`. Newsletter tie-in is always written to file regardless — it goes into the host's newsletter tool manually.
    - Otherwise, write everything to `outbox/episodes/EP###/distribution.md`.

12. **Write the distribution file.**
    - Path: `outbox/episodes/EP###/distribution.md`.
    - Format: one section per platform, each with a header, the character count, the draft body, and (if scheduled) the Blotato post ID.

13. **Print summary.**
    - Episode number, platforms generated, character counts per piece, voice-check status (clean or flagged words), scheduled vs draft state, file path, any URL placeholders left to fill.
    - Suggested next: schedule the posts in Blotato (if not already), then run `editorial-calendar` to mark the episode as published if not already done.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| Filesystem read | Load show-notes, clips.json, run-of-show, config | Required. |
| Blotato | Schedule posts to LinkedIn, X, Instagram, YouTube community | Drafts written to `distribution.md` for manual posting. |
| RSS / hosting platform | Detect the latest episode URL | Leave `[EPISODE URL]` placeholder. |
| Newsletter platform | Push the tie-in section | None. Always written to file for manual paste. |

## Examples

### Example 1: Full pack, Blotato scheduled

User: *"build the distribution pack for EP042 and schedule for tomorrow at 9am"*

```
EP042 — distribution pack

LinkedIn:    1820 chars  voice-clean  scheduled (Blotato id b_xyz1)
X (single):  271 chars   voice-clean  scheduled (Blotato id b_xyz2)
X (thread):  4 tweets    voice-clean  scheduled (Blotato id b_xyz3)
Instagram:   246 chars   voice-clean  scheduled (Blotato id b_xyz4)
YouTube:     412 chars   voice-clean  scheduled (Blotato id b_xyz5)
Newsletter:  340 words   voice-clean  written to file (manual paste)

All scheduled for 2026-05-02 09:00 PT.
Featured clip: C-EP042-01 (9.4 score).
Drafts also saved to outbox/episodes/EP042/distribution.md.
```

### Example 2: Drafts only, no Blotato

User: *"make the social copy for EP042"*

Skill writes all drafts to `outbox/episodes/EP042/distribution.md`. Run summary lists character counts and any voice-check flags, plus a note that Blotato is not connected so the host pastes manually.

### Example 3: Subset of platforms

User: *"draft only the LinkedIn and newsletter section for EP042"*

Skill runs with `platforms: linkedin,newsletter`, generates only those two pieces, skips X / Instagram / YouTube. Other platforms are not written to the distribution file at all.

### Example 4: Episode URL not yet live

User runs distribution-pack the morning of publish, before the episode is actually live on hosting platforms. Skill cannot resolve the URL, leaves `[EPISODE URL]` placeholders, and flags this clearly in the run summary so the host fills the URL in before scheduling or pasting.
