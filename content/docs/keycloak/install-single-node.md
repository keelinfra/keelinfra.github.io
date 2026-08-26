+++
title = "Install: single node"
description = "Install the full Keycloak stack on one machine — for evaluation, dev, or small internal setups. Same flow as HA, no cluster."
weight = 3
+++

One machine running the full stack: Keycloak, PostgreSQL, backups, monitoring. No HA.

```bash
git clone https://github.com/keelinfra/keycloak && cd keycloak
./configure -c examples/single-node.yml
./install
```

The definition file is the same format as the HA one, with a single entry under `nodes:` —
see [the single-node example](/docs/keycloak/example-single-node/).

## The growth caveat (read this before choosing single-node)

Growing from a single node to a 3-node cluster later means a **fresh 3-node install plus a realm
import** — there is no in-place path today. If HA is where you're headed, start with
[the 3-node install](/docs/keycloak/install-ha/); a 3-node cluster on small VMs beats a migration
later.

Single-node is exercised in CI on every commit (it's what the
[smoke workflow](https://github.com/keelinfra/keycloak/actions/workflows/smoke.yml) and the
[nightly upgrade matrix](https://github.com/keelinfra/keycloak/actions/workflows/upgrade-matrix.yml)
run on).
