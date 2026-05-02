# Virtual Executive Producer — Claude Code Build Prompt

You are building a reusable, open-source toolkit of Claude skills that automate the executive producer role for a solo-host conversational podcast. The end deliverable is a GitHub-ready project that another podcaster can clone, run an init, and use immediately.

## Project context

The reference show: a topical business commentary podcast in the StarTalk format. Primary host speaks ~90% of the time. A co-host living remotely throws out articles, news items, earnings reports, and follow-up questions to drive pacing. The host responds extemporaneously, drawing on deep operating experience.

Audience: business builders, executives, and founders. Tone: conversational, energetic, opinionated. Each episode covers two or three current items — articles, earnings reports, market moves, leadership stories — with the host providing analysis through a public-perception lens.

Secondary goal: every recorded episode produces 5–10 short clips (60–90 seconds) suitable for Instagram Reels, TikTok, and YouTube Shorts.

## Build philosophy

Build skills that hand the host ammunition, not scripts. The host speaks extemporaneously — research briefs should surface facts, contrarian angles, and surprising data points the host can pull from on the fly, never paragraphs of prepared remarks.

Skills must be composable. Output of one skill becomes input to the next: topic-radar feeds episode-program, episode-program feeds research-brief, transcripts feed show-notes and clip-finder, those feed distribution-pack.

Every skill must be runnable standalone with sensible defaults if upstream skills haven't been run. No hard dependencies between skills — only soft references through the config file.

Keep the project portable. Anyone who clones the repo and runs the init should be productive within one episode cycle.

## Phase 1 — Research and architecture

Start by researching current best practices for podcast executive producers. Use web search to confirm role definitions, then synthesize a one-page reference document at `docs/EP_ROLE.md`. Cover: editorial vision, show format ownership, talent direction, production scheduling, quality control, brand consistency, distribution strategy, performance review. Note which functions a solo creator can reasonably automate and which still need human judgment.

Use this synthesis to validate the skill list below. Adjust if research surfaces a function I've missed for this format.

## Phase 2 — Initialization skill

Build `skills/podcast-init/SKILL.md` first. This skill runs once when a new user clones the repo. It captures:

- Show name, tagline, audience description, voice and tone notes
- Recording stack, hosting platform, transcription provider
- Publishing destinations (Spotify, Apple, YouTube, etc.)
- Brand assets paths (logo, color palette, episode art template)
- Recurring segments and their structure
- Co-host name and contact preference
- Output targets: which Google Drive folder for run-of-show docs, which Notion database for the editorial calendar, etc.
- Default episode cadence and target runtime
- Newsletter tie-in toggle (host runs The Build newsletter; episodes should optionally produce a tie-in draft)

The init writes everything to `config/podcast.yaml`. Every other skill reads from this file. If the file is missing, skills should prompt the user to run init first.

## Phase 3 — Core skills (build in this order)

### topic-radar
Scans configured sources for episode-worthy material: business news, earnings calendars, founder stories, industry reports. Sources defined in config. Outputs a ranked shortlist with one-sentence hooks, a "why this matters now" note, and a relevance score against the show's audience.

Inputs: optional theme filter, lookback window (default 7 days).
Outputs: markdown table saved to `outbox/topics/YYYY-MM-DD.md`.

### episode-program
Takes 2–3 selected topics and produces a run-of-show. Creates a Google Doc through the Google Drive connector so the co-host can review async. Structure: cold open hook, segment-by-segment breakdown with time targets, host talking points (bullet ammunition, not scripted lines), suggested co-host setups and follow-up questions, transitions, closing call-to-action.

Inputs: topic IDs from topic-radar output, target runtime.
Outputs: shareable Google Doc URL, local copy in `outbox/episodes/EP###/run-of-show.md`.

### research-brief
For each topic on the rundown, produces a one-page brief: key facts with sources, three contrarian or non-obvious angles, surprising stats, relevant historical parallels, names and quotes the host might want to reference. Cite every claim with a working URL.

Inputs: topic from rundown, depth level (light, standard, deep).
Outputs: `outbox/episodes/EP###/briefs/topic-N.md`, optional Google Doc.

