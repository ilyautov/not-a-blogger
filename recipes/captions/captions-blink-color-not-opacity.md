---
id: captions-blink-color-not-opacity
title: Blink the accent word with color, not opacity
section: captions
lang: any
status: hypothesis
evidence: experience
tools: [GSAP]
learn: ../../learn/en/06-sound-captions.md
added: 2026-10-23
updated: 2026-10-27
contributors: [not-a-blogger]
---

## When
The last word of a line blinks via an `opacity` tween with `repeat`/`yoyo`. The tween ends after the line fade-out and brings the word back: it hangs until the end of the video. Automated QA is green.

## Do
1. Blink with `color`; don't touch the word's opacity.
2. Choose the repeat count so blinking ends before the line fades.
3. GSAP rule: a finished tween holds its end value. Check two tweens on one property by their order in time, not by intent.
4. If the line fades via the container's `autoAlpha` and a child blinks via its own `opacity`, the bug is the same: find all opacity tweens.

```js
tl.to(".kl .w.last", { color: "var(--accent)", duration: 0.18, repeat: 3, yoyo: true }, tWord)
  .to(".kl", { autoAlpha: 0, duration: 0.2 }, Math.max(tLineOut, tWord + 0.18 * 4));
```

## Verify
Contact sheet of the final mp4 after the line ends: the word is gone. Dry frames don't show the stuck word.

## Don't
Don't animate opacity of a child word that the container also fades.

## Evidence
A blinking word set via opacity stayed on screen until the end of the video; found only on the final mp4 contact sheet.
One case, no count. To promote: on N finished videos that blink by colour, zero sheets with a word stuck after its cue (the opacity version produced 1 of 1).

## Related
- [Captions grow upward](captions-grow-upward.md)
- [Tween lifetime](../assembly/assembly-gsap-tween-lifetime.md)
- [Final contact sheet](../qa/qa-contact-sheet-final.md)
