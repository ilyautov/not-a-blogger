# Teardown card of someone else's reel for a remake without plagiarism

- **Purpose:** the agent breaks down one viral reel by someone else second by second and extracts a transferable
  technique with a condition for applying it. The remake is made on your own material, not word for word.
- **Where tested:** Claude Code and Codex with a reel-directing skill; batches of short-video remakes.
- **Status:** hypothesis. References for remakes were broken down with this template; view growth from the remakes
  was not measured separately.

## Prompt

```text
Break down one reference video: {link or file}. My future video: topic "{topic}", hero {character},
{duration} s. Write the "Our version" section in {language}; write the teardown itself in English.

- Checked: frames / speech via ASR / continuous viewing / listening:
- Unavailable or unreliable:

## Opening
- First short line or paraphrase:
- First text:
- First object and action:
- Viewer, the clear promise and the unknown outcome:
- What is added right after the hook:

## Course of the video
| Time | Line or paraphrase | Visible event / role of text and host | New knowledge / expectation |

## Mechanics and assessment
- Sound: only what was heard; mark what was unavailable:
- Weak spot, with a specific moment:
- Facts, author's claims, fictional scene:
- Transferable technique, source timecode, condition for applying it:
- What to test on our material:

## Remake
- What we take: the second-by-second structure, the hook type, the rhythm of knowledge changes.
- What we do NOT take: the text of the lines, the jokes, the character, the music, the visual style, the frames.
- Our version in 5 lines on the same second-by-second structure, but with our own material and our own resolution.
```

## Why

A hit works through mechanics: what is shown in the first second, when new knowledge arrives, where the twist is.
Mechanics can be transferred; text and imagery cannot. The "checked" and "unavailable" fields keep the agent from
inventing sound or retention it never saw. A timecode for the technique makes the teardown verifiable.

## Pitfalls

- A verbatim copy of a successful video, even your own, was rated "slop". A remake follows the structure second by
  second, not the words.
- The agent describes sound of a video it never listened to. Write "unavailable" if the audio did not go through ASR
  or listening.
- Retention and completion of someone else's video are not visible from outside. Do not infer them from the view
  count.
- Do not translate or closely paraphrase the original's lines and jokes: that is plagiarism, not a technique.
