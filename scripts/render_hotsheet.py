#!/usr/bin/env python3
"""Render a hot sheet HTML page from a hotsheet.json episode file.

Deterministic transform — no model calls, no network, stdlib only.
The hot-sheet skill writes hotsheet.json; this script turns it into a
single self-contained HTML file the host opens in a browser tab and
records from.

Usage:
    python3 render_hotsheet.py /abs/path/to/hotsheet.json [-o /abs/path/out.html]

Default output: hotsheet.html next to the input JSON.

hotsheet.json schema (all string fields are plain text unless noted):
{
  "episode": "EP001",
  "title": "Working title",
  "date": "2026-06-11",
  "theme": "One-sentence common thread for the episode.",
  "intro": { "candidates": ["line 1", "line 2"] },          // cold open — hook before any branding
  "show_id": { "candidates": ["Welcome to ... I'm ..."] },  // optional, the who/what after the cold open
  "cards": [
    {
      "headline": "Card headline",
      "source": "r/biotech",
      "url": "https://...",            // optional
      "context": "15-second setup the host can glance at.",
      "stars": ["anchor fact 1", "anchor fact 2"],  // optional, the names/numbers/quotes to orient on
      "angle": "The host's pre-loaded take.",
      "riffs": ["prompt 1", "prompt 2"],
      "positions": ["position-slug"],   // optional, voice-library callbacks
      "node": "relative/path/to/node.md" // optional, for riff-capture
    }
  ],
  "signoff": { "candidates": ["sign-off 1", "sign-off 2"] }
}
"""

import argparse
import html
import json
import sys
from pathlib import Path


def esc(value):
    return html.escape(str(value or ""))


def render_lines(candidates, css_class):
    out = []
    for line in candidates or []:
        out.append(f'<p class="{css_class}">{esc(line)}</p>')
    return "\n".join(out)


def render_card(card, index):
    n = index + 1
    source = esc(card.get("source", ""))
    url = card.get("url", "")
    link = (
        f'<a class="source-link" href="{esc(url)}" target="_blank" rel="noopener">'
        f"{source or 'source'} &#8599;</a>"
        if url
        else f'<span class="source-link plain">{source}</span>'
    )
    stars = "\n".join(f"<li>{esc(s)}</li>" for s in card.get("stars", []))
    riffs = "\n".join(f"<li>{esc(r)}</li>" for r in card.get("riffs", []))
    chips = "\n".join(
        f'<span class="chip">{esc(p)}</span>' for p in card.get("positions", [])
    )
    node = esc(card.get("node", ""))
    return f"""
<section class="card" id="card-{n}" data-card="{n}" data-node="{node}">
  <div class="card-head">
    <button class="badge" title="Click or press X to mark riffed">{n}</button>
    <h2>{esc(card.get('headline', ''))}</h2>
    <label class="riffed-box" title="Mark this card riffed">
      <input type="checkbox" aria-label="Mark card {n} riffed"><span>riffed</span>
    </label>
  </div>
  <div class="meta-row">{link}{('<span class="chips">' + chips + '</span>') if chips else ''}</div>
  <p class="context">{esc(card.get('context', ''))}</p>
  {f'<ul class="stars">{stars}</ul>' if stars else ''}
  <div class="angle"><span class="angle-label">Your angle</span>{esc(card.get('angle', ''))}</div>
  {f'<ul class="riffs">{riffs}</ul>' if riffs else ''}
</section>"""


def render(data):
    episode = esc(data.get("episode", "EP?"))
    title = esc(data.get("title", "Untitled"))
    date = esc(data.get("date", ""))
    theme = esc(data.get("theme", ""))
    cards = data.get("cards", [])
    dots = "\n".join(
        f'<button class="dot" data-dot="{i + 1}" title="Card {i + 1}"></button>'
        for i in range(len(cards))
    )
    cards_html = "\n".join(render_card(c, i) for i, c in enumerate(cards))
    intro = render_lines((data.get("intro") or {}).get("candidates"), "big-line")
    show_id = render_lines((data.get("show_id") or {}).get("candidates"), "big-line")
    show_id_block = (
        '<div class="block-label">Show ID — who you are, what this is. '
        "Land it into the lens.</div>\n" + show_id
    ) if show_id else ""
    signoff = render_lines((data.get("signoff") or {}).get("candidates"), "big-line")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{episode} hot sheet — {title}</title>
