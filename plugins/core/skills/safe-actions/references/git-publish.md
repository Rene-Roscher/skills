# Git publish

Load this when the user asked you to commit, push, tag or release. Asking for one of these is not asking for the
others: "commit this" does not include a push.

## Before a commit

- Follow the repository's branch policy (trunk commits or pull requests). It is in the project facts file; don't
  assume a generic default.
- `git status` and `git diff --staged` show only files that belong to this change. Stage files by name, not with
  `git add -A` in a shared checkout.
- The commit message follows the project's format. Add no trailers or footers the project does not use.

## Before a push

1. Fetch, then list what the push would publish: `git log --oneline @{upstream}..HEAD` (or
   `git log --oneline origin/main..HEAD` when no upstream is set).
2. Read every commit in that range. A push publishes the pushed commit and every ancestor the remote does not have
   yet.
3. If the range contains commits that are not part of the requested change (someone's work in progress, commits
   that wait for an API or a deploy), stop. Name them and ask how to proceed.
4. Show the exact command and refspec you intend to run, and the branch it updates. On repositories that deploy on
   push, say so.

Ways to publish only the requested change, each of which needs the user's choice because it changes history or
creates branches:

- Create a branch from the remote branch and cherry-pick the fix onto it, then push that branch.
- Reorder local commits so the fix comes first, then push the fix by its commit: `git push origin [commit]:main`.
  The source of a refspec can be any commit expression; the destination must be a ref name.

## Before a repository or package goes public

A visibility switch or a first push to a public remote publishes every commit, not only the working tree.

1. Run the scanner over files and history, with the private term list (people, customers, internal projects and
   hosts), kept outside the repository:
   `python3 scripts/leak_scan.py [repo] --history --terms [file]`.
2. Read every finding. Resolve errors; read each warning and decide. A deliberate match (a fake key in a test
   fixture) gets `leak-scan: allow P02 [reason]` on its line or the line above.
3. Read README, docs, ADRs and changelog yourself: the scanner finds speaker prefixes and phrases such as
   "as you said", not a paraphrased chat decision or an internal process note. Claims about status, authorship
   and security are checked as `evidence-before-claims` describes.
4. A finding in history: before the first public push, rewrite the history with the user's approval (for example
   with `git filter-repo`) and scan again. After it, rotate every exposed secret first; removal alone does not
   revoke a copy someone already cloned.
5. Report what was scanned, the term list used (by count, never the terms) and the result, then ask for the
   visibility change as an approval-tier action.

## Force-push

- Never on a shared branch.
- On your own unshared branch, use `--force-with-lease`, which refuses the update when the remote ref is no longer
  the value you expect.

## Release checklist

A release is complete only when every step is done. Report the ones that are not.

1. Version bumped in the file the project uses, and the changelog entry written.
2. Release commit created.
3. Annotated tag created on that commit: `git tag -a [tag] -m "[message]"`.
4. Commit and tag pushed. `git push --follow-tags` pushes annotated tags that point at the commits being pushed;
   otherwise push the tag by name.
5. Release entry created on the forge, if the project uses one.
6. Registry check: the package, image or plugin is visible at the new version in the registry users install from.

A tag without a push, a push without a tag, or a tag whose release never reached the registry is half a release.

## Sources

- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository:
  rotate exposed secrets, rewrite history with `git filter-repo`, cached copies and forks keep the data; verified
  2026-11-05.
- https://git-scm.com/docs/git-push: `--follow-tags`, `--force-with-lease`, refspec source and destination;
  verified 2026-10.
