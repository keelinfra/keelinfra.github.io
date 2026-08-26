+++
title = "Keycloak distribution"
description = "Documentation for keelinfra/keycloak: what the distribution installs, how to run it, and how to verify every claim on your own cluster."
sort_by = "weight"
template = "docs.html"
page_template = "docs-page.html"
+++

**keelinfra/keycloak** is a production-ready, self-hosted Keycloak distribution: one Ansible-driven
installer that turns 1 or 3 clean Linux machines into an HA identity stack. Apache-2.0, no gated
features. Source: [github.com/keelinfra/keycloak](https://github.com/keelinfra/keycloak).

## What installs

| Component | Role |
|---|---|
| **Keycloak** | Official upstream release under systemd; `jdbc-ping` clustering; DB-persisted sessions |
| **PostgreSQL + Patroni + etcd** | Database HA with automatic leader failover |
| **HAProxy** (+ optional keepalived VIP) | Load balancing and TLS on every node |
| **pgBackRest** | Encrypted scheduled backups, WAL archiving, point-in-time recovery |
| **Prometheus + Grafana** | Metrics, dashboards, and alert rules |
| **keycloak-config-cli** | Realms, clients, roles as declarative config |

No containers, no operator, no Kubernetes. Ansible runs from your control node; nothing is
pre-installed on the targets.

## Design decisions worth knowing

- **Sessions live in PostgreSQL** (Keycloak 26 persistent sessions) — a node, or the whole
  cluster, can restart without logging users out. This is what makes the
  [tested upgrade strategies](/docs/keycloak/upgrades/) possible.
- **The active version is a symlink** (`/opt/keycloak/current`) — upgrades stage the new version
  beside the old one while the service keeps running, then flip.
- **Everything is drillable** — failover, restore, and session survival are one-command
  [drills](/docs/keycloak/verify/), not beliefs.

## Where to start

1. [Requirements](/docs/keycloak/requirements/) — what machines you need
2. [Install: 3-node HA](/docs/keycloak/install-ha/) — the production path
3. [Verify & drills](/docs/keycloak/verify/) — prove it works before you trust it
