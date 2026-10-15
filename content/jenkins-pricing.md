+++
title = "Agent8 for Jenkins pricing"
description = "Agent8 is free and MIT. Paid help: a plugin compatibility check for $1,500, a pilot on your AIX, Solaris or HP-UX hosts for $4,000, and yearly support from $3,000 per controller."
template = "jenkins-pricing.html"
path = "jenkins/pricing"

[[extra.services]]
name = "Plugin compatibility check"
price = 1500
price_label = "$1,500"
price_note = "fixed price"
mailto = "mailto:hello@keelinfra.io?subject=Agent8%20plugin%20compatibility%20check"
cta = "Ask for a check"
bullets = [
  "The plugins your builds use on old hosts, run on Agent8 with your host's Java",
  "Your Jenkins version, and the next LTS you plan to move to",
  "Written report: what works, what breaks, and what to do about each",
  "Delivered within ten business days of getting your plugin list",
]

[[extra.services]]
name = "Pilot on your platform"
price = 4000
price_label = "$4,000"
price_note = "fixed price, up to 3 hosts"
mailto = "mailto:hello@keelinfra.io?subject=Agent8%20pilot"
cta = "Plan a pilot"
bullets = [
  "Agent8 installed on up to 3 AIX, Solaris or HP-UX hosts with your team",
  "Your own jobs run end to end, including aborts and agent restarts",
  "We fix what breaks there in Agent8, or tell you in writing why we cannot",
  "Written report and a rollout runbook for the rest of the fleet",
]

[[extra.plans]]
name = "Standard"
price = 3000
price_label = "$3,000"
price_note = "per controller, per year, up to 20 hosts"
mailto = "mailto:hello@keelinfra.io?subject=Agent8%20Standard%20support"
cta = "Ask about Standard"
bullets = [
  "A tested Agent8 build within five business days of every Jenkins LTS",
  "Your installed build checked against each upcoming LTS, with a warning before it would be refused",
  "Email support from the people who build Agent8, reply within two business days",
  "Help with each controller upgrade across your hosts",
]

[[extra.plans]]
name = "Enterprise"
price = 8000
price_label = "from $8,000"
price_note = "per year, any number of hosts"
mailto = "mailto:hello@keelinfra.io?subject=Agent8%20Enterprise%20support"
cta = "Ask about Enterprise"
bullets = [
  "Everything in Standard, for all your controllers",
  "Each new build verified on your OS and Java versions before you get it",
  "Signed jars and an SBOM, prepared for your security review (not yet in the public releases)",
  "A named engineer, reply within one business day",
]
+++
