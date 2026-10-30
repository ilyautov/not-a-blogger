# Prompts

Texts that were actually sent to models and agents while building real videos. Every prompt is depersonalized: the
hero is `{character}`, the subject is `{topic}`, the length is `{duration}`. Fill in your own values and run.

Prompts that produce viewer-facing text (script, hook, captions, fact-check output) take a `{language}` placeholder:
the prompt itself is in English, the output is in whatever language your audience speaks.

If a rejected version existed, only the accepted one is here; what did not work is described under "Pitfalls".

## Files

| Group | File | What it does | Status |
|---|---|---|---|
| script | [scenario-from-material.md](script/scenario-from-material.md) | script built from real material, not from a scene | hypothesis |
| script | [viewer-knowledge-table.md](script/viewer-knowledge-table.md) | "what the viewer now knows" table, second by second | hypothesis |
| script | [hook-first-second.md](script/hook-first-second.md) | the first second on three tracks: picture, voice, caption | hypothesis |
| script | [antislop-brief.md](script/antislop-brief.md) | brief block "why past videos were called slop" | proven on 5 videos |
| script | [fact-check.md](script/fact-check.md) | check every claim and number against a source | proven on 5+ videos |
| script | [meaning-check.md](script/meaning-check.md) | meaning check on the script and on frames of the final mp4 | proven on 5 videos |
| image | [backdrop-preamble.md](image/backdrop-preamble.md) | text-free backdrop with room for a title; code adds the text | proven on 2 videos |
| image | [image-agent-wrapper.md](image/image-agent-wrapper.md) | wrapper: a CLI agent makes exactly one image | proven on 2 videos |
| video-gen | [character-passport.md](video-gen/character-passport.md) | archetype character passport reused in every shot | proven on 1 probe |
| video-gen | [json-shot-prompt.md](video-gen/json-shot-prompt.md) | JSON shot prompt: passport, place, action, camera | partial; negative prompt is a hypothesis |
| video-gen | [seed-sweep-still.md](video-gen/seed-sweep-still.md) | key frame: seed sweep on 9-frame clips | proven on 1 probe |
| video-gen | [vlm-judge.md](video-gen/vlm-judge.md) | a multimodal model picks the best take | hypothesis |
| video-gen | [film-look-reference-frame.md](video-gen/film-look-reference-frame.md) | film-look shot in two steps: reference frame, then motion to the line's audio | proven on 1 probe |
| agent | [batch-brief.md](agent/batch-brief.md) | brief skeleton for a batch of short videos with QA and handoff | proven on 5 videos |
| agent | [not-template-long.md](agent/not-template-long.md) | definition of a "non-template long video" for an agent | hypothesis |
| agent | [vertical-relayout-review.md](agent/vertical-relayout-review.md) | vertical by relayout, not crop; frame review before render | proven on 2 long videos and 8 shorts |
| agent | [reel-teardown-card.md](agent/reel-teardown-card.md) | second-by-second teardown of someone else's reel for a remake without plagiarism | hypothesis |
| voice | [reference-recording-text.md](voice/reference-recording-text.md) | text and instructions for recording your own voice reference (lang: ru) | proven on 1 series |
| voice | [tts-script-rules.md](voice/tts-script-rules.md) | line-writing rules for a Russian TTS voice clone, full and short form (lang: ru) | proven on dozens of videos |
| voice | [omnivoice-clone-snippet.md](voice/omnivoice-clone-snippet.md) | clone your own voice from 7 s: recording + exact transcript | proven on 1 video |
| voice | [asr-vocabulary-hint.md](voice/asr-vocabulary-hint.md) | `initial_prompt` vocabulary for ASR that checks takes; never the line itself | proven on 2 videos |

## File structure

1. Header: purpose, model or agent, where tested, status.
2. The prompt itself in a code block, with placeholders in curly braces.
3. "Why": 2–4 lines on what each important part does.
4. "Pitfalls": what broke, including rejected versions.

Anchor phrases that fixed a specific pitfall (for example `locked-off tripod shot`) must survive adaptation: drop
them and the pitfall comes back.

Language-specific prompts carry a `lang:` line in the header. Recording or synthesizing in another language?
Contribute a sibling prompt next to the existing one.

## Contribution rules

A prompt is accepted only if its header has a status and a description of what it was tested on.

- **Status**: "proven on N videos" (or probes), or "hypothesis". "Proven" means the prompt was actually sent to a
  model and the result went into a video a human watched. A prompt that never reached a model is a hypothesis,
  however convincing it looks.
- **Tested on**: model or agent, version if it matters, and the outcome: accepted, published, rejected.
- Do not submit a rejected version as a separate file. Add the accepted one and describe the rejected one in a
  single line under "Pitfalls".
- No people's names, no third-party account names, no personal paths or keys. Generating a real person from a
  photo or a name is not accepted: only your own voice and an invented archetype character.
- One prompt per file in its group: `prompts/<group>/<latin-name>.md`. A new group needs three or more prompts to
  justify it.
- Add a row to the table above. Run `bash scripts/privacy_check.sh` before opening a PR.
