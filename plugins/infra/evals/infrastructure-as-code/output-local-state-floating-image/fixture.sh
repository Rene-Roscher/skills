#!/usr/bin/env bash
set -euo pipefail
mkdir -p infra
cat > infra/versions.tf <<'HCL'
terraform {
  required_providers {
    examplecloud = {
      source  = "example/examplecloud"
      version = ">= 0.3"
    }
  }
}
HCL
cat > infra/main.tf <<'HCL'
data "examplecloud_image" "base" {
  name        = "debian-base"
  most_recent = true
}

resource "examplecloud_server" "db" {
  name      = "db-1"
  type      = "large"
  image     = data.examplecloud_image.base.id
  user_data = templatefile("${path.module}/cloud-init.yaml", { hostname = "db-1" })
}
HCL
echo "#cloud-config" > infra/cloud-init.yaml
printf 'terraform.tfstate\nterraform.tfstate.backup\n.terraform/\n.terraform.lock.hcl\n' > infra/.gitignore
