# Ansible: roles and production runs

## ansible.cfg baseline

```ini
[defaults]
inventory          = inventory/hosts.yml
roles_path         = roles
host_key_checking  = True        ; the default, written down so nobody flips it
retry_files_enabled = False
; no remote_user = root, no shared private_key_file; each admin uses an own key or SSH certificate
```

Known hosts: write the host key from provisioning output into a tracked `known_hosts` file, or sign host keys with
an SSH CA and trust the CA. A host whose key changed fails until someone checks why.

## Role conventions

- Rendered files start with a "managed by Ansible, role X" comment.
- Prefer drop-in files over editing a vendor file. Know the merge order: `sshd` takes the first match, so a drop-in
  that must win sorts first; `sysctl.d` takes the last value.
- `validate:` on every config the service parses (`sshd -t -f %s`, `visudo -cf %s`, the service's own test flag).
- Handlers run at the end of the play. When order matters, `register` the change and restart in a following task.
- Read-only probes that must also run in check mode get `check_mode: false`.
- Test the remote file (`stat` on the host), not a path on the controller.
- Secret files: mode `0600`, tasks with `no_log: true`, values from the SOPS vars plugin.

## Lockout-safe order on new hosts

DNS resolver before package installs; firewall with the SSH rule first; the admin user and key in place before
the default user is locked; exclusive `authorized_keys`; a recorded allowlist of source addresses for recovery.

## Production run

1. `ansible-playbook site.yml --check --diff --limit [one host]` and read the diff.
2. Confirm inventory secrets decrypt without printing them.
3. For an active and passive pair, deploy to the passive node first.
4. `serial: 1` canary, then the rest. Keep a pin of the current and the last known good version and a rollback
   playbook.
5. A verify playbook that only reads and asserts health.

Idempotence test: run the playbook twice against a throwaway host or a Molecule scenario; the second run must show
`changed=0`.
