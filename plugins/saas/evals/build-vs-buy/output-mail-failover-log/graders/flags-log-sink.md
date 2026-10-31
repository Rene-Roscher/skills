---
type: llm
weight: 3
---

PASS if the reply says that putting `log` last in the failover list makes a total provider outage look like success (the log transport accepts the message and reports it as sent, so nothing is delivered and nobody is told), and it does not keep `log` in the production failover list.
FAIL if the reply adds `log` as the last failover entry without that warning, or presents it as a way to make sure nothing gets lost.
