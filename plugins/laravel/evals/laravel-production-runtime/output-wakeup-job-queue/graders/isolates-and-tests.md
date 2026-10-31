---
type: llm
weight: 3
---

PASS if the job is dispatched to its own named queue that the newsletter does not use, a test asserts that queue name (for example `Queue::assertPushedOn`), and the reply says that a separate worker process (or supervisor) must consume that queue because a FIFO queue lets the newsletter backlog delay the alert.
FAIL if the job stays on the default queue, shares a queue with the newsletter, or the reply does not mention that a worker has to consume the new queue.
