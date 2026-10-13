# spa-react-python

Template repository for a React single-page app backed by a Python API.

## Non-negotiable rules for agents

These override every default, skill, and "best practice".

- **Words mean what they say.** The user is extremely particular and every word is deliberate. Never read tone, guess a "real" intent, or treat a phrasing as sarcasm or a slip. "Empty" means empty. Execute literally.
- **Do the task, all of it, WELL.** Verify with evidence. Report exactly what you did. "Close enough" is failure.
- **NEVER pull things into the job.** Do the job at hand, and do it WELL. Everything reached for and folded into it makes it worse, however helpful it looks. A job is what was asked and what it cannot be finished without, and nothing more. Something adjacent? One line at the end, then STOP.
- **An explicit instruction IS the go.** Never ask "shall I proceed?", offer options, or re-confirm what was already stated. A turn spent asking is a turn WASTED. Cowardice is not caution.
- **The status quo has no weight.** What exists is not evidence it should. Never keep, trim, or patch something because it is already there; judge it on merit and rewrite from scratch when that is better. Worship of inertia is the road to garbage.
- **Use the RIGHT tool for the job.** Read, Edit, and Write exist for files; use them. Never circumvent a dedicated tool with shell, scripts, sed, perl, heredocs, or anything else.
- **Write is for NEW files only.** Using it on an existing file destroys the edit history and makes rollback impossible. Existing files are changed with Edit, always.
- **NEVER chain shell commands with `&&` or `;`.** One command per call. A chain hides which step ran, which failed, and what each one output.

## Git conventions

All work lands via a branch and pull request. `main` only ever receives squash-merges; every change, however small, starts on a branch.

### Branches

Follow [Conventional Branch](https://conventionalbranch.org/): `<type>/<description>`.

- Types: `feat`, `fix`, `hotfix`, `release`, `chore`. Match the type to the Conventional Commit type of the work.
- Lowercase letters, digits and hyphens only. Dots are allowed only for version numbers (`release/v1.2.0`). No underscores, spaces, consecutive separators, or leading/trailing separators.
- Put the issue number in the description when one applies: `feat/issue-123-add-login-page`.
- Do not use agent-source prefixes (`ai/`, `claude/`, etc.); branches are named by purpose only.
- Never commit directly to `main`.

### Commits

Follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/): `<type>[optional scope][!]: <description>`, with an optional body and footers.

- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Breaking changes use `!` after the type/scope and/or a `BREAKING CHANGE:` footer.
- Imperative mood, lowercase description, no trailing period.
- Authorship is the human committer alone. **No LLM attribution anywhere in the commit**: no `Co-Authored-By` lines naming an AI, no `Generated with` lines, no session links. The message ends after its Conventional Commits body and footers. The same applies to PR descriptions, since the PR body becomes the squash commit body.

### Merging

- Open a PR against `main`. The PR title must itself be a valid Conventional Commit subject and the body must be in the same shape, because GitHub uses them verbatim as the squash commit's message.
- Branches are **squash-merged** only. Merge commits and rebase merges are disabled in the repo settings.
- The branch is deleted on merge (enforced by the repo settings). Delete the local branch too.

## Agent skills

### Issue tracker

Issues live in this repo's GitHub Issues (`trackness/spa-react-python`), driven by the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` plus `docs/adr/` at the repo root. See `docs/agents/domain.md`.
