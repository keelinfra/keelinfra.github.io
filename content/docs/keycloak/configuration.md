+++
title = "Configuration reference"
description = "Every field of the cluster definition file: nodes, SSH, domain, VIP, Keycloak version, and TLS modes."
weight = 4
+++

The cluster definition (`examples/ha-3node.yml` or `examples/single-node.yml`) is the only file
you edit. `./configure -c <file>` validates it and generates the Ansible inventory and vault.

## Fields

| Field | What it does |
|---|---|
| `cluster_name` | Names the cluster: the Patroni scope, the etcd cluster token and the CA file name. |
| `nodes` | The machines. One entry for single-node, three for HA. Each entry: `host` (IP or hostname Ansible connects to) and `name` (the node's cluster identity). The **first node** also hosts the backup repository, Prometheus, and Grafana. |
| `ssh_user` | SSH user for Ansible. Needs passwordless sudo. Key or agent auth only — password auth is not supported. |
| `ssh_private_key` | Optional path to a key; defaults to your SSH agent. |
| `domain` | Public entrypoint. Users reach Keycloak at `https://<domain>/`; point DNS at the VIP, any node, or your external LB. |
| `vip` | Optional keepalived VIP shared by the nodes (same L2 segment required). Leave empty to use an external load balancer or round-robin DNS. |
| `keycloak_version` | The version to **install**. Upgrades are driven by `./upgrade --to <version>`, not by editing this — after an upgrade, update it so a future `./configure` doesn't roll you back. |
| `tls_mode` | `selfsigned` today; `custom` is accepted but not implemented yet — see below. |

## TLS mode

- **`selfsigned`** — generates a local CA and per-node certificates. Good for evaluation and
  intranet use; trust the CA on clients.
- **`custom`** — planned: bring your own certificate. The value is accepted today, but the
  install still generates a self-signed CA, so don't rely on it yet.

Client traffic to Keycloak is TLS: HAProxy passes it through and Keycloak terminates it. Traffic
between the nodes is not encrypted yet: etcd, PostgreSQL replication and the Patroni API run
over plain connections on the node network, so keep that network private.

## Secrets

`./configure` generates database and admin credentials into an ansible-vault under `inventory/`;
the vault password lives in `inventory/.vault_pass` (keep it out of version control). Nothing
sensitive is written to plain-text inventory files.

## Annotated examples

- [3-node HA definition](/docs/keycloak/example-ha-3node/)
- [Single-node definition](/docs/keycloak/example-single-node/)
