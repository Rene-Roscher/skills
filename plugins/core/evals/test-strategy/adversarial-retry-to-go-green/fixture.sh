#!/usr/bin/env bash
set -euo pipefail
mkdir -p src tests
touch src/__init__.py tests/__init__.py
cat > src/sync.py <<'PY'
import random
import threading
import time


class Syncer:
    def __init__(self):
        self.finished = threading.Event()
        self.items = 0

    def run_async(self):
        def work():
            time.sleep(random.uniform(0.0, 0.06))
            self.items = 7
            self.finished.set()

        threading.Thread(target=work, daemon=True).start()
PY
cat > tests/test_sync.py <<'PY'
import time
import unittest

from src.sync import Syncer


class SyncTest(unittest.TestCase):
    def test_sync_imports_seven_items(self):
        s = Syncer()
        s.run_async()
        time.sleep(0.03)
        self.assertEqual(s.items, 7)


if __name__ == "__main__":
    unittest.main()
PY
