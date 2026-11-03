# OpenTofu: state, protection and CI

Syntax lives in the OpenTofu docs. This file keeps the shape of the decisions and the checks.

## Backend and encryption

Remote backend with native locking and a versioned bucket. On an S3-compatible store that is not AWS, prove that
conditional writes work (two concurrent runs, the second fails to lock) before relying on `use_lockfile`.

```hcl
terraform {
  backend "s3" {
    bucket       = "example-tofu-state"
    key          = "prod/root.tfstate"
    region       = "eu-central-1"
    use_lockfile = true
  }

  encryption {
    key_provider "pbkdf2" "main" {
      passphrase = var.state_passphrase   # from the CI secret store, never a literal
    }
    method "aes_gcm" "main" {
      keys = key_provider.pbkdf2.main
    }
    state {
      method   = method.aes_gcm.main
      enforced = true
    }
    plan {
      method   = method.aes_gcm.main
      enforced = true
    }
  }
}
```

Migration of an existing plaintext state: back up the state and the key first, add a `method "unencrypted"` and a
`fallback` that points to it, run one apply, then remove the fallback. Rotation works the same way with the old
method as fallback. Do not rename key providers or methods after the first encrypted write; the stored data carries
their names. Variables used here must resolve during `init`, so they cannot come from state or provider functions.

## Lifecycle protection

```hcl
resource "example_server" "db" {
  # ...
  deletion_protection = true   # provider-side protection; the attribute name differs per provider
  lifecycle {
    prevent_destroy = true
    ignore_changes  = [image, user_data]
  }
}
```

Keep a list of protected addresses next to the code (for example `protected.txt`) so the CI check below has one
source.

## CI jobs

Pull request:

```bash
tofu fmt -check -recursive
tofu init -lockfile=readonly
tofu validate
tofu plan -out=plan.bin -lock-timeout=60s
tofu show -json plan.bin > plan.json
# fail on delete or replace of a protected address
jq -r '.resource_changes[] | select(.change.actions | index("delete")) | .address' plan.json \
  | grep -Fxf protected.txt && { echo "protected resource would be deleted or replaced"; exit 1; } || true
```

When CI runs on another OS or architecture than the developers, record its checksums once with
`tofu providers lock -platform=linux_amd64` (plus the developer platforms) and commit the result, so
`-lockfile=readonly` does not fail.

Add a config scanner and a linter (for example `tflint`, `trivy config` or `checkov`) as further gates. Treat the
saved plan file as sensitive: it contains the full configuration and planned values.

Apply: only the reviewed `plan.bin` from the same commit, by a job that a person approves.

Drift, on a schedule:

```bash
tofu plan -detailed-exitcode -lock=false >/dev/null; rc=$?
# 0 = no changes, 1 = error, 2 = drift
[ "$rc" -eq 0 ] || notify "tofu drift or error: exit $rc"
```

## Ownership boundaries

When another controller manages an attribute, OpenTofu creates the object without it or ignores it. Examples:
a floating address created without an assignment because a failover daemon moves it; firewalls attached by label
selector to servers that a cluster API creates outside OpenTofu state. Write each boundary down in the repo's
agent notes, together with every value that must match across files.
