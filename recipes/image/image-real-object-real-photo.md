---
id: image-real-object-real-photo
title: Show a real object with a real photo, not a drawn primitive
section: image
lang: any
status: hypothesis
evidence: viewer-feedback
tools: [Wikimedia Commons]
learn: ../../learn/en/04-image-and-frame.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The scene needs a real car, gadget, or building and the draft draws it as an SVG silhouette.

## Do
1. For a real object (car, item, place), find a real photo under a free license: Wikimedia Commons, public domain, or CC.
2. Show it full-frame; change shot size with cuts; captions in the lower third; no cards or chrome.
3. Draw only what the story says "the AI drew".
4. Put license and author of every photo in the video description.

```bash
# license metadata of a Commons file
curl -s "https://commons.wikimedia.org/w/api.php?action=query&titles=File:EXAMPLE.jpg&prop=imageinfo&iiprop=extmetadata&format=json" \
 | python3 -c "import sys,json;d=json.load(sys.stdin);m=list(d['query']['pages'].values())[0]['imageinfo'][0]['extmetadata'];print(m['LicenseShortName']['value'],m.get('Artist',{}).get('value',''))"
```

## Verify
No drawn silhouettes of real objects in frame; every photo has an attribution line.

## Don't
Don't use photos with recognisable people without consent or care about personality rights.

## Evidence
No measurements. A video with a drawn car silhouette was sharply rejected ("why not take a picture of a real one"); the Commons-photo version was built but not rated.

## Related
- [One frame, one zone](../transitions/transitions-one-zone-no-chrome.md)
- [Chapter backgrounds in parallel](image-chapter-backgrounds-parallel.md)
