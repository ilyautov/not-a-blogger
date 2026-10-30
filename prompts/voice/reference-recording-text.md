# Reading text for recording your own voice reference

lang: ru

Recording in another language? Contribute a sibling prompt next to this one.

- **Purpose:** text and instructions for recording your own voice for TTS cloning. Only for your own voice or the
  voice of a person who gave consent.
- **Where tested:** F5-TTS (Russian model) with reference cloning; recorded on a laptop's built-in microphone.
- **Status:** proven on 1 video series: out of 3–4 takes the author picked one as the main reference and voiced the
  following videos with it.

## Prompt

Instructions for yourself and the take text (the quoted lines are read aloud in Russian; English glosses follow
after `#`):

```text
Clone reference: 3–4 takes of ~12 s each, files ref-01.wav, ref-02.wav...
Speak as if to a friend in the car: lively, ironic, with one speed-up and one pause. Clean, no "uhm" and no
laughing over words.

> Слушай, я сегодня проверил одну штуку, и это просто смешно. Нейросеть сама сказала, что так не бывает.
> Представляешь? Сама!

# gloss: "Listen, I tested one thing today, and it's just funny. The neural network itself said that can't
#         happen. Can you imagine? Itself!"
```

Your own version for the channel's topic, if needed:

```text
Write 3 lines in Russian for recording a voice reference, each 10–12 seconds when read aloud.
Channel topic: {topic}. Intonation: talking to a friend, irony, one speed-up and one pause in each line.
Required: a question, an exclamation, a short sentence of one or two words.
Forbidden: numbers as digits, Latin script, abbreviations, swearing, runs of words longer than five syllables.
Next to each line, give its exact transcript for the "audio + text" pair.
```

## Why

A clone copies not only the timbre but also the manner of the reference. Flat reading gives a flat, boring clone;
conversational delivery with a speed-up gives a lively one. A question, an exclamation and a short phrase in one
take show the model the full range of intonation. The exact transcript is mandatory: the model aligns the sound
with the text, and any mismatch spoils the clone.

## Pitfalls

- A reference with someone else's meme intonation was rejected by the author: "the voice is a meme, not mine".
  Record yourself in your normal manner, just livelier than when reading text.
- A built-in microphone gives clicks and crackle. Run the recording through a click filter before cloning
  (`ffmpeg -af adeclick`).
- Speeding synthesis up to 1.15× got the verdict "the voiceover is awful". Keep F5 speed at 1.0 and set the tempo
  through the reference.
- Level-match the finished synthesis takes and keep pauses between lines at 0.8 s or less: the author hears long
  pauses immediately.
- Do not clone someone else's voice without consent. Do not put voice references into the repository.
