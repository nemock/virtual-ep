---
name: voice-fingerprint
description: Learn the host's voice from past transcripts — recurring phrases, recurring opinions, recurring references, sentence-shape patterns — and write a fingerprint file the writing skills read so social copy and other host-facing drafts sound like the host from day one. Identifies signature phrases the host returns to, mental models they apply repeatedly, named entities they cite often, and stylistic patterns (sentence length, active voice ratio, transition habits). Suggests additions to the show's required-phrases and banned-phrases lists in config when patterns are clear. Run this skill when the user says "learn the host's voice", "build a voice fingerprint", "analyze past transcripts for voice", "what does the host sound like", "calibrate voice from past episodes", "voice fingerprint", or any equivalent ask. Run after at least 3–5 episodes have been published; rerun every 5–10 episodes to keep the fingerprint current.
version: 0.1.0
---

## Purpose

The base style guide in `style/voice.md` is universal — it lists banned words and broad principles. It does not know what the specific host actually sounds like. A new podcaster cloning this repo gets distribution-pack output that respects the rules but reads like nobody in particular.

This skill closes that gap. It reads past transcripts, identifies what the host sounds like at the line level, and writes a fingerprint document that every writing skill consults when drafting host-voice copy.

The fingerprint is data, not rules. It says "the host says 'the read here is' a lot" — it does not require new copy to use that phrase. The writing skills use the fingerprint as guidance for tone and rhythm, not as a checklist.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `lookback_episodes` | int | all available | Number of past episodes' cleaned transcripts to analyze. Default uses everything in `outbox/episodes/`. |
| `update_mode` | string | `incremental` | `full` rebuilds the fingerprint from scratch. `incremental` adds new findings since the last run, preserving manual edits the host made to the fingerprint file. |
| `min_phrase_frequency` | int | 3 | A phrase must appear in at least this many distinct episodes to make the signature-phrases list. |
| `confirm_suggestions` | bool | `true` | Whether to prompt the host before adding suggestions to `voice.required_phrases` or `voice.banned_phrases_extra` in the config. If `false`, the skill writes only to the fingerprint file. |

## Outputs

