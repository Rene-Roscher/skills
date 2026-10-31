# Shared workspace

Load this when other people or sessions may work in the same checkout, database or machine. Assume they do unless
you know otherwise: parallel agent sessions in one checkout are common.

## Formatters and fixers

- Pass an explicit list of the files you created or edited in this task. Don't run them on a directory, on the
  whole repository, or in a "changed files" or "dirty" mode: those modes include other sessions' uncommitted work.
- Check `git status --porcelain` right before. If it lists files you did not touch, they are someone else's.

## Git commands that discard work

`git checkout .`, `git restore .`, `git reset --hard`, `git clean`, and `git stash` act on every file in the
checkout, including files you did not create. Use them only on paths you own, by name, or ask first.

If you need a clean tree to test something, use a separate worktree (`git worktree add`) instead of clearing the
shared one.

## Migrations and databases

- Check migration status immediately before a rollback. Another session may have run a newer migration.
- Roll back by file or path, never by step count: a step count rolls back whatever ran last, which may not be
  yours.
- Give every parallel session its own test database. Derive its name from a per-session variable in the test
  bootstrap, and refuse the shared default name when parallel runs are possible.
- Never reset, wipe or reseed the shared dev database without asking. Its data may be someone's test setup.

## Lockfiles and generated files

- Change lockfiles only with the tool version the project pins (container, version manager, CI image). Another
  version can rewrite the lockfile so CI fails.
- Don't commit regenerated files that another session or a watcher is also writing.

## Processes, containers and ports

- Don't kill or restart processes you did not start, especially ones running as another user. Ask.
- Don't delete container volumes or run clean targets that wipe local data without approval.
- If a port is taken, pick another one for your process instead of stopping the one that holds it.

## Reports

When something in the workspace changed that you did not do (a file, a migration, a running process), mention it
in the report instead of undoing it.
