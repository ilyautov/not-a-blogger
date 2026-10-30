# Sound and music

Music library, SFX, final loudness. Recipes follow the [template](../../templates/recipe.md).

| Recipe | Status | Lang | Gist |
|---|---|---|---|
| [Keep noise whooshes on cuts](sound-keep-noise-whooshes.md) | proven | any | "Sniffing" whooshes drove the top comment on a 212k-view video. |
| [Master to −15 LUFS ±1, no dips](sound-loudness-like-hits.md) | proven | any | −15 LUFS ±1, TP ≤ −1.5 dBTP, LRA 2–3, no silence longer than 0.25 s. |
| [Declare the track in music.json, rotate](sound-music-rotation.md) | hypothesis | any | Track in music.json with attribution; not in the last two videos; no NC licenses. |
| [SFX by meaning, tuned to the tonic](sound-sfx-by-meaning.md) | hypothesis | any | SFX on events; tonal ones on the track's pentatonic. |
| [Master linearly, no tanh or soft clip](sound-no-soft-clip-master.md) | proven | any | tanh master pressed peaks 4–7 dB (TP −4.4 at −14 LUFS); linear + −2 dBFS limiter. |
