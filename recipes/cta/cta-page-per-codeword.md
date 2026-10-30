---
id: cta-page-per-codeword
title: Give every codeword its own static page and reply with its link
section: cta
lang: any
status: hypothesis
evidence: experience
tools: [GitHub Pages, HTML]
learn: ../../learn/en/08-vertical-publishing.md
added: 2026-10-23
updated: 2026-10-29
contributors: [not-a-blogger]
---

## When
Codeword material is sent differently each time: file in DM, channel post, plain text. Links get lost, material can't be updated, and on YouTube it can't be sent at all.

## Do
1. One static-site repo, one folder per word.
2. The person replies to comments with the direct page link; on YouTube the route is the profile link or a Related Video (see [YouTube link](cta-youtube-link-in-description.md)).
3. The agent builds and checks the pages locally and stops there. Pushing the repo and turning on GitHub Pages are external actions: the person does them ([AGENTS.md](../../AGENTS.md), rule 5). Hand over the local folder plus the exact commands below.
4. iPhone config profiles (`.mobileconfig`) are served by GitHub Pages as `application/octet-stream`, so the file may land in Files instead of installing. Give step-by-step workaround on the page (open from Files, then Settings → Profile Downloaded).

```text
guides/
  index.html          # list of all words
  styles.css          # shared style
  keys/index.html     # page for the word "keys"
  ads/index.html      # page for "ads" + downloads
```

```bash
# agent: local preview only
python3 -m http.server 8000 --directory guides     # open http://localhost:8000/keys/

# person's steps (the agent hands these over, does not run them)
git add keys && git commit -m "page for the word keys" && git push
# GitHub Pages: Settings -> Pages -> Deploy from branch (main, /root)
```

## Verify
Before handing over: the page renders in the local preview, every link and download in it resolves. After the person publishes: the page opens on a phone without login and the reply link leads exactly to it.

## Don't
- Don't treat the page as lead capture: it's public to everyone. If you need a contact, link onward to a channel or form.

## Evidence
No own click measurement.

## Related
- [Codeword in comments](cta-codeword-in-comments.md)
- [YouTube Shorts: profile link or Related Video](cta-youtube-link-in-description.md)
