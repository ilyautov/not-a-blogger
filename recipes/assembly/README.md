# Assembly

Timeline, GSAP, scene layout, running heavy steps. Recipes follow the [template](../../templates/recipe.md).

| Recipe | Status | Lang | Gist |
|---|---|---|---|
| [Lay out blocks to the frame's proportion](assembly-content-proportion.md) | proven | any | Quote 1080 px at 84+ px, chain in two columns; fill 25% → 32%. |
| [Frame = pure function of time](assembly-deterministic-timeline.md) | hypothesis | any | Paused timeline, seeded LCG, no Date.now. |
| [Never let a tween outlive its scene](assembly-gsap-tween-lifetime.md) | proven | any | All moves before t_out − 0.30; an overlay hung for ~6 minutes. |
| [Durations, easing, stagger from a table](assembly-motion-timing.md) | hypothesis | any | ≥ 3 eases, exit 2× faster than entry, items × stagger ≤ 0.5 s. |
| [Block at the cut, rows light on words](assembly-no-empty-scene-start.md) | proven | any | Block at the cut, rows at .24–.3 light up per word; fill 23% → 33–43%. |
| [Serialize heavy jobs behind a lock](assembly-serialize-heavy-jobs.md) | hypothesis | any | One TTS and one browser per machine via a lock. |
| [Terminal typing via stepped clip-path](assembly-terminal-typing.md) | proven | any | clip-path inset + steps(N); terminal scenes reach 70–76% fill. |
| [Anchor animation to word times](assembly-word-anchored-animation.md) | hypothesis | any | W(cue, "word") from alignment instead of timers. |
| [Render motion-heavy reels at 60 fps, set in one place for every stage](assembly-60fps-motion.md) | hypothesis | any | fps stored once (60 for motion reels), read by render, re-layout and verify; timings in seconds. |
| [Frame sheet before a draft render](assembly-frames-before-draft-render.md) | hypothesis | any | On a 15 s video draft/15 fps/fragment saved ≤ 4 s; check frames instead. |
| [Motion moves in frames and percent](assembly-motion-vocabulary-numbers.md) | hypothesis | any | Smear 1 frame at 150–300 %, boil every 2 frames, pop 0→1.15→1 in 8 frames, knife delete, baseline rise. |
