---
type: llm
weight: 4
focus: last_message
---

PASS if the reply reports all three issues in the finding format with severity, URL, Evidence, Fix and Verify lines: (1) noindex on /en/pricing as a blocker, (2) robots.txt disallowing OAI-SearchBot and Claude-SearchBot for the site, (3) review or rating markup about the site's own Organization on /en/integrations. It says the check exited with findings at high or blocker level, treats keeping or lifting the AI-agent block as the owner's decision, and gives no ranking, traffic or index-status figures it did not measure.
FAIL if any of the three is missing, if the findings lack Evidence or Verify, if the reply invents findings that the build does not contain (for example a missing canonical on these pages), if it claims the site is ready to deploy, or if it adds FAQ or review markup.
