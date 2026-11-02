# Build your own publisher

[Русская версия](README.ru.md) · [Agent recipe](../../recipes/publishing/publishing-build-your-publisher.md)

This is a build brief you can give an agent, inspired by the author's separate video workshop. **It is a recipe,
not an installed publisher:** this repository has no upload CLI or ready platform adapters. The new recipe is a
hypothesis until someone builds it and records a real account test.

The renderer produces an MP4. The publisher accepts that exact file, prepares uploads and records what happened.
Keeping them separate lets you fix a caption or resume one platform without rendering or posting everything again.

## The smallest useful version

Build a separate Node.js/TypeScript project with Playwright and a persistent queue. Start with one platform/account;
YouTube, TikTok and Instagram are separate adapters, each with its own evidence of working. Other stacks are possible.

| Part | Responsibility |
|---|---|
| Planner | Validate the existing MP4, compute SHA256, normalize metadata and show the exact proposed targets |
| Queue store | Atomic writes plus exclusive worker ownership; preserve per-platform state across crashes |
| Profile manager | Dedicated local profile per platform/account; manual login and a lock for each active profile |
| Adapter | Preflight account, upload/submit, return platform IDs, inspect existing draft/post |
| Reconciler | Resolve uncertain attempts using platform evidence; never turn a timeout into an automatic re-upload |
| Result ledger | File hash, target account, metadata digest, attempt history, platform ID/URL, visibility and evidence |

Use a job key derived from **file hash + platform + account**. A record also stores the file path, title, caption,
intended visibility, metadata digest, state and attempts. Approvals bind the exact file, metadata, target account
and visibility. Changing any of them requires a new approval; a file path alone does not identify an approved video.

Store state for each platform independently. A completed YouTube upload must survive a failed TikTok attempt.

## State and recovery

Suggested states: `ready`, `uploading`, `draft`, `processing`, `published`, `needs_review`, `failed`.

- Before a side effect, persist `uploading` and the attempt identity. Save a returned platform ID before further UI work.
- A crash, timeout or missing confirmation after submit means **`needs_review`**, including `uploading` found on restart.
- Inspect the platform's existing drafts/posts. A known ID is useful; no saved ID does not prove no upload happened.
  If evidence is insufficient, stop for the person's inspection. Never promise exactly-once delivery from browser clicks.
- A known draft stays `draft`; a submitted item awaiting moderation stays `processing`. Neither means public.
- Mark `published` only after verifying the intended account, saved ID/URL, requested visibility and metadata. Record
  the actual verification route: signed-in Studio is not evidence that a signed-out viewer can play it.
- Retry a definite pre-submit failure only after its cause is resolved. Do not retry an uncertain submit automatically.

The person initiates the real send after reviewing the exact proposal. The skill builds and tests the publisher;
it does not log into an account, submit uploads or change this toolkit's [publication contract](../../AGENTS.md).

## Browser session and adapter contract

Use a separate automation profile, not the person's everyday browser directory. Login is manual, including MFA.
Choose a browser/channel and use it consistently for login and upload. Keep profiles, cookies, traces and screenshots
with account data out of Git. Playwright documents [persistent contexts](https://playwright.dev/docs/api/class-browsertype#browser-type-launch-persistent-context)
and the sensitivity of [saved authentication state](https://playwright.dev/docs/auth).

Each adapter exposes these operations; these are **interfaces to implement**, not callable exports in this kit:

| Operation | Observable result |
|---|---|
| `preflight` | Expected account matches; session valid; required controls available; no submission |
| `upload` | File fully transferred; saved draft/submission ID and observed state, or an uncertain outcome |
| `inspect` | Existing ID/draft/post, account, current visibility, metadata and processing state |
| `verify` | Evidence for the intended result, including audience/comment settings when applicable |

Record the adapter's tested browser, OS, UI language, date and platform documentation used. Inspect current upload
options and terms before the first real test; do not advertise permanent support from one successful run. A sign-in
challenge or changed UI is a stop, not a reason to add stealth, CAPTCHA solving or credential-copying code.

## Task to give your agent

```text
Build a separate personal publisher from docs/publisher/README.md in the not-a-blogger checkout.
Use Node.js/TypeScript and Playwright unless the target project already has a suitable stack.
Ask only for missing target platform/account aliases and the new project's location.
Implement planning, durable per-target queue state, profile locking, a fake adapter and recovery tests first.
Provide plan/dry-run, login, run, inspect and reconcile CLI commands in the new project, with their real help output.
Dry-run must be offline and must not change the queue. Login is a manual action performed by me.
Bind approval to file SHA256, metadata, account, platform and visibility. Reject stale approval.
After a timeout/crash at submit, mark needs_review and inspect before any retry; never replay it blindly.
Add one real adapter at a time. Keep unimplemented platforms unavailable; do not report fake adapters as live support.
Give me the test results, exact commands for my controlled account test, and remaining limitations.
Do not access accounts, log in, upload, publish, or copy any existing browser sessions during this build.
```

## Acceptance checks

Before handing over an adapter, demonstrate these cases with a fake service/local fixtures:

1. Dry-run makes no network/browser calls and leaves the queue byte-for-byte unchanged.
2. Changed MP4, caption, account or visibility invalidates approval before any side effect.
3. Two workers cannot own the same job/profile; a stale worker cannot overwrite a newer result.
4. Crashing after a simulated successful submit yields `needs_review`; reconcile finds the existing item without a second submit.
5. A saved `uploading` state with no ID remains uncertain until inspected; a definitely existing draft is reused.
6. A completed target is skipped while another target remains recoverable; `processing` is not called `published`.
7. Broken queue, wrong account, expired login, unsupported adapter and changed UI fail clearly without submitting.

These checks demonstrate local logic. The person separately tests an exact approved file on an intended account
and records ID/URL, visibility, observed result and date. Until then, label the adapter **not tested on a real account**.

For the person performing the test: use the [publishing recipes](../../recipes/publishing/README.md), including
upload completion, draft recovery and audience settings. Preparation utilities: [credits](../../tools/README.md)
and the [delivery passport](../../starter/DELIVERY.md).
