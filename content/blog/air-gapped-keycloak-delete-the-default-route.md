+++
title = "\"Air-gap ready\" means nothing until you delete the default route"
date = 2026-10-16
description = "An HA Keycloak cluster pulls from at least five places on the internet during install. We put all of it in one 834 MB tarball, then proved it in CI the only honest way: delete the nodes' default route, install three nodes, run every drill, and do a rolling upgrade. 14 minutes, no network. What has to be in the bundle, and the two traps that make most offline kits fail on a real minimal server."
[extra]
og_image = "/assets/social-preview-keycloak.png"
+++

Plenty of infrastructure products say they support air-gapped installs. Ask how they know, and
the answer is usually that someone did it once, for a customer, a while ago.

That is not a test. An install that works offline today stops working the first time a role
gains a package, a dependency picks up a new dependency, or a step quietly reaches out to the
internet for something nobody wrote down. You find out on the customer's network, on the day they
scheduled the change window.

So here is our bar for the word: **a CI job that deletes the nodes' default route, then installs,
drills and upgrades the whole cluster.** If anything still needs the internet, the job goes red.
It runs on every change to the roles and once a week, because the package archives move under
you even when your code does not.

The latest run, on three nodes with no route out (condensed from the job log):

```
kc-node1: offline
kc-node2: offline
kc-node3: offline
...
./install          4 m 45 s    failed=0 on every node
./verify --drill all   1 m 59 s    failover, restore, rolling restart, alerts
./upgrade --offline    1 m 52 s    26.8.0 → 26.8.1, rolling
...
curl: (7) Failed to connect to github.com port 443 after 29 ms: Couldn't connect to server
```

That last line is the job checking, at the end, that the nodes really never got the internet back.
Whole job: 14 minutes, including building two bundles.

## What a Keycloak cluster downloads

Keycloak itself is one tarball. A Keycloak cluster you would run in production is not. Ours, on
Ubuntu 24.04, pulls from:

- **the Ubuntu archive**: the JDK, HAProxy, keepalived, chrony and the libraries under all of them;
- **PGDG** (apt.postgresql.org): PostgreSQL 17, Patroni, pgBackRest;
- **Grafana's repository**: Grafana;
- **GitHub releases**: Keycloak (174 MB), etcd (21 MB), keycloak-config-cli (95 MB);
- **Ansible Galaxy**: the collections the playbooks use, on the machine that runs them.

Five sources, three of them third-party package repositories with their own signing keys. A
typical "offline guide" covers the tarball and says to mirror the rest. That is where it goes
wrong.

## Trap one: your build machine already has half the dependencies

The obvious way to collect packages is `apt-get download` or `apt-get install --download-only` on
a machine with internet access. Both resolve dependencies against what is **already installed on
that machine**. Whatever it has, the bundle leaves out. Then a minimal server, the kind security
teams hand out, is missing a library halfway through the install.

The fix is to make apt believe nothing is installed. Point it at an empty package database and it
resolves the full tree, as a fresh system would:

```bash
: > /tmp/empty/status
apt-get install --download-only \
  -o Dir::State::status=/tmp/empty/status \
  -o Dir::Cache::archives=/out/repo \
  -o APT::Install-Recommends=true \
  "${packages[@]}"
```

Our list of about 20 packages becomes **305 packages, 593 MB**. That gap, from 20 to 305, is the
part people forget to mirror. Then `apt-ftparchive` turns the directory into a repository the
nodes can use, pinned above any internal mirror the customer already has, so nothing comes from
their mirror while the bundle has the package.

## Trap two: things nobody wrote down

The second trap is every download that isn't in a package list: a `get_url` in a role, an `apt
update` against a repository that is now unreachable, a collection installed on the control machine
on first run. Reading the code finds some of them. Deleting the route finds all of them, because
each one fails loudly on the first try.

This is also the only way the list stays right. Our package list says so in its header: when a
role starts installing something new, add it here, and the offline job fails if you forget. Nobody
has to remember. The test remembers.

## Day two is offline too

A cluster installed offline gets upgraded offline. That sounds obvious, but many kits stop at the
first install. Ours builds a bundle for the target version and the upgrade takes it:

```bash
./upgrade --to 26.8.1 --offline keelinfra-keycloak-offline-26.8.1-ubuntu24.04-amd64.tar.gz
```

The CI job also checks the failure case. Run the upgrade without a bundle that carries the target
version, and it stops **before it takes a backup or touches a node**:

```
error: this cluster installs offline, and the bundle in inventory/offline/ has no keycloak-26.8.1.tar.gz.
```

Failing early beats failing on node two of three with node one already upgraded.

## What we have not proved yet

The same rules apply to us, so here is what this does not cover:

- **Ubuntu 24.04 only.** Online installs also support Rocky Linux 9; an RPM bundle is not built
  yet.
- **The control machine keeps its internet in CI.** The Ansible collections are baked into the
  rig's control container, so the control machine's offline path is covered by checksums and an
  offline collection install, not by a control machine that is actually cut off.
- **834 MB per bundle.** It holds every package's full dependency tree, recommends included. It is
  big because a minimal server needs all of it.

## Try it

```bash
git clone https://github.com/keelinfra/keycloak && cd keycloak
bundle/build.sh --version 26.8.1          # on any machine with Docker and internet
# copy the checkout and the bundle across, then on the inside:
./configure -c cluster.yml --offline keelinfra-keycloak-offline-26.8.1-ubuntu24.04-amd64.tar.gz
./install
```

The [offline workflow](https://github.com/keelinfra/keycloak/actions/workflows/offline.yml) is
public, with every run's log. If your network is stricter than "no default route" (a proxy that
allows some hosts, a mirror that lags upstream), [tell us](mailto:hello@keelinfra.io). That is
exactly the kind of case we would rather drill in CI than discover on your change window.
