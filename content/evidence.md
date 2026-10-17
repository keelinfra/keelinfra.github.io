+++
title = "Evidence"
description = "Every claim keelinfra makes, and where its proof lives: public CI runs, published probe logs, and drills you can run against your own cluster."
template = "evidence.html"
[extra]
subtitle = "Every claim we make, and where its proof lives. If you find a claim on this site that isn't on this page, email us and we'll either add the receipt or delete the claim."
+++

## The ledger

<div class="table-scroll"><table class="ledger">
<thead><tr><th>Claim</th><th>Evidence</th><th>Last verified</th></tr></thead>
<tbody>
<tr><td>Rolling patch upgrades are zero-downtime</td><td>156/156 probes returned HTTP&nbsp;200 during a live 26.6.0 → 26.6.2 upgrade — <a href="/blog/zero-downtime-keycloak-upgrades/">the published probe log</a>, plus the <a href="https://github.com/keelinfra/keycloak/blob/main/UPGRADES.md">UPGRADES.md</a> row</td><td class="when">2026-08-25</td></tr>
<tr><td>Minor upgrades have a ~16&nbsp;s service window and sessions survive</td><td>Measured for 26.6.2 → 26.7.0, stop-start strategy — <a href="https://github.com/keelinfra/keycloak/blob/main/UPGRADES.md">UPGRADES.md</a></td><td class="when">2026-08-25</td></tr>
<tr><td>Every upgrade path is drilled nightly on 3 nodes under load-balancer probes, then failover, restore and session drills run</td><td><a href="https://github.com/keelinfra/keycloak/actions/workflows/ha-matrix.yml">The HA matrix</a>: public GitHub Actions, cron 01:47 UTC, on a 3-node container rig</td><td class="when">nightly, in public</td></tr>
<tr><td>Every supported upgrade path re-proves itself nightly</td><td><a href="https://github.com/keelinfra/keycloak/actions/workflows/upgrade-matrix.yml">The upgrade matrix</a>: public GitHub Actions, cron 03:17 UTC — install the old version, log in, upgrade, and the pre-upgrade session must still refresh</td><td class="when">nightly, in public</td></tr>
<tr><td>Rocky Linux 9 and AlmaLinux 9 nodes install and pass every drill</td><td><a href="https://github.com/keelinfra/keycloak/actions/workflows/ha-smoke.yml">The HA smoke workflow</a> runs the same 3-node install, health checks and drills on Rocky Linux 9 and AlmaLinux 9 next to Ubuntu (containers, so SELinux is off)</td><td class="when">every roles change</td></tr>
<tr><td>Installs on real VMs with SELinux enforcing</td><td><a href="https://github.com/keelinfra/keycloak/actions/workflows/vm.yml">The VM workflow</a> boots three KVM VMs from the Rocky Linux 9 and Ubuntu 24.04 cloud images, installs, runs every drill, reaches Keycloak through the real VIP, and on Rocky fails if a node is not enforcing or logged any SELinux denial</td><td class="when">every roles change and weekly</td></tr>
<tr><td>A clean 3-node install takes ~10 minutes</td><td><a href="https://github.com/keelinfra/keycloak/actions/workflows/ha-smoke.yml">The HA smoke workflow</a> installs 3 nodes from scratch on every change to the roles — run durations are public</td><td class="when">every roles change</td></tr>
<tr><td>A 3-node cluster installs and upgrades with no internet access on the nodes</td><td><a href="https://github.com/keelinfra/keycloak/actions/workflows/offline.yml">The offline workflow</a> builds <a href="https://github.com/keelinfra/keycloak/blob/main/bundle/README.md">offline bundles</a> for two releases, on Ubuntu 24.04 and on Rocky Linux 9, removes the nodes' default route, then installs from one, runs every drill, and rolls onto the next release from the other; a bundle missing the target version stops the upgrade before it touches the cluster</td><td class="when">every roles change and weekly</td></tr>
<tr><td>Sessions survive a full rolling restart</td><td><code>./verify --drill session</code> — runs in CI on every commit, and on your cluster whenever you like</td><td class="when">every commit</td></tr>
<tr><td>Backups actually restore</td><td><code>./verify --drill restore</code> — pgBackRest restores the latest backup to a scratch directory; CI runs it on every commit and nightly on 3 nodes, and you can run it on your own cluster</td><td class="when">every commit</td></tr>
<tr><td>The cluster's database can be put back to a point in time</td><td><a href="https://github.com/keelinfra/keycloak/actions/workflows/ha-smoke.yml">The HA smoke workflow</a> writes a row, drops its table, runs <code>./restore --time</code> to the moment in between and checks the row is back, then runs every health check, on 3 nodes with Ubuntu, Rocky Linux 9 and AlmaLinux 9</td><td class="when">every roles change</td></tr>
<tr><td>A lost node can be replaced by a blank machine</td><td><a href="https://github.com/keelinfra/keycloak/actions/workflows/ha-smoke.yml">The HA smoke workflow</a> deletes a node of the running cluster, starts a blank machine at its address, runs <code>./replace-node</code> and then every health check, on 3 nodes with Ubuntu, Rocky Linux 9 and AlmaLinux 9</td><td class="when">every roles change</td></tr>
<tr><td>The whole cluster can be rebuilt from the off-site backup</td><td><a href="https://github.com/keelinfra/keycloak/actions/workflows/ha-smoke.yml">The HA smoke workflow</a> writes a row, deletes all three nodes, runs <code>./rebuild</code> on blank machines, checks the row is back and runs every health check, on 3 nodes with Ubuntu, Rocky Linux 9 and AlmaLinux 9</td><td class="when">every roles change</td></tr>
<tr><td>PostgreSQL fails over automatically</td><td><code>./verify --drill failover</code> — Patroni switchover with a write test through the load balancer; CI runs it on 3 nodes on every roles change and nightly</td><td class="when">nightly, in public</td></tr>
<tr><td>Agent8 runs Jenkins builds on Java 8, including CentOS 6.10 and OpenJ9</td><td><a href="https://github.com/keelinfra/agent8/actions/workflows/ci.yml">Agent8 CI</a>: HotSpot 8 on CentOS 6.10 and OpenJ9 8 against the current Jenkins LTS and weekly — Pipeline, Git checkout, credentials, abort and agent restart; Java 11 and 17 against the LTS</td><td class="when">every change and weekly</td></tr>
<tr><td>An older Agent8 release keeps working after a controller upgrade, within limits</td><td>The version-skew job in <a href="https://github.com/keelinfra/agent8/actions/workflows/ci.yml">Agent8 CI</a> runs the latest release against the newer weekly controller; Jenkins 2.586 refusing the build for 2.462.3 is recorded in the <a href="https://github.com/keelinfra/agent8#install">README</a></td><td class="when">every change and weekly</td></tr>
</tbody>
</table></div>

