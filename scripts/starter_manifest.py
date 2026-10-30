#!/usr/bin/env python3
"""Rebuild starter/SOURCE-MANIFEST.json: path, size and sha256 of every tracked starter file.

Usage: python3 scripts/starter_manifest.py [--check]
Without flags it REWRITES the manifest. With --check it fails if a hash, size or the file list is stale (for CI).
"""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STARTER = ROOT / "starter"
MANIFEST = STARTER / "SOURCE-MANIFEST.json"


def tracked():
    out = subprocess.run(["git", "ls-files", "-z", "."], cwd=STARTER, capture_output=True, check=True).stdout
    return sorted(p for p in out.decode().split("\0") if p and p != MANIFEST.name and (STARTER / p).is_file())


def entries():
    res = []
    for p in tracked():
        b = (STARTER / p).read_bytes()
        res.append({"path": p, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()})
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Rebuild starter/SOURCE-MANIFEST.json (rewrites it unless --check).")
    ap.add_argument("--check", action="store_true", help="do not write; exit 1 if the manifest is stale")
    a = ap.parse_args(argv)
    new = entries()
    old = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"files": []}
    if a.check:
        if old.get("files") != new:
            was = {f["path"]: f["sha256"] for f in old.get("files", [])}
            now = {f["path"]: f["sha256"] for f in new}
            for p in sorted(set(was) | set(now)):
                if was.get(p) != now.get(p):
                    print(f"stale: {p}")
            print("starter/SOURCE-MANIFEST.json is stale: run python3 scripts/starter_manifest.py")
            return 1
        print("starter manifest is fresh")
        return 0
    if old.get("files") == new:
        print("starter manifest already fresh")
        return 0
    data = {"version": f"{date.today():%Y.%m.%d}-r1", "files": new}
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(new)} files written to starter/SOURCE-MANIFEST.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
