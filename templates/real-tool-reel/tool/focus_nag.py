#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Focus nag: a laptop that tells you off when you open a distracting site instead of working. macOS only.

Every interval_s it reads the front app and the URL of the active tab in Safari or Google Chrome. If the domain is
in the blocklist:
  strike 1 -> line 1 is spoken ("Again? The deadline is Friday.")
  strike 2 -> line 2 ("I can see you.")
  strike 3 -> line 3 ("That's it. Back to work."), the tab is closed, work_url opens, the counter resets.
             After the line finishes the tab is closed only if the same browser is still in front and its front tab
             still shows the blocked URL; otherwise nothing is closed or opened.
No strikes for reset_after_s also resets the counter. Staying on a blocked site counts again every nag_every_s.

DRY RUN IS THE DEFAULT: without --live nothing touches the browser or plays sound; lines of "app<TAB>url" are read
from --feed or stdin and the actions are printed. Use it to plan and test the scenario of the video.

Standard library only (Python 3.9+) plus macOS built-ins: osascript, lsappinfo, say, afplay, open.
macOS permission needed in --live: only "Automation" (Terminal -> Safari / Google Chrome), asked on first use.
Accessibility and Screen Recording are NOT needed: the front app comes from lsappinfo.
Nothing is sent anywhere or written to disk.

  python3 focus_nag.py --feed demo.tsv        # dry run of the scenario (default)
  printf 'Safari https://youtube.com\\n' | python3 focus_nag.py
  python3 focus_nag.py --live --check         # once: what the nag sees, then exit (triggers the permission prompt)
  python3 focus_nag.py --live                 # the real thing; Ctrl+C to stop
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
DEFAULTS = {
    "interval_s": 1.5,            # how often to look
    "reset_after_s": 600,         # this long without strikes and the counter starts over
    "nag_every_s": 20,            # staying on a blocked site: next strike after this many seconds
    "blocklist": ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "twitch.tv", "reddit.com", "x.com"],
    # a line is either a sound file next to this script ("sounds/1.aiff") or "say:<text>" spoken by macOS `say`
    "lines": ["say:Again? The deadline is Friday.", "say:I can see you.", "say:That's it. Back to work."],
    "voice": "",                  # `say -v` voice name, empty = system default
    "work_url": "https://example.com/",   # what opens on strike 3: your document or playlist
    "close_tab": True,
    "browsers": {"Safari": "safari", "Google Chrome": "chrome"},
}


# ---------------------------------------------------------------- logic (platform-free, covered by tests)

def host_of(url: Optional[str]) -> str:
    if not url:
        return ""
    try:
        h = urlparse(url if "://" in url else "https://" + url).hostname or ""
    except ValueError:
        return ""
    return h.lower().rstrip(".")


def is_blocked(url: Optional[str], blocklist: Iterable[str]) -> bool:
    """youtube.com matches youtube.com, www.youtube.com, m.youtube.com, but not notyoutube.com."""
    h = host_of(url)
    if not h:
        return False
    for d in blocklist:
        d = d.lower().strip().lstrip(".")
        if d and (h == d or h.endswith("." + d)):
            return True
    return False


@dataclass
class Action:
    kind: str                 # "say" | "close_tab" | "open"
    arg: str = ""
    browser: str = ""
    url: str = ""             # close_tab: the URL that earned the strike; the tab is closed only if it still shows it


@dataclass
class Nag:
    """Strike counter. step() gets what is in front and the time, returns what to do."""
    blocklist: list
    lines: list
    work_url: str = ""
    close_tab: bool = True
    reset_after_s: float = 600
    nag_every_s: float = 20
    browsers: dict = field(default_factory=lambda: dict(DEFAULTS["browsers"]))
    strikes: int = 0
    last_strike_at: Optional[float] = None
    on_bad: bool = False          # a blocked site was in front last time

    def __post_init__(self):
        if not isinstance(self.lines, list) or not self.lines:
            raise ValueError('config "lines" must be a non-empty list: at least one "say:<text>" or a sound file per strike')
        bad = [x for x in self.lines if not isinstance(x, str) or not x.strip()]
        if bad:
            raise ValueError(f'config "lines" has empty or non-string entries: {bad}')

    def step(self, app: Optional[str], url: Optional[str], now: float) -> list:
        if self.last_strike_at is not None and now - self.last_strike_at >= self.reset_after_s:
            self.strikes = 0
            self.last_strike_at = None
        bad = app in self.browsers and is_blocked(url, self.blocklist)
        if not bad:
            self.on_bad = False
            return []
        fresh = not self.on_bad
        nag = self.on_bad and self.last_strike_at is not None and now - self.last_strike_at >= self.nag_every_s
        self.on_bad = True
        if not (fresh or nag):
            return []
        self.strikes += 1
        self.last_strike_at = now
        n = min(self.strikes, len(self.lines))
        acts = [Action("say", self.lines[n - 1])]
        if self.strikes >= len(self.lines):
            if self.close_tab:
                acts.append(Action("close_tab", browser=app, url=url or ""))
            if self.work_url:
                acts.append(Action("open", self.work_url, browser=app))
            self.strikes = 0
            self.on_bad = False       # the tab is gone: the next visit is "fresh" again
        return acts


