#!/usr/bin/env python3
"""Lint recipes/ and learn/.

Recipes: front matter fields, enums, required sections, id == file name, relative links resolve,
language-specific recipes invite a sibling in another language, `status: proven` only with measured evidence
(measurement, ab-test, video-metric; CONTRIBUTING rule 3).
Learn: every relative link resolves, learn/ru and learn/en have the same chapter files.

Usage: python3 scripts/lint_recipes.py [repo_root]   (exit 1 on any error or when no recipes are found)
"""
import argparse
import re
import sys
from pathlib import Path

REQUIRED_KEYS = ["id", "title", "section", "lang", "status", "evidence", "added"]
STATUSES = {"proven", "hypothesis", "outdated"}
EVIDENCE = {"measurement", "ab-test", "video-metric", "viewer-feedback", "experience"}
MEASURED_EVIDENCE = {"measurement", "ab-test", "video-metric"}   # the only evidence kinds that justify status: proven
REQUIRED_SECTIONS = ["## When", "## Do", "## Verify", "## Evidence"]
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    data = {}
    for line in m.group(1).splitlines():
        line = line.split(" #", 1)[0].rstrip()
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip()
    return data


def check_links(p, text, root, errors):
    for link in LINK.findall(text):
        if link.startswith(("http://", "https://", "mailto:")):
            continue
        if not (p.parent / link).resolve().exists():
            errors.append(f"{p.relative_to(root)}: broken link {link}")


def lint(root):
    errors = []
    # recipes live in recipes/<section>/; files directly in recipes/ (README.md, BY-SYMPTOM.md) are generated indexes
    recipes = sorted(p for p in (root / "recipes").rglob("*.md")
                     if p.name != "README.md" and p.parent != root / "recipes")
    for p in recipes:
        rel = p.relative_to(root)
        text = p.read_text(encoding="utf-8")
        fm = front_matter(text)
        if fm is None:
            errors.append(f"{rel}: no front matter")
            continue
        for k in REQUIRED_KEYS:
            if not fm.get(k):
                errors.append(f"{rel}: missing field {k}")
        if fm.get("id") and fm["id"] != p.stem:
            errors.append(f"{rel}: id '{fm['id']}' != file name")
        if fm.get("section") and fm["section"] != p.parent.name:
            errors.append(f"{rel}: section '{fm['section']}' != folder {p.parent.name}")
        if fm.get("status") and fm["status"] not in STATUSES:
            errors.append(f"{rel}: status '{fm['status']}' not in {sorted(STATUSES)}")
        if fm.get("evidence") and fm["evidence"] not in EVIDENCE:
            errors.append(f"{rel}: evidence '{fm['evidence']}' not in {sorted(EVIDENCE)}")
        if fm.get("status") == "proven" and fm.get("evidence") in EVIDENCE and fm["evidence"] not in MEASURED_EVIDENCE:
            errors.append(f"{rel}: status proven requires evidence in {sorted(MEASURED_EVIDENCE)}, got '{fm['evidence']}' "
                          "(CONTRIBUTING rule 3: a number, an A/B or a published video's metric; otherwise status: hypothesis)")
        if fm.get("lang") not in (None, "", "any") and "contribute" not in text.lower():
            errors.append(f"{rel}: lang={fm['lang']} recipe must invite a sibling for other languages (word 'contribute')")
        for s in REQUIRED_SECTIONS:
            if s not in text:
                errors.append(f"{rel}: missing section '{s}'")
        check_links(p, text, root, errors)
    learn = root / "learn"
    if learn.exists():
        for p in sorted(learn.rglob("*.md")):
            check_links(p, p.read_text(encoding="utf-8"), root, errors)
        langs = [d for d in learn.iterdir() if d.is_dir()]
        names = {d.name: {p.name for p in d.glob("*.md")} for d in langs}
        if "ru" in names and "en" in names and names["ru"] != names["en"]:
            errors.append(f"learn/: ru and en chapters differ: {sorted(names['ru'] ^ names['en'])}")
    for p in sorted((root / "examples").rglob("*.md")) if (root / "examples").exists() else []:
        check_links(p, p.read_text(encoding="utf-8"), root, errors)
    return recipes, errors


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lint recipes/ and learn/: front matter, sections, links, ru/en parity.")
    ap.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parent.parent,
                    help="repository root (default: the parent of scripts/)")
    a = ap.parse_args(argv)
    root = a.root.resolve()
    if not (root / "recipes").is_dir():
        print(f"{root}: no recipes/ folder")
        return 1
    recipes, errors = lint(root)
    if not recipes:
        errors.append(f"{root / 'recipes'}: no recipes found")
    for e in errors:
        print(e)
    print(f"recipes: {len(recipes)}, errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