<style>
  :root {{
    --bg: #0e1116; --panel: #161b22; --text: #e8e8e4; --dim: #9aa4b2;
    --accent: #f0b429; --accent-dim: #8a6a1d; --done: #3fb950; --line: #2d333b;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--text);
    font: 20px/1.55 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  }}
  header {{
    position: sticky; top: 0; z-index: 10; background: rgba(14,17,22,.95);
    backdrop-filter: blur(6px); border-bottom: 1px solid var(--line);
    padding: 10px 28px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  }}
  header .ep {{ color: var(--accent); font-weight: 700; letter-spacing: .04em; }}
  header .theme {{ color: var(--dim); font-size: 15px; flex: 1; min-width: 200px; }}
  .dots {{ display: flex; gap: 6px; }}
  .dot {{
    width: 14px; height: 14px; border-radius: 50%; border: 1px solid var(--dim);
    background: transparent; cursor: pointer; padding: 0;
  }}
  .dot.done {{ background: var(--done); border-color: var(--done); }}
  main {{ max-width: 880px; margin: 0 auto; padding: 32px 28px 30vh; }}
  h1 {{ font-size: 34px; line-height: 1.2; margin: 8px 0 4px; }}
  .date {{ color: var(--dim); margin-bottom: 28px; }}
  .block-label {{
    color: var(--accent); text-transform: uppercase; letter-spacing: .12em;
    font-size: 13px; font-weight: 700; margin: 36px 0 10px;
  }}
  .big-line {{
    font-size: 28px; line-height: 1.4; margin: 0 0 14px; padding: 14px 18px;
    background: var(--panel); border-left: 4px solid var(--accent); border-radius: 6px;
  }}
  .card {{
    background: var(--panel); border: 1px solid var(--line); border-radius: 10px;
    padding: 22px 24px; margin: 22px 0; scroll-margin-top: 70px;
  }}
  .card.focused {{ border-color: var(--accent); }}
  .card.done {{ opacity: .55; }}
  .card.done .badge {{ background: var(--done); border-color: var(--done); color: #0e1116; }}
  .card-head {{ display: flex; gap: 14px; align-items: flex-start; }}
  .badge {{
    flex: 0 0 auto; width: 38px; height: 38px; border-radius: 50%;
    border: 2px solid var(--accent); background: transparent; color: var(--accent);
    font-size: 18px; font-weight: 700; cursor: pointer; margin-top: 2px;
  }}
  .card h2 {{ font-size: 29px; line-height: 1.25; margin: 0; flex: 1; }}
  .riffed-box {{
    flex: 0 0 auto; margin-left: auto; display: flex; align-items: center; gap: 8px;
    color: var(--dim); font-size: 14px; cursor: pointer; padding-top: 8px;
  }}
  .riffed-box input {{ width: 22px; height: 22px; accent-color: var(--done); cursor: pointer; }}
  .card.done .riffed-box {{ color: var(--done); }}
  .meta-row {{ margin: 10px 0 0 52px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }}
  .source-link {{ color: var(--accent); text-decoration: none; font-size: 15px; font-weight: 600; }}
  .source-link:hover {{ text-decoration: underline; }}
  .source-link.plain {{ color: var(--dim); }}
  .chips {{ display: flex; gap: 6px; flex-wrap: wrap; }}
  .chip {{
    font-size: 12px; color: var(--dim); border: 1px solid var(--line);
    border-radius: 999px; padding: 2px 10px;
  }}
  .context {{ margin: 14px 0 0 52px; font-size: 21px; }}
  .stars {{ list-style: none; margin: 14px 0 0 52px; padding: 0; font-size: 21px; }}
  .stars li {{ margin: 7px 0; padding-left: 28px; position: relative; }}
  .stars li::before {{ content: "\\2726"; position: absolute; left: 2px; color: var(--accent); }}
  .angle {{
    margin: 16px 0 0 52px; padding: 12px 16px; border-left: 4px solid var(--accent);
    background: rgba(240,180,41,.07); border-radius: 6px; font-size: 21px;
  }}
  .angle-label {{
    display: block; color: var(--accent); font-size: 12px; font-weight: 700;
    text-transform: uppercase; letter-spacing: .12em; margin-bottom: 4px;
  }}
  .riffs {{ margin: 14px 0 0 52px; padding-left: 22px; font-size: 21px; }}
  .riffs li {{ margin: 6px 0; }}
  footer {{
    max-width: 880px; margin: 0 auto; padding: 0 28px 60px; color: var(--dim); font-size: 14px;
  }}
  .copy-btn {{
    background: transparent; border: 1px solid var(--accent); color: var(--accent);
    border-radius: 6px; padding: 8px 16px; font-size: 15px; cursor: pointer;
  }}
  .copy-btn:hover {{ background: rgba(240,180,41,.1); }}
  kbd {{
    background: var(--panel); border: 1px solid var(--line); border-radius: 4px;
    padding: 1px 6px; font-size: 13px;
  }}
</style>
</head>
<body>
<header>
  <span class="ep">{episode}</span>
  <span class="theme">{theme}</span>
  <div class="dots">{dots}</div>
</header>
<main>
  <h1>{title}</h1>
  <p class="date">{date}</p>

  <div class="block-label">Cold open — the hook, before any branding</div>
  {intro}

  {show_id_block}

  <div class="block-label">Topics</div>
  {cards_html}

  <div class="block-label">Sign-off — pick one</div>
  {signoff}

  <div class="block-label">After recording</div>
  <p><button class="copy-btn" id="copy-summary">Copy riff summary</button></p>
</main>
<footer>
  <kbd>j</kbd>/<kbd>k</kbd> or <kbd>&darr;</kbd>/<kbd>&uarr;</kbd> next / previous card &nbsp;&middot;&nbsp;
  <kbd>x</kbd>, the checkbox, or the number marks a card riffed &nbsp;&middot;&nbsp;
  <span id="sync-status">riffed state persists in this browser</span>
</footer>
<script>
(function () {{
  var EP = {json.dumps(data.get("episode", "EP"))};
  var KEY = "hotsheet-" + EP;
  var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
  var dots = Array.prototype.slice.call(document.querySelectorAll(".dot"));
  var focus = 0;

  // Served over http (hotsheet_server.py): every change is POSTed to /riffed
  // and lands in riffed.json on disk. Opened as a plain file: localStorage
  // only, and the copy button is the way to report the session.
  var SERVER = location.protocol === "http:" || location.protocol === "https:";
  var statusEl = document.getElementById("sync-status");

  function load() {{
    try {{ return JSON.parse(localStorage.getItem(KEY)) || {{}}; }}
    catch (e) {{ return {{}}; }}
  }}
  function save(state) {{ localStorage.setItem(KEY, JSON.stringify(state)); }}
  function push(state) {{
    if (!SERVER) return;
    var nodes = {{}};
    cards.forEach(function (c) {{
      if (state[c.dataset.card] && c.dataset.node) nodes[c.dataset.card] = c.dataset.node;
    }});
    fetch("/riffed", {{
      method: "POST",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify({{ episode: EP, cards: state, nodes: nodes }})
    }}).then(function (r) {{
      statusEl.textContent = r.ok ? "riffed state saved to disk" : "save failed — use the copy button";
    }}).catch(function () {{
      statusEl.textContent = "server gone — use the copy button";
    }});
  }}
  function paint() {{
    var state = load();
    cards.forEach(function (c, i) {{
      var done = !!state[c.dataset.card];
      c.classList.toggle("done", done);
      c.classList.toggle("focused", i === focus);
      c.querySelector(".riffed-box input").checked = done;
      if (dots[i]) dots[i].classList.toggle("done", done);
    }});
  }}
  function setCard(n, value) {{
    var state = load();
    state[n] = value;
    save(state);
    push(state);
    paint();
  }}
  function toggle(n) {{ setCard(n, !load()[n]); }}
  function go(i) {{
    focus = Math.max(0, Math.min(cards.length - 1, i));
    // Instant jump, not smooth: Chrome drops smooth programmatic scrolls in
    // some contexts, and a hard cut reads better on a mid-recording glance.
    cards[focus].scrollIntoView({{ block: "start" }});
    paint();
  }}

  cards.forEach(function (c) {{
    c.querySelector(".badge").addEventListener("click", function () {{
      toggle(c.dataset.card);
    }});
    c.querySelector(".riffed-box input").addEventListener("change", function (e) {{
      setCard(c.dataset.card, e.target.checked);
    }});
  }});
  dots.forEach(function (d, i) {{
    d.addEventListener("click", function () {{ go(i); }});
  }});
  document.addEventListener("keydown", function (e) {{
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    if (e.key === "j" || e.key === "ArrowDown") {{ e.preventDefault(); go(focus + 1); }}
    if (e.key === "k" || e.key === "ArrowUp") {{ e.preventDefault(); go(focus - 1); }}
    if (e.key === "x") toggle(cards[focus].dataset.card);
  }});
  document.getElementById("copy-summary").addEventListener("click", function () {{
    var state = load();
    var riffed = cards.filter(function (c) {{ return state[c.dataset.card]; }})
                      .map(function (c) {{ return c.dataset.card; }});
    var text = "riff-capture " + EP + " --cards " + (riffed.join(",") || "none");
    navigator.clipboard.writeText(text).then(function () {{
      var btn = document.getElementById("copy-summary");
      btn.textContent = "Copied: " + text;
      setTimeout(function () {{ btn.textContent = "Copy riff summary"; }}, 3000);
    }});
  }});
  if (SERVER) {{
    // riffed.json on disk is the durable copy — adopt it over localStorage.
    fetch("/riffed").then(function (r) {{ return r.json(); }}).then(function (d) {{
      if (d && d.cards) save(d.cards);
      statusEl.textContent = "riffed state saved to disk";
      paint();
    }}).catch(function () {{
      statusEl.textContent = "server gone — use the copy button";
    }});
  }}
  paint();
}})();
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Render hotsheet.json to HTML.")
    parser.add_argument("json_path", help="Absolute path to hotsheet.json")
    parser.add_argument("-o", "--output", help="Output HTML path (default: alongside input)")
    args = parser.parse_args()

    src = Path(args.json_path)
    if not src.is_file():
        sys.exit(f"error: {src} not found")
    data = json.loads(src.read_text(encoding="utf-8"))

    required = ["episode", "title", "cards"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        sys.exit(f"error: hotsheet.json missing required fields: {', '.join(missing)}")
    if not isinstance(data["cards"], list) or not data["cards"]:
        sys.exit("error: hotsheet.json has no cards")

    out = Path(args.output) if args.output else src.with_name("hotsheet.html")
    out.write_text(render(data), encoding="utf-8")
    print(f"wrote {out} ({len(data['cards'])} cards)")


if __name__ == "__main__":
    main()
