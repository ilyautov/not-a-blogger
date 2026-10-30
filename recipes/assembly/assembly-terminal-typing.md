---
id: assembly-terminal-typing
title: Type terminal commands with a stepped clip-path mask
section: assembly
lang: any
status: proven
evidence: measurement
tools: [GSAP, CSS]
learn: ../../learn/en/07-assembly-qa.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
A code block appears whole and hangs; nothing happens inside the frame; it reads as a slide.

## Do
1. Reveal each line with `clip-path: inset(0 100% 0 0) → inset(0 0 0 0)` and `ease: steps(N)`, N = character count.
2. Blink a caret next to it; terminal output arrives after the command, on the narrator's word.
3. Put `white-space: pre` on the line, not the container; otherwise newlines between child `div`s become significant and lines drift.
4. Make the terminal a large filled panel.
5. If typing outlasts the line, shorten the command (optional parts, domain) or type faster.

```js
function type(line, t, cps = 28) {
  const n = line.textContent.length;
  tl.fromTo(line, { clipPath: "inset(0 100% 0 0)" },
                  { clipPath: "inset(0 0% 0 0)", duration: n / cps, ease: `steps(${n})` }, t);
}
```

```css
.term { background: #111b21; border-radius: 12px; padding: 32px; }
.term .line { white-space: pre; font-family: "JetBrains Mono", monospace; }
```

## Verify
Contact sheet shows intermediate typing states; in the fill measurement terminal scenes score above the rest.

## Don't
Don't put `white-space: pre` on the terminal container.

## Evidence
Terminal scenes gave 70–76% frame fill vs ~21% for pill chains.

## Related
- [Content proportion](assembly-content-proportion.md)
- [No Ken Burns](../camera/camera-no-ken-burns.md)
- Example: [Agent said tests passed](../../examples/agent-cheats-long/README.md)
