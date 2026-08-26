+++
title = "Evidence"
description = "Every claim keelinfra makes, and where its proof lives: public CI runs, published probe logs, and drills you can run against your own cluster."
template = "page.html"
[extra]
subtitle = "Every claim we make, and where its proof lives. If you find a claim on this site that isn't on this page, email us and we'll either add the receipt or delete the claim."
+++

## The ledger

<div class="table-scroll"><table class="ledger">
<thead><tr><th>Claim</th><th>Evidence</th><th>Last verified</th></tr></thead>
<tbody>
<tr><td>Rolling patch upgrades are zero-downtime</td><td>156/156 probes returned HTTP&nbsp;200 during a live 26.6.0 → 26.6.2 upgrade — <a href="/blog/zero-downtime-keycloak-upgrades/">the published probe log</a>, plus the <a href="https://github.com/keelinfra/keycloak/blob/main/UPGRADES.md">UPGRADES.md</a> row</td><td class="when">2026-08-25</td></tr>
<tr><td>Minor upgrades have a ~16&nbsp;s service window and sessions survive</td><td>Measured for 26.6.2 → 26.7.0, stop-start strategy — <a href="https://github.com/keelinfra/keycloak/blob/main/UPGRADES.md">UPGRADES.md</a></td><td class="when">2026-08-25</td></tr>
<tr><td>Every supported upgrade path re-proves itself nightly</td><td><a href="https://github.com/keelinfra/keycloak/actions/workflows/upgrade-matrix.yml">The upgrade matrix</a>: public GitHub Actions, cron 03:17 UTC — install the old version, log in, upgrade, and the pre-upgrade session must still refresh</td><td class="when">nightly, in public</td></tr>
<tr><td>A clean install takes ~10 minutes</td><td><a href="https://github.com/keelinfra/keycloak/actions/workflows/smoke.yml">The smoke workflow</a> installs from scratch on every commit — run durations are public</td><td class="when">every commit</td></tr>
<tr><td>Sessions survive a full rolling restart</td><td><code>./verify --drill session</code> — runs in CI on every commit, and on your cluster whenever you like</td><td class="when">every commit</td></tr>
<tr><td>Backups actually restore</td><td><code>./verify --drill restore</code> — pgBackRest restore to a scratch directory, on your own cluster</td><td class="when">run it yourself</td></tr>
<tr><td>PostgreSQL fails over automatically</td><td><code>./verify --drill failover</code> — Patroni switchover with a write test through the load balancer</td><td class="when">run it yourself</td></tr>
</tbody>
</table></div>

<div class="badges">
<a href="https://github.com/keelinfra/keycloak/actions/workflows/smoke.yml"><img src="https://github.com/keelinfra/keycloak/actions/workflows/smoke.yml/badge.svg" alt="smoke CI status"></a>
<a href="https://github.com/keelinfra/keycloak/actions/workflows/upgrade-matrix.yml"><img src="https://github.com/keelinfra/keycloak/actions/workflows/upgrade-matrix.yml/badge.svg" alt="upgrade matrix CI status"></a>
</div>

## Claims we do not make (yet)

- **Air-gapped installs.** The offline bundle is planned and will ship with the [subscription](/pricing/). Until it exists, we don't sell it.
- **A single-node-to-HA growth path.** Growing from one node to three today means a fresh 3-node install plus a realm import. Documented, not hidden.
- **An SLA.** We publish measurements, not promises. An uptime number without a public probe log is marketing.
- **SOC 2 / ISO certification.** Certifications attest to how a vendor handles your data. Your data never reaches us — the code is auditable and the drills are runnable instead.

## Corrections

Found a claim that's wrong, stale, or missing a receipt? Email
[hello@keelinfra.io](mailto:hello@keelinfra.io?subject=Evidence%20correction) — we correct within
one business day.
