+++
title = "Upgrade drill: your Keycloak upgrade, rehearsed before the maintenance window"
description = "Fixed price, $4,000 per upgrade path. We run your Keycloak upgrade on a three-node cluster loaded with your realm configuration, and hand you a written report and a runbook."
template = "page.html"

[extra]
subtitle = "$4,000 per upgrade path · fixed price · you keep the report and the runbook"
+++

Most Keycloak upgrades that go wrong were never run before the night they mattered. The
upgrade drill is that missing run: your source version, your target version and your realm
configuration, on a three-node HA cluster that is not production. You learn what breaks, how
long the service window is and whether logged-in users survive it, while there is still time
to do something about it.

It is the same drill this distribution runs on
[every upgrade path it lists](/docs/keycloak/upgrades/), every night, in public CI. The
difference is that this one carries your realm instead of a test realm.

## When it is worth paying for

- You are on 26.7 or earlier.
  [26.8.0](https://github.com/keycloak/keycloak/releases/tag/26.8.0) shipped on 2026-10-01
  and upstream supports one release at a time, so the fixes now land ahead of you.
- You are on a stream with no community artifacts (26.2, 26.4, 26.6), and the way to a
  patched version is a minor upgrade nobody on your team has run.
- Your realm is not a default one: custom providers, custom authentication flows or themes,
  LDAP or Active Directory federation, SAML or OIDC brokering.
- Someone will ask you, before the change is approved, how you know it will work.

If you run a stock realm on a path that is already in the
[table](/docs/keycloak/upgrades/), you probably do not need this. The nightly runs are your
evidence, and they cost nothing.

## What we run

1. Install your source version on three nodes, with PostgreSQL HA and a load balancer in
   front of each node, the way the distribution builds it.
2. Import your realm configuration, with your providers and themes deployed.
3. Log in, and keep the session.
4. Run the upgrade to your target version, rolling for a patch, stop-start for a minor,
   while every node's load balancer is probed once a second.
5. Assert that all three nodes run the target version, that every balancer sees every node
   up, and that the session from step 3 still refreshes.
6. Run the failover, backup-restore and session drills on the upgraded cluster.

If a step fails, that is the result you paid for. We find out why, fix what is ours to fix,
tell you what is yours, and run it again.

## What you get

- **A written report.** What was run, with versions and checksums. The probe tally and the
  measured service window. Everything that broke, with the cause, and what was changed to
  get past it.
- **A runbook for your window.** The commands in order, what to check after each one, and
  the point after which you roll back instead of forward.
- **A rollback procedure that was executed,** not only written down.
- **A walkthrough** for the people who will do the upgrade: a call or in writing, your
  choice.

## What it does not prove

The drill cluster is three containers standing in for VMs. They share one kernel, so a
sysctl, firewall, time-sync or virtual-IP problem on your machines will not show up there,
and the service window we measure describes that cluster, not your hardware. The report says
this again next to the numbers. If you want the same drill on a staging environment of your
own, that is the [migration engagement](/pricing/#services), and we quote it after the drill
has shown how much work it is.

## What we need from you

- Source and target versions, and the cluster shape.
- A realm export. Configuration is what breaks upgrades, so leave the users out; nothing in
  the drill needs real accounts, credentials or secrets. Redact hostnames.
- Your custom providers and themes as build artifacts, or a description if they cannot leave
  your network. In that case we tell you which checks could not be run.

## Price

**$4,000 per upgrade path, fixed.** A path is one source version to one target version. The
price and the deliverables are agreed in writing before work starts; if it takes us longer,
that is our problem, not your invoice.

A drill that passes may be all you need: your team runs the window with the runbook. If you
want us on the call during the window, or the upgrade is part of a move off RH-SSO or a
managed vendor, that is [Migration & upgrades](/pricing/#services), from $5,000.

## The free version

For a stock realm on a single node, the drill is free:
[request the path](https://github.com/keelinfra/keycloak/issues/new?template=upgrade_path_request.yml)
and we run it in public CI. A passing path joins the nightly matrix; a failing one gets
written up, with what broke.

## Ask for a drill

Write to
[hello@keelinfra.io](mailto:hello@keelinfra.io?subject=Upgrade%20drill)
with the version you are on, the version you want to reach, the cluster shape, and what
would make a naive upgrade break. You get an answer within one business day, including
"you don't need this" when you don't.
