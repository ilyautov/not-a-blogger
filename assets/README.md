# assets

README banners and the GitHub social preview. The illustration is the author's mascot at an editing desk; like the
mascot itself it is not covered by the repository licenses, see [BRAND.md](../docs/BRAND.md). Provenance: the picture
was generated on 24.10.2026 with an image model (codex-cli `image_generation`) and composed with Alumni Sans and
Onest (both SIL OFL) over it; no stock footage, no third-party art.

| File | Size | Used in |
|---|---|---|
| `readme-banner.jpg` | 1774×887 | README.ru.md |
| `readme-banner-en.jpg` | 1774×887 | README.md |
| `social-preview.jpg` | 1280×640 | GitHub → Settings → Social preview (uploaded by hand) |
| `before-after.jpg`, `before-after-en.jpg` | 1696×638 | README.ru.md, README.md |
| `pipeline.svg`, `pipeline-en.svg` | 1280×250 | README.ru.md, README.md |
| `qa-contact-sheet.jpg` | 1200×676 | both READMEs |
| `examples-grid.jpg` | 1150×670 | both READMEs |

Before/after and the contact sheet are real frames of two published long-forms, not mock-ups. "Before" is frame
369.9 s of a 20-minute long-form on the old card layout (grid occupancy 25 % at that frame, 24 % median over the
video); "after" is second 42 of "The agent said the tests passed" (79 % at that frame, 78 % median). Both numbers come
from the 16×8 grid measurement described in `docs/QA-THRESHOLDS.md`. The contact sheet is that video's own QA sheet.
`examples-grid.jpg` is composed from the `examples/*/poster.jpg` files.

`textbook/`: thirteen 1536×1024 illustrations for the PDF textbook (`scripts/build_textbook_pdf.py`), the cover and one
per numbered chapter. Same mascot and status as above (see [BRAND.md](../docs/BRAND.md)), no text inside the pictures, so
the Russian and English PDFs share them. Provenance: generated with an image model (codex-cli `image_generation`),
`ch00`, `ch01`, `ch03`, `ch05`, `ch06`, `ch07` on 23.10.2026 and the rest on 29.10.2026; prompts in
[textbook/PROMPTS.md](textbook/PROMPTS.md). They are story illustrations, not screenshots of the pipeline.

`textbook/style-atlas/`: eight teaching images for chapter 04 in both languages. Six JPEGs are byte-identical
copies of curated frame boards from the author's workshop catalog (23.10.2026); two are JPEG conversions of static
collage/comic studies (19.10.2026), without cropping or resizing. The latter do not establish animation. Generated
1950s/film scenes are stylizations, not documentary archive. Sources, original/published SHA256, dimensions and
historical status dates are in [source-manifest.json](textbook/style-atlas/source-manifest.json).
[Atlas CREDITS.md](textbook/style-atlas/CREDITS.md) preserves the Commons photographers and CC BY-SA 4.0 terms for
photo material/adaptations in the two studies. These terms are separate from the book's general text license;
the existing [author-brand exceptions](../docs/BRAND.md) still apply. Examples teach staging, not reuse of the
mascot or a claim that source-workshop engines are bundled.
