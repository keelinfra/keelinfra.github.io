+++
title = "Keycloak pricing"
description = "The distribution is free and Apache-2.0. A $400 health check, fixed-scope services from $3,000, emergency help at $200/hour, and a self-hosted subscription from $4,500 per production cluster per year."
template = "pricing.html"
path = "keycloak/pricing"
aliases = ["/pricing/"]

[extra]
subscription_price = 4500

# Shown on its own above the service cards: the small first step.
[[extra.services]]
name = "Keycloak health check"
featured = true
price = 400
price_label = "$400"
price_note = "fixed price"
mailto = "mailto:hello@keelinfra.io?subject=Keycloak%20health%20check"
cta = "Book a health check"
blurb = "Send your Keycloak and database versions and a realm and config export with secrets removed, or walk us through your setup on a one-hour call. Within three business days you get a written report: which known CVEs reach your version and configuration, what in your clustering, proxy, hostname and database settings matches the failure modes we see in the field, where backups and restores have gaps, and the upgrade path we would take. Subscribe within 60 days and the $400 comes off your first year."

[[extra.services]]
name = "Upgrade drill"
price = 4000
price_label = "$4,000"
price_note = "per path, fixed price"
mailto = "mailto:hello@keelinfra.io?subject=Upgrade%20drill"
cta = "Ask for a drill"
details = "/upgrade-drill/"
bullets = [
  "Your upgrade, run on a 3-node cluster with your realm configuration",
  "Every node probed once a second; the service window measured",
  "Written report: what broke, why, and what got past it",
  "A runbook and an executed rollback for your own window",
]

[[extra.services]]
name = "Deployment & HA hardening"
price = 3000
price_label = "from $3,000"
price_note = "fixed scope"
mailto = "mailto:hello@keelinfra.io?subject=Deployment%20%26%20HA%20hardening"
cta = "Get a quote"
bullets = [
  "Production HA deployment on your VMs or bare metal",
  "PostgreSQL HA, backups/PITR, monitoring included",
  "Failover & restore drills run with your team",
  "Handover runbook + 30 days of email support",
]

[[extra.services]]
name = "Migration & upgrades"
price = 5000
price_label = "from $5,000"
price_note = "fixed scope"
mailto = "mailto:hello@keelinfra.io?subject=Migration%20%2F%20upgrade"
cta = "Get a quote"
bullets = [
  "Legacy / RH-SSO / managed-vendor → self-hosted",
  "Multi-version upgrade paths, rehearsed on a staging copy",
  "Session & realm integrity verified before cutover",
  "Rollback plan you can actually execute",
]

[[extra.services]]
name = "Emergency & expert help"
price = 200
price_label = "$200"
price_note = "/hour"
mailto = "mailto:hello@keelinfra.io?subject=Keycloak%20help"
cta = "Email us"
bullets = [
  "Production down, upgrade gone wrong, cluster split-brain",
  "Architecture & config review",
  "Root-cause analysis with a written post-mortem",
  "No retainer required",
]
+++
