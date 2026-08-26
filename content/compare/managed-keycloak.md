+++
title = "Managed Keycloak providers vs. self-hosting: an honest comparison"
description = "Phase Two, Skycloak, DIY, and keelinfra compared on the axes that matter to an operator: license, data custody, air-gap, public ops docs, upgrade testing, exit path, and price model. With citations."
weight = 1
+++

*Last reviewed: 2026-08-26. Vendors change — if anything here is out of date, email
[hello@keelinfra.io](mailto:hello@keelinfra.io?subject=Comparison%20correction) and we'll correct
it within one business day.*

## When managed Keycloak is the right answer

Honestly: often. If you have no ops team, no data-residency constraint, and you want the 2am pager
to be someone else's problem, both vendors below do that genuinely well —
[Phase Two](https://phasetwo.io) has SOC 2 and ISO 27001, enterprise customers, and a real
published SLA; [Skycloak](https://skycloak.io) has flat infrastructure pricing, a strong security
page, and first login in minutes. If that's you, use them.

This page exists for the buyer they both structurally cannot serve: the team whose identity data
**cannot live on someone else's cloud** — regulated industries, data residency, air-gapped
networks, formal change control. Skycloak's own blog puts it plainly: if identity data can't
leave your infrastructure, "a SaaS identity provider is off the table by definition."

## The table

<div class="table-scroll"><table>
<thead><tr><th></th><th>keelinfra</th><th>Phase Two</th><th>Skycloak</th><th>DIY</th></tr></thead>
<tbody>
<tr><td><strong>Where identity data lives</strong></td><td class="yes">Your machines, always</td><td>Their cloud; on-prem via <a href="https://phasetwo.io/product/onprem/">consulting + container</a></td><td>Their cloud (<a href="https://skycloak.io/security/">4 regions</a>)</td><td class="yes">Your machines</td></tr>
<tr><td><strong>License of the ops layer</strong></td><td class="yes">Apache-2.0, all of it</td><td>Extensions are <a href="https://phasetwo.io/blog/licensing-change/">Elastic License v2</a> (relicensed from AGPL in 2023; not OSI open source; <a href="https://phasetwo.io/docs/introduction/open-source/">restricts on-prem redistribution</a>)</td><td>Proprietary SaaS</td><td>n/a — you write it</td></tr>
<tr><td><strong>Air-gapped / offline</strong></td><td>Designed for it — offline bundle ships with the <a href="/pricing/">subscription</a></td><td class="no">Not offered; container <a href="https://github.com/p2-inc/phasetwo-containers">phones home by default</a></td><td class="no">Not offered — SaaS by definition</td><td>Possible, all on you</td></tr>
<tr><td><strong>HA / backup / upgrade docs public?</strong></td><td class="yes">Yes — <a href="/docs/keycloak/">docs</a>, and CI-proven</td><td class="no">No — <a href="https://phasetwo.io/docs/introduction/">docs</a> cover app integration; ops is sold as <a href="https://phasetwo.io/pricing/support/">support</a></td><td>n/a — they operate it for you</td><td>Upstream docs only</td></tr>
<tr><td><strong>Upgrade testing you can inspect</strong></td><td class="yes"><a href="https://github.com/keelinfra/keycloak/actions/workflows/upgrade-matrix.yml">Nightly public CI matrix</a> + <a href="/blog/zero-downtime-keycloak-upgrades/">published probe logs</a></td><td class="no">None published; upgrades are a <a href="https://phasetwo.io/support/zero-downtime-upgrades/">service engagement</a></td><td class="no">None published; <a href="https://skycloak.io/docs/faqs/">no version pinning</a>, sequential upgrades only</td><td>Yours to build</td></tr>
<tr><td><strong>SLA / uptime — verifiable?</strong></td><td>No SLA — <a href="/evidence/">measurements and drills</a> instead</td><td class="yes">Published <a href="https://phasetwo.io/company/sla/">SLA doc</a> with credit formula</td><td>"99.99%" on the homepage; <a href="https://skycloak.io/sla/">SLA page</a> says best-effort below Enterprise; no public status page</td><td>n/a</td></tr>
<tr><td><strong>Exit path</strong></td><td class="yes">Nothing to export — it's already your database</td><td>Your data in their container/cloud, ELv2 terms on extensions</td><td><a href="https://skycloak.io/docs/features/database-export/">DB export</a>: Launch tier and up, credentials excluded by default, files expire in 24h</td><td class="yes">n/a</td></tr>
<tr><td><strong>Custom extensions / SPIs</strong></td><td class="yes">Unrestricted — it's your Keycloak</td><td>Their ecosystem, ELv2 terms</td><td>Custom JARs are <a href="https://skycloak.io/docs/features/extensions/">Enterprise-only</a>; curated marketplace below that</td><td class="yes">Unrestricted</td></tr>
<tr><td><strong>Who carries the 2am pager</strong></td><td>You — with drills, runbooks, and a <a href="/pricing/">$200/hr emergency line</a></td><td class="yes">Them (managed); you + retainer (self-hosted)</td><td class="yes">Them</td><td>You, alone</td></tr>
<tr><td><strong>Time to first login</strong></td><td>~10 minutes — but you bring 1–3 VMs</td><td class="yes">Minutes, free trial</td><td class="yes">Minutes, free trial</td><td>Days to weeks</td></tr>
<tr><td><strong>Compliance paperwork</strong></td><td>None from us — your data never reaches us; auditable source instead</td><td class="yes">SOC 2 Type II, ISO 27001</td><td class="yes">SOC 2, ISO 27001, HIPAA claimed; documented pentests &amp; subprocessors</td><td>Yours</td></tr>
<tr><td><strong>Pricing model</strong></td><td>$0 OSS · <a href="/pricing/">$1,500/node/yr</a> sub · fixed-scope services</td><td><a href="https://phasetwo.io/pricing/hosting/">$149–2,999/mo</a> by MAU; <a href="https://phasetwo.io/pricing/support/">support $3.5K–7.5K/mo</a></td><td><a href="https://skycloak.io/pricing/">$29–599/mo</a> by infrastructure + Enterprise</td><td>Your engineers' time</td></tr>
</tbody>
</table></div>

## How to read it

**If you can use a managed cloud**, the pager row and the compliance row may be all that matters —
and both vendors win them. Per-MAU cost is the thing to model carefully: Skycloak's
infrastructure-based pricing is genuinely different from Phase Two's MAU tiers.

**If your data can't leave**, the structural facts are these. Phase Two's self-hosted offering is
a container image plus a support retainer ($42K–90K/yr at
[their published rates](https://phasetwo.io/pricing/support/)) — the HA, backup, and upgrade
knowledge stays behind the retainer. Skycloak has no self-hostable product at all. In both cases
the ops knowledge is the paywall.

keelinfra's bet is the opposite: the ops knowledge **is** the product, and it's Apache-2.0 —
[the installer](https://github.com/keelinfra/keycloak), [the docs](/docs/keycloak/), the
[drills](/docs/keycloak/verify/), the [upgrade runbooks](/docs/keycloak/upgrades/), and the
[nightly CI that re-proves them](https://github.com/keelinfra/keycloak/actions/workflows/upgrade-matrix.yml).
You pay for [people and guarantees](/pricing/), not for access to how it works.

## What we concede

- With keelinfra, **the 2am pager is still yours.** We give you drills, runbooks, and an
  emergency line — we don't carry it for you.
- Managed gets you to first login faster. Ten minutes and three VMs is fast for self-hosted;
  it is not faster than a free trial button.
- We have no SOC 2 — and we'd argue you don't need ours, because nothing of yours touches us.
  But if your procurement checklist requires a vendor certificate for the software supply chain,
  that's a real difference today.

*Also in this series: [Phase Two alternatives](/compare/phase-two-alternative/) ·
[Skycloak alternatives](/compare/skycloak-alternative/)*
