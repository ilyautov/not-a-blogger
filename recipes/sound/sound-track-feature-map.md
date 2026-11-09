---
id: sound-track-feature-map
title: Map the track's beats, hits and envelopes for accents, and treat cuts on the beat as optional
section: sound
lang: any
status: hypothesis
evidence: measurement
tools: [Python, librosa, ffmpeg]
learn: ../../learn/en/06-sound-captions.md
added: 2026-11-09
updated: 2026-11-09
contributors: [not-a-blogger]
---

## When
You want the picture to react to the music (a background pulse on the kick, an interface click on the snare, a
caption landing on a downbeat), or an editor told you that every cut must land on the beat.

## Do
1. Analyse the track once; the map is cached next to it by SHA256: beats, downbeats, sections, kick / snare / hat
   hits with strength 0..1, and 100 Hz envelopes `rms`, `low`, `mid`, `high`.
2. Check `quality.beat_confidence`: below 1.3 the rhythm is weak (orchestral, ambient), don't use the beats. A
   `downbeat_margin` below 0.15 means the bar phase is a guess.
3. Export the map in video time (`--offset` = the track second where the video starts) and load
   `tools/audio/audio-feats.js` in the scene. Use `hit('kick', t)` and `env('low', t)` in canvas scenes; in GSAP
   timelines bake reactions with `pulses(...)` and `follow(...)`.
4. Use it for accents: pulses, UI sounds, a caption on a downbeat. For cuts, `cuts` only proposes the last beat
   ≤ 0.6 s before each phrase's first word; take a proposal where the edit asks for a hit, leave the rest on the word.

```bash
python3 tools/audio/audio_feats.py analyze music/track.mp3
python3 tools/audio/audio_feats.py export music/track.mp3 --offset 12 --duration 30 --out scene/audio-feats.gen.js
python3 tools/audio/audio_feats.py cuts music/track.mp3 --offset 12 --words voice-track.json --out qa/beat-cuts.json
```

## Verify
`show` prints a plausible BPM and hits per minute for the track; in the rendered video the pulse lands on audible
kicks (check 3–4 hits on the frame strip against the waveform); `qa/beat-cuts.json` has `"applied": false`.

## Don't
- Don't snap every cut to the beat as a rule; it is not what makes a hit.
- Don't call the full-mix hits "the drummer's part": without stems kick, snare and hat are approximate.
- Don't use `onUpdate` callbacks for the reaction in a seeked GSAP timeline; they are not called. Bake tweens.

## Evidence
- Breakdown of one niche hit reel and the author's remake of it: cuts landed on a half-beat in 33–35 % of cases for
  both, where random cuts would land in 31–33 %. Neither the hit nor the remake cut on the beat; the hit differed by
  continuous camera drift inside shots, not by cut placement.
- Tests: on a synthetic 120 BPM click track the tool finds the tempo and every thump within 30 ms (`tests/test_audio_feats.py`).
- The accent use (pulses, UI sounds) is not measured for viewer effect: hypothesis.
- Method after mexicat/pdoom-video (MIT): band onsets, fast-attack slow-release envelopes, cut on the last beat before
  the word; code is our own, without stems.

## Related
- [SFX by meaning, tuned to the tonic](sound-sfx-by-meaning.md)
- [Keep noise whooshes on cuts](sound-keep-noise-whooshes.md)
- [Break down the reference before a remake](../idea/idea-breakdown-reference-before-remake.md)
