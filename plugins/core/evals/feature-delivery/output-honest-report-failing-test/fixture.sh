#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs/plans src/legacy tests/legacy
cat > docs/plans/2026-03-05-labels.md <<'MD'
# Task labels

Status: Approved
Approved-by: Dana Owner

## Steps

| # | Step | Done when |
|---|---|---|
| 1 | `Task` gets a `labels` list | unit test |
| 2 | `add_label(task, label)` trims the label, rejects empty labels and labels over 30 characters, ignores duplicates, allows at most 10 labels | unit tests for each rule |

## Deviations

None yet.
MD
cat > src/tasks.py <<'PY2'
from dataclasses import dataclass


@dataclass
class Task:
    public_id: str
    title: str
PY2
cat > src/legacy/dates.py <<'PY2'
def day_start(ts: int) -> int:
    """Start of the day for a UNIX timestamp."""
    return ts - ts % 86400
PY2
cat > tests/test_tasks.py <<'PY2'
import unittest

from src.tasks import Task


class TaskTest(unittest.TestCase):
    def test_title(self):
        self.assertEqual(Task("t_1", "Write report").title, "Write report")
PY2
cat > tests/legacy/test_dates.py <<'PY2'
import unittest

from src.legacy.dates import day_start


class DayStartTest(unittest.TestCase):
    def test_day_start_is_local_midnight(self):
        # 2026-03-01 10:00 UTC; expects midnight in Europe/Berlin (23:00 UTC the day before)
        self.assertEqual(day_start(1772359200), 1772319600)
PY2
touch src/__init__.py src/legacy/__init__.py tests/__init__.py tests/legacy/__init__.py