### cohost-brief
Produces a separate Google Doc for the remote co-host. Different audience, different framing than the master run-of-show. Contains: cold-open setup line the co-host delivers, segment-by-segment "throw" lines that hand off to the host, two to four follow-up questions per segment, articles and links the co-host should have queued, pacing notes (when to interject, when to let the host run uninterrupted), recurring segment cues if applicable.

Pulls from the run-of-show and optionally from research briefs so the co-host has the same factual grounding without rereading every brief.

Inputs: episode ID, optional question density (light, standard, heavy).
Outputs: shareable Google Doc URL, local copy in `outbox/episodes/EP###/cohost-brief.md`.

### show-notes
Post-production. Consumes a transcript (or audio file path for transcription via configured provider) and produces:
- Three title options under 100 characters each, optimized for YouTube and podcast platforms
- Episode description (long-form for YouTube, short for Apple/Spotify)
- Chapter markers with timestamps
- Five key takeaways
- All links and references mentioned in the episode
- Cleaned-up transcript with filler words removed

Outputs: `outbox/episodes/EP###/show-notes.md`.

### clip-finder
Scans the transcript for clip-worthy moments. Targets: punchy openers, contrarian takes, surprising stats, emotional beats, complete narrative arcs that stand alone without context. Each candidate clip includes start and end timestamps, a transcript excerpt, a suggested hook caption, a platform recommendation (Reels, TikTok, Shorts), and a why-this-clips note.

Aim for 8–12 candidates per episode. Quality over quantity.

Outputs: `outbox/episodes/EP###/clips.md` and a JSON file editors can import.

### distribution-pack
Generates ready-to-post assets:
- LinkedIn post (host-voice, 1300–2000 characters)
- X/Twitter post and a 4-tweet thread option
- Instagram caption for the audiogram or clip
- YouTube community post
- Newsletter tie-in section for The Build (if enabled in config)

Where the Blotato connector is available, schedule posts directly. Otherwise output drafts to `outbox/episodes/EP###/distribution.md`.

### editorial-calendar
Maintains the show's lineup in a Google Sheet (created during init, ID stored in config). Tracks: episode number, working title, status (idea, scheduled, recorded, edited, published), topics covered, recurring segments hit, target publish date, actual publish date, runtime, download or view counts once available, top-performing clip, notes.

Also writes recording dates and publish dates to a Google Calendar (calendar ID in config) so the co-host sees the schedule in their own calendar app.

Provides a `next-episode` command that returns what's on deck and what's missing.

### post-show-debrief
Closes the loop. Pulls early performance data from configured analytics, summarizes listener comments if available, scores the episode against its own goals. Writes to `outbox/episodes/EP###/debrief.md` and updates the editorial calendar entry. Feeds insights back to topic-radar's relevance scoring over time.

## Phase 4 — Templates and examples

Create `templates/` with markdown skeletons for each output type: run-of-show, research brief, show notes, clip spec, distribution pack, debrief. Skills fill these templates rather than generating structure from scratch.

Create `examples/sample-episode/` showing one complete cycle: topic shortlist → run-of-show → briefs → mock transcript → show notes → clips → distribution pack → debrief. Use a fictional episode topic so the example ships with the repo.

## Phase 5 — Documentation

Write a `README.md` that covers: what this is, who it's for, the StarTalk-style format it assumes, quick-start (clone, install, run init, run topic-radar), the skill catalog, a workflow diagram showing how skills compose, and customization notes for podcasters with different formats.

Write a `CONTRIBUTING.md` for adapting skills to other formats (interview-driven shows, narrative shows, panel shows). Note which skills need rework for each format.

## SKILL.md conventions

Every skill folder contains a single `SKILL.md` with this structure:

1. YAML frontmatter: name, description (written for trigger accuracy — what the skill does and when to invoke it), version
2. Purpose section: one paragraph
3. Inputs: explicit list with types and defaults
4. Outputs: explicit list with file paths
5. Process: numbered steps Claude follows when the skill activates
6. Connectors and APIs used: list with fallback behavior if unavailable
7. Examples: at least one complete invocation with sample inputs and abbreviated outputs

Descriptions matter most. Write them so Claude reliably triggers the right skill from natural language. Test trigger phrasing against multiple paraphrases before considering a skill done.

## Tech assumptions and connectors

