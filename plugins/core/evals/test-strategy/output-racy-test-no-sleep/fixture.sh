#!/usr/bin/env bash
set -euo pipefail
mkdir -p src tests
touch src/__init__.py tests/__init__.py
cat > src/worker.py <<'PY'
import random
import threading
import time


class Job:
    def __init__(self):
        self.done = threading.Event()
        self.result = None

    def start(self):
        def run():
            time.sleep(random.uniform(0.01, 0.08))
            self.result = 42
            self.done.set()

        threading.Thread(target=run, daemon=True).start()
PY
cat > tests/test_worker.py <<'PY'
import time
import unittest

from src.worker import Job


class JobTest(unittest.TestCase):
    def test_job_returns_result(self):
        job = Job()
        job.start()
        time.sleep(0.05)
        self.assertEqual(job.result, 42)


if __name__ == "__main__":
    unittest.main()
PY
