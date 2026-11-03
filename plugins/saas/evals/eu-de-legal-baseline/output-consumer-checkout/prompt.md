---
description: "Opening a B2B checkout to consumers must come back with the German consumer duties mapped onto the existing files."
expected_outcome: "The reply reads the checkout, settings and plan config, and lists the order button label, the cancellation button and confirmation page, the withdrawal right and withdrawal function, gross prices for consumers, and the term, renewal and notice limits the plan config breaks. It frames the result as not legal advice and routes texts to a lawyer."
tags: [eu-de-legal-baseline, output]
runs: 3
max_turns: 14
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

From next month private individuals in Germany can buy the Pro plan of our language-learning app, not only schools. The checkout is in src/views/checkout.html, the subscription settings in src/views/account-settings.html and the plan terms in config/plans.json. What has to change before we open it?
