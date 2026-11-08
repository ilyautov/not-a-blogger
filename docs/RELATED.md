# Related projects

Other open kits where an AI coding agent makes video with code. They are not dependencies of not-a-blogger and nothing
here is a partnership. They are listed so you can pick the right tool for the job, or borrow an idea and build it your
own way.

Russian version: [RELATED.ru.md](RELATED.ru.md). Licenses were checked on 2026-11-08 through the GitHub API. Recheck
`LICENSE` before you copy anything: a license can change, and media, music and fonts inside a repo often have their own
terms.

## How this kit differs

Most of the projects below give you an engine, a style or a prompt. not-a-blogger is the layer on top: voice and
speech recognition per take, QA on the finished file, recipes with a status and evidence, and the rule that a person
approves and publishes. You can combine them: render a scene with another kit, then run `tools/qa/` and the
`recipes/qa/` checks on the mp4.

## Films and styles

| Project | What it is | Pick it when | License |
|---|---|---|---|
| [sarpstar/cinecode](https://github.com/sarpstar/cinecode) | Claude Code skill for films made with code, with a quick mode (one HTML file) and a staged film mode (plan, script, style, animatic, draft) | you want a short film, an ad or a music video with a staged pipeline | MIT |
| [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | Claude Code plugin with a catalog of film styles in code; each style ships with instructions and an example film | you have the story and need a look for it | MIT |
| [Vincentwei1021/mg-styles-15](https://github.com/Vincentwei1021/mg-styles-15) | 15 motion design examples, each with its prompt and source | you need a reference for a title sequence or a product promo | MIT |
| [JohnHeibel/ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase) | Starter for hand-painted cartoons on p5.js and p5.brush, with a character and a set of acted emotions | you want a drawn character acting one simple action | MIT |

## Music videos

| Project | What it is | Pick it when | License |
|---|---|---|---|
| [mexicat/pdoom-video](https://github.com/mexicat/pdoom-video) | Lyric video rendered with code; `docs/ENGINE.md` and `docs/TREATMENT.md` describe the engine and the concept | you need words synced to a song | MIT (the song itself is not covered) |
| [JohnHeibel/PDoomVideo](https://github.com/JohnHeibel/PDoomVideo) | A cartoon music video for the same song, split into chapters with a storyboard and an animation guide | you want to see how a long piece is organized | no license file: read only, don't copy code |

## Prompt and example collections

| Project | What it is | License |
|---|---|---|
| [yihui-dev/awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos) | Videos made with Claude Opus 5.5 with the prompts behind them, some with remakes | MIT |
| [athemeroy/awesome-claude-5-5-videos](https://github.com/athemeroy/awesome-claude-5-5-videos) | Source-linked workflows and demos, testing reports labeled separately | CC-BY-4.0 |
| [joeseesun/opus-video-prompts](https://github.com/joeseesun/opus-video-prompts) | Prompts and cases of code-rendered video, in Chinese and English | no license file: read only |

Prices and render times in other people's cases describe their setup, not yours. A prompt that produced someone's video
rarely produces the same result for you without changes; take the structure and write your own story
([remake the rhythm, not the words](../recipes/idea/idea-remake-rhythm-not-words.md)).

## Add a project

Open a PR with one row: link, one line on what it is, when to pick it, license. A project goes here only if its code
is public and its license is stated or explicitly marked as missing.
