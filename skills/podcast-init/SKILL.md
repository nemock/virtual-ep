---
name: podcast-init
description: Initialize the Virtual EP toolkit for a new podcast. Walks the user through a one-time interactive setup that captures show identity, host and co-host details, recording stack, transcription provider, publishing destinations, brand assets, recurring segments, topic sources, output targets, and connectors, then writes config/podcast.yaml. Run this skill first when cloning the repo, when the config file is missing, or when the user says "set up the podcast", "initialize the EP toolkit", "first-time setup", "configure my show", "run init", or any equivalent. Other skills depend on this config file and will redirect the user here if it is missing.
version: 0.1.0
---

## Purpose

This skill is the front door of the toolkit. It captures everything the other nine skills need to know about the show in a single config file at `config/podcast.yaml`. Every downstream skill reads from this file. No other skill writes to it.

The init runs once when a new user clones the repo, and again any time the show's setup changes (new co-host, new transcription provider, new distribution channel). It is conversational, validates as it goes, and degrades gracefully when a connector is unavailable — capturing what is known and noting what the user must wire up later.

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `mode` | string | `interactive` | `interactive` walks the user through Q&A. `from-template` writes a defaults-only skeleton without prompting. `update` opens the existing config and walks only changed sections. |
| `force` | bool | `false` | If `true`, overwrites an existing `config/podcast.yaml` without confirmation. Default behavior asks first. |
| `template_path` | string | `config/podcast.yaml.example` | Source skeleton for `from-template` mode. |

## Outputs

| Output | Path | Notes |
|---|---|---|
| Config file | `config/podcast.yaml` | Canonical configuration read by every other skill. |
| Editorial calendar | Google Sheet (id stored in config) | Created during init if Google Sheets connector is available. Falls back to `outbox/editorial-calendar.csv`. |
| Drive folder structure | Google Drive (ids stored in config) | Created during init if Google Drive connector is available. Skipped otherwise. |
| Setup summary | stdout | Prints a summary of what was captured, which connectors are wired up, and what manual steps remain. |

## Process

When this skill activates, follow these steps in order.

1. **Check for an existing config.**
   - If `config/podcast.yaml` exists and `force` is false, ask the user: overwrite, update in place, or abort. Default to update.
   - If the user picks update, run only the sections they choose; preserve the rest.

2. **Walk the show identity section.**
   - Ask for show name, tagline, one-paragraph description, target audience, cadence, target runtime, and episode number format. Suggest defaults from the template.

3. **Walk the host section.**
   - Capture host name and short bio.
   - Ask whether the host runs a tie-in newsletter. If yes, capture the newsletter name and URL — `distribution-pack` will draft a tie-in section per episode.

4. **Walk the co-host section.**
   - Capture name, email, and contact preference. If contact preference is `gmail`, note that the Gmail connector should be wired so `cohost-brief` can deliver the brief by email.
   - Ask the default question density (light, standard, heavy). This becomes the default for the `cohost-brief` skill.

5. **Walk the recording stack and transcription.**
   - Capture recording platform.
   - Ask which transcription provider to use. If anything other than `whisper-local`, ask for the env var name that will hold the API key. Never accept or store the key itself in the config.

6. **Walk publishing and analytics.**
   - Capture primary host platform and any show URLs the user already has.
   - Ask which analytics sources are connected. Each one the user enables means `post-show-debrief` will pull from it.

7. **Walk brand assets.**
   - Ask for paths to logo, episode art template, color palette, and fonts. Verify each path resolves; warn if it does not, but do not block.

8. **Walk recurring segments.**
   - Show the default segment list from the template (cold open, closing CTA, plus two example named segments).
   - Ask the user to keep, edit, or replace each one. Capture target seconds and a one-line description per segment.

9. **Walk topic sources.**
   - Capture RSS feeds, websites, earnings calendars, newsletters, and any Twitter or X lists the user wants `topic-radar` to scan.
   - Set the default lookback window in days.

