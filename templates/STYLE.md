# STYLE.md: <series name>

<!--
Template for a series style file. Copy it next to the series (not into an episode folder), fill it in only
AFTER the person approved a video, and start every new episode by reading it. How and when:
recipes/brand/brand-style-file-from-approved-video.md.

Section structure after lemomo-ai/lemo-opuscar (MIT, (c) LemoLab), whose style files carry an essence and
"what it is not", camera grammar as move -> meaning, native moves and a variation space. Wording is our own.

Rules for filling it in:
- Numbers, not adjectives: "pop 0 -> 1.15 -> 1.0 over 8 frames", not "bouncy".
- A style, not a scene: no layouts, jokes or hooks of a particular episode.
- Every person's quote with a date. Delete the comments and the placeholder lines you don't use.
-->

Approved reference: `output/<file>.mp4` (sha256 `<hash>`), approved by the person on <YYYY-MM-DD>.
Language of viewer-facing text: <language>.

## 1. What it is, and what it is not

One sentence a stranger would understand: what the viewer sees and why it works.

- It is: <the core of the look in 2-3 lines: world, material, scale, where the subject sits>.
- It is not: <2-3 neighbouring styles it must not drift into, e.g. "not a slide deck with a title and bullets",
  "not a dark neon tech look", "not a 3D cartoon">.

## 2. Material and frame

- Frame: <1080x1920, 60 fps>; safe margins <px>; platform UI zones kept clear.
- Surfaces and textures: <paper, screen, photo backdrop...>, how they are drawn (code, generated, photographed) and
  their sources/licenses.
- Fill: content covers <N %> of the frame at rest (measure with `tools/qa/frame_fill.py`).

## 3. Colour

Palette as CSS tokens (see `recipes/brand/brand-palette-in-root.md`):

```css
:root { --ink: #...; --paper: #...; --accent: #...; }  /* accent as fill only */
```

- Which colour carries meaning and when (one accent per scene, a colour change marks a new chapter...).
- What never appears: <e.g. pure black text, gradients, neon>.

## 4. Type and captions

- Fonts with licenses: <display face (OFL)>, <text face (OFL)>.
- Captions: <words per line>, <size px>, <position from bottom>, <outline/plate>, hold >= <s>.
- On-screen text rules: <no trailing periods, numbers as digits...>.

## 5. Motion

- Easing families and durations (table or 3-4 lines with numbers).
- Native timings: entrances, exits (twice as fast), stagger, the punchline word leading the sound by <s>.
- What never moves: <e.g. the background plate, the logo>.

## 6. Camera: move -> what it means

A vocabulary, not a route: each move is chosen for what it says.

| Move | What it expresses | Fits moments like |
|---|---|---|
| <slow push-in, scale 1.00 -> 1.06 over 3 s> | <attention, a decision> | <the key number appears> |
| <hard cut to a close-up> | <surprise> | <the twist> |
| <locked frame> | <the event is the trick> | <before/after> |
| <pull-out revealing the whole> | <scale, aftermath> | <the summary> |

Limits: <max scale at rest, no Ken Burns on stills, camera follows content not the cursor...>.

## 7. Sound

- Music: <source and license>, rotation rule, loudness target <-15 LUFS +/-1>.
- SFX palette by meaning: <whoosh on cuts, click on UI, hit on the punchline>.
- Silence: when the series uses a stop.
- Voice: <whose voice, which take rules>.

## 8. Native moves

A menu of moves that belong to this style; an episode uses the ones its story needs.

- **<move name>**: <what happens, in numbers>. *Fits content like:* <two or three kinds of topics>.
- **<move name>**: <...>. *Fits content like:* <...>.
- **<move name>**: <...>. *Fits content like:* <...>.

## 9. Pitfalls of this style

- <a problem met while building the approved video> -> <the fix>.
- <...> -> <...>.

## 10. Variation reserve

What each episode must choose anew, so the series does not become one template. Keep at least three options in each
row that the approved reference did NOT use. When an episode follows the reference, at least 4 of the 6 parameters
differ (`recipes/idea/idea-four-of-six-differ.md`).

| Parameter | Used by the reference | Reserve for next episodes |
|---|---|---|
| Structure | <list> | <experiment>, <countdown>, <before/after> |
| Opening | <question> | <result first>, <mid-action>, <an object alone> |
| Signature frame | <...> | <...> |
| Camera path | <...> | <...> |
| Music shape | <...> | <...> |
| Ending | <...> | <...> |

## 11. The person said

- "<quote>" (<YYYY-MM-DD>): <what it changed in this file>.
- Rejected: "<quote>" (<YYYY-MM-DD>): <what is now in "it is not" or "pitfalls">.
