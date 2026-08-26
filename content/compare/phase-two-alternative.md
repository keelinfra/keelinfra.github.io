+++
title = "Phase Two alternatives for self-hosted Keycloak"
description = "Phase Two is strong managed hosting with a services arm — but its self-hosted story is a container plus a retainer. What to check before you commit, and when keelinfra is the better fit."
weight = 2
+++

*Last reviewed: 2026-08-26. Every fact below links to Phase Two's own pages. Out of date? Email
[hello@keelinfra.io](mailto:hello@keelinfra.io?subject=Comparison%20correction) — corrected within
one business day.*

## What Phase Two is genuinely good at

[Phase Two](https://phasetwo.io) runs managed Keycloak with SOC 2 Type II and ISO 27001, big-name
customers, a real [published SLA](https://phasetwo.io/company/sla/), and a widely used extension
ecosystem — their [keycloak-orgs](https://github.com/p2-inc/keycloak-orgs) organizations extension
predates Keycloak's native one and has real adoption. If you want hosted Keycloak with enterprise
paperwork, they are a serious choice.

## What to check if you need to self-host

1. **The license on the extensions.** The extension suite is
   [Elastic License v2](https://phasetwo.io/blog/licensing-change/) — relicensed from AGPL in
   2023, not OSI open source, and the
   [restriction](https://phasetwo.io/docs/introduction/open-source/) explicitly covers "bundling
   and distribution by companies who sell their products for on-prem and private cloud use." If
   you ship an on-prem product embedding their extensions, read it with a lawyer.
2. **What the on-prem deliverable actually is.** The
   [on-prem page](https://phasetwo.io/product/onprem/) offers to "manage your on-premise Keycloak
   deployment" — a services engagement. The artifact is a
   [container image](https://github.com/p2-inc/phasetwo-containers) whose README points production
   users at the managed service, and which
   [sends an anonymous usage ping by default](https://github.com/p2-inc/phasetwo-containers)
   (disable with `PHASETWO_ANALYTICS_DISABLED=true`) — worth knowing before an air-gap review.
3. **Where the ops docs are.** The [docs](https://phasetwo.io/docs/introduction/) are deep on app
   integration and authentication features, and don't cover HA topology, backup/DR, or upgrade
   procedure — those live in [support plans](https://phasetwo.io/pricing/support/) from $3,500 to
   $7,500 per month (24×7 coverage at the Gold tier).
4. **The economics.** Self-hosting with a support retainer costs $42K–90K/yr at published rates —
   more than their own managed Enterprise tier. That pricing tells you which product they want
   you on.

## Where keelinfra fits

keelinfra is built for exactly the case Phase Two's self-hosted path treats as an exception:
**the distribution is the product.** HA cluster, PostgreSQL failover, backups with PITR,
monitoring, and tested upgrades are [Apache-2.0 open source](https://github.com/keelinfra/keycloak)
with [public docs](/docs/keycloak/) — and the upgrade claims are
[re-proven nightly in public CI](https://github.com/keelinfra/keycloak/actions/workflows/upgrade-matrix.yml).
Nothing phones home ([grep the source](/security/)). Support is
[$1,500 per node per year](/pricing/), not $3,500 per month.

What Phase Two has that we don't: SOC 2/ISO certificates, a managed cloud, and their extension
ecosystem. If those decide it, choose them — [the full comparison table](/compare/managed-keycloak/)
keeps the score honestly.

**Leaving a managed vendor?** Our [migration service](/pricing/) rehearses the cutover on a
staging copy before touching production — session and realm integrity verified, rollback plan
included.
