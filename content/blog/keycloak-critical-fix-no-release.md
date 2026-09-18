+++
title = "Keycloak fixed a critical account-takeover bug. Three of its release streams can't install the fix."
date = 2026-09-18
description = "CVE-2026-18963 (CVSS 9.1) is fixed in 26.4.15, 26.6.6 and 26.7.2. Only one of those is a release you can download. On 26.4 and 26.6 the fix is a git tag with no artifact; on 26.2 it does not exist at all. Where the fix actually is, why your scanner may not tell you, and the tested way off each stream."
[extra]
og_image = "/assets/social-preview-keycloak.png"
+++

In August, upstream Keycloak fixed **CVE-2026-18963** on three branches: 26.4.15 and
26.6.6 were tagged on 2026-08-11, and 26.7.2 was released on 2026-08-19. It is about as
bad as an identity-provider bug gets: an unauthenticated attacker could drive the
reset-credentials ("Forgot password") flow to completion without the emailed verification
token and set a new password on any account. CVSS 9.1, critical
([GHSA-4gv3-mc9p-5wqc](https://github.com/advisories/GHSA-4gv3-mc9p-5wqc)).

If you run 26.7, you upgrade and you are done. If you run anything older, it is worth
understanding exactly where that fix is — because for most of the affected versions, it is
not somewhere you can `docker pull` from.

## Where the fix actually is

Keycloak's community project supports one release: the latest. When a new minor ships, the
previous minor's branch keeps receiving backports — they feed Red Hat's commercial build —
and those backports are **tagged** in git. What they are not is **released**: no GitHub
release, no tarball, no image on quay.io. The tag exists; the artifact does not.

That is the position three streams were in when this CVE landed:

| Stream | Last community artifact | Fix is in | What that means |
|---|---|---|---|
| 26.7 | 26.7.3 (released 2026-08-31) | 26.7.2 | Upgrade. Done. |
| 26.6 | 26.6.4 (released 2026-06-26) | 26.6.6 — **tag only** | Fix exists; nothing to install |
| 26.4 | 26.4.7 | 26.4.15 — **tag only** | Fix exists; nothing to install |
| 26.2 | 26.2.5 | **nowhere** | Last tag is 26.2.16, cut 2026-05-06 — three months before the fix |

(Checked against the `quay.io/keycloak/keycloak` tag list and the GitHub releases page on
2026-08-31, and again on 2026-09-18.)

The 26.6 case is the one the
[upstream issue thread](https://github.com/keycloak/keycloak/issues/51833) filled up with.
Between 26.6.4 and 26.6.6 there are 69 commits carrying twelve CVE fixes; a cluster on
26.6.4 has every one of them written and none of them installable. The most-upvoted
comments in that thread asked for images of the patched tags as a one-off exception. The
maintainers' position, stated earlier in the same thread, is the policy: 26.6 stopped being
a supported release the moment 26.7.0 shipped.

## Why your scanner may say you are fine

Two details make this worse than the version table suggests.

The CVE was filed against *Red Hat build of Keycloak*. An operator in the thread reported
that Trivy did not flag the vanilla community image for it at the time. The GitHub
advisory now carries version ranges for `org.keycloak:keycloak-services`, so a dependency
scanner looking at the Maven artifact will see it; a container scanner looking at a
`quay.io/keycloak/keycloak:26.6.4` image may not. "Our scans are clean" is not evidence
here.

And there is no clean audit-log signature. A legitimate reset produces a
`GET /login-actions/action-token` — the email click — before the password changes; the
bypass does not. That is a reverse-proxy-log check, not a Keycloak-event check. Someone
[published a hunting script](https://github.com/kyos-public/keycloak-cve-2026-18963-hunt)
for it; the thread's corrections to its first version are worth reading before you trust
any single signal. If you sat on an affected version for a while with Forgot-password on,
assume you need to look.

## What people did

Three things, roughly in the order they appeared in the thread:

1. **Turn off Forgot-password on every realm.** It closes the route. It also breaks
   self-service password reset for everyone, which is why it is a stopgap and not a fix.
   Custom reset flows that do not use the standard `reset-credential-email` step need
   their own review.
2. **Build the tag yourself.** The source is there; `mvn` runs.
   [Phase Two](https://quay.io/repository/phasetwo/keycloak?tab=tags) started publishing
   images built from every upstream tag on 2026-08-25. We build the tarballs the same way —
   unmodified upstream tags, built in public CI, with the hashes and a smoke test
   [published alongside](https://github.com/keelinfra/keycloak/blob/main/lts/VERIFICATION-26.6.6.md) —
   and install them with a `--dist-url` flag. Whichever you use: it is a compile, not a
   patch. Nothing in those builds was written by anyone but upstream.
3. **Jump minors.** The officially supported route. We have
   [drilled 26.6.2 → 26.7.3](/docs/keycloak/upgrades/) and it works. The one place *not*
   to land is 26.7.0–26.7.2, which carry
   [six non-security regressions](/blog/keycloak-26-7-3-cve-triage/) including sustained
   high CPU on every node after upgrade.

None of those helps 26.2.

## 26.2 is the ugly one

There is no 26.2 tag with this fix. 26.2.16 was cut on 2026-05-06; the reset-credentials
fix landed on the other branches on 2026-08-11; no 26.2 tag has been cut since. Building
26.2.16 from source — which we did, and published — gets you 171 commits' worth of
backports, but not this one, because it does not exist for that branch. Nobody publishes a
fixed 26.2, because there is no upstream tag to build one from.

The only fix for a 26.2 cluster is to stop being a 26.2 cluster. And that is not a version
bump. Between 26.2 and 26.6 sit several minors' worth of schema migrations — including the
26.6 one that upstream itself added a slowness warning for — and an Infinispan major
(15 → 16). On the maintenance branches themselves, Infinispan point-version bumps mean a
rolling upgrade briefly runs mixed cache versions across nodes. Each of those is fine when
rehearsed and a bad night when not.

We have not drilled 26.2 → 26.6 yet. Every path we list, we have run first, and this one we
have not — so it is not listed. It is also exactly the path we most want to hear about: if
you are on 26.2,
[tell us where you need to get to](https://github.com/keelinfra/keycloak/issues/new?template=upgrade_path_request.yml)
and we will rehearse it in public CI and publish what happens, pass or fail.

## We got this one wrong, too

Three weeks after 26.6.6 was tagged, our own triage of the 26.6 stream described
CVE-2026-18963 as a minor authentication-flow issue. We had mapped the CVE to the wrong
commit. The community tags carry no release notes, the CVE is registered under a different
product's name, and when you are sorting twelve fixes by commit subject, "throw exception
and rollback when token verification fails in reset credentials" and "use model ID to set
the auth note" are one careless read apart. We
[corrected it](https://github.com/keelinfra/keycloak/pull/13) with the GHSA ranges as the
source of truth, and we are saying so here because it is the point: triage on
artifact-less branches is genuinely hard, and if you are doing it from commit logs, check
every CVE id against the advisory database before you decide what it is.

## Upstream is moving

On 2026-09-11 the Keycloak maintainers opened a proposal for
[extended release support](https://github.com/keycloak/keycloak/discussions/52655) and put
four options to a vote: latest‑1 with a three- or six-month cadence, or an LTS line with or
without an extended maintenance tail. As of 2026-09-18 it has 41 votes and "LTS with
extended maintenance" leads. Two things to know before you relax: it applies to 27.x
onward, not to any 26.x you run today, and 26.8 — the last 26.x — is planned to get about
twelve months of support in total.

What the proposal does not yet say is whether maintained tags will ship artifacts. Every
option on that poll only helps if the tag you are told is supported is something you can
install. If that matters to you, that is the thread to say it in.

## If you run Keycloak today

```bash
bin/kc.sh --version     # from your Keycloak home — what are you actually on?
```

- **26.7.0–26.7.2** → 26.7.3. Both the CVE and the regressions are behind you.
- **26.6.x** → 26.6.6. A third-party image, or a from-source build:
  ```bash
  ./upgrade --to 26.6.6 --dist-url https://github.com/keelinfra/keycloak/releases/download/kc-26.6.6-keel1/keycloak-26.6.6.tar.gz
  ```
  We run 26.6.4 → 26.6.6 nightly on a single node. The minor hop from 26.6.6 to 26.7.3 is
  not on our list yet; 26.6.2 → 26.7.3 is.
- **26.4.x** → 26.4.15 (a third-party image, or build the tag), or straight to 26.6.6 or
  26.7.3.
- **26.2.x** → off the branch. Until you are: Forgot-password off on every realm, and check
  the proxy logs for resets with no preceding email click.

Which of the other eleven 26.6 CVEs reach a plain OIDC deployment — fewer than you would
think; this one is the exception — is in our [CVE policy](/docs/keycloak/cve-policy/).

---

*keelinfra is an open-source (Apache-2.0) self-hosted Keycloak distribution — HA cluster,
Patroni-managed PostgreSQL, pgBackRest backups, monitoring, and upgrade paths re-proven
nightly in public CI. If you know Pigsty: that, for Keycloak. A subscription adds CVE
notification for the version you actually run and upgrade help along a path we have already
drilled: [keelinfra.io/pricing](https://keelinfra.io/pricing) · hello@keelinfra.io.*

*Keycloak is a trademark of The Linux Foundation. keelinfra is an independent project, not
affiliated with or endorsed by The Linux Foundation or the Keycloak project.*
