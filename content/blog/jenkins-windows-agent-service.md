+++
title = "Running a Jenkins agent as a Windows service: five things that break"
date = 2026-10-17
description = "A Windows agent installed as a service with WinSW works on day one and fails months later: a stale agent.jar, a service that gives up after a reboot, the wrong account, a secret in plain text, and UI tests that cannot see a desktop. What causes each one, and a WinSW config that avoids them."
+++

Most Windows build agents end up the same way. Someone downloads `agent.jar`, copies the launch
command from the node page, wraps it in [WinSW](https://github.com/winsw/winsw) so it runs as a
service, and it works. Months later the agent is offline, nobody remembers how it was set up,
and the fix is a remote desktop session and a guess.

The Jenkins documentation covers installing the controller on Windows, not running an agent as
a service, so most setups are copied from a blog post or a colleague's folder. WinSW is still the
usual tool. It has had no stable release since v2.12.0 and no active maintainer, but it is not
deprecated and still works
([community.jenkins.io thread](https://community.jenkins.io/t/winsw-deprecated-any-alternatives/27244)).

These are the five failures that come up most often, and one config that avoids all of them.

## 1. The agent.jar on disk is older than the controller

`agent.jar` is downloaded once and then left alone. The controller is upgraded every few months.
Jenkins refuses agents whose remoting version is below a minimum it raises over time. Our own CI
saw Jenkins 2.586 refuse a remoting build made for Jenkins 2.462.3, about two years older, with
`Agent version 3256.3258.v858f3c9a_f69d or newer is required`. A jar that was copied in 2022 and
committed to a setup repository is far below that.

The fix is not to keep a copy at all. The controller serves the matching jar at
`/jnlpJars/agent.jar`, and WinSW can download it every time the service starts (see the config
below). Each restart then picks up the controller's current version.

## 2. The service does not come back after a reboot

The service is set to start automatically, but after patch night it is stopped. Windows started
it before the network was ready, the agent could not reach the controller, the process exited,
and the service stayed down. A common workaround is a batch file in the Startup folder that
restarts the service at logon. That only runs when someone logs on, which on a build server is
rarely.

Two WinSW settings fix it: `<delayedAutoStart/>` starts the service after the boot rush, and
`<onfailure action="restart" delay="..."/>` makes Windows restart it when it exits. Repeat the
`onfailure` line for successive failures. The last one is used for every failure after that, so
the service keeps retrying until the controller is reachable.

## 3. The service runs as LocalSystem

Without a `<serviceaccount>` element the service runs as LocalSystem. Builds then run with full
rights on the machine but without the build user's profile: no mapped network drives, no user
certificate store, and a different Git and SSH configuration from the one you tested with by
hand. Some of that "works on my login, fails in Jenkins" debugging comes down to this.

Run the service as a dedicated local or domain account without administrator rights. Give it
"Log on as a service" (`<allowservicelogon>true</allowservicelogon>` does that) and write access
to the agent folder only. A group managed service account (user name ending in `$`, no
password) avoids storing a password at all.

## 4. The secret sits in the XML file

The launch command on the node page includes the agent secret, and it usually gets pasted
straight into `<arguments>`. The XML file then holds a credential that lets anyone connect as
that agent, and it tends to get copied around: into a share, a wiki page, a Git repository.

`agent.jar` reads the secret from a file when the value starts with `@`, so `-secret @secret.txt`
keeps it out of the XML. Restrict that file to the service account.

## 5. UI tests cannot see a desktop

Services run in session 0, which has no interactive desktop. A build that drives a browser in
headed mode, takes screenshots, or automates a desktop application will hang or fail when the
agent runs as a service, even though the same job passed when the agent ran in a console
window.

For those jobs, run the agent in the logged-on user's session instead of as a service (for
example a scheduled task at logon with auto-logon enabled), or switch the tests to headless
mode where the tool supports it. Keep the service for everything else.

## A WinSW config that avoids all five

Put WinSW's executable in the agent folder as `jenkins-agent.exe` and save this next to it as
`jenkins-agent.xml`. Replace the controller URL, node name, Java path and account. Turn on
WebSocket for the node in Jenkins, so the agent needs no extra TCP port.

```xml
<service>
  <id>jenkins-agent</id>
  <name>Jenkins agent</name>
  <description>Jenkins inbound agent</description>

  <!-- 1. fetch the controller's own agent.jar on every start -->
  <download from="https://jenkins.example.com/jnlpJars/agent.jar"
            to="%BASE%\agent.jar" failOnError="true" />

  <executable>C:\Java\jdk-21\bin\java.exe</executable>
  <!-- 4. the secret comes from a file, not from this XML -->
  <arguments>-jar "%BASE%\agent.jar" -url https://jenkins.example.com/ -name win-build-01 -secret @"%BASE%\secret.txt" -webSocket -workDir "%BASE%"</arguments>

  <!-- 2. start after the boot rush, and keep retrying -->
  <delayedAutoStart/>
  <onfailure action="restart" delay="10 sec" />
  <onfailure action="restart" delay="1 min" />
  <resetfailure>1 hour</resetfailure>

  <!-- 3. a dedicated account, not LocalSystem -->
  <serviceaccount>
    <domain>EXAMPLE</domain>
    <user>svc-jenkins-agent</user>
    <password>change-me</password>
    <allowservicelogon>true</allowservicelogon>
  </serviceaccount>

  <log mode="roll" />
</service>
```

Then, from an elevated prompt in the agent folder:

```bat
jenkins-agent.exe install
jenkins-agent.exe start
jenkins-agent.exe status
```

Because `failOnError` is true, a controller that is down at boot makes the service exit, and
`onfailure` brings it back a minute later, so the agent reconnects on its own once the controller
is up. The element names follow the
[WinSW 2.12 configuration reference](https://github.com/winsw/winsw/blob/v2.12.0/doc/xmlConfigFile.md),
and the `agent.jar` options were checked against remoting 3386 (`-url`, `-name`, `-webSocket` and
`-secret @file`). Use a recent Java build as well: a JDK unzipped once in 2022 has missed years of
security updates.

## Many Windows agents, or old ones?

If you run more than a handful of Windows agents, the next step is configuration management
(Ansible's `win_` modules, DSC, or your existing tooling) that writes this XML and the secret
file, so no agent is set up by hand.

If some of your build hosts are not Windows but AIX, Solaris, HP-UX or old Linux that cannot run
Java 21, the agent is a harder problem. That is what
[Agent8](https://github.com/keelinfra/agent8) is for, and we can help you sort out which hosts
need what.
[Tell us about your build hosts →](/jenkins-assessment/)

---

*keelinfra helps teams keep self-hosted infrastructure on supported, patched versions when
their environment makes upgrading hard. Questions or corrections: hello@keelinfra.io.*

*Jenkins is a trademark of LF Charities Inc. keelinfra is an independent project, not
affiliated with or endorsed by the Jenkins project.*
