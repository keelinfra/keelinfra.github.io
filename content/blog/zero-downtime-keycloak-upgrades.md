+++
title = "Zero-downtime Keycloak patch upgrades, measured: 156/156 probes"
date = 2026-08-26
description = "We upgraded a 3-node HA Keycloak cluster while probing it every second: 156 probes, 156 × HTTP 200, and a pre-upgrade session that survived every node being replaced. The numbers, the orchestration, and the three mistakes we made."
[extra]
og_image = "/assets/social-preview-keycloak.png"
+++

Everyone claims zero-downtime upgrades. Almost nobody publishes the probe log.

We upgraded a 3-node HA Keycloak cluster from 26.6.0 to 26.6.2 while hitting it with
a request every second. **156 probes, 156 × HTTP 200, zero failures** — and a session
opened *before* the upgrade was still valid *after* every node had been replaced.

Then we did a minor upgrade (26.6.2 → 26.7.0), measured a 65-second outage window,
got annoyed, re-ordered the orchestration, and cut it to **16 seconds**. Sessions
survived that too.

This post is the numbers, the orchestration, and the three mistakes we made on the
way. Everything here is reproducible from the open-source repo —
[keelinfra/keycloak](https://github.com/keelinfra/keycloak) — with one command.

## Why Keycloak upgrades scare people

Two reasons, historically:

1. **Sessions lived in Infinispan.** Restart the cluster wrong and every user is
   logged out. Nothing pages a CISO faster than "SSO logged out the whole company."
2. **No rolling updates.** Until recently, mixed-version clusters were unsupported,
   full stop.

Keycloak 26 changed the physics of both. [Persistent user
sessions](https://www.keycloak.org/docs/latest/release_notes/) put sessions in
PostgreSQL by default — a node (or the whole cluster) can restart without logging
anyone out. And since 26.6, [rolling updates for patch
releases](https://www.keycloak.org/server/update-compatibility) are GA: 26.6.0 →
26.6.2 can be done node by node with zero downtime.

Upstream gives you the *capability*. What it doesn't give you is the
*orchestration* — the drain/replace/verify choreography — or any proof that your
particular path works. That's the part we automated and measured.

## The setup

Three clean VMs (this run: Multipass on Apple Silicon; same playbooks run on any
Ubuntu 24.04 hosts). On each node:

- Keycloak 26.6.0 — official tarball under systemd, `jdbc-ping` discovery,
  DB-persisted sessions (26.x defaults)
- PostgreSQL 17 with Patroni (etcd DCS), automatic failover
- HAProxy — port 443 load-balances all Keycloak nodes; 5433 always routes to the
  Patroni leader
- pgBackRest — encrypted backups + WAL archiving

The whole stack comes up with `./configure && ./install` in about 12 minutes on this
laptop-hosted Multipass rig (CI installs on clean VMs in ~10 — timings are public in the
[smoke workflow](https://github.com/keelinfra/keycloak/actions/workflows/smoke.yml)).

## The patch upgrade: 26.6.0 → 26.6.2, rolling

The orchestration per node (Ansible, `serial: 1`):

```
1. STAGE      download + unpack 26.6.2, render config, kc.sh build
              → the running service is untouched during the slow part
2. DRAIN      disable the node on every HAProxy
              (runtime API: "disable server keycloak_https/<node>")
3. WAIT 5s    let in-flight requests finish
4. CUT OVER   /opt/keycloak/current -> keycloak-26.6.2   (symlink flip)
5. RESTART    systemd restart, wait for /health/ready = 200
6. RETURN     re-enable the node on every HAProxy
```

The measurement: a probe loop on the operator machine, one request per second
against the public entrypoint, straight through the upgrade:

```bash
while :; do
  curl -sk -o /dev/null -w "$(date +%T) %{http_code}\n" \
    --max-time 3 https://sso.example/realms/demo/.well-known/openid-configuration
  sleep 1
done
```

Result:

```
$ awk '{print $2}' uptime_probe.log | sort | uniq -c
    156 200
```

Every probe during the entire rolling upgrade returned 200. No timeouts, no 5xx,
no connection resets.

**Session survival**, verified the honest way: log in *before* the upgrade, keep
the `refresh_token`, upgrade all three nodes, then redeem the token:

```bash
# before: password grant against the demo realm → save refresh_token
# after:
curl -sk https://sso.example/realms/demo/protocol/openid-connect/token \
  -d "grant_type=refresh_token&client_id=admin-cli&refresh_token=$OLD_TOKEN"
# → 200, fresh access_token. The session outlived every node it was born on.
```

That's the DB-persisted sessions doing their job: the session state lives in
PostgreSQL, so it doesn't care which Keycloak process serves the request.

## The minor upgrade: 26.6.2 → 26.7.0, and a 4× improvement we owe you honesty about

Minor upgrades may run schema migrations, so upstream's supported procedure is
stop → migrate → start, not rolling. Sessions still survive — they're in the
database — but there is a real service window. The only question is how long.

Our first implementation was naive:

```
stop all nodes  →  download 26.7.0  →  unpack  →  build  →  start
                   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                   all of this inside the outage window
```

Measured: **65 seconds of downtime.** Most of it was downloading a 250 MB tarball
three times — with the service already stopped. Embarrassing, easy to fix:

```
STAGE on all nodes (download + unpack + build — service still running)
  → stop all
  → flip symlinks
  → start node 1 (runs DB migrations)
  → start nodes 2..n
```

Measured after re-ordering: **16 seconds.**

```
     57 200      ← before
     16 000     ← the window (connection refused)
     28 200      ← after; pre-upgrade session still refreshes fine
```

The lesson generalizes: *never put artifact acquisition inside a service window.*
Obvious in retrospect. We publish the number anyway, because "measured 16s
stop-start window" is a claim you can hold us to, and "zero downtime" for minor
upgrades would be a lie — if a vendor tells you otherwise, ask for their probe log.

## Three mistakes worth stealing from

**1. The official tarball ships with a default build — and it breaks naive
idempotence.** Keycloak's tarball comes pre-built for dev-mode h2. If your
automation checks "does the optimized build output exist?" the answer is *always
yes*, your `kc.sh build` silently never runs, and the server dies on startup with
`--optimized`. We now stamp builds with a checksum of the effective config and
rebuild when it drifts.

**2. systemd quietly ate our heap flag.** `Environment=JAVA_OPTS_KC_HEAP=-Xms512m
-Xmx1024m` — without quotes, systemd parses `-Xmx1024m` as a second (invalid)
assignment and drops it. The service runs fine with an uncapped heap… until the
day it doesn't. `journalctl` had been warning about it the whole time:
`Invalid environment assignment, ignoring: -Xmx1024m`. Read your warnings.

**3. Drain on *every* load balancer, not just the local one.** Each node runs its
own HAProxy, and each HAProxy backends *all* Keycloak nodes. Draining a node only
on its local proxy still leaves it taking traffic from the other two. The drain
loop talks to every proxy's runtime socket before touching the node.

## Reproduce it yourself

```bash
git clone https://github.com/keelinfra/keycloak && cd keycloak
./configure -c examples/ha-3node.yml   # 3 clean Ubuntu 24.04 hosts + SSH
./install                              # ≈12 min: HA KC + PG HA + backups + monitoring
./verify --drill session               # login → rolling restart → session must survive
./upgrade --to 26.6.2                  # the rolling upgrade from this post
```

Every upgrade path we support is listed in
[UPGRADES.md](https://github.com/keelinfra/keycloak/blob/main/UPGRADES.md) — and a
path only gets listed after it has been executed end-to-end, sessions verified.
That CI matrix now runs nightly:
[the upgrade matrix](https://github.com/keelinfra/keycloak/actions/workflows/upgrade-matrix.yml)
re-proves every supported path in public — install the old version, log in, upgrade,
and the pre-upgrade session must still refresh.

---

*keelinfra is an open-source (Apache-2.0), production-ready self-hosted Keycloak
distribution. If you'd rather have the people who wrote this run your deployment,
migration, or a very bad Keycloak day: [keelinfra.io](https://keelinfra.io) ·
hello@keelinfra.io.*

*Keycloak is a trademark of The Linux Foundation. keelinfra is an independent
project, not affiliated with or endorsed by The Linux Foundation, CNCF, Red Hat,
or the Keycloak project.*
