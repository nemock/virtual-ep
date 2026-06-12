#!/usr/bin/env python3
"""Serve a hot sheet episode folder and persist riffed-card state to disk.

Deterministic infrastructure — no model calls, stdlib only. The hot-sheet
skill starts this in the background and opens the page it serves. Every
checkbox toggle on the page POSTs the full riffed state here, which lands in
riffed.json next to hotsheet.html. riff-capture reads riffed.json, so the
host never has to report which cards they covered.

Usage:
    python3 hotsheet_server.py /abs/path/to/outbox/episodes/EP### [--port 8765] [--idle-hours 4]

Endpoints:
    GET  /riffed   -> current riffed.json (or {} if none yet)
    POST /riffed   -> validate, stamp, write riffed.json
    GET  /<file>   -> static files from the episode folder

Binds 127.0.0.1 only. Exits on its own after --idle-hours with no requests,
so nothing is left to babysit. If the chosen port is busy it walks up to the
next free one and prints the final URL.
"""

import argparse
import json
import sys
import threading
import time
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class Handler(SimpleHTTPRequestHandler):
    server_version = "HotsheetServer/0.1"

    def log_message(self, fmt, *args):
        pass  # keep the background task log quiet

    def _touch(self):
        self.server.last_request = time.monotonic()

    def do_GET(self):
        self._touch()
        if self.path == "/riffed":
            state_path = Path(self.server.episode_dir) / "riffed.json"
            body = state_path.read_bytes() if state_path.is_file() else b"{}"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self):
        self._touch()
        if self.path != "/riffed":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        if length > 65536:
            self.send_error(413)
            return
        try:
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict) or not isinstance(data.get("cards"), dict):
                raise ValueError("payload must be an object with a 'cards' object")
        except (ValueError, json.JSONDecodeError) as err:
            self.send_error(400, f"bad payload: {err}")
            return
        data["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        state_path = Path(self.server.episode_dir) / "riffed.json"
        state_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.send_response(204)
        self.end_headers()


def main():
    parser = argparse.ArgumentParser(description="Serve a hot sheet and persist riffed state.")
    parser.add_argument("episode_dir", help="Absolute path to the episode folder")
    parser.add_argument("--port", type=int, default=8765, help="First port to try (default 8765)")
    parser.add_argument("--idle-hours", type=float, default=4.0,
                        help="Exit after this many hours with no requests (default 4)")
    args = parser.parse_args()

    episode_dir = Path(args.episode_dir)
    if not (episode_dir / "hotsheet.html").is_file():
        sys.exit(f"error: {episode_dir}/hotsheet.html not found — render the hot sheet first")

    server = None
    for port in range(args.port, args.port + 20):
        try:
            server = ThreadingHTTPServer(
                ("127.0.0.1", port),
                partial(Handler, directory=str(episode_dir)),
            )
            break
        except OSError:
            continue
    if server is None:
        sys.exit(f"error: no free port in {args.port}–{args.port + 19}")

    server.episode_dir = str(episode_dir)
    server.last_request = time.monotonic()
    idle_seconds = args.idle_hours * 3600

    def watchdog():
        while True:
            time.sleep(30)
            if time.monotonic() - server.last_request > idle_seconds:
                print(f"idle for {args.idle_hours}h — shutting down", flush=True)
                server.shutdown()
                return

    threading.Thread(target=watchdog, daemon=True).start()
    print(f"serving {episode_dir.name} at http://127.0.0.1:{server.server_address[1]}/hotsheet.html "
          f"(auto-exits after {args.idle_hours}h idle)", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
