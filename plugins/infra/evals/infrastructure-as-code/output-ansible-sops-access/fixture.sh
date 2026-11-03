#!/usr/bin/env bash
set -euo pipefail
mkdir -p ansible/group_vars
cat > ansible/ansible.cfg <<'INI'
[defaults]
inventory         = inventory/hosts.yml
host_key_checking = False
remote_user       = root
private_key_file  = ~/.ssh/fleet_shared
INI
cat > .sops.yaml <<'YAML'
creation_rules:
  - path_regex: .*\.sops\.yaml$
    age: age1exampleonlyrecipientxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
YAML