# ---------------------------------------------------------------- macOS (only with --live)

def _run(cmd: list, timeout: float = 3) -> Optional[str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        if "-1743" in r.stderr:   # Automation permission missing
            print("! macOS did not allow reading the tab: System Settings > Privacy & Security > Automation", file=sys.stderr)
        return None
    return r.stdout.strip()


def front_app() -> Optional[str]:
    """Front app name without Accessibility permission: lsappinfo is built into macOS."""
    asn = _run(["lsappinfo", "front"])
    if not asn:
        return None
    out = _run(["lsappinfo", "info", "-only", "name", asn]) or ""
    # format: "LSDisplayName"="Safari"
    return out.split("=", 1)[1].strip().strip('"') if "=" in out else None


SCRIPTS = {
    # ident: which tab exactly (another tab with the same URL must not be closed instead); w = window, t = tab
    "safari": {"url": 'tell application "{app}" to get URL of current tab of front window',
               "tab": "current tab", "ident": '(id of w as text) & ":" & (index of t as text)'},
    "chrome": {"url": 'tell application "{app}" to get URL of active tab of front window',
               "tab": "active tab", "ident": '(id of t as text)'},
}


def _as_str(s: str) -> str:
    """AppleScript string literal."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def ident_script(kind: str, app: str) -> str:
    tab = SCRIPTS[kind]["tab"]
    return (f'tell application {_as_str(app)}\n  set w to front window\n  set t to {tab} of w\n'
            f'  return {SCRIPTS[kind]["ident"]}\nend tell')


def close_script(kind: str, app: str, url: str, ident: str) -> str:
    """Close the front tab only if it is the same tab (window and tab identity) and still shows `url`: check and
    close happen inside one AppleScript call, so a tab switched to during the spoken line, or another tab with
    the same URL, is never the one closed. Returns "closed" or "kept"."""
    tab = SCRIPTS[kind]["tab"]
    return (f'tell application {_as_str(app)}\n'
            f'  if (count of windows) is 0 then return "kept"\n'
            f'  set w to front window\n'
            f'  set t to {tab} of w\n'
            f'  if {SCRIPTS[kind]["ident"]} is not {_as_str(ident)} then return "kept"\n'
            f'  if URL of t is {_as_str(url)} then\n'
            f'    close t\n'
            f'    return "closed"\n'
            f'  end if\n'
            f'  return "kept"\n'
            f'end tell')


class Mac:
    def __init__(self, browsers: dict, voice: str = ""):
        self.browsers = browsers
        self.voice = voice
        self.player: Optional[subprocess.Popen] = None
        self.seen_tab: Optional[str] = None   # identity of the tab read by the last observe(): the strike's tab

    def observe(self):
        app = front_app()
        self.seen_tab = None
        if app in self.browsers:
            url = _run(["osascript", "-e", SCRIPTS[self.browsers[app]]["url"].format(app=app)])
            self.seen_tab = _run(["osascript", "-e", ident_script(self.browsers[app], app)])
            return app, url
        return app, None

    def do(self, a: Action) -> bool:
        """Run one action. Returns False when close_tab was cancelled: the user moved on to another app or tab
        while the line was playing; the caller then skips the rest of this strike (no work_url pops up)."""
        if a.kind == "say":
            if self.player and self.player.poll() is None:
                self.player.wait()            # lines do not overlap
            if a.arg.startswith("say:"):
                self.player = subprocess.Popen(["say"] + (["-v", self.voice] if self.voice else []) + [a.arg[4:]])
            else:
                self.player = subprocess.Popen(["afplay", str(HERE / a.arg)])
        elif a.kind == "close_tab":
            if self.player:
                self.player.wait()            # let the last line finish before the tab disappears
            # identity re-check after the wait: same front app, same URL in its front tab (checked atomically)
            if not a.url or not self.seen_tab or front_app() != a.browser:
                return False
            script = close_script(self.browsers[a.browser], a.browser, a.url, self.seen_tab)
            return _run(["osascript", "-e", script]) == "closed"
        elif a.kind == "open":
            _run(["open", "-a", a.browser, a.arg] if a.browser else ["open", a.arg])
        return True


class DryRun:
    """Fake source: lines "app<TAB>url" (or "app url"). Runs nothing, only prints."""
    def __init__(self, lines: Iterable[str]):
        self.lines = iter(lines)

    def observe(self):
        for raw in self.lines:
            raw = raw.rstrip("\n")
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            if "\t" in raw:
                app, _, url = raw.partition("\t")
            else:
                app, _, url = raw.rpartition(" ")
                if not app or not ("." in url or "://" in url):
                    app, url = raw, ""
            return app.strip() or None, url.strip() or None
        raise EOFError

    def do(self, a: Action):
        print(f"  -> {a.kind} {a.arg} {a.browser}".rstrip(), flush=True)


def load_config(path: Optional[Path]) -> dict:
    cfg = dict(DEFAULTS)
    p = path or HERE / "config.json"
    if p.exists():
        cfg.update({k: v for k, v in json.loads(p.read_text(encoding="utf-8")).items() if not k.startswith("_")})
    return cfg


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Focus nag (dry run unless --live)")
    ap.add_argument("--config", type=Path)
    ap.add_argument("--live", action="store_true", help="really watch the browser, speak and close tabs (macOS)")
    ap.add_argument("--feed", type=Path, help="dry run input: lines app<TAB>url (default: stdin)")
    ap.add_argument("--tick", type=float, help="dry run time step, seconds (default interval_s)")
    ap.add_argument("--check", action="store_true", help="with --live: show the front app and URL once and exit")
    a = ap.parse_args(argv)
    cfg = load_config(a.config)
    try:
        z = Nag(blocklist=cfg["blocklist"], lines=cfg["lines"], work_url=cfg["work_url"], close_tab=cfg["close_tab"],
                reset_after_s=cfg["reset_after_s"], nag_every_s=cfg["nag_every_s"], browsers=cfg["browsers"])
    except ValueError as e:
        print(f"focus_nag: {e} ({a.config or HERE / 'config.json'})", file=sys.stderr)
        return 2
    if not a.live:
        src = DryRun(a.feed.read_text(encoding="utf-8").splitlines() if a.feed else sys.stdin)
        clock, tick = 0.0, a.tick or cfg["interval_s"]
        while True:
            try:
                app, url = src.observe()
            except EOFError:
                return 0
            acts = z.step(app, url, clock)
            print(f"[{clock:7.1f}s] {app or '-'} {url or ''}  strikes: {z.strikes}", flush=True)
            for act in acts:
                src.do(act)
            clock += tick
    if platform.system() != "Darwin":
        print("--live works on macOS only (osascript, lsappinfo); use the dry run elsewhere", file=sys.stderr)
        return 2
    mac = Mac(cfg["browsers"], cfg.get("voice", ""))
    if a.check:
        app, url = mac.observe()
        print("front:", app, "| url:", url, "| blocked:", is_blocked(url, cfg["blocklist"]))
        return 0
    missing = [s for s in cfg["lines"] if not s.startswith("say:") and not (HERE / s).exists()]
    if missing:
        print("missing sound files:", missing, file=sys.stderr)
        return 1
    print("Watching. Stop: Ctrl+C", flush=True)
    try:
        while True:
            app, url = mac.observe()
            for act in z.step(app, url, time.monotonic()):
                print(time.strftime("%H:%M:%S"), act.kind, act.arg, act.browser, flush=True)
                if not mac.do(act):
                    print(time.strftime("%H:%M:%S"), "close_tab cancelled: the front tab changed", flush=True)
                    break
            time.sleep(cfg["interval_s"])
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