10. **Walk output targets.**
    - For each connector (Google Drive, Google Sheets, Google Calendar, Notion), check whether the connector is available in the current Claude environment.
    - If Google Drive is available: offer to create a folder structure now. On confirmation, create folders for run-of-show, briefs, and co-host briefs. Store the folder IDs in the config.
    - If Google Sheets is available: offer to create the editorial calendar sheet now with the correct columns (episode number, working title, status, topics, segments, target publish, actual publish, runtime, downloads, top clip, notes). Store the sheet ID in the config.
    - If Google Calendar is available: ask which calendar to write recording and publish dates to. Store the calendar ID.
    - If a connector is unavailable, set `enabled: false` for that target and note in the summary that the user can rerun init after connecting it.

11. **Walk distribution.**
    - Ask whether Blotato is connected. If yes, capture which social accounts are linked. If no, set `enabled: false` and note that `distribution-pack` will write drafts to local files.
    - Set the default clip count target and clip length range.

12. **Walk voice extensions.**
    - Show the user the default banned-word list from `style/voice.md` and ask if they want to add show-specific banned words, banned phrases, or required phrases. Write any extras to the `voice:` block in the config.

13. **Validate.**
    - Every required field is non-empty: show name, audience, cadence, target runtime, host newsletter toggle, co-host name (or explicit "none"), transcription provider, primary publishing host.
    - Every API key reference points to an env var name, never a literal key.
    - Every path that should resolve does resolve, or is flagged in the summary.

14. **Write the file.**
    - Write `config/podcast.yaml` with section headers as comments matching the template structure. Preserve the user's input order within each section.

15. **Print a setup summary.**
    - Show: what was captured, which connectors are connected, which fell back to local, and what the user should run next.
    - Suggested next command: `topic-radar` with the default lookback window.

## Connectors and APIs

| Connector | Use during init | Fallback |
|---|---|---|
| Google Drive | Create folder structure for run-of-show, briefs, co-host briefs | Skip; mark `enabled: false`; user can rerun init later |
| Google Sheets | Create editorial calendar with correct columns | Write `outbox/editorial-calendar.csv` skeleton instead |
| Google Calendar | Identify the calendar for recording and publish dates | Skip; `editorial-calendar` will print dates instead of writing them |
| Gmail | Verify the co-host email is reachable | Skip verification |
| Blotato | Confirm which social accounts are linked | Mark `enabled: false`; distribution-pack writes local drafts |
| Notion | Create or link the editorial database | Mark `enabled: false`; defaults to Google Sheets |
| Transcription provider | Validate the env var is set, never the key value | Warn if env var is unset; do not block init |

The skill never blocks on a missing connector. Every section either captures the value, marks the section disabled, or notes the manual step in the final summary.

## Examples

### Example 1: First-time setup, full interactive

User: *"set up the podcast"*

Skill walks all 15 steps. Output (abbreviated):

```
Show identity captured: "The Build", weekly, 45 min target.
Host: configured. Newsletter tie-in: enabled (The Build).
Co-host: configured (gmail contact, standard question density).
Recording: Riverside.
Transcription: whisper-local (no API key needed).
Publishing: buzzsprout primary, Spotify and Apple URLs captured.
Analytics: Spotify for Podcasters and YouTube Studio enabled.
Brand: logo path verified. Episode art template path NOT FOUND — please verify.
Segments: cold-open, earnings-watch, founder-of-the-week, closing-cta.
Topic sources: 4 RSS feeds, 2 websites, 1 earnings calendar.
Connectors:
  Google Drive   ✓ folders created
  Google Sheets  ✓ editorial calendar created
  Google Calendar  ✓ writing to "Podcast Production"
  Blotato       ✗ not connected — drafts will write to outbox/
Voice extensions: 0 extra banned words, 0 required phrases.

config/podcast.yaml written.

Next: run topic-radar to pull a topic shortlist for the past 7 days.
```

### Example 2: Update mode

User: *"the co-host's email changed, update the config"*

Skill detects existing config, offers update mode, and walks only the co-host section. Writes the change. Prints a one-line summary.

### Example 3: Template-only

User: *"just give me the example config so I can fill it in by hand"*

Skill copies `config/podcast.yaml.example` to `config/podcast.yaml` and exits. No prompting. Reminds the user to run init in interactive mode later if they want connector setup.
