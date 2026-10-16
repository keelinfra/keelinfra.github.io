+++
title = "Help moving legacy build hosts to current Jenkins"
description = "Agent8 is free and open source. Write to us for help rolling it out: AIX, Solaris and HP-UX pilots, plugin compatibility on a Java 8 agent, and a free first look at which path each build host needs."
template = "assessment.html"

[extra]
subtitle = "First answer free · in writing · within two business days"
+++

[Agent8](https://github.com/keelinfra/agent8) is free and open source, and you can roll it out
yourself: the README has the install script and an Ansible playbook, and
[GitHub issues](https://github.com/keelinfra/agent8/issues) are the place for bugs.

Write to us when that is not enough:

- **Your hosts run AIX, Solaris or HP-UX.** Agent8 connects on real Solaris and HP-UX; builds there, and AIX, are still being verified. We run it
  with you on your platform as a pilot, and fix what breaks.
- **You need to know whether your plugins work.** Plugins that run their own code on agents
  are the main open risk on a Java 8 agent. CI tests Git checkout (JGit) and credentials
  binding; others, such as Maven, Docker or command-line git, still need testing. We check the
  ones your builds use.
- **You have many hosts, or you need support you can put in a contract.**
- **You are not sure which path each host needs.** Some can run a normal Java 21 agent, some
  builds can move into a container, and the rest need agent8.

The first answer is free and in writing: for each host, the highest Java it can run with the
vendor source for it, the path that fits, and what we have not verified for your platform. If
every host you have can run a normal agent, that is what we will tell you. The background is in
[Jenkins requires Java 21. What happens to your AIX 7.1 and RHEL 6 build hosts?](/blog/jenkins-java-21-aix-rhel6-build-hosts/)

Pilots, plugin checks and yearly support have fixed prices, listed on the
[pricing page](/jenkins/pricing/).

Leave out hostnames, IP addresses, credentials and anything else you would not put in an
email to a stranger. Operating system versions and what each host builds are enough.
