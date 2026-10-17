+++
title = "Security & verifiability"
description = "How to report vulnerabilities in keelinfra, what ships secure by default, how it maps to NIS2, DORA and the Cyber Resilience Act, and why nothing phones home."
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
  is installed.
- **TLS between the nodes.** A cluster-internal CA encrypts etcd, PostgreSQL replication, the
  Patroni API and the metrics scrapes; `./verify` fails if one of them answers in plaintext.
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

## NIS2 and DORA reviews

No product makes you compliant; your controls and your auditor do. But identity is one of the first
systems a NIS2 or DORA review looks at, and these are the questions it asks:

| The review asks | Where it comes from | What the distribution gives you |
|---|---|---|
| Can you restore it, and have you tried? | NIS2 Art. 21(2)(c); DORA Art. 12 | Scheduled pgBackRest backups, an optional encrypted off-site copy to S3, point-in-time `./restore --time`, and `./verify --drill restore` you can run on your own cluster and keep the output as evidence |
| Is it encrypted in transit? | NIS2 Art. 21(2)(h); DORA Art. 9 | TLS to Keycloak and between every node by default; `./verify` fails on a plaintext listener |
| Access control and MFA? | NIS2 Art. 21(2)(i)–(j); DORA Art. 9 | Upstream Keycloak's OTP and WebAuthn, on infrastructure you control, with audit events in your own database |
| What is your exposure to this vendor, and how do you exit? | DORA Art. 28–30 | We never hold your data or run your systems. The distribution is Apache-2.0 and runs without us; stopping the subscription changes nothing on your cluster |

The backup, restore and TLS claims are re-checked in public CI: [the evidence ledger](/evidence/).
If your auditor wants something not listed here, [ask us](mailto:hello@keelinfra.io?subject=NIS2%2FDORA%20question).

## Cyber Resilience Act

The EU Cyber Resilience Act puts security duties on whoever sells software in the EU. Its
reporting duties apply since 11 September 2026; the rest from 11 December 2027. keelinfra sells
subscriptions for the distribution and its Keycloak builds, so we treat ourselves as their
manufacturer and do now what the act will require:

- **SBOM with every new release.** A CycloneDX file listing what the release contains or installs.
- **Signed provenance.** `gh attestation verify <file> --repo keelinfra/keycloak` shows a download
  came unmodified from our public release workflow.
- **Free security updates**, for everyone, until at least 31 December 2031, with a public advisory
  for each fix.
- **Reporting.** An actively exploited vulnerability in our products goes to ENISA within 24 hours,
  and to you at the same time.

What we meet, what is still open, and how we read the act:
[CRA.md](https://github.com/keelinfra/keycloak/blob/main/CRA.md). If you ship software into the EU
and want to know what it means for your own release pipeline,
[ask us](mailto:hello@keelinfra.io?subject=CRA%20question).

## What we don't have

No SOC 2, no ISO 27001 badge. Those certifications attest to how a vendor handles your data — and
your data never reaches us. There is nothing of yours for us to secure, lose, or subpoena.
What we offer instead is auditable source and reproducible drills:
[the evidence ledger](/evidence/).

## Supported versions

The distribution is supported until at least 31 December 2031, and security updates are free.
Until tagged releases begin, the latest commit on `main` is the supported version and security
fixes land there. Details: [SECURITY.md](https://github.com/keelinfra/keycloak/blob/main/SECURITY.md#supported-versions).
