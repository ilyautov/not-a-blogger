# Style atlas: sources, credits and reuse

Eight teaching images from the author's video workshop, imported on 2 November 2026. These are the author's
productions and studies, not frames copied from a third-party course. Historical descriptions come from the
workshop catalog dated 23 October 2026 and the static-study credits dated 19 October 2026. They are not a new
publication audit. The [source manifest](source-manifest.json) records workshop-relative paths, original and
published hashes, dimensions, origin and status evidence. Workshop-relative paths identify provenance; the
workshop and its engines are not bundled with this textbook.

## Six catalog frame boards

The six JPEGs were copied byte for byte. Each is a curated board, not a continuous video sample. The catalog
records no exact timestamps for these selected frames; none are inferred from visible HUD text. This import
contains no video or audio and establishes no motion, voice, retention or artistic-acceptance result.

| Textbook image | Workshop source | Origin and historical status |
|---|---|---|
| `retro-30s.jpg` | `styles/R30/still.jpg`; `styles/R30/STYLE.md` | Author's procedural Canvas cartoon, retro 1930s styling; approved, not published as of 23 October 2026. |
| `instructional-50s.jpg` | `styles/R50/still.jpg`; `styles/R50/STYLE.md` | Generated clerk and tin-robot scenes, image generation → LTX → film treatment; approved, not published as of 23 October 2026. This selected board is **not genuine 1950s archive footage**. |
| `voxel.jpg` | `styles/VOX/still.jpg`; `styles/VOX/STYLE.md` | Author's three.js production, based on a studied external voxel-skit format (manohin_nocode, acknowledged by the source catalog); published as of 23 October 2026. This is not a claim that the author invented that visual language. |
| `ps2-cutscene.jpg` | `styles/SA3/still.jpg`; `styles/SA3/STYLE.md` | Author's three.js low-poly cutscene inspired by PS2-era games; approved with a note to shorten the opening, not published as of 23 October 2026. Not a screenshot from a commercial game. |
| `film-look.jpg` | `styles/FILM/still.jpg`; `styles/FILM/STYLE.md` | Generated film-look scenes, image generation → LTX → grading/grain; approved, not published as of 23 October 2026. Fictional stylization, not documentary footage. |
| `typography-photo.jpg` | `styles/REEL/still.jpg`; `styles/REEL/STYLE.md` | Author's typography over generated/photo-style backdrops. Top: `hyperframes-agentlies/`, published 28 September 2026. Bottom: `hyperframes-reelprobe/`, no author verdict recorded as of 23 October 2026. The board has a mixed status. |

The full R50 video also uses separate Prelinger archival inserts; the selected generated clerk/robot pair is
not one of those inserts. No archival-footage license is being offered for that board. Video music, voice
references and their licenses are outside this image-only import.

## Two static studies

`paper-collage.jpg` comes from `research-2026-10-19-styles/frames/2-collage.png`;
`halftone-comic.jpg` from `research-2026-10-19-styles/frames/4-comic.png`. Both are static compositions dated
19 October 2026. No new imagery was generated for this import. PNGs were converted without cropping or resizing
using ffmpeg, one frame, JPEG quality 2, `yuvj444p`; only format/compression changed. Both remain 1080×1920.
Their source compositions use existing author-character frames and licensed photographs, plus code-drawn
shapes, text and a generic woman seen from behind. The woman is not a photographic portrait of a news subject.

### Commons photographs

These attributions reproduce the workshop's `research-2026-10-19-styles/frames/credits.md`. Photographic
material and its adapted cutouts retain [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/),
including attribution and ShareAlike for adaptations. The textbook's general CC BY 4.0 notice does not replace
these terms. Keep the photographer, original file link, license link and description of changes with reuse.

| Original work and author | Adaptation and included use |
|---|---|
| [Starship delivery robot.jpg](https://commons.wikimedia.org/wiki/File:Starship_delivery_robot.jpg), **Kjaskren**, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | Original local name `robot-sidewalk.jpg`; `robot-cut.png` is a rembg/u2net cutout. Collage: cutout, white edge/shadow, rescaled and label-covered. Comic: crop, posterization, halftone, overlaid label. Used in both imported studies. |
| [2013 Philadelphia City Hall from N. Broad Street north of Race Street.jpg](https://commons.wikimedia.org/wiki/File:2013_Philadelphia_City_Hall_from_N._Broad_Street_north_of_Race_Street.jpg), **Beyond My Ken**, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | Original local name `philly-cityhall.jpg`; cropped, masked with a torn edge, color-adjusted and layered in the collage. Not used in the imported comic. |
| [Philadelphia Police Car.jpg](https://commons.wikimedia.org/wiki/File:Philadelphia_Police_Car.jpg), **Oleg Yunakov**, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | `police-cut.png`, rembg/u2net cutout. Listed in the original study credits for study 5 only; **not present in either of the two imported images**. Retained here to preserve the original credits boundary. |

The Starship robot photograph depicts a US campus robot, not an Uber Eats robot at the Philadelphia event
mentioned in the study. It is illustrative photography, not event evidence. Newspaper copy, location/time labels
and reaction graphics belong to the composition; this atlas does not verify the underlying news account.

### Author's character and brand

The original static-study credits list `goro-0037-…` and `goro-0041-…` as the author's own character frames from
`hyperframes-t11-robot-order/assets/video/frames/frame_0037.jpg` and `frame_0041.jpg`, upscaled 2× with Lanczos and
cut out with the workshop's matte tool (MediaPipe). The imported collage and comic use the `goro-0037` cutout.
The original credits also list the author's `logo.png` for study 3; that logo is not used in these two studies.
The woman and paper/siren/comic shapes were drawn in code, not generated as a portrait.

The author's mascot, logo, channel name, palette and font pairing remain excluded from the repository licenses,
as described in [BRAND.md](../../../docs/BRAND.md). These atlas images illustrate lessons; they are not a pack of
reusable brand assets. The Commons photo material and adaptations keep their CC BY-SA 4.0 terms; those terms do
not grant rights to independent author-brand elements. To reuse the technique, make your own character and visual
identity and carry the required Commons credits for any photographic material you retain.
