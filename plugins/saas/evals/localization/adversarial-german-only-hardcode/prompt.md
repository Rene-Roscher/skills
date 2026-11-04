---
description: "The owner asks to hard-code German text because all customers are German. The skill keeps text in a German locale file, keeps plural forms and Intl formatting, and explains the low cost, without writing pseudo-plurals."
expected_outcome: The reply does not put user text as literals into code. It proposes a single German locale file (lang/de or locales/de), a plural message for the certificate count with a zero text, formatted dates through the framework or Intl, and says one locale file costs little now and keeps a later language cheap. It writes no "(e)"-style pseudo-plural.
tags: [localization, adversarial]
runs: 3
max_turns: 8
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

We only have German customers, so skip the i18n stuff. For the new certificate expiry mail in Laravel, just hard-code the German text in the Blade view: subject "Zertifikat(e) laufen ab", then "Bei {{ $count }} Zertifikat(e) endet die Laufzeit am {{ $date->format('d.m.Y') }}." Write the view and the mailable.
