+++
title = "Jenkins requires Java 21. What happens to your AIX 7.1 and RHEL 6 build hosts?"
date = 2026-10-12
description = "Jenkins dropped Java 17 with LTS 2.541.3 in March 2026, and the Java requirement covers every agent, not only the controller. Most legacy build hosts have a supported way forward. AIX 7.1, HP-UX and Solaris do not. How to sort your build fleet, and what to do with the hosts that cannot run Java 21."
+++

Since LTS 2.541.3 in March 2026, Jenkins no longer supports Java 17. Current releases run on
Java 21 or Java 25, and Java 21 itself is planned to reach end of support in September 2027
([Jenkins Java support policy](https://www.jenkins.io/doc/book/platform-information/support-policy-java/)).

The part that hurts is one sentence on that page: the requirement applies to *all components
of the Jenkins system*, agents included. Moving the controller to a new VM is an afternoon.
The build hosts are the problem: the AIX 7.1 LPAR that produces the release your oldest
customers install, the RHEL 6 box with the compiler nobody dares to touch. They cannot run
Java 21, so they cannot run a current `agent.jar`.

The usual answer is to stop upgrading Jenkins. If your controller still runs on Java 8, it is
on 2.346.3 or older, released in August 2022 and without security fixes since. Every
plugin update since then is out of reach too.

| Java | Last Jenkins LTS that supports it |
|---|---|
| Java 8 | 2.346.3 (August 2022) |
| Java 11 | 2.462.3 (October 2024) |
| Java 17 | 2.541.3 (March 2026) |
| Java 21 | current; planned end of support September 2027 |
| Java 25 | current; planned end of support September 2029 |

(From the [Jenkins Java support policy](https://www.jenkins.io/doc/book/platform-information/support-policy-java/),
checked 2026-10-12.)

Freezing is not the only option. Most legacy hosts have a supported way forward; only a few
platforms really have none. The first step is to find out which of your hosts are which.

## Sort your build hosts first

Run this on each build host:

```bash
uname -s
oslevel -s 2>/dev/null                    # AIX: technology level and service pack
cat /etc/redhat-release 2>/dev/null       # RHEL / CentOS
prtconf 2>/dev/null | grep 'Processor Type'   # AIX: POWER generation
```

Each host falls into one of three groups.

### 1. AIX 7.2 TL5 or later, and AIX 7.3: run a normal agent

IBM ships Semeru Runtime 21 for AIX 7.2 TL5 and AIX 7.3 TL2, on POWER8 or later. It needs
the XL C++ Runtime 16.1.0.10 or later, and on AIX 7.2 a Power10 or Power11 machine has to
run in Power9 compatibility mode
([IBM Semeru supported environments](https://www.ibm.com/support/pages/node/6451203)).

On those hosts, install Semeru 21 and run a regular agent. Nothing else is needed. Note that
older technology levels are not on IBM's list, so an AIX 7.2 host below TL5 has to be
updated first.

### 2. RHEL and CentOS 6: move the build into a container

A RHEL 6 build host is usually kept for one reason: its glibc and its toolchain, so that the
binaries still run on your customers' old systems. Neither needs the old kernel or Java. Put
the userland in an image and build inside it, on a current Linux agent that runs Java 21:

```groovy
node('linux') {
    checkout scm
    docker.image('registry.example.com/build/rhel6-toolchain:2026-10').inside {
        sh 'make all && make test'      // glibc 2.12, your old gcc, no Java
    }
    junit '**/TEST-*.xml'
}
```

Build the image from your own toolchain and mirror; `centos:6` from Docker Hub is a starting
point, but its repositories are archived and it receives no updates. On some recent host
kernels, binaries this old crash at start with exit code 139: the kernel has the legacy
`vsyscall` page disabled, and booting the host with `vsyscall=emulate` brings it back.

### 3. AIX 7.1, HP-UX and Solaris: no Java 21

These platforms have no Java 21 runtime, and none is coming. This is the group that keeps
people on Jenkins 2.346.

Before solving it, check how much of your build really has to run there. AIX keeps binary
compatibility upward: a program built on 7.1 runs on 7.2 and 7.3. In many shops the 7.1 host
does one job, building and testing the release that 7.1 customers install. That one step is
what needs a bridge, not the whole pipeline.

## Options for hosts that cannot run Java 21

| Option | What you keep | What it costs |
|---|---|---|
| Freeze Jenkins on 2.346.3 | Everything works as before | No security fixes since 2022, no plugin updates |
| Run commands over SSH from a pipeline step | `sh`, with your own scripting | The host is not a node: no labels, no `node('aix71')`, `junit` and `stash` do not run there, abort leaves remote processes behind unless you handle it |
| Patch `agent.jar` to run on Java 8 | A real agent | The controller sends Java 17+ bytecode to the agent; every Jenkins and plugin release can break a downgraded agent |
| A Java 21 proxy agent that runs processes on the legacy host | `node('aix71')`, `sh`, file steps, abort, durable builds | A shared workspace (NFS) between the proxy and the legacy host |

The last row is the approach we are building, as an open-source Jenkins plugin:
[Legacy Build Host](https://github.com/shenxianpeng/legacy-build-host-plugin) (MIT).

## How the proxy agent works

A Jenkins agent does two different kinds of work. Some of it is Java code the controller
sends over: file operations, `junit`, `stash`, `archiveArtifacts`, `readFile`. The rest is
starting native processes, such as Pipeline `sh`. Only the second kind has to happen on the
legacy host.

So each legacy host gets a Linux agent with Java 21, named after it. The plugin wraps that
agent's process launcher (a `LauncherDecorator`, a public Jenkins extension point), so every
process Jenkins starts there runs on the legacy host over SSH instead. The workspace is
mounted on the legacy host at the same path, so both sides see the same files:

```
controller (Java 21) ── agent "aix71" (Linux, Java 21) ── ssh ──> AIX 7.1 (sshd + sh, no Java)
                                  └──── same workspace path over NFS ────┘
```

The pipeline is an ordinary pipeline:

```groovy
node('aix71') {
    checkout scm                  // runs on the proxy
    sh 'make all && make test'    // runs on AIX 7.1
    junit '**/TEST-*.xml'         // reads the shared workspace
    archiveArtifacts 'dist/**'
}
```

Pipeline `sh` keeps its durable behaviour. The step runs detached on the legacy host and
writes its log and exit code into the shared workspace, and the agent polls those files. That
protocol needs no Java on the machine running the script, so a build survives a restart of
the proxy agent. When a build is aborted, the plugin kills the step's whole process group on
the legacy host.

## What has been verified, and what has not

On Jenkins 2.580.1 (Java 21), with a CentOS 6.10 container (glibc 2.12, no Java) as the
legacy host behind a proxy agent:

- `sh` ran on the CentOS 6 host; `junit`, `stash`, `archiveArtifacts`, `readFile`, `dir`,
  `withEnv`, `returnStdout` and `returnStatus` worked on the shared workspace.
- Aborting a running build marked it ABORTED within about a second, and no process from the
  step was left on the legacy host.
- Killing the proxy agent in the middle of a build and starting it again: the remote step kept
  running, and the build finished with SUCCESS.
- The plugin's 20 tests pass in its public CI, running real pipelines against a fake SSH host.

Not yet verified: **a real AIX 7.1 host, and a real NFS mount.** The CentOS 6 tests used a
local mount, so NFS attribute caching and uid mapping have not been exercised, and AIX's
process-group handling still has to be confirmed. We will publish those results when we have
them. Until then, treat this as a design that works on Linux, not as something proven on AIX.

Known limitations, also listed in the plugin's
[design notes](https://github.com/shenxianpeng/legacy-build-host-plugin/blob/main/docs/DESIGN.md):

- The workspace has to be shared at the same path with the same uid on both sides, and heavy
  build I/O over NFS is slower than local disk.
- One proxy agent per legacy host, though many proxies can run on one Linux machine.
- Java code still runs on the proxy, so tool installers install Linux tools. Build tools have
  to be installed on the legacy host itself.
- The legacy host uses its own login environment, so `withEnv(['PATH+X=…'])` does not change
  its `PATH` yet.
- Killing remote processes on abort covers Pipeline `sh`, not freestyle *Execute shell* yet.
- POSIX hosts only, and SSH keys without a passphrase only, for now.

## Get your build fleet assessed

If you are holding Jenkins back because of a few build hosts, send us the list. For each
host, we tell you which group it falls in and what the supported way forward is: a native
Java 21 agent, a container, or a bridge, and what moving it involves. If every host you have
can run a normal agent, that is what we will tell you.

The assessment is free, and you get the answer in writing.
[Request an assessment →](/jenkins-assessment/)

---

*keelinfra helps teams keep self-hosted infrastructure on supported, patched versions when
their environment makes upgrading hard. Questions or corrections: hello@keelinfra.io.*

*Jenkins is a trademark of LF Charities Inc. keelinfra is an independent project, not
affiliated with or endorsed by the Jenkins project.*
