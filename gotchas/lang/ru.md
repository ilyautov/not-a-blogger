# Russian TTS and ASR pitfalls

Measured on a Russian voice clone (F5-TTS Russian fine-tune, OmniVoice) and Whisper-family ASR. Russian examples in
quotes, English gloss in brackets. Recipes with fixes: `recipes/voice/` (look for `lang: ru`).

## TTS

- **F5-TTS clips the tail of a line.** 0 s of trailing silence in all 6 measured takes, cut off at −44 dB. Add a
  sacrificial last word and cut by word alignment.
- **Automatic cut misses the sacrificial word.** In 34 of 246 takes (14%). Rescue by energy and check ASR on the last
  0.9 s.
- **Punctuation barely makes pauses.** Period ≈0.43 s, colon 0.30, dash, comma and ellipsis ≈0.08. Need a pause?
  Synthesize segments separately.
- **The first word gets damaged.** A leading vowel gets a glued-on «к» [k] sound; a leading consonant word disappears
  entirely. Make the first word sacrificial.
- **A line starting with the lead-token word loses it.** The clone wrapper prepends «Так,» [so,] and cuts it by
  timestamps, so «Так что…» [so that…] loses the real word. Rephrase the start.
- **Stress marks don't help.** «+» marks and doubled vowels work inconsistently («модэль» [model with hard e],
  «флАгман» [flagship]). Replace a stubborn word with a synonym.
  Doubling worked twice: «Ахуееть» on F5 and «Двеести» [two hundred, stress on е] on OmniVoice voice design, which
  also stopped the first word from being half-swallowed. Order stays as in voice-stress-by-rewording: reword first,
  doubling is the fallback, checked by ear. Captions keep the normal spelling.
- **Unicode stress marks (U+0301) give a heavy accent in OmniVoice.** *Hypothesis.* Agents put a combining acute on
  almost every word; the owner heard «как будто лютый акцент» [like a thick foreign accent]. Count per video: 0 in the
  two that took off, 47–433 in the rest. Same text and seed with and without marks sound different. The blind A/B is
  not listened to yet. Strip U+0301 before synthesis (`tools/voice/ru_tts_text.py` does) and reword a mis-stressed word.
- **Too many «!» in OmniVoice lines.** *Hypothesis.* The engine doesn't act an exclamation and once slipped into
  falsetto on one. One series had «!» or «?!» in 67 % of lines against 10 % in approved references. Keep «!» to about
  one line in ten.
- **«ИИ» [AI] gets swallowed.** Say «нейросеть» [neural network] instead.
- **RUAccent can put the stress on the wrong syllable.** «+учит» instead of «уч+ит» [teaches] in a check of one
  video's lines. Don't trust automatic stress placement without listening; reword the line instead.
- **Fixed seed.** Regeneration repeats the same defect; only a text edit fixes it.
- **Chatterbox is slow in Russian.** 4.5 syllables/s vs 5.4 for F5, stress drifts. Fine for English.
- **Stretched interjections break differently per engine.** Two of six engines inserted an extra vowel into a
  stretched swear word. Tune the spelling per engine.

## ASR

- **«гит» heard as «гид»** [git → guide] in all 12 takes while the audio was right. Re-check with large-v3 and a topic
  vocabulary prompt.
- **The ttsqc detector of Russian TTS defects (GPL-3.0) gives decoder garbage on our takes.** 15 runs: no clipped
  endings or insertions found; every hit sat at confidence 0.43–0.48 against a 0.4 threshold and showed greedy
  wav2vec2 output where the audio was clean. Its scorer is calibrated on its authors' corpus and the config targets
  CUDA. Not adopted; GPL-3.0 also rules out copying its code. Its "parse confidence" did drop (28 %, 43 %) on takes
  with phonetic spelling or smeared speech.
- **«ChatGPT»** comes out as «чад джи пяти» [chad gee five]. Expect English brand names to be mangled; verify by ear.

## Text from the agent

- **"Write simply" doesn't change Russian answers; a countable rule does.** *Hypothesis.* «Сначала ответ, одна мысль в
  предложении, до 15 слов, без вступлений, выводов и длинных тире» in `CLAUDE.md`: 8 questions × 1 run, words −47 %,
  scanner markers 24 → 9, longest sentence 30 → 16 words. Recipe: `recipes/text/text-claude-md-plain-russian.md`.

Have the same issues in another language? Contribute a sibling file next to this one.
