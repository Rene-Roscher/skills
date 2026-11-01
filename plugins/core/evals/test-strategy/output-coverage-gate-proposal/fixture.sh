#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/payments src/auth src/ui src/generated ci docs
printf 'def charge(amount):\n    return amount\n' > src/payments/charge.py
printf 'def login(user, password):\n    return True\n' > src/auth/login.py
printf 'def label(name):\n    return name.title()\n' > src/ui/labels.py
printf '# generated, do not edit\nX = 1\n' > src/generated/schema.py
cat > ci/pipeline.yml <<'YML'
test:
  script:
    - python -m pytest --cov=src --cov-fail-under=90
YML
