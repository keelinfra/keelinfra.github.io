+++
title = "Example: 3-node HA cluster"
description = "The annotated cluster definition for a 3-node HA install."
weight = 8
[extra]
source_repo_path = "examples/ha-3node.yml"
source_sha = "5c622bf"
+++

<!-- GENERATED from keelinfra/keycloak@5c622bf (examples/ha-3node.yml) by scripts/sync_docs.py — edit it THERE, not here. -->

The complete cluster definition for a production 3-node HA install — this is the only file you edit. Run `./configure -c examples/ha-3node.yml` against it.

```yaml
---
# keelinfra/keycloak cluster definition
# This is the only file you need to edit. Run:  ./configure -c examples/ha-3node.yml

cluster_name: keycloak-prod

# The three nodes. First node also hosts the backup repository,
# Prometheus, and Grafana. All nodes run Keycloak + PostgreSQL + etcd.
nodes:
  - host: 10.0.0.11
    name: kc-node1
  - host: 10.0.0.12
    name: kc-node2
  - host: 10.0.0.13
    name: kc-node3

# SSH connection for Ansible (agent or key-based; password auth not supported)
ssh_user: ubuntu
# ssh_private_key: ~/.ssh/id_ed25519   # optional, defaults to agent

# Public entrypoint. Users reach Keycloak at https://<domain>/
# Point DNS at the VIP (if enabled) or at any node / your external LB.
domain: sso.example.com

# Optional keepalived VIP shared by the three nodes (same L2 segment required).
# Leave empty to skip VIP and use an external load balancer or round-robin DNS.
vip: ""

# Keycloak version to install. Upgrades are driven by ./upgrade, not by editing this.
keycloak_version: "26.6.0"

# TLS: "selfsigned" generates a local CA and certs (good for eval/intranet).
# Set to "custom" and drop your cert/key at files/tls/<domain>.crt|.key for production.
tls_mode: selfsigned
```
