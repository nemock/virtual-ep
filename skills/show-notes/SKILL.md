---
name: show-notes
description: Build the post-production package for a recorded episode. Consumes a transcript file or an audio file (transcribing via the configured provider if needed) and produces three title options under 100 characters each, a long-form YouTube description, a short Apple/Spotify description, chapter markers with timestamps, five key takeaways, the full list of links and references mentioned, and a filler-cleaned transcript. Run this skill when the user says "build show notes", "make the show notes", "show notes for EP042", "process the recording", "post-production for EP042", "clean the transcript", "write the description", or any equivalent post-recording ask. Run after recording is complete and a transcript or audio file is available.
version: 0.1.0
---

## Purpose

This is the post-production wrap. After recording, the host has a raw audio file or a raw transcript and needs the show ready to publish across YouTube, Apple, and Spotify. The skill produces every piece of metadata and copy each platform asks for, plus a cleaned transcript.

The titles are voice-checked. The descriptions are platform-tuned. The chapter markers align with the run-of-show segments where possible. The transcript keeps the host's words intact and only strips filler.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `transcript_path` | string | none | Path to a transcript file (`.txt`, `.md`, `.srt`, `.vtt`). Provide this OR `audio_path`. |
| `audio_path` | string | none | Path to the audio file. If provided and `transcript_path` is empty, the skill transcribes via the configured provider first. |
| `episode_number` | string | latest | Auto-detects the most recent `outbox/episodes/EP###/` folder. Override with explicit `EP042`. |
| `provider_override` | string | from config | Override `transcription.provider` for this run only. |

Exactly one of `transcript_path` or `audio_path` is required. If both are given, `transcript_path` wins.

## Outputs

| Output | Path | Notes |
|---|---|---|
| Show notes | `outbox/episodes/EP###/show-notes.md` | Titles, descriptions, chapters, takeaways, links. Always written. |
| Cleaned transcript | `outbox/episodes/EP###/transcript-clean.md` | Filler removed, speaker labels preserved. Always written. |
| Raw transcript | `outbox/episodes/EP###/transcript-raw.md` | Only written if the skill ran transcription itself. |

## Process

When this skill activates, follow these steps in order.

1. **Verify config and episode folder.**
   - If `config/podcast.yaml` is missing, redirect to `podcast-init`.
   - If the episode folder does not exist, create it from the episode number.

2. **Resolve the transcript.**
   - If `transcript_path` is provided, load it.
   - Otherwise transcribe `audio_path` using `transcription.provider` from config:
     - `whisper-local`: invoke local Whisper. No API key required.
     - `assemblyai` / `deepgram` / `rev`: load the API key from the env var named in `transcription.api_key_env`. If the env var is unset, stop and tell the user to set it.
   - Save the raw output to `outbox/episodes/EP###/transcript-raw.md` with timestamps and speaker labels where the provider supports them.

3. **Load context for naming and structure.**
   - Read the episode's `run-of-show.md` if it exists. The segment titles and time targets calibrate chapter markers and key-takeaway selection.
   - Read any `briefs/topic-N.md` files. Sources cited there are the seed list for the links section.
   - Load `style/voice.md` and `voice.banned_words_extra` for the voice check.

4. **Generate the three title options.**
   - Each under 100 characters, including spaces.
   - Each in a different shape: one declarative ("Anthropic just shipped Opus 5 — here's what changed"), one question or curiosity-gap ("Did Spotify just save the podcast ad business?"), one direct-benefit or specific-claim.
   - All voice-checked. No banned words. No clichés. No "the future of" or "deep dive" framings.
   - Avoid the host's name in the title unless it is part of the show's standard format.

5. **Generate the YouTube description (long form).**
   - 1500–2500 characters.
   - Opens with a 2–3 line hook that lands the angle without spoiling it.
   - Followed by a chapter list with timestamps (matches the chapter markers below).
   - Followed by a "What we covered" bulleted list of the topics.
   - Followed by the links and references list.
   - Ends with the show's standard CTA block (subscribe, newsletter tie-in if `host.newsletter_tie_in.enabled`, follow links).
   - Voice-checked.

6. **Generate the short description (Apple, Spotify).**
   - 200–400 characters.
   - One-line hook, then a one-line topic summary, then a one-line CTA.
   - Voice-checked.

