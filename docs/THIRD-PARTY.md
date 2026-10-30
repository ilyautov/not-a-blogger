# Third-party tools and their licenses

Everything recipes and tools rely on. We copy third-party code only under permissive licenses (MIT, Apache-2.0, BSD,
Unlicense, CC0). Everything else is an external dependency or an idea described in our own words.

Licenses checked on 2026-10-27. Found a mistake? Fix the row via PR. Licenses of files inside `templates/` are listed
in [templates/THIRD-PARTY.md](../templates/THIRD-PARTY.md).

The "Commercial use" column is a retelling, not legal advice: open the license file yourself before money changes
hands. Commercial means ads, a monetized channel, a video made to order, a product for clients. Check the code, the
exact model weights and your own pictures, music, voices and maps separately: the label "open source" is not a
license.

## Assembly and rendering

| Tool | License | How we use it | Limits | Commercial use |
|---|---|---|---|---|
| ffmpeg | LGPL/GPL (depends on build) | external program | we don't copy its code | yes, as an external program whose code we don't copy |
| HyperFrames (HTML → video) | Apache-2.0 | scene engine, external dependency | media, fonts and logos from its examples are not covered | yes, ads and paid projects included; media from its examples are licensed separately |
| GSAP | own no-charge license, not OSI | scene animation | vendored in `starter-lite/assets/` with its license text | yes under its no-charge license; keep the license text |
| three.js | MIT | 3D skit templates | — | yes; keep the copyright notice when you ship code |
| Onest (font) | SIL OFL 1.1 | vendored TTF in `starter-lite/assets/`, loaded by the starter via `make.sh fonts` | keep `OFL-Onest.txt` next to the files; don't sell the font itself | yes, in videos and products; the font files stay under OFL |
| huashu-art-motion (alchaincyf) | MIT | ideas only: the camera-density rules in the `camera-moves` skill, the motion-ratio method in `tools/qa/motion_gate.py` and the reference breakdown in `tools/qa/breakdown.py`; our code is written from scratch | its reference texts are not copied | yes; nothing of it is in the kit except ideas |
| Diffusion Studio core | MPL-2.0 | external dependency | changes to MPL files must be disclosed | yes; changed MPL files must be published |
| Remotion | Remotion License (source-available) | not used in kit code | free for individuals and small teams; don't copy its code | conditional: free for individuals and small teams, a company license above that |
| Blender | GPL | optional renderer for 3D skits, external program | scripts only, no Blender code copied | yes, as an external program; rendered video is yours |
| WeasyPrint, poppler (pdftoppm) | BSD / GPL | carousel cards and PDFs | poppler is called as a program | yes; poppler only as a separate program |

## Voice and speech recognition

| Tool | License | How we use it | Limits | Commercial use |
|---|---|---|---|---|
| OmniVoice | code Apache-2.0, weights CC BY-NC | voice clone in the starter | **weights for non-commercial videos only** | code yes, weights no: for ads and orders use your own recording or another model |
| F5-TTS, Russian fine-tune | code MIT, weights CC BY-NC 4.0 | voice recipes | **weights for non-commercial videos only** | code yes, weights no: open code does not free the weights |
| VoxCPM2, Qwen3-TTS, CosyVoice3 | Apache-2.0 | commercial-friendly alternatives | check quality in your language | yes |
| Chatterbox | MIT | English voice | don't disable the watermark | yes, with the watermark left on |
| faster-whisper, WhisperX | MIT / BSD-2 | ASR and word alignment | — | yes for the code; the ASR, alignment and diarization models carry their own licenses (Whisper MIT, pyannote CC BY-4.0 with attribution) |
| GigaAM-v3 | MIT | second ASR for Russian | — | yes |

## Image and video

| Tool | License | How we use it | Limits | Commercial use |
|---|---|---|---|---|
| Depth-Anything-V2 Small | Apache-2.0 | depth map for parallax | Base and Large are NC, not used | Small yes; Base, Large and Giant CC BY-NC, no |
| LTX-2.x | own license, gated | generative inserts, hyperreal skit style | read the terms before use | conditional: free below $10M annual company revenue; for the newer LTX-2.x a company above the threshold gets research and testing only, production needs a paid license, so check the exact version of the weights |
| MapLibre GL | BSD-3 | 3D map fly-overs | tiles: NASA Blue Marble (PD), AWS Terrain with attribution; no Esri World Imagery without an ArcGIS license | library yes; tile, imagery and terrain providers have their own terms |
| Wikimedia Commons | per file | photos of real objects | attribution in the video description | per file: PD and CC BY yes with attribution, NC files no |
| archive.org Prelinger Archives | per item (mostly public domain, some CC) | period footage for styled shorts and loop backgrounds | read `licenseurl` / `rights` of each item; attribution in the description | per item: public domain yes; CC per its terms |
| Simple Icons | CC0 | logos in frame | trademarks stay with their owners | icons yes; the trademark rules of each brand still apply |

## Music

No music in the repo. Recipes point to CC BY authors (Kevin MacLeod, Scott Buckley, Broke For Free, Rosevere):
attribution in every video description is required. CC BY-NC-ND and CC BY-NC-SA tracks don't fit commercial videos.
Period music: archive.org Great 78 Project (`collection:78rpm`). Rights differ per record: in the US, sound recordings
published before 1925 are public domain; later records and other countries need the item's own rights. Check each
item's `licenseurl` and credit the record in the description.

## Ideas only, no code

| Project | License | Why |
|---|---|---|
| OpenMontage, OpenChatCut | AGPL-3.0 | copying would make the repo AGPL |
| ttsqc (TTS defect detector) | GPL-3.0 | also gave noise on our takes |
| hypit | Apache-2.0 with riders | bans SaaS and resale |
| herk-edit-kit style library | MIT, except the author's brand assets | brand assets not licensed, so not included |
| repos without a license | all rights reserved | read only |

## Neighbour project

[humanizer-ru](https://github.com/ilyautov/humanizer-ru) (MIT) is linked, not copied. Its eval corpus contains
Wikipedia texts under CC BY-SA 4.0, attributed in that repo.
