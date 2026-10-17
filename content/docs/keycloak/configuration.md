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
| `tls_mode` | `selfsigned` (default) or `custom` — see below. |
| `tls_cert_file` | With `custom`: your certificate in PEM, server certificate first, then any intermediates. |
| `tls_key_file` | With `custom`: its private key in PEM, without a passphrase. |
| `tls_ca_file` | Optional, with `custom`: a private CA certificate the nodes should trust. |
| `internal_tls` | `true` (default): traffic between the nodes uses TLS from a cluster-internal CA. See [below](#traffic-between-the-nodes). |

## TLS mode

- **`selfsigned`** — generates a local CA and one server certificate that lists the domain and
  every node. Good for evaluation and intranet use; trust the CA on clients.
- **`custom`** — uses your certificate. Set `tls_cert_file` and `tls_key_file`, plus `tls_ca_file`
  if a private CA issued it. Relative paths are relative to the cluster definition file. Before
  anything is installed, `./configure` stops if the certificate has expired, does not list
  `domain` (exactly or through a wildcard), or does not match the key, and it warns when the
  certificate expires within 30 days. HAProxy passes TLS through, so every node serves this
  certificate and it only needs to cover `domain`.

To renew a custom certificate, replace the files and run `./configure` and `./install` again.
Keycloak re-reads its certificate files every hour, so the new one is served within the hour
without a restart. To switch at once, restart Keycloak one node at a time
(`sudo systemctl restart keycloak`). The same steps move a cluster from `selfsigned` to `custom`.

Client traffic to Keycloak is TLS: HAProxy passes it through and Keycloak terminates it.

## Traffic between the nodes

Encrypted by default. The install creates a cluster-internal CA on the first node and gives each
node its own certificate. etcd, the Patroni API, PostgreSQL (replication and Keycloak's
connections) and the metrics exporters use TLS, and `./verify` fails if one of them answers in
plaintext. Keycloak's own cluster traffic (port 7800) is mutual TLS. The one plain port is 57800,
which carries only Keycloak's liveness checks (node names and addresses). Details in the
[deployment guide](/docs/keycloak/deployment/#before-you-start).

`internal_tls: false` in the cluster definition turns this off. Clusters installed before it
existed keep running unencrypted; etcd cannot switch in place, so moving one to TLS means a new
install.

## Secrets

`./configure` generates database and admin credentials into an ansible-vault under `inventory/`;
the vault password lives in `inventory/.vault_pass` (keep it out of version control). Nothing
sensitive is written to plain-text inventory files.

## Annotated examples

- [3-node HA definition](/docs/keycloak/example-ha-3node/)
- [Single-node definition](/docs/keycloak/example-single-node/)
