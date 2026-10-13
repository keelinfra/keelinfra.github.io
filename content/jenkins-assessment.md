+++
title = "Jenkins legacy build host assessment"
description = "Free, written assessment for teams held back on old Jenkins versions by AIX, RHEL/CentOS 6, HP-UX or Solaris build hosts: the highest Java each host can run, and whether it needs a Java 21 agent, a container or agent8."
template = "assessment.html"

[extra]
subtitle = "Free · answered in writing · within two business days"
+++

Jenkins now needs Java 21 on the controller and on every agent. If a few build hosts are the
reason you are still on an old Jenkins, tell us what they are. For each one, you get back:

- **The highest Java it can run**, with the vendor source for it.
- **The way forward for that host**: a normal Java 21 agent, a container on a current Linux
  agent, or [agent8](https://github.com/keelinfra/agent8), the Jenkins agent that runs on Java 8.
- **What we have not verified** for your platform, said plainly, so you can test it before you
  rely on it.

If every host you have can run a normal agent, that is what we will tell you. The background
is in [Jenkins requires Java 21. What happens to your AIX 7.1 and RHEL 6 build hosts?](/blog/jenkins-java-21-aix-rhel6-build-hosts/)

Leave out hostnames, IP addresses, credentials and anything else you would not put in an
email to a stranger. Operating system versions and what each host builds are enough.
