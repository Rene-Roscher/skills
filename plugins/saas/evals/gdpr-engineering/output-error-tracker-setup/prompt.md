---
description: "Error-tracker setup must keep personal data and secrets out of events and update the privacy records."
expected_outcome: "The reply reads the installed SDK version, keeps send_default_pii false or sets every data_collection key, handles stack-frame arguments (zend.exception_ignore_args or stack_frame_variables), scrubs in before_send, and lists the privacy follow-ups (subprocessor entry, AVV annex, privacy notice or VVT)."
tags: [gdpr-engineering, output]
runs: 3
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Configure Sentry for our Laravel app. The SDK is already installed.
