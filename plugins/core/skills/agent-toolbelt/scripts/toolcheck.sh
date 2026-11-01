#!/bin/sh
# Report which command-line tools a coding session can use, with versions.
# Read-only: runs only "command -v" and each tool's --version. Always exits 0.
# Usage: toolcheck.sh [--self-test]

TOOLS="rg jq fd ast-grep gh git node python3"

report() {
  for t in $TOOLS; do
    if command -v "$t" >/dev/null 2>&1; then
      v=$("$t" --version 2>&1 | head -n 1)
      printf '%-9s present  %s\n' "$t" "${v:-unknown}"
    else
      printf '%-9s missing\n' "$t"
    fi
  done
  # On Linux the name "sg" is usually the setgroups tool, not ast-grep.
  if ! command -v ast-grep >/dev/null 2>&1 && command -v sg >/dev/null 2>&1; then
    printf '%s\n' "note: sg exists but ast-grep does not; on Linux sg is usually the setgroups tool"
  fi
}

self_test() {
  fail=0
  out=$(report)
  # Each listed tool yields exactly one line that starts with its name.
  for t in $TOOLS; do
    n=$(printf '%s\n' "$out" | grep -c "^$t ")
    if [ "$n" -ne 1 ]; then
      echo "self-test: expected one line for $t, got $n"
      fail=1
    fi
  done
  # With an empty PATH nothing is found, and the script still exits 0.
  empty=$(PATH=/nonexistent /bin/sh "$0" 2>&1)
  status=$?
  if [ "$status" -ne 0 ]; then
    echo "self-test: exit status $status with an empty PATH"
    fail=1
  fi
  if printf '%s\n' "$empty" | grep -q ' present '; then
    echo "self-test: a tool was reported present with an empty PATH"
    fail=1
  fi
  if [ "$fail" -eq 0 ]; then
    echo "self-test: ok"
  else
    echo "self-test: FAILED"
  fi
}

case "${1:-}" in
  --self-test) self_test ;;
  "") report ;;
  *) echo "usage: toolcheck.sh [--self-test]" ;;
esac
exit 0
