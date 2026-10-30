# Shoot checklist: a real tool running on camera

Fill in the bracketed parts for your tool. The example is `tool/focus_nag.py`.

## 0. Prepare (5 minutes)

1. Use a browser or profile that is **not** the one you publish or log in to accounts from. A clean Safari window
   or a fresh browser profile is enough. No personal tabs, bookmarks bar hidden.
2. Open the "work" tabs the scenario needs (for the example: any document, plus the page from `work_url`).
3. Turn on Do Not Disturb so no notification with a name or a message lands in the frame.
4. Sound up if the tool speaks: the phone must hear it.
5. Rehearse with the dry run: `python3 tool/focus_nag.py --feed tool/demo.tsv`. Edit `demo.tsv` until the printed
   actions match your script beat by beat.

## 1. First run and the permission prompt

```sh
python3 tool/focus_nag.py --live --check
```

macOS asks "Terminal wants access to control Safari" (Automation). **Film this prompt**: it is the honest part of
the video and viewers ask about it. Allow. Chrome asks separately.

If macOS asks for Accessibility or Screen Recording, something is wrong: the example does not need them. Deny.

Then: `python3 tool/focus_nag.py --live`, terminal behind the browser.

## 2. Takes (15–20 s each, film 2–3)

Phone vertical, over the shoulder: laptop screen and hands in frame, no face needed. Side light, no glare.

1. [Setup line, on camera or voice-over.] Screen shows the work document.
2. [Trigger 1.] Tool reacts with line 1.
3. [Trigger 2.] Line 2.
4. [Trigger 3.] Line 3 and the visible action (tab closes by itself, work page opens).
5. [Punch line.]

Leave 2–3 s between triggers: **pauses must be longer than the poll interval** (`interval_s`, 1.5 s here) or the tool
misses a beat. If a take breaks: Ctrl+C, start again, the counter starts from zero.

Also film separately:
- close-up of the screen at the moment the tool acts (2 takes);
- close-up of the macOS permission prompt;
- **the terminal** with the command and its log lines, 2–3 s: proof that it is a real program, not an edit.

## 3. After

- Stop: Ctrl+C. Revoke: System Settings > Privacy & Security > Automation > Terminal, untick the browsers.
- Check every frame for names, notifications, tabs, bookmarks and account avatars before editing.
- Put the tool and its README where viewers can get it (a gist or a repo), link in the description.
