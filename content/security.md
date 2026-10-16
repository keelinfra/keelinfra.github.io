+++
title = "Security & verifiability"
description = "How to report vulnerabilities in keelinfra, what ships secure by default, and why nothing phones home."
template = "page.html"
+++

## Report a vulnerability

For the Keycloak distribution, report privately via GitHub:
[**Report a vulnerability**](https://github.com/keelinfra/keycloak/security/advisories/new)
(Security tab → Report a vulnerability). For Agent8, email
[hello@keelinfra.io](mailto:hello@keelinfra.io?subject=Agent8%20security%20report). Please don't
open public issues for security reports.

You'll get an acknowledgment within 3 business days. We keep you informed while we validate and
fix, coordinate disclosure with you, and credit you in the advisory unless you prefer otherwise.
The full policy lives in
[SECURITY.md](https://github.com/keelinfra/keycloak/blob/main/SECURITY.md).

**In scope:** insecure defaults shipped by the distribution (TLS configuration, exposed listeners,
file permissions, secret handling in inventories and vaults); privilege escalation or secret
disclosure caused by our playbooks or roles; flaws in the install/upgrade/backup/verify tooling
that could corrupt or expose data.

**Out of scope:** vulnerabilities in upstream Keycloak, PostgreSQL, HAProxy, etc. — report those
upstream. When a fixed upstream CVE affects deployments made by this distribution, we ship the
version bump and document the operator actions in
[UPGRADES.md](https://github.com/keelinfra/keycloak/blob/main/UPGRADES.md).

## Secure by default

- **TLS to Keycloak.** `tls_mode: selfsigned` generates a local CA; `tls_mode: custom` uses your
  own certificate, which `./configure` checks for expiry, domain and key match before anything
  is installed. Traffic between the nodes (etcd, PostgreSQL replication, the Patroni API) is not
  encrypted yet, so keep the node network private.
- **Secrets stay encrypted.** Generated credentials live in an ansible-vault; nothing sensitive is
  written in plain text to the inventory.
- **No password SSH.** Key or agent-based authentication only.
- **Change the drill realm.** Every install creates the `demo` realm the session drill uses
  (user `demo`, password `demo12345`). Change or remove it before go-live.
- **Your database, your sessions.** Identity data, sessions and audit events live in the
  PostgreSQL cluster the distribution installs on your machines — nowhere else.

## Nothing phones home

The distribution makes **no network calls to keelinfra** — no telemetry, no license checks, no
registry pulls from our infrastructure. Artifacts are fetched from upstream project sources at
install time, or from an [offline bundle](https://github.com/keelinfra/keycloak/blob/main/bundle/README.md) you build and carry in yourself, which removes
even that.
Grafana, installed from its upstream packages, keeps its default usage reporting; set
`reporting_enabled = false` in `grafana.ini` if you want it off.

Verify it: `grep -r "keelinfra.io" roles/ playbooks/` in the
[source](https://github.com/keelinfra/keycloak). It's not there.

## What we don't have

No SOC 2, no ISO 27001 badge. Those certifications attest to how a vendor handles your data — and
your data never reaches us. There is nothing of yours for us to secure, lose, or subpoena.
What we offer instead is auditable source and reproducible drills:
[the evidence ledger](/evidence/).

## Supported versions

Until tagged releases begin, the latest commit on `main` is the supported version and security
fixes land there.
