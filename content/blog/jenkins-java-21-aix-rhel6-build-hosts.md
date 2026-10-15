+++
title = "Jenkins requires Java 21. What happens to your AIX 7.1 and RHEL 6 build hosts?"
date = 2026-10-13
description = "Jenkins needs Java 21 on the controller and on every agent. AIX 7.1, Solaris and HP-UX cannot run it, so their teams stay on Jenkins 2.346.3. Where each Jenkins version is locked, the highest Java each legacy platform can run, with sources, and Agent8: a Jenkins agent that runs on Java 8."
+++

Plenty of companies ship software on a long tail of platforms. Besides mainstream Linux there is
AIX, HP-UX, Solaris, and a set of RHEL 6 machines, often with a RHEL 5 box or two in a corner.
These hosts have built releases for years, nobody wants to touch them, and they are Jenkins
agents: every platform build of the product comes from them.

On those systems, Java stops at 8. Jenkins, meanwhile, keeps raising its Java baseline: Java 11
from 2.361.1 LTS in 2022, Java 17 from 2.479.1 LTS in 2024, and today Java 21 or 25
([Jenkins Java support policy](https://www.jenkins.io/doc/book/platform-information/support-policy-java/)).
The sentence on that page that hurts is that the requirement applies to *all components of the
Jenkins system*, agents included.

Then the security scan arrives. An old controller is a list of CVEs, and IT does not negotiate.
So the team has to pick one:

- **Upgrade the controller.** The audit passes, and every AIX, HP-UX, Solaris and old RHEL
  agent can no longer connect.
- **Don't upgrade.** The old agents keep working, and the whole Jenkins stays on a release
  nobody patches, with an exception request every audit cycle.

What teams usually end up doing is keeping a second, old Jenkins just for those platforms, which
means two systems to run and two sets of CVEs, or building those platforms by hand. Some drive
the old hosts over SSH from a modern agent with an SSH plugin. That works on paper, but logs,
aborts, workspaces and artifacts are all theirs to wire up, and the host never behaves like a
real node.

This post covers where Jenkins gets locked, which Java each of these platforms can actually run,
with sources, and Agent8, an open-source Jenkins agent that runs on Java 8.

## Where Jenkins gets stuck

Each Java version Jenkins drops leaves a last release behind. If your oldest build host can
only run Java 8, the newest Jenkins it can join is 2.346.3, released in August 2022. It has had
no security fixes since, and neither have the plugin versions that still install on it.

| Highest Java on your oldest agent | Last Jenkins LTS | Last weekly |
|---|---|---|
| Java 8 | 2.346.3 (August 2022) | 2.356 |
| Java 11 | 2.462.3 (October 2024) | 2.462 |
| Java 17 | 2.541.3 (March 2026) | 2.544 |
| Java 21 | current; planned end of support September 2027 | current |
| Java 25 | current; planned end of support September 2029 | current |

Source: [Jenkins Java support policy](https://www.jenkins.io/doc/book/platform-information/support-policy-java/),
checked 2026-10-13.

## The highest Java each legacy platform can run

This is the table we could not find in one place. "Vendor" means the operating system vendor's
own Java or the Java its vendor certifies for it.

| Platform | Java 8 | Java 11 | Java 17 / 21 | Sources |
|---|---|---|---|---|
| RHEL 5 | Oracle JDK 8 only; certified for 5.5+, now listed as no longer supported. Red Hat's own OpenJDK stops at 7 | no | no | [Oracle JDK 8 certified systems](https://www.oracle.com/java/technologies/javase/products-doc-jdk8-jre8-certconfig.html), [Red Hat OpenJDK lifecycle](https://access.redhat.com/articles/1299013) |
| RHEL / CentOS 6 | yes. Red Hat's OpenJDK 8 (from 6.6) is retired, last update 1.8.0_275, and not part of ELS; Temurin 8 runs on CentOS 6.10 | Oracle JDK 11 was certified, now no longer supported | **x86_64: yes, Amazon Corretto 17 and 21** (Corretto 25 needs RHEL 7+) | [Red Hat OpenJDK lifecycle](https://access.redhat.com/articles/1299013), [Oracle JDK 11 certified systems](https://www.oracle.com/java/technologies/javase/products-doc-jdk11certconfig.html), [Amazon Corretto FAQ](https://aws.amazon.com/corretto/faqs/) |
| RHEL 7 | yes (Red Hat, 7.1+) | yes (Red Hat, 7.6+) | not from Red Hat | [Red Hat OpenJDK lifecycle](https://access.redhat.com/articles/1299013) |
| AIX 7.1 | yes: IBM SDK, Java Technology Edition 8, on 7100-03 or later | no | no | [IBM Java for AIX](https://www.ibm.com/support/pages/java-sdk-aix), [IBM Semeru supported environments](https://www.ibm.com/support/pages/node/6451203) |
| AIX 7.2 TL5+, AIX 7.3 TL2+ (POWER8 or later) | yes | yes | **yes: IBM Semeru 17 and 21** | [IBM Semeru supported environments](https://www.ibm.com/support/pages/node/6451203) |
| Solaris 10 / 11, SPARC and x64 | yes: Oracle JDK 8 (Solaris 10 Update 9+, Solaris 11) | Oracle JDK 11 on Solaris 11.3+ SPARC | no: OpenJDK removed the Solaris ports in JDK 15 | [Oracle JDK 8 certified systems](https://www.oracle.com/java/technologies/javase/products-doc-jdk8-jre8-certconfig.html), [Oracle JDK 11 certified systems](https://www.oracle.com/java/technologies/javase/products-doc-jdk11certconfig.html), [JEP 381](https://openjdk.org/jeps/381) |
| HP-UX 11i v3, Integrity (Itanium) | yes: HPE JDK 8 | not established | no | [HPE community: Java versions for HP-UX](https://community.hpe.com/t5/operating-system-hp-ux/may-i-know-which-is-the-latest-version-of-java-hp-ux-supportable/m-p/7045100/highlight/true) |
| HP-UX, PA-RISC | no: the last PA-RISC build in HPE's list is JDK 7 | no | no | same |

Checked 2026-10-13; RHEL 6 row corrected 2026-10-15. Two things stand out.

**Java 8 runs almost everywhere. Java 21 runs on few of them.** AIX 7.1 is a common
example: it is often described as unable to run modern Java, but IBM's Java 8 supports it. What
it cannot run is anything newer. The same is true of Solaris and HP-UX on Itanium.

**A few hosts are worse off.** On RHEL 5, the only Java 8 is Oracle JDK 8, no longer supported
there, and Oracle JDK 8 updates need an Oracle subscription for commercial use. HP-UX on
PA-RISC stops at Java 7. Those hosts are outside what anything below can fix.

## Sort your build hosts

Run this on each build host:

```bash
uname -s
oslevel -s 2>/dev/null                        # AIX: technology level and service pack
prtconf 2>/dev/null | grep 'Processor Type'   # AIX: POWER generation
cat /etc/redhat-release 2>/dev/null           # RHEL / CentOS
java -version 2>&1 | head -1                  # what is installed today
```

Then each host takes one of these paths:

- **AIX 7.2 TL5+ or 7.3 TL2+ on POWER8 or later:** install IBM Semeru 21 and run a normal
  agent. It needs the XL C++ Runtime 16.1.0.10 or later. Nothing else is required.
- **RHEL / CentOS 6 x86_64:** install Amazon Corretto 21 and run a normal agent. Corretto 17
  and 21 list RHEL 6+ as supported; Corretto 25 needs RHEL 7+, so this lasts until Jenkins
  requires Java 25.
- **RHEL / CentOS 6, if what you need is the old glibc and toolchain:** you can build in a
  container image of that userland on a current Linux agent instead. This keeps the old
  binaries compatible without keeping the old machine.
- **AIX 7.1, Solaris, HP-UX on Itanium:** these can run Java 8 and nothing newer. RHEL 6
  hosts whose installed JDK must not change are in the same place. That is the gap Agent8 is for.

## Agent8: a Jenkins agent that runs on Java 8

[Agent8](https://github.com/keelinfra/agent8) is an open-source (MIT) build of the Jenkins agent
that runs on Java 8 and connects to a current controller on Java 21. The legacy host
stays an ordinary node: labels, executors, `sh`, file steps, `junit`, `stash`, aborts and the
script console work as on any other agent.

It replaces the `agent.jar` the host already runs. On the build host, with its existing Java 8:

```bash
curl -fsSLO https://raw.githubusercontent.com/keelinfra/agent8/main/install.sh
sh install.sh --url https://jenkins.example.com/ --replace /path/to/agent.jar
```

The script reads the remoting version of the controller's `agent.jar`, downloads the Agent8
release built for it, in the build for the host's Java, checks it against the release's `sha256sums.txt`, test-starts it on the
host's Java, and swaps it in. The old jar is kept as `agent.jar.before-agent8`, and
`--restore` puts it back. Then restart the agent with the command it already uses:

```bash
java -jar /path/to/agent.jar -url https://jenkins.example.com/ -secret <secret> -name <node> -workDir /srv/jenkins
```

The script is plain `sh`, written for RHEL 6, AIX, Solaris and HP-UX. Hosts without internet
access can be given the jars from the
[releases](https://github.com/keelinfra/agent8/releases) with `--from DIR`. For many hosts,
an [Ansible playbook](https://github.com/keelinfra/agent8/tree/main/ansible) runs the same
script and needs no Python on the hosts. Run it again after each controller upgrade: Jenkins
refuses agents older than a minimum remoting version that it raises over time, and Jenkins 2.586
already refuses the Agent8 build for 2.462.3.

One controller setting matters. If the Versions Node Monitors plugin is installed, its
*JVM Version* monitor takes every agent whose Java is older than the controller's offline
seconds after it connects, and its *Remoting Version* monitor does the same when the agent's
build differs from the controller's. Set them not to disconnect agents; the
[README](https://github.com/keelinfra/agent8) has the configuration-as-code snippet.

Java 8 is the main target. The same build also makes jars for hosts that stop at Java 11, such
as Solaris, and at Java 17; the script picks the right one from the host's Java.

### How it works

A Jenkins agent runs two kinds of Java code: remoting itself, and classes the controller sends
while builds run, such as core and plugin code for file operations, `junit`, `stash` and
launching processes. All of it is compiled for Java 17 or 21. Agent8 makes it run on Java 8 in
three steps:

1. **Remoting is downgraded ahead of time.** [JvmDowngrader](https://github.com/unimined/JvmDowngrader)
   rewrites `agent.jar` to Java 8 bytecode and adds stand-ins for newer JDK APIs. The one call
   it cannot handle is patched in the remoting source.
2. **Classes from the controller are downgraded as they load,** by JvmDowngrader's Java agent,
   which the Agent8 jar starts for itself, so the start command does not change.
3. **Serialization stays compatible with the controller.** Downgrading adds synthetic members,
   which changes the default `serialVersionUID` of classes that do not declare one, and the
   controller would reject every call. Agent8 pins the UID the controller computes. It also adds
   the serial form of `List.of`, `Set.of` and `Map.of`, which Java 8 does not have.

### What has been verified, and what has not

Agent8 is released and free to use; support for AIX, Solaris and HP-UX is still experimental.
Its CI tests every change, and runs weekly, against the current Jenkins
LTS and weekly release. Each run installs Agent8 with `install.sh` over a stock `agent.jar` on
an old Java, starts it with the usual command, and checks:

- objects written on Java 21 are read correctly on Java 8;
- Pipeline builds run on the agent;
- a Git checkout with JGit and a `withCredentials` block work, which means plugin code sent
  by the controller runs on the old Java;
- aborting a build stops it on the agent;
- the build survives a restart of the agent in the middle of it;
- the script console works;
- `--replace` and `--restore` swap the jar in and back out.

The Java 8 runs use Temurin 8 on CentOS 6.10, and OpenJ9 8 (IBM Semeru) on Linux, which is
the JVM family of IBM Java 8 on AIX. Java 11 and Java 17 builds are tested on Linux against the current LTS.

Not yet verified: **AIX with IBM Java 8, Solaris, and HP-UX.** OpenJ9 on Linux covers the JVM
that AIX uses, but not AIX itself. We will publish those results
when we have them. Until then, treat Agent8 as working on Linux with Java 8, not as proven on
your platform.

Known gaps:

- A newer JDK API that JvmDowngrader cannot stub fails only when that code runs. Git checkout
  and credentials binding are tested; other plugins that run code on agents, such as Maven or
  Docker, still need testing.
- Use an inbound agent for now. The SSH Build Agents plugin copies its own `remoting.jar` to
  the host, and that jar does not run on Java 8.
- The Maven project type (maven-plugin), which starts its own agent JVM, is untested.

## Try it, or get help

Agent8 is free and open source. If you can try it yourself, start with the
[README](https://github.com/keelinfra/agent8), and report anything that breaks as a
[GitHub issue](https://github.com/keelinfra/agent8/issues).

Write to us instead if your hosts run AIX, Solaris or HP-UX, where Agent8 has not been verified
yet, if you need to know whether the plugins your builds use work on a Java 8 agent, or if you
want the rollout done with you rather than by you. The first answer is free: for each host, the
highest Java it can run, which path above fits it, and what has and has not been verified for
that platform.
[Tell us about your build hosts →](/jenkins-assessment/)

---

*keelinfra helps teams keep self-hosted infrastructure on supported, patched versions when
their environment makes upgrading hard. Questions or corrections: hello@keelinfra.io.*

*Jenkins is a trademark of LF Charities Inc. keelinfra is an independent project, not
affiliated with or endorsed by the Jenkins project.*