<div class="badges">
<a href="https://github.com/keelinfra/keycloak/actions/workflows/ha-matrix.yml"><img src="https://github.com/keelinfra/keycloak/actions/workflows/ha-matrix.yml/badge.svg" alt="HA matrix CI status"></a>
<a href="https://github.com/keelinfra/agent8/actions/workflows/ci.yml"><img src="https://github.com/keelinfra/agent8/actions/workflows/ci.yml/badge.svg" alt="Agent8 CI status"></a>
<a href="https://github.com/keelinfra/keycloak/actions/workflows/smoke.yml"><img src="https://github.com/keelinfra/keycloak/actions/workflows/smoke.yml/badge.svg" alt="smoke CI status"></a>
<a href="https://github.com/keelinfra/keycloak/actions/workflows/upgrade-matrix.yml"><img src="https://github.com/keelinfra/keycloak/actions/workflows/upgrade-matrix.yml/badge.svg" alt="upgrade matrix CI status"></a>
</div>

## The last seven nights

Every supported upgrade path, every night, in public. The table is rebuilt
from the GitHub Actions API each morning; a red mark stays here for a week.

<!-- ci-results -->

## Claims we do not make (yet)

- **A single-node-to-HA growth path.** Growing from one node to three today means a fresh 3-node install plus a realm import. Documented, not hidden.
- **An SLA.** We publish measurements, not promises. An uptime number without a public probe log is marketing.
- **SOC 2 / ISO certification.** Certifications attest to how a vendor handles your data. Your data never reaches us — the code is auditable and the drills are runnable instead.

## Corrections

Found a claim that's wrong, stale, or missing a receipt? Email
[hello@keelinfra.io](mailto:hello@keelinfra.io?subject=Evidence%20correction) — we correct within
one business day.
