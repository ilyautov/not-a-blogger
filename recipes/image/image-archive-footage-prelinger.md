---
id: image-archive-footage-prelinger
title: Take period footage and music from archive.org collections, checking licenseurl per item
section: image
lang: any
status: hypothesis
evidence: experience
tools: [archive.org API, ffmpeg]
learn: ../../learn/en/04-image-and-frame.md
added: 2026-10-28
updated: 2026-10-28
contributors: [not-a-blogger]
---

## When
A video is styled as an era (a 1950s educational film, a 1930s cartoon, a wartime newsreel) and generated "old footage" looks synthetic. You need real period footage and period music without paying for stock.

## Do
1. Search the Prelinger Archives (`collection:prelinger`, ephemeral films) for footage and the Great 78 Project (`collection:78rpm`) for music, through the public API:

```bash
curl -s 'https://archive.org/advancedsearch.php?q=collection:prelinger+AND+typewriter&fl[]=identifier&fl[]=title&fl[]=year&fl[]=licenseurl&rows=50&output=json'
curl -s 'https://archive.org/metadata/<identifier>' | python3 -c 'import json,sys; m=json.load(sys.stdin)["metadata"]; print(m.get("licenseurl"), m.get("rights"))'
# file list in the same metadata JSON; download: https://archive.org/download/<identifier>/<file>
```

2. Check `licenseurl` (and `rights`) on **every item**, not on the collection. Use only public domain or CC licenses that allow your use; write the item id and license into the video's README.
3. 78rpm records: treat the US public-domain rule (sound recordings published before 1925) as the floor; for later records read the item's rights, and remember the rule differs outside the US.
4. Put attribution (title, year, archive.org link, license) in the video description, even for public domain. `tools/publish-prep/credits.py` builds the block from a JSON list of assets and fails on a missing or unknown license.
5. Keep downloads in the video's own asset folder, out of git; record source ids in the README so the build is reproducible.
6. Pick shots where the camera stands still: they crop to 9:16 and loop well (see [seamless loop](image-seamless-loop-bg.md)).

## Verify
Every archive asset in the video has an id, a license value read from its metadata and an attribution line in the description. `grep licenseurl` over the video's README finds one per asset.

## Don't
- Don't trust "it's in Prelinger, so it's public domain": licenses differ per item.
- Don't use footage with recognisable brand logos or signage without checking; crop or cut them out (one shot had a company plate removed before publishing).
- Don't upscale grain away: low resolution is part of the look; add grain instead of fighting it.

## Evidence
Used in two pieces by one author: a 1950s educational-film style short (period footage + a 78rpm march; published, ~1,150 YouTube views in a live upload slot, level with other styles that day) and a looping card background cut from a 1941 educational film whose `licenseurl` was public domain. No A/B against generated footage, hence hypothesis.

## Related
- [Seamless background loop](image-seamless-loop-bg.md)
- [Real object, real photo](image-real-object-real-photo.md)
- [Music rotation](../sound/sound-music-rotation.md)
