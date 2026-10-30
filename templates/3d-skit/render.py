# SPDX-License-Identifier: MIT
"""Frame-by-frame deterministic render of the 3D skit in headless Chromium.

Local HTTP server on this folder -> index.html?style=<style> -> window.setTime(i/fps) -> JPEG screenshot -> ffmpeg.
The browser never has to keep up with real time, so a heavy frame does not drop and a re-render is identical.

  python3 render.py --style voxel --stills 1,3.5          # stills/<style>-01.00.jpg ...
  python3 render.py --style ps1 --gpu                     # output/<style>.mp4 (muxed with audio/mix.wav if present)
  python3 render.py --style clean --start 2 --end 4       # a slice, for quick checks
Without --gpu Chromium uses SwiftShader (CPU): slow but works everywhere. With --gpu on a Mac it uses Metal (~0.03-0.06 s/frame).
"""
from __future__ import annotations

import argparse
import functools
import json
import subprocess
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
W, H = 1080, 1920


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    from playwright.sync_api import sync_playwright
    ap = argparse.ArgumentParser()
    ap.add_argument('--style', default='clean', choices=['voxel', 'ps1', 'clean'])
    ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--stills', help='comma-separated seconds, e.g. 1,3.5')
    ap.add_argument('--gpu', action='store_true')
    ap.add_argument('--start', type=float, default=0)
    ap.add_argument('--end', type=float)
    ap.add_argument('--out', type=Path, help='output folder for stills (default stills/)')
    a = ap.parse_args()
    tl = json.loads((HERE / 'timeline.json').read_text()); dur = a.end or tl['duration']
    srv = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(HERE)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    args = ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] if a.gpu else ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']
    errs, enc = [], None
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True, args=args)
            pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1)
            # Без GPU (CI, swiftshader) первый кадр three.js компилирует шейдеры дольше 30 с по умолчанию
            pg.set_default_timeout(180000)
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
            t0 = time.time()
            pg.goto(f'http://127.0.0.1:{srv.server_port}/index.html?style={a.style}')
            try:
                pg.wait_for_function('window.ready===true', timeout=180000)
            except Exception:
                raise SystemExit(f'scene did not start: {errs}')
            print('load', round(time.time() - t0, 2), 's', flush=True)
            if a.stills:
                d = a.out or HERE / 'stills'; d.mkdir(parents=True, exist_ok=True)
                for t in map(float, a.stills.split(',')):
                    pg.evaluate('t=>window.setTime(t)', t)
                    pg.screenshot(path=str(d / f'{a.style}-{t:05.2f}.jpg'), type='jpeg', quality=90)
                    print('still', t, flush=True)
            else:
                out = HERE / 'output' / f'{a.style}-noaudio.mp4'; out.parent.mkdir(exist_ok=True)
                enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-framerate', str(a.fps), '-i', '-', '-an',
                                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)],
                                       stdin=subprocess.PIPE)
                i0, total = round(a.start * a.fps), round(dur * a.fps)
                for i in range(i0, total):
                    pg.evaluate('t=>window.setTime(t)', i / a.fps); enc.stdin.write(pg.screenshot(type='jpeg', quality=95))
                    if i % 60 == 0: print(f'frame {i}/{total}', flush=True)
                enc.stdin.close()
                if enc.wait(timeout=120): raise SystemExit('ffmpeg failed')
                aud = HERE / 'audio/mix.wav'
                if aud.exists() and not a.start and not a.end:
                    final = HERE / 'output' / f'{a.style}.mp4'
                    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(out), '-i', str(aud), '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', str(final)], check=True)
                    print('->', final.relative_to(HERE), flush=True)
            b.close()
    finally:
        if enc and enc.poll() is None: enc.kill()
        srv.shutdown()
    if errs:
        raise SystemExit(f'page errors: {errs[:10]}')


if __name__ == '__main__':
    main()
