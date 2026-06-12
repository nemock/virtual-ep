# Recording rig — solo riff sessions

Reference setup for recording hot-sheet riff episodes locally. Written around a
specific rig (Elgato Facecam 4K + Maono PD400X + OBS Studio on a Mac) but the
structure applies to any camera/mic: lock everything manual, record a local
master, keep the hot sheet near the lens.

## Principles

- **Record locally.** No browser recorders, no cloud. A solo show has no remote
  guest, so there is nothing for Riverside-style tools to solve. The master file
  lands on disk, ready for the post chain.
- **Lock all auto settings.** Auto-exposure, auto-white-balance, and auto-focus
  hunt mid-take and read as glitches. Set once, lock, reuse.
- **One scene, one click.** All per-session friction should be: open OBS, hit
  Record.

## Camera — Elgato Facecam 4K

Set in Elgato Camera Hub (settings persist):

| Setting | Value | Why |
|---|---|---|
| Resolution / frame rate | 4K @ 30 fps | Talking head does not need 60 fps; 30 looks natural, halves file size, and YouTube serves 4K30 beautifully. |
| Shutter | 1/60 | Standard 180° rule at 30 fps — natural motion blur. |
| ISO / exposure | Manual, set for your lighting, then lock | No mid-take brightness pumping. |
| White balance | Manual, matched to your key light, locked | No color drift. |
| Focus area | Optimized focus area on your face, then lock focus | The riff format means you barely move — fixed focus is safer than tracking. |
| HDR | Off | SDR keeps the OBS → YouTube pipeline simple and predictable. Revisit only if you build an HDR-aware post chain. |
| Cinematic effects / bokeh | Taste call — test once, then leave it | If used, verify it holds up during hand gestures before trusting it for a full episode. |

Connect to a USB-3 port (uncompressed 4K needs the bandwidth).

## Mic — Maono PD400X

- Connect via **USB** (the XLR path needs an interface and buys you nothing
  here; the onboard DSP is fine).
- 4–8 inches from your mouth, slightly off-axis, out of frame or bottom of frame.
  It's a dynamic mic — it wants to be close, and in exchange it ignores the room.
- Gain: set so normal speech peaks around **−12 to −6 dB** in the OBS audio
  meter. Never let it touch 0.
- EQ/DSP in Maono Link: **flat**. The audio-cleanup pass downstream does the
  polish; stacking two processing chains causes weirdness.
- Kill the mic's monitoring latency complaints by monitoring through the mic's
  own headphone jack, not OBS.

## OBS Studio

One-time setup:

- **Settings → Video:** Base and Output canvas 3840×2160, 30 fps.
- **Settings → Output (Recording):**
  - Format: **Hybrid MP4** (crash-safe — a power cut doesn't eat the take).
  - Encoder: Apple VT (hardware) H.264 — or HEVC if disk space matters more
    than edit-tool compatibility.
  - Quality: high / ~50 Mbps for 4K30.
  - Audio: 48 kHz, single track.
- **Scene "Riff":**
  - Video Capture Device → Facecam 4K, full frame.
  - Audio Input Capture → PD400X.
  - Desktop audio: **disabled** (nothing on screen should be heard).
- **Recordings folder:** `recordings/` in this repo (gitignored) or wherever
  the archive convention points.

## Hot sheet placement

Put the hot sheet browser window **directly under the camera**, as narrow and
as close to the lens as it will go. A glance down-and-back reads as "checking
my notes" — natural podcast behavior. A glance to a side monitor reads as
distraction. The sheet's type sizes are built for this distance; `j`/`k` moves
between cards without touching the mouse.

## Per-session checklist

1. Hot sheet is open and served (checkboxes saving to disk — footer says so).
2. OBS open, "Riff" scene active, mic meter peaking −12 to −6 dB on a test sentence.
3. Hit Record. Say the cold open. Riff. Check cards off as you go.
4. Stop. The master lands in the recordings folder — archive it raw.
5. **Transcribe — always.** whisper-local on the master, into the episode
   folder. The transcript feeds quote extraction and show notes; it is a
   standing step, not an option.
6. Audio cleanup — **optional.** A dynamic mic worked close usually doesn't
   need it. Spot-check the master; run the cleanup pass only if the raw
   audio has a defect (hum, rumble, uneven levels) worth fixing.
7. "Capture EP###" — spent topics get marked, quotes get banked.
8. Upload to YouTube, add to the podcast playlist (full episodes only).
