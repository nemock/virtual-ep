# Virtual EP

A Claude-powered toolkit that automates the executive producer role for a solo-host conversational podcast. Clone the repo, run the init skill, and you have nine composable skills covering everything from topic scouting to post-show debriefs.

## What this is

Nine `SKILL.md` files Claude can invoke through natural language. Each one handles a piece of the executive producer's job:

- Scanning sources for episode-worthy material
- Building run-of-show docs and per-topic research briefs
- Producing a separate prep doc for the remote co-host
- Generating titles, descriptions, chapters, and a cleaned transcript from raw audio
- Surfacing 8–12 clip candidates per episode for short-form distribution
- Drafting platform-specific social copy with banned-word voice checks
- Maintaining the editorial calendar and syncing recording/publish dates to a shared calendar
- Pulling early performance data and writing a debrief that closes the loop

The skills compose. The output of one becomes input to the next. Each one also runs standalone with sensible defaults if upstream skills haven't been used.

## Who it's for

Solo creators running a topical conversational podcast in the StarTalk format — primary host who carries 80–95% of the talk time, with a remote co-host who throws articles, news items, and follow-up questions to drive pacing.

The reference show is business commentary aimed at founders and operators. The toolkit adapts to other commentary formats with light customization. Interview, narrative, and panel formats need more rework — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Format assumptions

The default skill set is built around these assumptions. If your show breaks them, expect to rework one or more skills.

- One primary host who speaks most of the time
- One remote co-host who introduces topics and drops follow-up questions
- Each episode covers two or three topics, ~45 minutes total runtime
- Topical material — current news, earnings, founder stories, leadership moves
- Public-perception lens on each topic (the host has an opinion, not just analysis)
- Audio + video distribution plus 5–10 short-form clips per episode
- Optional newsletter tie-in

## Quick start

```bash
# 1. Clone the repo
git clone <this-repo> my-podcast-ep
cd my-podcast-ep

# 2. Open it in Claude Code (or your Claude harness of choice)

# 3. Run the init skill
"set up the podcast"
# Walks through the interactive setup, writes config/podcast.yaml,
# creates the editorial calendar Google Sheet if Drive is connected.

# 4. Find topics for the next episode
"what's worth covering this week"
# Runs topic-radar, writes outbox/topics/YYYY-MM-DD.md.

# 5. Build the run-of-show
"plan the next episode with T-YYYYMMDD-01 and T-YYYYMMDD-02"
# Runs episode-program, writes outbox/episodes/EP001/run-of-show.md
# and creates a Google Doc if Drive is connected.

# 6. Per topic, build a research brief
"research T-YYYYMMDD-01"
"research T-YYYYMMDD-02"
# Each writes outbox/episodes/EP001/briefs/topic-N.md.

# 7. Build the co-host brief
"build the cohost brief"

# 8. Record. Then process the recording
"build show notes from this transcript: outbox/episodes/EP001/transcript-raw.md"

# 9. Find clips
"find clips for EP001"

# 10. Draft distribution
"build the distribution pack"

# 11. After the episode is live for a week
"debrief EP001"
```

## Skill catalog

| Skill | When to use | Output |
|-------|-------------|--------|
| `podcast-init` | First-time setup or any config change | `config/podcast.yaml` |
| `topic-radar` | "What should we cover this week?" | `outbox/topics/YYYY-MM-DD.md` |
| `episode-program` | Build the run-of-show for a recording | `outbox/episodes/EP###/run-of-show.md` (+ Google Doc) |
| `research-brief` | Per-topic deep prep | `outbox/episodes/EP###/briefs/topic-N.md` |
| `cohost-brief` | Co-host prep document | `outbox/episodes/EP###/cohost-brief.md` (+ Google Doc) |
| `show-notes` | Post-recording packaging | `show-notes.md`, `transcript-clean.md` |
| `clip-finder` | Surface short-form moments | `clips.md`, `clips.json` |
| `distribution-pack` | Draft platform-specific social copy | `distribution.md` (+ Blotato schedule) |
| `editorial-calendar` | Track the production pipeline | Google Sheet (or CSV) row, calendar event |
| `post-show-debrief` | Close the loop on a published episode | `debrief.md` + calendar update |

Three additional skills extend the toolkit once the show has a few episodes of history:

| Skill | When to use | Output |
|-------|-------------|--------|
| `recurring-segment` | Define and populate named beats like "Earnings Watch" with this week's material | `outbox/episodes/EP###/segments/<id>.md` |
| `cross-episode-arc` | Find callback opportunities and surface running threads | `outbox/episodes/EP###/callbacks.md`, `outbox/themes/themes-YYYY-MM-DD.md` |
| `voice-fingerprint` | Learn the host's voice from past transcripts | `style/voice-fingerprint.md` + optional config additions |

