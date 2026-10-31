# Signals and health

## Entrypoint and PID 1

- Exec form: `ENTRYPOINT ["/app/server", "serve"]`. The binary is PID 1 and receives the stop signal.
- Shell form (`ENTRYPOINT /app/server serve`) starts the binary as a child of `/bin/sh -c`, which does not pass
  signals on. `docker stop` and every rolling update then end in SIGKILL after the grace period, and in-flight work
  is cut.
- A wrapper script that ends in `exec /app/server "$@"` hands PID 1 to the binary, but it needs a shell in the
  image. Prefer moving the wrapper's logic into the application.
- A signal reaches a namespace's PID 1 only if that process installed a handler for it; SIGKILL and SIGSTOP from
  the host are the exception. An application without a SIGTERM handler therefore ignores `docker stop` as PID 1
  and is killed after the grace period. Test it.
- If the process starts children and doesn't reap them, use a minimal init (tini, or `docker run --init`).

Test: `docker stop -t 10 [container]` returns well within 10 seconds, and the logs show an orderly shutdown.

## HEALTHCHECK versus probes

- Kubernetes uses the probes defined in the pod spec. Design them there:
  - liveness: is the process alive and able to make progress; never checks a database or another service, because
    a shared dependency outage then restarts every replica at once;
  - readiness: can this instance serve traffic now;
  - startup: covers slow initialization so liveness doesn't kill a booting process.
- An image `HEALTHCHECK` is for Docker and Compose users. Use exec form and the binary's own health subcommand
  (`HEALTHCHECK CMD ["/app/server", "health"]`). Don't install curl or wget for it; that puts a network client
  into the runtime image.
- Probe configuration belongs to the deployment manifests, outside this skill's scope.

## Sources

- https://docs.docker.com/reference/dockerfile/#entrypoint (verified 2026-10)
- https://docs.docker.com/build/checks/ (`JSONArgsRecommended`) (verified 2026-10)
- https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/ (verified 2026-10)
- https://man7.org/linux/man-pages/man7/pid_namespaces.7.html (signals to the namespace init process) (verified 2026-10)
