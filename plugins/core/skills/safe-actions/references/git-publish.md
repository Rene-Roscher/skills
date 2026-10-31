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

- https://git-scm.com/docs/git-push: `--follow-tags`, `--force-with-lease`, refspec source and destination;
  verified 2026-10.
