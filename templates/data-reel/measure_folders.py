# SPDX-License-Identifier: MIT
"""Read-only measurement: how much space a folder takes and what eats it -> real-numbers.json.

Walks PATH (does not follow symlinks), sums file sizes per top-level subfolder and per file kind, counts files,
measures how much has not been modified for a year. Writes only aggregates: no file names, no full paths,
no contents. Subfolder names are written unless --hide-names (then "Folder 1", "Folder 2", ...).
Nothing is deleted, moved or changed.

One size metric for every number in the file (size_metric): logical file sizes by default, or with --du the disk
space actually allocated (st_blocks, what `du` counts: smaller for sparse/compressed files, bigger for tiny ones).
Folders or files that could not be read are counted (unreadable_dirs, unreadable_entries) and the measurement is
marked "complete": false; reel_from_numbers.py refuses such a file unless told --allow-incomplete.

  python3 measure_folders.py ~/Downloads                       # -> ./real-numbers.json (current folder, not the repo)
  python3 measure_folders.py ~/Downloads --hide-names --top 6
  python3 measure_folders.py ~/Projects --du                   # allocated disk space (like du) instead of file sizes
  python3 measure_folders.py ~/Downloads --out /tmp/n.json
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
GB = 1e9
KINDS = {
    'video': {'.mp4', '.mov', '.mkv', '.avi', '.webm', '.m4v'},
    'images': {'.jpg', '.jpeg', '.png', '.heic', '.gif', '.webp', '.tif', '.tiff', '.raw', '.cr2', '.nef', '.psd'},
    'audio': {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg'},
    'archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.tgz', '.bz2', '.xz', '.dmg', '.iso', '.pkg'},
    'documents': {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.key', '.pages', '.numbers', '.txt', '.md', '.csv'},
    'code': {'.py', '.js', '.ts', '.json', '.html', '.css', '.go', '.rs', '.java', '.c', '.cpp', '.h', '.swift', '.rb', '.sh'},
}
EXT = {e: k for k, es in KINDS.items() for e in es}


def kind_of(name: str) -> str:
    return EXT.get(os.path.splitext(name)[1].lower(), 'other')


def size_of(st: os.stat_result, du: bool) -> int:
    """Logical size, or with du=True the allocated size (st_blocks * 512; st_size where st_blocks does not exist)."""
    if du and hasattr(st, 'st_blocks'):
        return st.st_blocks * 512
    return st.st_size


def counted(st: os.stat_result, du: bool, seen: set) -> bool:
    """With du=True a hard-linked file takes disk space once, like du: the second name of the same inode is skipped."""
    if not du or st.st_nlink < 2:
        return True
    key = (st.st_dev, st.st_ino)
    if key in seen:
        return False
    seen.add(key)
    return True


def walk(root: Path, year_ago: float, du: bool = False, seen: set = None):
    """Sizes of regular files under root, without following symlinks. Unreadable entries are counted, not fatal:
    files that fail lstat go to 'skipped', folders that cannot be listed go to 'skipped_dirs'."""
    total = files = old = skipped = 0; biggest = 0; kinds = {}; bad_dirs = []
    seen = set() if seen is None else seen
    for dirpath, dirnames, filenames in os.walk(root, onerror=bad_dirs.append, followlinks=False):
        dirnames[:] = [d for d in dirnames if not os.path.islink(os.path.join(dirpath, d))]
        for f in filenames:
            try:
                st = os.lstat(os.path.join(dirpath, f))
            except OSError:
                skipped += 1; continue
            if not os.path.isfile(os.path.join(dirpath, f)) or os.path.islink(os.path.join(dirpath, f)):
                continue
            if not counted(st, du, seen):
                continue
            s = size_of(st, du); total += s; files += 1; biggest = max(biggest, s)
            if st.st_mtime < year_ago: old += s
            k = kinds.setdefault(kind_of(f), [0, 0]); k[0] += s; k[1] += 1
    return {'bytes': total, 'files': files, 'old_bytes': old, 'biggest': biggest, 'kinds': kinds, 'skipped': skipped,
            'skipped_dirs': len(bad_dirs)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('path', type=Path)
    ap.add_argument('--top', type=int, default=6, help='how many biggest subfolders to keep by name')
    ap.add_argument('--hide-names', action='store_true', help='write "Folder N" instead of subfolder names')
    ap.add_argument('--du', action='store_true', help='allocated disk space (st_blocks, like du) for every number instead of file sizes')
    ap.add_argument('--out', type=Path, default=Path('real-numbers.json'),
                    help='where to write (default: real-numbers.json in the current folder, so folder names never land in the repo)')
    a = ap.parse_args()
    root = a.path.expanduser().resolve()
    if not root.is_dir(): raise SystemExit(f'not a folder: {a.path}')
    year_ago = time.time() - 365 * 86400
    t0 = time.time()
    seen = set()   # inodes already counted under --du, shared by all folders and loose files
    folders, loose = [], {'bytes': 0, 'files': 0, 'old_bytes': 0, 'biggest': 0, 'kinds': {}, 'skipped': 0, 'skipped_dirs': 0}
    try:
        entries = sorted(os.scandir(root), key=lambda e: e.name)
    except OSError as e:
        raise SystemExit(f'cannot read the folder: {a.path} ({e.strerror})')
    for e in entries:
        try:
            if e.is_symlink(): continue
            if e.is_dir():
                folders.append((e.name, walk(Path(e.path), year_ago, a.du, seen)))
            elif e.is_file():
                st = e.stat(follow_symlinks=False)
                if not counted(st, a.du, seen): continue
                sz = size_of(st, a.du); loose['bytes'] += sz; loose['files'] += 1
                loose['biggest'] = max(loose['biggest'], sz); loose['old_bytes'] += sz if st.st_mtime < year_ago else 0
                k = loose['kinds'].setdefault(kind_of(e.name), [0, 0]); k[0] += sz; k[1] += 1
        except OSError:
            loose['skipped'] += 1
    every = [w for _, w in folders] + [loose]
    total = sum(w['bytes'] for w in every)
    kinds = {}
    for w in every:
        for k, (b, n) in w['kinds'].items():
            kk = kinds.setdefault(k, [0, 0]); kk[0] += b; kk[1] += n
    folders.sort(key=lambda x: -x[1]['bytes'])
    top = folders[:a.top]; rest = folders[a.top:]
    share = lambda b: round(b / total, 3) if total else 0.0
    res = {
        'measured_at': datetime.datetime.now().isoformat(timespec='minutes'),
        'tool': 'measure_folders.py ' + ('os.walk allocated disk space' if a.du else 'os.walk file sizes') + ', read-only',
        'size_metric': 'allocated' if a.du else 'logical',
        'target_label': '~' if root == Path.home() else root.name,     # never the full path
        'names_hidden': a.hide_names,
        'total_bytes': total, 'total_gb': round(total / GB, 2),
        'files': sum(w['files'] for w in every), 'subfolders': len(folders),
        'biggest_file_gb': round(max((w['biggest'] for w in every), default=0) / GB, 2),
        'older_than_1y_gb': round(sum(w['old_bytes'] for w in every) / GB, 2),
        'older_than_1y_share': share(sum(w['old_bytes'] for w in every)),
        'by_folder': [{'name': f'Folder {i + 1}' if a.hide_names else n, 'gb': round(w['bytes'] / GB, 2), 'files': w['files'], 'share': share(w['bytes'])}
                      for i, (n, w) in enumerate(top)],
        'other_folders': {'count': len(rest), 'gb': round(sum(w['bytes'] for _, w in rest) / GB, 2)},
        'loose_files': {'count': loose['files'], 'gb': round(loose['bytes'] / GB, 2)},
        'by_kind': {k: {'gb': round(b / GB, 2), 'files': n, 'share': share(b)} for k, (b, n) in sorted(kinds.items(), key=lambda kv: -kv[1][0])},
        'unreadable_entries': sum(w['skipped'] + w['skipped_dirs'] for w in every),
        'unreadable_dirs': sum(w['skipped_dirs'] for w in every),
        'complete': not any(w['skipped'] or w['skipped_dirs'] for w in every),
        'seconds': round(time.time() - t0, 1),
    }
    a.out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps({k: res[k] for k in ('target_label', 'total_gb', 'files', 'older_than_1y_gb')}, ensure_ascii=False), '->', a.out)
    if not res['complete']:
        print(f"warning: incomplete measurement, {res['unreadable_dirs']} folders and "
              f"{res['unreadable_entries'] - res['unreadable_dirs']} files could not be read (no permission?); "
              'the numbers are too low. Grant access (macOS: Full Disk Access for the terminal) and measure again', file=sys.stderr)
    if not a.hide_names:
        print('note: subfolder names are in the file and may end up on screen; use --hide-names if any of them is private')


if __name__ == '__main__':
    main()
