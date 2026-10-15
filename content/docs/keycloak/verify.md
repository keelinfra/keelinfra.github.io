+++
title = "Verify & drills"
description = "One-command drills that prove failover, backup restore, and session survival on your own cluster — the same checks CI runs on every commit and every night."
weight = 6
+++

The distribution ships with drills, not beliefs. Run them on your cluster whenever you like —
before go-live, after a change, during a game day.

```bash
./verify                     # health checks only
./verify --drill failover    # PostgreSQL leader switchover
./verify --drill restore     # restore every backup repository to a scratch directory
./verify --drill session     # rolling restart; logins must survive
./verify --drill alert       # test alert; every configured receiver must accept it
./verify --drill all         # everything
```

## What each drill proves

**Health (`./verify`)** — Patroni member state, etcd endpoint health, Keycloak readiness on every
node, and PostgreSQL reachability through the load balancer. Then backups and monitoring: every
backup repository holds a backup, Prometheus and Alertmanager are ready, every scrape target is
up, every metric an alert rule or the dashboard uses has data, and Grafana serves the dashboard.

**Failover** — finds the current PostgreSQL leader, switches it over to a healthy replica via
Patroni, then **writes through the load balancer** to prove the cluster kept accepting writes.
This is the drill version of "what happens at 2am when the DB node dies."

**Restore** — restores the latest pgBackRest backup into a scratch directory and verifies the
restored cluster files, once per repository: the first node's, and the off-site bucket when
`backup_s3` is set. A backup you never restored is a rumor; this drill turns it into a fact.
It does not touch the live database.

**Session** — logs into the demo realm (password grant), rolling-restarts **every** Keycloak
node, then refreshes the pre-restart token. If the refresh succeeds, DB-persisted sessions are
doing their job: no user gets logged out by a restart.

**Alert** — posts a test alert to Alertmanager and waits until every receiver configured in
`alerting` (webhook, email) has been sent it without a failure. With no receiver configured, it
says so and passes.

## What CI runs

- **Every commit** ([smoke](https://github.com/keelinfra/keycloak/actions/workflows/smoke.yml)):
  clean single-node install + health checks + the session and restore drills.
- **Every change to the roles** ([HA smoke](https://github.com/keelinfra/keycloak/actions/workflows/ha-smoke.yml)):
  a clean 3-node install with an S3 bucket and a webhook receiver, then all drills, failover
  included.
- **Every night, on 3 nodes** ([HA matrix](https://github.com/keelinfra/keycloak/actions/workflows/ha-matrix.yml)):
  every supported upgrade path under load-balancer probes, then the failover, restore and
  session drills.
- **Every night** ([upgrade matrix](https://github.com/keelinfra/keycloak/actions/workflows/upgrade-matrix.yml)):
  for every supported upgrade path — install the old version, log in, upgrade, and the
  pre-upgrade session must still refresh on the new version.

The same assertions, in public. [The evidence ledger](/evidence/) maps every claim to its receipt.
