# Stack notes: PHP

PHP images are the hardest case for a minimal runtime: the interpreter, its extensions and their shared libraries
all have to be collected, and PHP code often starts processes through a shell.

## Dependencies

- `composer install --no-dev` against a committed `composer.lock`, with `--no-scripts` if the scripts need the
  full app. Run `composer validate` in CI; it fails on a lock that is out of date with `composer.json`.
- Private packages: an auth token through a secret mount (for example an `auth.json` mounted with `target=`),
  never an `ARG`.
- Never `composer update` in an image build.

## Moving to distroless or another minimal base

Inventory before switching:

1. Shell use. `shell_exec` is documented as executing via the shell. `proc_open` with a string command takes a
   command line; with an array (PHP 7.4 and later) it starts the process directly, without a shell. Check
   `exec`, `system`, `passthru`, `popen`, backticks, and libraries that build command lines (for example a process
   component's "from shell command line" constructor). Each one fails without `/bin/sh`. Convert to the array form
   or keep a shell base.
2. Extensions. Build them in a stage based on the same distribution, then run `ldd` on the PHP binary and on every
   `.so` in the extension directory, and copy the libraries the runtime base lacks.
3. System files. PHP's key generation reads an OpenSSL configuration file. With `OPENSSL_CONF` pointing at a
   missing file, `openssl_pkey_new()` returns `false` and throws nothing (PHP 8.3.10 and 8.4.26, reproduced
   2026-10-31). Check that the runtime image has the file where its OpenSSL build looks, or copy it from the build
   stage and set `OPENSSL_CONF`. Also check the CA bundle, time zone data and locales.
4. Writable paths. Framework caches, compiled views and sessions often write next to the code. Pre-build them in
   the image as root-owned files where the framework allows it, and mount the rest as tmpfs or volumes.
5. The process manager or application server. Confirm it runs as the numeric user, writes nothing outside declared
   paths, and handles SIGTERM.

Then run the full test suite inside the final image. A missing `openssl.cnf` or library shows up as functions that
return `false`, not as a startup error.

## Opcache and read-only code

With code owned by root and read-only, anything the runtime caches on disk needs a declared writable path. If
opcache's file cache (`opcache.file_cache`) is enabled, point it at one.

Sources: https://www.php.net/manual/en/function.proc-open.php,
https://www.php.net/manual/en/function.shell-exec.php, https://getcomposer.org/doc/03-cli.md (verified 2026-10).
