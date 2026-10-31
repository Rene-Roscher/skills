# Guard artifacts

Load when the project should enforce these rules in its own repository. Propose them to the owner; create them
only when asked. Each guard needs a known-positive case that proves it fires.

1. Test bootstrap guard: the target runtime minor lives in one place (for example the platform setting in the
   package manifest). The test bootstrap compares it with the running version and aborts the suite on a
   mismatch.
2. Required CI job on the production database engine, sharded if it is slow. An in-memory lane may run first
   for fast feedback.
3. `scripts/health-gate`: prints start times of the running components, build times against the last commit
   that touched their source, and port owners. It exits non-zero when a running artifact is older than its
   source. See the checks in the runtime gate reference.
4. Workflow lint: `|| true`, `continue-on-error` and permissive no-files settings fail unless a `# reason:`
   comment sits on the same or the previous line.
5. Guard-suite count: parse the JUnit report and fail below a minimum test count.
6. Pending-schema check: the deploy pipeline and the local end-to-end entry point fail when the framework's
   migration status lists a pending migration.
7. Environment pin test: each value the test config forces is asserted from inside the running app.
8. Build version: the app exposes its version through an endpoint or header, the release workflow records the
   version it deployed, and a post-deploy check compares the two.
9. Completion report template at `docs/templates/completion-report.md`: items verbatim, status from the
   ladder, evidence, environment differences checked.
10. Optional mutation testing on the modules where a silent bug costs most, such as money, authentication and
    tenant scoping.
