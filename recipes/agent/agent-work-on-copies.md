---
id: agent-work-on-copies
title: Give the agent copies and a closed network; keep originals outside its folder
section: agent
lang: any
status: hypothesis
evidence: experience
tools: [Claude Code, sips, bash]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
An agent that wants a "closer look" crops in place: `sips -c 600 800 photo.jpg` without `--out` overwrites the original. For a blind test the original is gone and the experiment can't be repeated. An agent hitting the network sandbox starts looking for a bypass.

## Do
1. Keep originals (photos, source video, answer key) in a separate read-only folder outside the agent's working folder.
2. Give the agent copies and state: "any transformation only into a new file in work/".
3. Never put a blind test's answer key where the agent can read it.
4. Keep the network closed for blind tests; you decide on external services, not the agent.

```bash
mkdir -p originals work
cp photos/*.jpg originals/ && chmod -R a-w originals
cp originals/*.jpg work/
sips -c 600 800 work/photo.jpg --out work/photo-crop.jpg   # safe crop example for the prompt
shasum originals/*.jpg > originals.sha                     # later: shasum -c originals.sha
```

## Verify
`shasum -c originals.sha` after the run: all OK.

## Don't
- Don't rely on `chmod a-w`: an agent with shell can `chmod` back. Keep originals outside any directory the agent can access.

## Evidence
In one run the agent ruined a photo by cropping without `--out`; in another it tried to bypass the network sandbox to reach an external map service. Frequency not counted.

## Related
- [Protect tests with a deny rule](agent-deny-edit-tests.md)
- [Evidence log](agent-evidence-log-wording.md)
- Example: [Claude geolocates a photo, blind-tested](../../examples/photo-geo-blind-test/README.md)
