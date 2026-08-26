+++
title = "Requirements"
description = "What you need to install the keelinfra Keycloak distribution: 1 or 3 Linux nodes, SSH with sudo — nothing pre-installed on targets."
weight = 1
+++

## Target nodes

- **1 or 3 Linux nodes.** Three for production HA; one for evaluation, dev, or small internal
  setups (no HA — see [the growth caveat](/docs/keycloak/install-single-node/)).
- **Supported OS:** Ubuntu 22.04 / 24.04, RHEL/Rocky 9, Debian 12.
- **SSH access with sudo** from your control node (key or agent based — password auth is not
  supported).
- That's it. Ansible runs from the control node; **nothing is pre-installed on the targets.**

## Control node

Any machine with `ansible-core` and SSH access to the targets — your laptop works. The
`./configure` script checks for what it needs and tells you if something is missing.

## Network

- Nodes reach each other on the internal ports for PostgreSQL, etcd, and Keycloak clustering.
- Users reach `https://<domain>/` on any node, the optional keepalived VIP, or your external
  load balancer.
- Outbound internet access at install time to fetch upstream artifacts (the planned
  [air-gapped bundle](/pricing/) removes this).

## Sizing

The [3-node example](/docs/keycloak/example-ha-3node/) runs comfortably on 4&nbsp;GB / 2&nbsp;vCPU
nodes for evaluation. Size production nodes to your login volume; the monitoring stack shows you
exactly where the headroom goes.