| Output | Path | Notes |
|---|---|---|
| Voice fingerprint | `style/voice-fingerprint.md` | Living document the writing skills read. |
| Config updates | `config/podcast.yaml` | Optional. Suggested additions to `voice.required_phrases` (host's signature phrases) or `voice.banned_phrases_extra` (overused or off-brand phrases). Confirmed with the host before writing. |
| Run summary | stdout | Episodes scanned, phrases found, suggestions confirmed. |

## Process

When this skill activates, follow these steps in order.

1. **Verify config and find input transcripts.**
   - If `config/podcast.yaml` is missing, redirect to `podcast-init`.
   - Find every `outbox/episodes/EP*/transcript-clean.md`. Sort by episode number.
   - If fewer than 3 transcripts exist, warn that fingerprint quality will be low. Continue if the user wants — a partial fingerprint beats no fingerprint.

2. **Resolve update mode.**
   - `full`: rebuild from scratch. Overwrite `style/voice-fingerprint.md`.
   - `incremental`: load existing fingerprint, identify which episodes are new since last run, run analysis only on those, merge findings.

3. **Extract host turns.**
   - For each transcript, isolate `HOST:` speaker turns. Discard co-host turns.
   - Concatenate. The corpus is the union of all host speech.

4. **Run the analyses.**

   **Signature phrases**
   - Extract n-grams of length 2–6 from the host corpus.
   - Filter against an English stopword n-gram baseline (drop "in the", "and the", "is going to" — generic English).
   - Filter against `style/voice.md` banned words (any phrase containing a banned word is dropped).
   - Keep n-grams that appear in at least `min_phrase_frequency` distinct episodes.
   - Rank by `episode_count × log(total_occurrences)`.
   - Top 20 are the host's signature phrases.

   **Recurring opinions**
   - Identify positions the host states across multiple episodes on the same subject.
   - Look for explicit-stance markers: "the read is", "I think", "look — ", "the truth is", followed by a position.
   - Cluster by subject (company, frame, industry).
   - Surface positions held in 2+ episodes with their stance and any evolution.

   **Recurring references**
   - Named entities (people, companies, books, papers, historical events) the host returns to across episodes.
   - Rank by episode count. Top 15 are the host's go-to references.
   - For each, note the typical use — illustration, parallel, criticism, praise.

   **Sentence-shape patterns**
   - Average sentence length (words).
   - Distribution: short (<10 words), medium (10–25), long (25+).
   - Active vs passive voice ratio.
   - Transition habit: how the host moves between thoughts ("And so", "Look —", "Right.", "OK.").
   - Question rate: how often the host asks rhetorical questions.

   **Verbal tics worth flagging**
   - Phrases the host uses *too much* — appearing in 7+ of the last 10 episodes. These are candidates for `voice.banned_phrases_extra` because overuse weakens them.
   - Filler patterns that survived the transcript-clean step (phrases not in the standard filler list).

5. **Build the fingerprint document.**
   - Path: `style/voice-fingerprint.md`.
   - Format:

     ```markdown
     # Voice Fingerprint — {{updated_date}}

     Built from {{N}} transcripts ({{date_range}}).

     ## Signature phrases

     The host returns to these. Use them sparingly in host-voice copy — they carry weight when they appear because the host has earned them.

     - "the read here is" — appears in 14 of 17 episodes
     - "look at the math" — 11 of 17
     - ...

     ## Recurring opinions

     ### On Anthropic
     Stance: bullish on enterprise positioning, skeptical of consumer.
     Evolution: in EP032 said "Anthropic won't cut prices"; in EP041 acknowledged the cut as a strategic shift.
     Use this when: drafting takes about Anthropic in distribution-pack.

     ### On Spotify
     Stance: bearish on content strategy, bullish on programmatic infrastructure.
     ...

     ## Recurring references

     - **Daniel Ek** — appears in 9 episodes. Typical use: leadership-strategy framing.
     - **Intel Atom (2008)** — appears in 4 episodes. Typical use: historical parallel for flagship-vs-volume strategy.
     - **Pandora 2014** — 3 episodes. Typical use: ad-load history.

     ## Sentence-shape patterns

     - Average sentence length: 14.2 words
     - Distribution: 38% short, 51% medium, 11% long
     - Active voice ratio: 92%
     - Top transitions: "And so", "Look —", "Right.", "OK."
     - Rhetorical questions: ~3 per episode

     ## Verbal tics flagged for moderation

     - "at the end of the day" — appeared in 9 of 17 episodes. Already in the banned-phrases default list; host should consciously avoid in-show.
     - "actually" — appears 4–7 times per episode. Not banned but overused; consider variants.

     ## Suggestions for config

     Add to `voice.required_phrases` (signature phrases worth preserving when natural):
     - "the read here is"
     - "look at the math"

     Add to `voice.banned_phrases_extra` (overused, weaken on repetition):
     - "actually" (when used as a verbal tic, not as a real correction)
     ```

6. **Confirm config suggestions.**
   - If `confirm_suggestions: true`, show each proposed addition to the host and ask which to keep.
   - Write only confirmed additions to `config/podcast.yaml` under `voice.required_phrases` and `voice.banned_phrases_extra`.

7. **Print summary.**
   - Episodes scanned, signature phrases identified, opinions clustered, references catalogued, suggestions made vs confirmed, fingerprint path.
   - Suggested next: rerun in 5–10 episodes to keep the fingerprint current. The longer the corpus, the more accurate the fingerprint.

## How writing skills consume the fingerprint

`distribution-pack` and `episode-program` should read `style/voice-fingerprint.md` when present and use it as soft guidance:

- When drafting LinkedIn copy, prefer sentence shapes that match the host's distribution.
- When pulling parallels, lean toward the host's recurring references over inventing new ones.
- When choosing transition language, use the host's habits.
- Never *force* a signature phrase into copy where it does not fit. Forced repetition weakens the phrase.

The fingerprint is not a rule. It is a tonal map. The base voice rules in `style/voice.md` are still the floor.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| Filesystem read | Load all `transcript-clean.md` files | Required. |
| Filesystem write | Write fingerprint, optionally update config | Required. |

The skill is local-only.

## Examples

### Example 1: First run after 5 published episodes

User: *"learn the host's voice"*

```
Transcripts scanned: 5 (EP001–EP005).
Signature phrases identified: 8 (above frequency threshold).
Recurring opinions clustered: 4 subjects.
Recurring references: 6 entities.
Verbal tics flagged: 2.

Suggested config additions:
  Required phrases: 3 candidates ("the read here is", "look at the math", "and so")
  Banned phrases extra: 1 candidate ("actually" — overused)

Confirm each? [y/n per item]
...

Voice fingerprint written to style/voice-fingerprint.md.
2 of 4 suggestions added to config/podcast.yaml.

Rerun after 5 more episodes for sharper analysis.
```

### Example 2: Incremental update

User: *"update the voice fingerprint with the new episodes"*

Skill runs in `incremental` mode. Loads the existing fingerprint. Finds 3 new episodes since the last update. Adds new signature-phrase candidates and updates frequency counts on existing ones. Preserves any manual edits the host made to the fingerprint file (sections marked with `<!-- manual -->` are not overwritten).

### Example 3: Thin corpus

User runs the skill after 2 published episodes. Output:

```
Transcripts scanned: 2. Below the recommended threshold of 3.

Signature phrases: 3 candidates, all below the 3-episode-frequency floor.
Opinions: too thin to cluster reliably.
References: 4 candidates, but coverage too sparse.

Fingerprint file written but flagged as preliminary. Do not commit suggestions
to config until the corpus reaches at least 5 episodes. Rerun then.
```
