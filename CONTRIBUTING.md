# Contributing

This toolkit is opinionated. The default skill set is built for a solo-host conversational commentary show in the StarTalk format. Other formats work with varying degrees of rework. This document maps the differences.

## How the skills are structured

Every skill is a single `SKILL.md` file with seven sections:

1. YAML frontmatter (name, description, version)
2. Purpose
3. Inputs
4. Outputs
5. Process
6. Connectors and APIs
7. Examples

The description in the frontmatter is the trigger string Claude uses to decide when to invoke the skill. Description quality matters more than any other field — write it so the skill fires reliably across at least three paraphrases of the same intent.

## Adapting to other formats

### Interview-driven shows

Skills that work as-is:

- `podcast-init` (capture interviewer-only host, leave co-host empty)
- `editorial-calendar`
- `post-show-debrief`

Skills that need rework:

- **`topic-radar`** → repurpose as **guest-radar**. Source-scanning becomes guest sourcing: who's launching, who's in the news, who's on book tour. Rank candidates instead of stories. Output a guest shortlist with hook angles per guest.
- **`episode-program`** → repurpose as **interview-program**. Run-of-show structure changes: cold open, guest intro, segment-by-segment line of questioning, follow-up branches, closing. Talking-point bullets become *question* bullets.
- **`research-brief`** → repurpose as **guest-brief**. Per-guest dossier: bio, prior interviews, public positions, contradictions in their record, things they have not been asked, sensitive topics.
- **`cohost-brief`** → drop entirely or repurpose as **producer-brief** if you have a producer running the board.

Skills that are largely format-neutral:

- `show-notes`, `clip-finder`, `distribution-pack` — work without changes. Show-notes generates titles around the guest name. Clip-finder treats the guest's strongest moments as candidates the same way it treats host takes.

### Narrative shows

Narrative-driven shows (single-host or multi-host scripted reporting, Serial-style) need substantial rework on the front half of the pipeline.

Skills that work as-is:

- `editorial-calendar`
- `post-show-debrief`

Skills that need rework:

- **`topic-radar`** → repurpose as **story-radar**. Output is candidate *story arcs*, not single news items. Each candidate needs estimated episode count and reporting effort.
- **`episode-program`** → repurpose as **script-outline**. The output is a narrative outline (cold open, scene-by-scene structure, transitions, closing tag), not a run-of-show with talking-point bullets.
- **`research-brief`** → keep the structure, change the inputs. Briefs are per scene or per source, not per topic. Citations are still required, depth is usually `deep`.
- **`cohost-brief`** → drop entirely. Narrative shows do not have a co-host.

Skills that need light adaptation:

- **`show-notes`** — chapters become scene markers. Description style is more literary; check that the voice rules don't fight the format.
- **`clip-finder`** — narrative shows produce different clip categories. Add a "scene moment" category and demote "contrarian" since narrative voice rarely runs that way.
- **`distribution-pack`** — the LinkedIn post format probably needs a complete rewrite. Newsletter tie-in is more natural for narrative shows than for commentary.

### Panel shows

Panel shows (3+ recurring hosts, no clear primary) sit between commentary and interview formats.

Skills that work as-is:

- `podcast-init` (treat each panelist as a co-host with their own contact preference)
- `topic-radar`
- `editorial-calendar`
- `post-show-debrief`

Skills that need rework:

- **`episode-program`** → multi-host run-of-show. Talking-point bullets need ownership labels (which panelist takes which beat). Time budgeting becomes harder because pacing is shared.
- **`research-brief`** → unchanged in structure but distribution changes. Each panelist gets their own copy.
- **`cohost-brief`** → split into per-panelist briefs. Each panelist gets a tailored doc with their throw lines, their angle, and the questions other panelists might lob at them.

Skills that work with light adaptation:

- `show-notes`, `clip-finder`, `distribution-pack` — work without changes. Clip-finder may benefit from a per-panelist breakdown if one panelist consistently produces stronger clips.

### Daily news briefings

Short-form daily formats (NPR's Up First style, 10–15 minutes) work with the existing skills if you accept these constraints:

- Reduce `target_runtime_minutes` to 12.
- Reduce default brief depth to `light`.
- Tighten `clip-finder.target_count` to 3–4 clips per episode.
- Collapse `topic-radar` lookback to 24 hours.
- Run `show-notes` and `distribution-pack` faster — the format trades depth for speed.

The structure of the skills holds; only the parameters change.

## Adding a new skill

To add a new skill (e.g., the stretch goals from the build spec):

1. Create `skills/<skill-name>/SKILL.md` following the seven-section structure.
2. Write the description in the YAML frontmatter for trigger accuracy. Test it against three paraphrases.
3. Document inputs, outputs, and process steps. Be explicit about file paths.
4. List connectors with fallback behavior for each.
5. Include at least one complete example with abbreviated outputs.
6. Add an entry to the skill catalog in `README.md`.
7. If the skill has a per-output template, add it to `templates/`.

Three additional skills extend the toolkit once the show has a few episodes of history:

- **`recurring-segment`** — manages named beats (Earnings Watch, Founder of the Week, Mailbag) with per-segment populate strategies. `episode-program` reads the populated artifact when slotting a segment in; falls back to the static description if the skill has not run.
- **`cross-episode-arc`** — surfaces themes spanning multiple episodes, identifies resolved predictions, detects stance shifts, and suggests callbacks for the next episode.
- **`voice-fingerprint`** — analyzes past transcripts to identify the host's signature phrases, recurring opinions, and references. Writes `style/voice-fingerprint.md` that the writing skills consult as soft tonal guidance.

These three are designed to come online after the show has 3–5 published episodes. Run `voice-fingerprint` first to build a baseline, then `cross-episode-arc` once you have enough lookback to find threads, then `recurring-segment` whenever a named beat is ready to be defined more rigorously.

## Voice and style

All host-facing and audience-facing copy follows [style/voice.md](style/voice.md). Per-show extensions live in `config/podcast.yaml`. When adding a new skill or a new output, run the voice-check rules against generated copy before considering the output complete.

## Testing skill descriptions

Before considering a skill done:

1. Write the description in the frontmatter.
2. Compose three different ways a host might ask for that skill in natural language.
3. Verify the description contains enough trigger language that all three paraphrases would reasonably activate it.
4. Verify the description does not overlap with adjacent skills' triggers in ways that would cause the wrong skill to fire.

Trigger overlap is the most common bug. `topic-radar` should not fire on "research this topic" — that's `research-brief`. `episode-program` should not fire on "what should we cover" — that's `topic-radar`. Read every description against every other description and look for collisions.

## Pull requests

Contributions welcome. When proposing changes:

- Keep skills standalone — never introduce a hard runtime dependency between two skills. Soft references through `config/podcast.yaml` and through `outbox/` artifacts are fine.
- Keep connectors degrading gracefully. If a skill needs a connector, define a fallback path that writes to local files.
- Keep templates in sync with their skill's output spec. If you change one, change the other.
- Keep the example episode regenerated when the templates change shape — readers expect what they see in the example to match what they get when they run the skills.
