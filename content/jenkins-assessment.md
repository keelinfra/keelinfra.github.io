+++
title = "Jenkins legacy build host assessment"
description = "Free, written assessment for teams held back on old Jenkins versions by AIX, RHEL/CentOS 6, HP-UX or Solaris build hosts: which hosts can run a Java 21 agent, which can move into a container, and which need a bridge."
template = "assessment.html"

[extra]
subtitle = "Free · answered in writing · within two business days"
+++

Jenkins now needs Java 21 on the controller and on every agent. If a few build hosts are the
reason you are still on an old Jenkins, tell us what they are. For each one, you get back:

- **Which group it is in**: it can run a normal Java 21 agent, its build can move into a
  container on a current Linux agent, or it needs a bridge because no Java 21 exists for it.
- **The way forward for that host**, with what has to change on it and what stays as it is.
- **What we have not verified** for your platform, said plainly, so you can test it before you
  rely on it.

If every host you have can run a normal agent, that is what we will tell you. The background
is in [Jenkins requires Java 21. What happens to your AIX 7.1 and RHEL 6 build hosts?](/blog/jenkins-java-21-aix-rhel6-build-hosts/)

Leave out hostnames, IP addresses, credentials and anything else you would not put in an
email to a stranger. Operating system versions and what each host builds are enough.
