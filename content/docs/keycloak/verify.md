+++
title = "Verify & drills"
description = "One-command drills that prove failover, backup restore, and session survival on your own cluster — the same checks CI runs on every commit."
weight = 6
+++

The distribution ships with drills, not beliefs. Run them on your cluster whenever you like —
before go-live, after a change, during a game day.

```bash
./verify                     # health checks only
./verify --drill failover    # PostgreSQL leader switchover
./verify --drill restore     # backup restore to a scratch directory
./verify --drill session     # rolling restart; logins must survive
./verify --drill all         # everything
```

## What each drill proves

**Health (`./verify`)** — Patroni member state, etcd endpoint health, Keycloak readiness on every
node, and PostgreSQL reachability through the load balancer.

**Failover** — finds the current PostgreSQL leader, switches it over to a healthy replica via
Patroni, then **writes through the load balancer** to prove the cluster kept accepting writes.
This is the drill version of "what happens at 2am when the DB node dies."

**Restore** — restores the latest pgBackRest backup into a scratch directory and verifies the
restored cluster files. A backup you never restored is a rumor; this drill turns it into a fact.
It does not touch the live database.

**Session** — logs into the demo realm (password grant), rolling-restarts **every** Keycloak
node, then refreshes the pre-restart token. If the refresh succeeds, DB-persisted sessions are
doing their job: no user gets logged out by a restart.

## What CI runs

- **Every commit** ([smoke](https://github.com/keelinfra/keycloak/actions/workflows/smoke.yml)):
  clean single-node install + health checks + the session drill.
- **Every night** ([upgrade matrix](https://github.com/keelinfra/keycloak/actions/workflows/upgrade-matrix.yml)):
  for every supported upgrade path — install the old version, log in, upgrade, and the
  pre-upgrade session must still refresh on the new version.

The same assertions, in public. [The evidence ledger](/evidence/) maps every claim to its receipt.
