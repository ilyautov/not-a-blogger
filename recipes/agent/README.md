# Working with an AI agent

Claude Code and Codex as editor and assistant: permissions, batch runs, clean runs, checking what the agent calls "done". Format: [recipe template](../../templates/recipe.md).

| Recipe | Status | Lang | Gist |
|---|---|---|---|
| [agent-clean-run-setting-sources](agent-clean-run-setting-sources.md) | hypothesis | any | `claude -p --setting-sources "" --plugin-dir` for out-of-the-box demos. |
| [agent-deny-edit-tests](agent-deny-edit-tests.md) | proven | any | `deny: Edit(./tests/**)` holds; `Write(...)` doesn't apply to paths. |
| [agent-evidence-log-wording](agent-evidence-log-wording.md) | hypothesis | any | Ask for an EVIDENCE.md log, not "your reasoning". |
| [agent-feedback-name-the-frame](agent-feedback-name-the-frame.md) | hypothesis | any | Feedback names the second, the defect and the action; five-question checklist. |
| [agent-stdin-dev-null](agent-stdin-dev-null.md) | proven | any | `</dev/null` on agent CLIs inside `while read` loops. |
| [agent-unambiguous-csv-columns](agent-unambiguous-csv-columns.md) | proven | any | One quantity per column name, units in name, own control number. |
| [agent-verify-cli-in-binary](agent-verify-cli-in-binary.md) | proven | any | Check every command in the script via `--help`, `/help`, `strings`. |
| [agent-work-on-copies](agent-work-on-copies.md) | hypothesis | any | Originals outside the agent's folder, copies in work/, hashes checked. |
