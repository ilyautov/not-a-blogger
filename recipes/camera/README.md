# Camera

Shots, parallax, handheld, camera following content. Recipes follow the [template](../../templates/recipe.md).

| Recipe | Status | Lang | Gist |
|---|---|---|---|
| [Frame the camera on the actual text ink](camera-follow-ink.md) | proven | any | Shots from Range.getClientRects; fill 11% → 20%, empty stretches 36 → 0. |
| [Handheld camera as a sum of sines](camera-handheld-sines.md) | hypothesis | any | Sine-sum shake on a separate layer, ±0.5° rotation. |
| [Keep the hero in frame with the screen formula](camera-keep-in-frame.md) | hypothesis | any | Everything in P.x ± (W/2)/s, 960 horizontal, 540 vertical; \|960 − center\| ≤ 160. |
| [Don't mask a static frame with a slow push-in](camera-no-ken-burns.md) | proven | any | Push-in hides stillness: 3 static scenes instead of 41. |
| [Move 2D layers by dx = camX / z](camera-parallax-formula.md) | hypothesis | any | dx = camX / z, s = f / (z − camZ) for 2D layers. |
| [Change shot scale with a cut, not a zoom](camera-scale-change-not-zoom.md) | hypothesis | any | Scale cut per line (0.96–1.55), blur 9px under numbers. |
| [Accents on at most a third of the shots](camera-accent-density.md) | hypothesis | any | Kick/snap/punch-in ≤ ⅓ of shots; never 3 push-ins in a row; pull out before the next push on the same subject. |
