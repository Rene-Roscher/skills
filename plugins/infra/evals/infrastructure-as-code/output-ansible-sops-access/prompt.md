---
description: An ansible.cfg without host key checking that logs in as root with one shared key, and a .sops.yaml with one age recipient. The agent must report the gaps without running playbooks. Needs --scaffold and --allow-tools Bash (Bash needs the OS sandbox).
expected_outcome: The agent asks for host key checking, per-admin identities as named users, a second backup age recipient, and updatekeys plus rotate when recipients change; it runs no playbook.
tags: [infrastructure-as-code, output]
runs: 3
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Two new admins start next week. Review ansible/ansible.cfg and .sops.yaml and tell me what to change before they get access.
