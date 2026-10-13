+++
title = "Jenkins requires Java 21. What happens to your AIX 7.1 and RHEL 6 build hosts?"
date = 2026-10-13
description = "Jenkins needs Java 21 on the controller and on every agent. AIX 7.1, RHEL 6, Solaris and HP-UX cannot run it, so their teams stay on Jenkins 2.346.3. Where each Jenkins version is locked, the highest Java each legacy platform can run, with sources, and agent8: a Jenkins agent that runs on Java 8."
+++

Since LTS 2.541.3 in March 2026, Jenkins no longer supports Java 17. Current releases run on
Java 21 or Java 25 ([Jenkins Java support policy](https://www.jenkins.io/doc/book/platform-information/support-policy-java/)).

The part that hurts is one sentence on that page: the requirement applies to *all components
of the Jenkins system*, agents included. Moving the controller to a new VM is an afternoon.
The build hosts are the problem: the AIX 7.1 LPAR that produces the release your oldest
customers install, the RHEL 6 box with the compiler nobody dares to touch, the Solaris and
HP-UX machines that still ship product. None of them can run Java 21, so none of them can
run a current `agent.jar`.

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
| RHEL / CentOS 6 | yes. Red Hat's OpenJDK 8 (from 6.6) is retired, last update 1.8.0_275, and not part of ELS; Temurin 8 runs on CentOS 6.10 | Oracle JDK 11 was certified, now no longer supported | no | [Red Hat OpenJDK lifecycle](https://access.redhat.com/articles/1299013), [Oracle JDK 11 certified systems](https://www.oracle.com/java/technologies/javase/products-doc-jdk11certconfig.html) |
| RHEL 7 | yes (Red Hat, 7.1+) | yes (Red Hat, 7.6+) | not from Red Hat | [Red Hat OpenJDK lifecycle](https://access.redhat.com/articles/1299013) |
| AIX 7.1 | yes: IBM SDK, Java Technology Edition 8, on 7100-03 or later | no | no | [IBM Java for AIX](https://www.ibm.com/support/pages/java-sdk-aix), [IBM Semeru supported environments](https://www.ibm.com/support/pages/node/6451203) |
| AIX 7.2 TL5+, AIX 7.3 TL2+ (POWER8 or later) | yes | yes | **yes: IBM Semeru 17 and 21** | [IBM Semeru supported environments](https://www.ibm.com/support/pages/node/6451203) |
| Solaris 10 / 11, SPARC and x64 | yes: Oracle JDK 8 (Solaris 10 Update 9+, Solaris 11) | Oracle JDK 11 on Solaris 11.3+ SPARC | no: OpenJDK removed the Solaris ports in JDK 15 | [Oracle JDK 8 certified systems](https://www.oracle.com/java/technologies/javase/products-doc-jdk8-jre8-certconfig.html), [Oracle JDK 11 certified systems](https://www.oracle.com/java/technologies/javase/products-doc-jdk11certconfig.html), [JEP 381](https://openjdk.org/jeps/381) |
| HP-UX 11i v3, Integrity (Itanium) | yes: HPE JDK 8 | not established | no | [HPE community: Java versions for HP-UX](https://community.hpe.com/t5/operating-system-hp-ux/may-i-know-which-is-the-latest-version-of-java-hp-ux-supportable/m-p/7045100/highlight/true) |
| HP-UX, PA-RISC | no: the last PA-RISC build in HPE's list is JDK 7 | no | no | same |

Checked 2026-10-13. Two things stand out.

**Java 8 runs almost everywhere. Java 21 runs on almost none of them.** AIX 7.1 is a common
example: it is often described as unable to run modern Java, but IBM's Java 8 supports it. What
it cannot run is anything newer. The same is true of RHEL 6, Solaris and HP-UX on Itanium.

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
- **RHEL / CentOS 6, if what you need is the old glibc and toolchain:** you can build in a
  container image of that userland on a current Linux agent instead. This keeps the old
  binaries compatible without keeping the old machine.
- **AIX 7.1, RHEL 6 hosts you have to keep, Solaris, HP-UX on Itanium:** these can run Java 8
  and nothing newer. That is the gap agent8 is for.

## agent8: a Jenkins agent that runs on Java 8

[agent8](https://github.com/keelinfra/agent8) is an open-source (MIT) build of the Jenkins agent
that runs on Java 8 and connects to a current controller on Java 21 or 25. The legacy host
stays an ordinary node: labels, executors, `sh`, file steps, `junit`, `stash`, aborts and the
script console work as on any other agent.

It is built from your controller's own `agent.jar`, so the remoting versions match:

```bash
curl -fsSO https://jenkins.example.com/jnlpJars/agent.jar
./build.sh agent.jar        # produces dist/agent8.jar and dist/jvmdg.jar
```

On the legacy host, start an inbound agent with the two jars:

```bash
java -javaagent:agent8.jar -javaagent:jvmdg.jar -jar agent8.jar \
     -url https://jenkins.example.com/ -secret <secret> -name <node> -workDir /srv/jenkins
```

Rebuild `agent8.jar` whenever the controller is upgraded.

### How it works

A Jenkins agent runs two kinds of Java code: remoting itself, and classes the controller sends
while builds run, such as core and plugin code for file operations, `junit`, `stash` and
launching processes. All of it is compiled for Java 17 or 21. agent8 makes it run on Java 8 in
three steps:

1. **Remoting is downgraded ahead of time.** [JvmDowngrader](https://github.com/unimined/JvmDowngrader)
   rewrites `agent.jar` to Java 8 bytecode and adds stand-ins for newer JDK APIs. The one call
   it cannot handle is patched in the remoting source.
2. **Classes from the controller are downgraded as they load,** by JvmDowngrader's Java agent.
3. **Serialization stays compatible with the controller.** Downgrading adds synthetic members,
   which changes the default `serialVersionUID` of classes that do not declare one, and the
   controller would reject every call. agent8 pins the UID the controller computes. It also adds
   the serial form of `List.of`, `Set.of` and `Map.of`, which Java 8 does not have.

### What has been verified, and what has not

agent8 is experimental. Its CI runs weekly against the current Jenkins LTS and weekly release,
with the agent on Temurin 8 in a CentOS 6.10 container:

- objects written on Java 21 are read correctly on Java 8;
- Pipeline builds run on the Java 8 agent;
- aborting a build stops it on the agent;
- restarting the agent in the middle of a build;
- the script console.

Not yet verified: **AIX with IBM Java 8, Solaris, and HP-UX.** The JVM is what matters most
here, and IBM's J9 is not HotSpot, so AIX needs its own testing. We will publish those results
when we have them. Until then, treat agent8 as working on Linux with Java 8, not as proven on
your platform.

Known gaps:

- A newer JDK API that JvmDowngrader cannot stub fails only when that code runs. Plugins that
  run code on agents, such as git, Maven, Docker and credentials binding, still need testing.
- Use an inbound agent for now. The SSH launcher copies the controller's own `remoting.jar`
  to the agent, which does not run on Java 8.
- Jenkins could add a hard check on the agent's Java version in a future release.

## Get your build fleet assessed

If a few build hosts are holding your Jenkins back, send us the list. For each host, we tell
you the highest Java it can run, which path above fits it, and what we have and have not
verified for that platform. If every host you have can run a normal Java 21 agent, that is
what we will tell you.

The assessment is free, and you get the answer in writing.
[Request an assessment →](/jenkins-assessment/)

---

*keelinfra helps teams keep self-hosted infrastructure on supported, patched versions when
their environment makes upgrading hard. Questions or corrections: hello@keelinfra.io.*

*Jenkins is a trademark of LF Charities Inc. keelinfra is an independent project, not
affiliated with or endorsed by the Jenkins project.*
