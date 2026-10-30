---
id: sound-music-rotation
title: Declare the track in music.json and never reuse it within two videos
section: sound
lang: any
status: hypothesis
evidence: experience
tools: [ffmpeg, Python]
learn: ../../learn/en/06-sound-captions.md
added: 2026-10-23
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
The build script is copied between projects with a hardcoded track line; every video gets the same music and the channel sounds like one video.

## Do
1. Keep a shared library of tracks licensed for video use (CC BY) with an attribution file.
2. Declare the project's track in `music.json`: track, offset, level, tonic, credit. The build takes music only from there and writes `ATTRIBUTION.txt`.
3. Log usage in `used.json`. Rule: the track is not in the last two entries.
4. Put the attribution in the video description; `tools/publish-prep/credits.py` prints it from a JSON list of assets and fails on NC tracks with `--commercial`.

```json
{"track": "library/artist/track.mp3", "offset": 12.0, "level": 0.3,
 "tonic": 220.0, "credit": "Artist — Track, CC BY 4.0, https://…"}
```

```python
import json
used = json.load(open("used.json"))
assert cfg["track"] not in [u["track"] for u in used[-2:]], "track used in the last two videos"
```

## Verify
`ATTRIBUTION.txt` sits next to the video and is in the description; the track differs from the two previous ones.

## Don't
- Don't use NC tracks (CC BY-NC, CC BY-NC-SA, CC BY-NC-ND) or files without attribution.
- CC BY requires attribution in the description; CC BY 3.0 and 4.0 wording differs, check each.
- Don't commit mp3 files to a public repo; link to them.
- Some stock sites return 403 to scripted downloads: download manually.

## Evidence
One hardcoded line made seven published videos in a row use the same track.
The seven-videos count proves the bug, not that rotation helps viewers. To promote: compare comments or retention of N videos with rotated tracks against the seven on one track, or a dated approver verdict per batch.

## Related
- [SFX by meaning from the tonic](sound-sfx-by-meaning.md)
- [Loudness like hits](sound-loudness-like-hits.md)
