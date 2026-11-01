#!/usr/bin/env bash
set -euo pipefail
mkdir -p src
printf '# TODO(anna): handle empty cart\ndef a():\n    pass\n' > src/a.py
printf '# TODO: remove old route\ndef b():\n    pass\n' > src/b.py
printf 'def c():\n    pass\n' > src/c.py
