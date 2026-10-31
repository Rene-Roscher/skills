# Deploy verification

Load when the task ends in "live".

Deploys and production checks leave the machine. Ask first where `safe-actions` says so; reading a public
endpoint is usually fine, changing anything is not.

## 1. Did the deploy run

- Find the release or deploy run for the merged commit in the CI system, for example `gh run list --workflow
  [deploy workflow] --branch [branch]` on GitHub Actions.
- Check that it started, finished and succeeded. A queued run that never started is not a deploy. Runners can
  stop picking up jobs, for example after a billing problem on hosted runners.
- Check that it deployed the commit you mean, not an older one.

## 2. Is the new version running

- Read the version the app reports: a version endpoint, a response header, a build ID in the page source, or
  the image digest the orchestrator runs.
- Compare it with the commit or tag of the release run.
- For staged or canary rollouts, check what share of traffic runs the new version.

## 3. Is the change visible

- Observe the changed behaviour at the production surface: the changed response, the rendered page, the job
  result.
- Caches and CDNs can serve the old response. Check cache headers, or request a path that bypasses the cache.
- Documentation and static sites are deploys too. Merged docs are not published docs.

## Wording

| Situation | Write |
|---|---|
| Merged, no deploy run found | merged, deploy not confirmed |
| Deploy run succeeded, version not checked | deployed, not seen live |
| Version matches and the change is visible | live |
| Production not reachable from here | deployed, live check not possible from this environment |