7. **Generate chapter markers.**
   - Format: `MM:SS Title` per line for episodes under an hour, `HH:MM:SS Title` for longer.
   - Always start with `00:00 Cold Open` (or the configured cold-open segment title).
   - Match the run-of-show segments where possible. Detect actual segment boundaries in the transcript by looking for the throw lines from the run-of-show; adjust timestamps to where the segment actually started in the audio.
   - Aim for 5–10 chapters. Sub-chapters within a topic segment are fine if the host took a clear detour.

8. **Generate five key takeaways.**
   - Each one sentence.
   - Action-oriented or insight-shaped, never recap-shaped.
   - Voice-checked.

9. **Build the links and references list.**
   - Scan the transcript for URLs, company names, named people, books, papers, products, and events.
   - For URLs: include verbatim with a one-line description.
   - For named entities: search the relevant research brief for a source URL; if found, link it. If not found, leave the entity in plain text and flag in the run summary.
   - Group as: "Mentioned on the show" (URLs spoken) and "Background reading" (sources from the briefs).

10. **Clean the transcript.**
    - Remove pure filler: "um", "uh", "like" (used as a filler, not as a verb), "you know" (used as a filler), repeated false starts.
    - Keep all substantive content. Never paraphrase. Never trim a complete thought.
    - Keep speaker labels in the format `HOST:` and `<COHOST_NAME>:`.
    - Keep timestamps at the start of each speaker turn if the source had them.
    - Write to `outbox/episodes/EP###/transcript-clean.md`.

11. **Write the show notes file.**
    - Path: `outbox/episodes/EP###/show-notes.md`.
    - Format:

      ```markdown
      # EP### — Show Notes

      ## Title options
      1. ...
      2. ...
      3. ...

      ## YouTube description
      ...

      ## Apple / Spotify description
      ...

      ## Chapters
      00:00 Cold Open
      ...

      ## Key takeaways
      - ...

      ## Links and references

      Mentioned on the show:
      - [Title](url) — one-line description

      Background reading:
      - [Title](url) — one-line description
      ```

12. **Voice check.**
    - All generated copy (titles, descriptions, takeaways) passes the banned-word and banned-phrase rules.
    - Transcript content is not voice-checked — those are the host's actual words.

13. **Print summary.**
    - Episode number, character counts (per title and description), chapter count, takeaway count, link count, transcript word count before and after cleaning, any flagged entities without source URLs.
    - Suggested next: `clip-finder EP###`, then `distribution-pack EP###`.

## Connectors and APIs

| Connector | Use | Fallback |
|---|---|---|
| Transcription provider | Convert audio to text | Required when `audio_path` is provided. If the configured provider's env var is unset, stop with a clear message. |
| Filesystem read | Load run-of-show, briefs, raw transcript | Required. |
| Filesystem write | Write show-notes.md and transcript-clean.md | Required. |

The skill does not need Drive, Gmail, or Blotato. Output is local-only by design — the host pastes the description and chapters into the publishing platform manually since the formatting differs per platform.

## Examples

### Example 1: Transcript already produced

User: *"build show notes for EP042 from this transcript: outbox/episodes/EP042/transcript-raw.md"*

```
EP042 — Anthropic Opus 5 and the Spotify ad business

Title options (all under 100 chars, voice-checked):
  1. Anthropic ships Opus 5 — what actually changed and who should care (84)
  2. Did Spotify just save the podcast ad business? (49)
  3. Two AI launches, one ad miracle: the week the model layer split (66)

YouTube description: 2120 chars. Apple/Spotify description: 312 chars.
Chapters: 7. Key takeaways: 5. Links: 11 (9 verified, 2 unsourced — flagged).
Transcript: 11,840 words → 10,920 words after filler cleanup.

Outputs:
  outbox/episodes/EP042/show-notes.md
  outbox/episodes/EP042/transcript-clean.md

Next: clip-finder EP042, then distribution-pack EP042.
```

### Example 2: Audio file, transcribe first

User: *"process the EP042 recording at recordings/ep042.wav"*

Skill transcribes via the configured provider (e.g., AssemblyAI), writes `transcript-raw.md`, then runs the rest of the pipeline. Run summary notes the provider used and the transcription duration.

### Example 3: Run-of-show missing

User runs show-notes on an episode where no `run-of-show.md` exists (host recorded without prep, or the file was deleted). Skill proceeds with no segment guidance: chapter markers are inferred from natural topic shifts in the transcript, takeaways are extracted purely from content. Run summary notes the missing run-of-show.