Each skill folder has a `SKILL.md` with full input/output specs, process steps, connector behavior, and examples.

## Workflow

```
              topic-radar
                 ↓ (host picks 2–3 topic IDs)
            episode-program
                 ↓
       ┌─────────┴──────────┐
       ↓                    ↓
 research-brief        cohost-brief
   (per topic)
       │                    │
       └──────── recording ─┘
                 ↓
            show-notes ────────→ transcript-clean.md
                 ↓
            clip-finder
                 ↓
          distribution-pack
                 ↓
                publish
                 ↓
         post-show-debrief
                 ↓
        feeds back into → topic-radar's relevance scoring
```

The editorial-calendar skill runs orthogonally — call it any time to check what's on deck or to mark status changes.

## Project structure

```
.
├── README.md
├── CONTRIBUTING.md
├── BUILD_PROMPT.md
├── config/
│   └── podcast.yaml.example
├── docs/
│   └── EP_ROLE.md            # Reference: what an EP does and what stays human
├── style/
│   └── voice.md              # Banned words, banned phrases, voice rules
├── skills/
│   ├── podcast-init/
│   ├── topic-radar/
│   ├── episode-program/
│   ├── research-brief/
│   ├── cohost-brief/
│   ├── show-notes/
│   ├── clip-finder/
│   ├── distribution-pack/
│   ├── editorial-calendar/
│   ├── post-show-debrief/
│   ├── recurring-segment/
│   ├── cross-episode-arc/
│   └── voice-fingerprint/
├── templates/                # Markdown skeletons each skill fills in
├── examples/
│   └── sample-episode/       # One complete cycle, fictional but illustrative
└── outbox/                   # Where every skill writes its output
    ├── topics/
    └── episodes/
```

## Connectors

The toolkit anchors on Google Workspace and degrades gracefully when a connector is unavailable.

| Connector | Used by | Fallback |
|-----------|---------|----------|
| Google Drive | episode-program, research-brief, cohost-brief | Local markdown files only |
| Google Sheets | editorial-calendar | `outbox/editorial-calendar.csv` |
| Google Calendar | editorial-calendar | Print dates to stdout |
| Gmail | cohost-brief, post-show-debrief | Print email bodies to stdout |
| Blotato | distribution-pack | Local drafts in `distribution.md` |
| Transcription (Whisper local / AssemblyAI / Deepgram / Rev) | show-notes | Required when audio is provided; choice picked during init |
| Analytics (Spotify / Apple / YouTube / Buzzsprout) | post-show-debrief | Skip the missing source, run the debrief on the rest |

No skill blocks because of a missing connector. Every fallback writes a local file the host can use manually.

## Customization

The toolkit is built for a specific format but most skills adapt with a single config change.

**Different cadence**: change `show.cadence` and `show.target_runtime_minutes` in `config/podcast.yaml`. Daily news shows can use the same skills with shorter target runtimes and tighter brief depth.

**Different segment structure**: edit the `segments` block. Add or remove recurring named segments — `episode-program` slots them into every run-of-show automatically.

**Different audience**: change `show.audience` and `show.description`. `topic-radar` and the writing skills calibrate scoring and voice against these fields.

**Different banned words**: extend `voice.banned_words_extra` and `voice.banned_phrases_extra` in the config without editing the canonical [style/voice.md](style/voice.md).

**Solo show, no co-host**: set `cohost.name` to empty. The `cohost-brief` skill will skip running and `episode-program` will produce a host-only rundown.

For format changes that go deeper than config — interview-led, narrative-led, panel — see [CONTRIBUTING.md](CONTRIBUTING.md).

## What this toolkit does not do

- It does not record. Use Riverside, Zencastr, SquadCast, or whatever you already use.
- It does not edit. Use Descript, Hindenburg, or your DAW of choice.
- It does not replace human editorial judgment. See [docs/EP_ROLE.md](docs/EP_ROLE.md) for the explicit list of decisions the host should keep on their own desk.
- It does not pad output. When a topic radar week is thin or a clip finder run produces only six candidates, the skill says so rather than fluffing the list.

## Reference

- [docs/EP_ROLE.md](docs/EP_ROLE.md) — what an executive producer does and which functions a solo creator can automate
- [style/voice.md](style/voice.md) — voice rules, banned words, banned phrases
- [config/podcast.yaml.example](config/podcast.yaml.example) — full configuration schema with comments
- [examples/sample-episode/](examples/sample-episode/) — one complete production cycle, illustrative
- [BUILD_PROMPT.md](BUILD_PROMPT.md) — the original spec this repo was built from

## License

MIT.
