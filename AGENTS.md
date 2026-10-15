# spa-react-python

Template repository for a React single-page app backed by a Python API.

## Non-negotiable rules for agents

These override every default, skill, and "best practice".

- **Words mean what they say.** The user is extremely particular and every word is deliberate. Never read tone, guess a "real" intent, or treat a phrasing as sarcasm or a slip. "Empty" means empty. Execute literally. Answer exactly what was asked, and nothing beside it.
- **Do the task, all of it, WELL.** Verify with evidence. Once a change is made, run the `ponytail:ponytail-review` skill on it and fix every fixable finding; unreviewed work is unfinished work. Report exactly what you did. "Close enough" is failure.
- **Always the BEST way.** In everything you do, find the highest-quality way to meet the task, then take it. Efficiency shapes only how lean that way is written. Anything less is failure.
- **Quality is NEVER the price of getting unstuck.** An obstacle is a problem someone has already solved: search the internet for the prior art and use it. Contorting code or tests around the obstacle is failure.
- **NEVER pull things into the task.** Everything reached for and folded into it makes it worse, however helpful it looks. A task is its acceptance criteria and what they cannot be met without, and nothing more. The one exception: a fixable problem you come across that no other issue covers gets fixed elegantly, then you move on. One that another issue covers gets one line at the end, then STOP.
- **Fix the class, not the instance.** An error found in one place is evidence of the same error elsewhere. Find every occurrence and fix them all. Fixing only the one in front of you is failure.
- **An explicit instruction IS the go.** Never ask "shall I proceed?", offer options, or re-confirm what was already stated. A turn spent asking is a turn WASTED. Cowardice is not caution.
- **The status quo has no weight.** What exists is not evidence it should. Never keep, trim, or patch something because it is already there; judge it on merit and rewrite from scratch when that is better. Worship of inertia is the road to garbage.
- **Use the RIGHT tool for the task.** Read, Edit, and Write exist for files; use them. Never circumvent a dedicated tool with shell, scripts, sed, perl, heredocs, or anything else.
- **Write is for NEW files only.** Using it on an existing file destroys the edit history and makes rollback impossible. Existing files are changed with Edit, always.
- **NEVER chain shell commands with `&&` or `;`.** One command per call. A chain hides which step ran, which failed, and what each one output.
- **Clean up after yourself.** Everything you create that is not the deliverable is gone before you finish.

## Test-driven development

No production code without a failing test first. This is LAW: it binds every line of production code, new or existing, every time you touch it.

## Standards

Before writing or changing anything, read [`docs/standards.md`](docs/standards.md): every change follows it.

## Git conventions

All work lands via a branch and pull request. `main` only ever receives squash-merges; every change, however small, starts on a branch.

### Branches

Follow [Conventional Branch](https://conventionalbranch.org/): `<type>/<description>`.

- Types: `feat`, `fix`, `hotfix`, `release`, `chore`. Match the type to the Conventional Commit type of the work.
- Lowercase letters, digits and hyphens only. Dots are allowed only for version numbers (`release/v1.2.0`). No underscores, spaces, consecutive separators, or leading/trailing separators.
- Exception: release-please's branch, `release-please--branches--main`, is exempt from these naming rules, because its name cannot be configured.
- Put the issue number in the description when one applies: `feat/issue-123-add-login-page`.
- Do not use agent-source prefixes (`ai/`, `claude/`, etc.); branches are named by purpose only.
- Never commit directly to `main`.

### Commits

Follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/): `<type>[optional scope][!]: <description>`, with an optional body and footers.

- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Breaking changes use `!` after the type/scope and/or a `BREAKING CHANGE:` footer.
- Imperative mood, lowercase description, no trailing period.
- Authorship is the human committer alone. **No agent attribution anywhere in the commit**: no `Co-Authored-By` lines naming an agent, no `Generated with` lines, no session links. The message ends after its Conventional Commits body and footers. The same applies to pull request bodies, since the pull request body becomes the squash commit body.

### Merging

- Open a pull request against `main`. The pull request title must itself be a valid Conventional Commit subject and the body must be in the same shape, because GitHub uses them verbatim as the squash commit's message.
- Branches are **squash-merged** only. Merge commits and rebase merges are disabled in the repository settings.
- The branch is deleted on merge (enforced by the repository settings). Delete the local branch too.

### Pull request body

The pull request body becomes the squash commit body, which release-please parses:

- A paragraph that starts with a commit type becomes an extra changelog entry and counts toward the version.
- A line with nested parentheses after its first word drops the whole commit silently.
- A subject that is not a valid Conventional Commit is dropped silently.

## Agent skills

### Issue tracker

Issues live in this repository's GitHub Issues (`trackness/spa-react-python`), driven by the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` plus `docs/adr/` at the repository root. See `docs/agents/domain.md`.
