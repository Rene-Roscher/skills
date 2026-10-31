# Moving to a minimal runtime

A minimal base removes the shell, the package manager and most system files. The app keeps working only if
everything it uses at run time is copied in on purpose. Do the inventory before the switch, then prove it inside
the final image.

## Inventory

1. Processes the app starts. Search the code and its dependencies for calls that run a command line through a
   shell (string-form process calls, `system`-style functions, backticks, "from shell command line" helpers).
   Each one fails without `/bin/sh`. Replace it with an argument-array call that starts the binary directly, or
   keep a shell base and record why.
2. Executables the app calls by name. Each must exist in the runtime image at the path the app expects.
3. Shared libraries. In the build stage, run `ldd` on the main binary and on every native extension or module, and
   copy the libraries the base doesn't carry.
4. System files read at run time: CA bundle, TLS and OpenSSL configuration, `/etc/passwd` and `/etc/group` entries
   for the runtime UID, time zone data, locales, `/etc/nsswitch.conf` where name resolution depends on it.
5. Writable paths: cache, tmp, uploads, sockets. Declare them; they become volumes or tmpfs.
6. Debug and operations needs. Without a shell, `kubectl exec` into the container does nothing useful. Plan for
   ephemeral debug containers or logs and metrics instead.

## Proving it

- Run the full test suite inside the final image, not only in the build image. Missing system files often show
  up as a function returning `false` or an empty result, not as an exception.
- Run the smoke test under production constraints (`--read-only`, `--cap-drop=ALL`, `no-new-privileges`, numeric
  user).
- List the executables in the final image (`docker export` piped to `tar -t`, filtered on `bin/`) and compare
  against a committed allowlist.
- Record the scanner finding counts before and after the switch in the change.

## Traps

- `:debug` distroless variants add a busybox shell. Busybox brings many applets, network clients among them
  (`busybox --list` shows which). Never tag a debug variant as the production image.
- Libraries copied into the image by hand are not in the package database, so OS-package scanning does not see
  them. Generate an SBOM in the build stage that lists them, or scan the build stage too.
- A slim image that "only" adds a shell for one startup script keeps the whole shell attack surface. Move the
  script's logic into the application or an init container where possible.

## Sources

- https://github.com/GoogleContainerTools/distroless (verified 2026-10)
- https://docs.docker.com/build/building/best-practices/ (verified 2026-10)
