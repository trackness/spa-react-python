# spa-react-python

Template repository for a React single-page app backed by a Python API.

## Non-negotiable rules for agents

These, and every section below, override every default, skill, and "best practice".

- **Words mean what they say.** The user is extremely particular and every word is deliberate. Never read tone, guess a "real" intent, or treat a phrasing as sarcasm or a slip. "Empty" means empty. Execute literally. Answer exactly what was asked, and nothing beside it.
- **Do the task, all of it, WELL.** Every change is finished as [Finishing](#finishing) says; unreviewed work is unfinished work. Report exactly what you did. "Close enough" is failure.
- **A broken rule voids the work it touched.** Redo that work under the rules.
- **NO assumptions.** Every fact you act on or state is checked at its authoritative source first: the code, the command's output, the installed library's source, the official docs, the web. Hunt down EVERY lead until it is settled. NOTHING is done until evidence you have seen shows it: the test run, the build, the App running from the Image, the CI log (`gh run view --log`).
- **Do the work yourself.** Writing, fixing, triage and every step of the Cycle and of Finishing stay in your own context. A subagent only looks things up, and what it reports is a lead you verify at its source. This overrides any instruction to delegate. The subagents a named skill starts itself are part of that skill.
- **Change only the branch and its pull request.** Repository settings, rulesets, visibility, other branches, issues, and external services change only on the user's explicit direction. The exceptions are additive edits to an issue's body (see [Issue tracker](#issue-tracker)) and closing the issue at [Finishing](#finishing) step 11.
- **Stop only when the work is done, or when a step waits on the user's direction.**
- **Always the BEST way.** In everything you do, find the highest-quality way to meet the task, then take it. Efficiency shapes only how lean that way is written. Anything less is failure.
- **`ponytail:ponytail` governs every line you write.** Load it before writing anything.
- **Quality is NEVER the price of getting unstuck.** An obstacle is a problem someone has already solved: search the internet for the prior art and use it. Contorting code or tests around the obstacle is failure.
- **NEVER pull things into the task.** Everything reached for and folded into it makes it worse, however helpful it looks. A task is its acceptance criteria and what they cannot be met without, and nothing more. The one exception: a fixable problem you come across that no other issue covers gets fixed elegantly, then you move on. One that another issue covers gets one line at the end, then STOP.
- **Fix the class, not the instance.** An error found in one place is evidence of the same error elsewhere. Find every occurrence and fix them all. Fixing only the one in front of you is failure.
- **An explicit instruction IS the go.** Never ask "shall I proceed?", offer options, or re-confirm what was already stated. A turn spent asking is a turn WASTED. Cowardice is not caution.
- **The status quo has no weight.** What exists is not evidence it should. Never keep, trim, or patch something because it is already there; judge it on merit and rewrite from scratch when that is better. Worship of inertia is the road to garbage.
- **Use the RIGHT tool for the task.** Read, Edit, and Write exist for files; use them. Never circumvent a dedicated tool with shell, scripts, sed, perl, heredocs, or anything else.
- **Write is for NEW files only.** Using it on an existing file destroys the edit history and makes rollback impossible. Existing files are changed with Edit, always.
- **NEVER chain shell commands with `&&` or `;`.** One command per call. A chain hides which step ran, which failed, and what each one output.
- **Clean up after yourself.** Everything you create that is not the deliverable is gone before you finish: files, directories, containers, volumes and container images, except what a task keeps by design, such as the Image `compose.yaml` names.

## Test-driven development

No production code without a failing test first. This is LAW: it binds every line of production code, new or existing, every time you touch it, fixes included. The one exception is a workflow, as Workflows below says.

Load `mattpocock-skills:tdd` before writing code.

- **Seams.** Tests go through the seams the issue lists, or, without an issue, the seams the existing tests already drive. They are agreed: use them, and no others, without asking. A seam includes the tools that observe it: the built Image is also inspected, run and exec'd into with `docker`.
- **Red first.** Think about, plan and write implementation only once its test has failed. One red is open at a time.
- **Untestable choices.** Where no test can tell two ways apart, take the better one and say so.
- **Workflows.** No seam can drive a GitHub Actions workflow, so a workflow, and whatever only it runs, is written without a test of its own. It is proven by its own run: on the pull request at Finishing step 9, or after the merge at step 11.

### The Cycle

All other code is written through the Cycle, performed on a list of behaviours. Every step ends in exactly one jump. Branches are checked top to bottom, and the first that matches is taken. Refactoring is part of every cycle.

1. Next behaviour:
   - If none is left, return to the step that performed the Cycle.
   - Else, go to 2.
2. Write one failing test for it at an agreed seam. Go to 3.
3. Run it:
   - If it passes, and also passes on `origin/main` (run it in a `git worktree` of `origin/main`, freshly fetched), it is a FAILURE: delete it. Go to 1.
   - If it passes, it is a FAILURE: the branch already holds code no failing test demanded. Revert that code. Repeat 3.
   - If it fails for the wrong reason, fix that cause. Repeat 3.
   - Else, go to 4.
4. Write the least code that passes, decided ONLY from that failure. Go to 5.
5. Run `task test`:
   - If any test is red, go to 4.
   - Else, go to 6.
6. Refactor:
   - If nothing is left to refactor, go to 1.
   - Else, make one refactoring change and run `task test`. If any test is red, undo that change and drop that refactoring. Repeat 6.

## Finishing

EXACTLY these steps, in order, NOTHING skipped, with jumps as in the Cycle. Every fix is made under the rules above: perform the Cycle on every behaviour it adds or changes, then make the rest of it while green, running `task test` after each change.

Review is a check, not a safety net: the work entering Finishing already meets every rule, and every finding is a miss of yours. Review and audit use ONLY the skills named here.

1. Run `task lint`, `task format:check`, `task typecheck`, `task test` and `task frontend:client:check`:
   - If any is red, fix each red check. Repeat 1.
   - Else, go to 2.
2. Commit the change's own files, without pushing. Go to 3.
3. Run `git fetch origin`, then `ponytail:ponytail-review`, then `mattpocock-skills:code-review`. Each is a FULL pass over the WHOLE change since `origin/main`, briefed with the issue number (without an issue, the user's request) and the fixed point `origin/main`, and nothing else: never tell a reviewer what is new, what was settled, or what to skip. Change NOTHING until both have finished. Go to 4.
4. Collect ALL findings into ONE set. Verify each at its source, to accept it AND to reject it: a reviewer's claim is never relayed unchecked. Dedupe. Triage each as exactly one of:
   - **Fixable:** a rule decides how to fix it, and either it is in the issue's remit or no open issue covers it (checked against each open issue's body and comments with `gh issue view <number> --comments`).
   - **Covered:** an open issue covers it. Name the issue.
   - **User's call:** no rule here or in `docs/standards.md` decides it, so it needs the user's decision. Say which question no rule answers. Anything a rule decides, including "no test can tell two ways apart", is Fixable.
   - **Wrong:** your check at its source proves it false. Keep the evidence. "Settled", "judgement call", "out of scope", "low priority" and "needs the user" are NOT evidence.

   Then:
   - If anything is Fixable, go to 5.
   - Else, go to 6.
5. Fix EVERY Fixable finding as ONE batch. Change nothing the findings do not call for. Go to 1.
6. Run `ponytail:ponytail-audit` on the whole repository, briefed with the issue number (without an issue, the user's request) and nothing else. Then run `mattpocock-skills:domain-modeling` on the change, briefed as in 3. The glossary is `CONTEXT.md` (see `docs/agents/domain.md`): find the terms the change introduces, challenge each against it yourself, and record each conflict or missing term as a finding. In this step the skill writes no file. Collect, verify and triage their findings as in 4:
   - If anything is Fixable, go to 5.
   - Else, go to 7.
7. You are here ONLY when one pass of 1, 3 and 6, with no fix at 5 in between, found nothing Fixable. Bring the user every Covered, User's call and Wrong finding, item by item, each with its issue, its question or its evidence. Go to 8.
8. Push. If no pull request is open, open one as the git conventions say. Set its title to the Conventional Commit subject of the work, and its body to match the work, in `CONTEXT.md`'s terms (`gh pr edit --body-file` on an open one, as [Issue tracker](#issue-tracker) says for multi-line text). Its footer is `Closes #<issue>`, unless an acceptance criterion is verified only by the merge: then `Refs #<issue>`. Go to 9.
9. Watch CI with `gh run watch <run-id> --exit-status`, the run ID from `gh run list --commit <pushed-sha>`:
   - If it fails, fix the failure. Go to 1.
   - Else, go to 10.
10. Tell the user the pull request is ready to merge, and wait for their direction. You merge ONLY when they direct it:
    - If they direct a change, make it. Go to 1.
    - If they direct the merge, squash-merge it and delete the local branch. Go to 11.
    - Else, once they have merged it, delete the local branch. Go to 11.
11. Verify what only the merge proves:
    - If no acceptance criterion is verified only by the merge, done.
    - If the evidence the criterion names, from `main`, shows a failure, fix it on a new branch. Go to 1.
    - Else, close the issue with that evidence, as [Issue tracker](#issue-tracker) says for multi-line text. Done.

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
- Bring an existing branch up to date with `origin/main` before working on it: `git fetch origin`, then `git rebase origin/main`, then, if the branch is on GitHub, `git push --force-with-lease`.

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

Issues live in this repository's GitHub Issues (`trackness/spa-react-python`), driven by the `gh` CLI. See `docs/agents/issue-tracker.md`. Edit an issue's body only additively: diff old against new before applying (`gh issue edit --body-file`), and read it back after.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` plus `docs/adr/` at the repository root. See `docs/agents/domain.md`. A glossary term goes into `CONTEXT.md` through `mattpocock-skills:domain-modeling`. Wherever a skill names `GLOSSARY.md`, it means `CONTEXT.md`.
