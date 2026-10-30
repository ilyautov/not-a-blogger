# Labels and triage

One maintainer runs the kit, so the rules are simple: a bot checks the form, a human decides.

## Labels

| Label | When |
|---|---|
| `recipe` | a new technique is proposed |
| `example` | a video breakdown with metrics |
| `gotcha` | a tool or platform pitfall |
| `lang:<code>` | language-specific pitfall, recipe or translation |
| `translation` | a textbook chapter or a pitfalls file is being translated; the maintainer adds `lang:<code>` by hand, an issue form can't set it |
| `tool` / `template` | a utility or a project skeleton |
| `bug` | a script in `tools/`, `starter/` or `starter-lite/` fails or gives a wrong result |
| `needs-evidence` | interesting, but needs a number, an A/B test or a video link |
| `good first issue` | has a verification path, a clear scope and a named person who will answer |
| `outdated` | a recipe stopped working: model, platform or engine version changed |
| `wontfix` | not about solo content production, an ad, or a duplicate |

## `good first issue` rule

Only when all three hold:

1. The issue names the file to change, with a sample next to it.
2. There is a command or a sign that shows it's done.
3. A person is named who will answer within a week.

One such issue in progress per newcomer. Taken and not done in two weeks: we unassign, no hard feelings.

## Timing

- Reply to an issue: one week.
- Review of a recipe PR: one week.
- A `hypothesis` recipe is accepted if it follows the template and doesn't duplicate an existing one.