The project anchors on Google Workspace. Run-of-show docs, co-host briefs, and research briefs live in Google Drive. The editorial calendar is a Google Sheet. Recording and publish dates write to Google Calendar. Optional comms to the co-host go through Gmail.

For social distribution, use Blotato when available — it handles cross-posting to LinkedIn, X, Instagram, and YouTube community. When Blotato isn't connected, write drafts to local files for manual posting.

For transcription, support pluggable providers: Whisper (local), AssemblyAI, Deepgram, Rev. User picks during init.

For analytics, support pluggable sources: Spotify for Podcasters, Apple Podcasts Connect, YouTube Studio, Buzzsprout. User picks during init.

When a connector or API isn't available, skills must degrade gracefully — write to local files and tell the user which manual step to take.

## Style guide for generated content

All host-facing and audience-facing copy follows these rules:

- Active voice, short sentences, direct address
- No clichés, no metaphor-heavy openers, no "in conclusion" or "in summary"
- No semicolons, no emojis, no hashtags in body copy
- Avoid: accordingly, additionally, arguably, certainly, consequently, hence, however, indeed, moreover, nevertheless, thus, undoubtedly, adept, commendable, dynamic, efficient, ever-evolving, exciting, exemplary, innovative, invaluable, robust, seamless, synergistic, transformative, vibrant, vital, efficiency, innovation, integration, implementation, landscape, optimization, realm, tapestry, transformation, aligns, augment, delve, embark, facilitate, maximize, underscores, utilize
- No "a testament to," "it's worth noting," "specifically," "on the contrary"

Bake these rules into a `style/voice.md` file the writing skills reference.

## Project structure

```
virtual-ep/
├── README.md
├── CONTRIBUTING.md
├── BUILD_PROMPT.md
├── config/
│   └── podcast.yaml.example
├── docs/
│   └── EP_ROLE.md
├── style/
│   └── voice.md
├── skills/
│   ├── podcast-init/SKILL.md
│   ├── topic-radar/SKILL.md
│   ├── episode-program/SKILL.md
│   ├── research-brief/SKILL.md
│   ├── cohost-brief/SKILL.md
│   ├── show-notes/SKILL.md
│   ├── clip-finder/SKILL.md
│   ├── distribution-pack/SKILL.md
│   ├── editorial-calendar/SKILL.md
│   └── post-show-debrief/SKILL.md
├── templates/
├── examples/
│   └── sample-episode/
└── outbox/
    ├── topics/
    └── episodes/
        └── .gitkeep
```

## Acceptance criteria

The project is done when:

1. A new user clones the repo, runs the init skill, and gets a populated `config/podcast.yaml`
2. Running topic-radar with no arguments produces a topic shortlist for the past week
3. Running episode-program against three selected topics produces a Google Doc URL the user can open
4. Running research-brief on each topic produces fact-cited briefs with working URLs
5. Running cohost-brief produces a separate Google Doc the co-host can open with setup lines, throws, and follow-up questions for each segment
6. Running show-notes against a sample transcript produces titles under 100 characters, a description, chapters, and a cleaned transcript
7. Running clip-finder against the same transcript produces 8+ clip candidates with timestamps and captions
8. Running distribution-pack produces post drafts in the configured voice with no banned words
9. Editorial-calendar reflects the current episode in the configured Google Sheet and shows what's on deck
10. The example episode walks through the full cycle end to end
11. Every SKILL.md description triggers reliably across at least three paraphrased prompts

## Stretch goals (after core works)

- A `recurring-segment` framework so users can define custom segments (e.g., "Earnings Watch," "Founder of the Week") and have them populate automatically
- A `cross-episode-arc` skill that surfaces themes spanning multiple episodes and suggests callbacks
- A `voice-fingerprint` skill that learns the host's recurring phrases, opinions, and references from past transcripts so distribution-pack copy reads in the host's voice from day one

## How to start

Begin with Phase 1 research. Confirm the skill list. Build podcast-init. Then build topic-radar and episode-program in parallel since they form the upstream pair. Build research-brief and cohost-brief next since both depend on episode-program output. Show me each skill's SKILL.md before moving to the next so I can validate trigger phrasing and output format.

Ship the example episode last, after all skills work, so it reflects real outputs rather than mocked ones.
