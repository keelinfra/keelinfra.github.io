+++
title = "Install: 3-node HA"
description = "Install a production HA Keycloak cluster on three clean Linux machines in about ten minutes."
weight = 2
+++

## 1. Describe your cluster

Copy and edit the [3-node example definition](/docs/keycloak/example-ha-3node/) — hosts, SSH user,
public domain, Keycloak version, TLS mode. It is the only file you edit; every field is documented
in the [configuration reference](/docs/keycloak/configuration/).

## 2. Configure and install

```bash
git clone https://github.com/keelinfra/keycloak && cd keycloak
./configure -c examples/ha-3node.yml   # validates nodes, generates inventory + vault
./install                              # ~10 minutes on 3 clean VMs
```

`./configure` writes a generated inventory under `inventory/` (secrets go into an ansible-vault).
`./install` runs the playbooks: PostgreSQL + Patroni + etcd first, then Keycloak, HAProxy, TLS,
backups, and monitoring.

## 3. First login

Open `https://<your-domain>/admin`. The bootstrap admin credentials are printed at the end of the
install (and stored in the vault).

## 4. Point DNS

Point your domain at the keepalived VIP (if you set `vip:`), at any node, or at your external
load balancer. With `tls_mode: selfsigned`, trust the generated local CA in your browser or
switch to your own certificates — see [TLS configuration](/docs/keycloak/configuration/#tls-mode).

## 5. Prove it

```bash
./verify                     # health of every component
./verify --drill session     # rolling restart; logins must survive
```

Run the [full drill set](/docs/keycloak/verify/) before you put traffic on it — that's what it's
for.
