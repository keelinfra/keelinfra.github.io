#!/usr/bin/env python3
"""Fetch the last nights of keelinfra/keycloak's scheduled upgrade drills
into data/ci-results.json, which the evidence page renders at build time.

The deploy workflow runs this daily before `zola build`. If GitHub cannot be
reached the committed file is left as it is, so the site still builds and
shows the date of the snapshot it has.

Usage: scripts/fetch_ci.py [--nights 7]
Env:   GITHUB_TOKEN (optional; raises the API rate limit)
"""
import json, os, re, sys, urllib.request
from datetime import datetime, timezone

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, "data", "ci-results.json")
REPO = "keelinfra/keycloak"
WORKFLOWS = [
    ("ha-matrix.yml", "3 nodes, load balancer probed every second, then every drill"),
    ("upgrade-matrix.yml", "single node: install, log in, upgrade, the session must refresh"),
]
PATH_JOB = re.compile(r"^(?P<from>\S+) → (?P<to>\S+) \((?P<strategy>[^)]+)\)$")


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def workflow(file, what, nights):
    runs = get(f"https://api.github.com/repos/{REPO}/actions/workflows/{file}/runs"
               f"?event=schedule&status=completed&per_page={nights}")["workflow_runs"]
    runs = list(reversed(runs))  # oldest first, so the table reads left to right
    paths = {}
    for i, run in enumerate(runs):
        jobs = get(f"https://api.github.com/repos/{REPO}/actions/runs/{run['id']}/jobs?per_page=100")["jobs"]
        for job in jobs:
            m = PATH_JOB.match(job["name"])
            if not m:
                continue
            row = paths.setdefault(job["name"], {**m.groupdict(), "results": [None] * len(runs)})
            minutes = None
            if job.get("started_at") and job.get("completed_at"):
                t0 = datetime.fromisoformat(job["started_at"].replace("Z", "+00:00"))
                t1 = datetime.fromisoformat(job["completed_at"].replace("Z", "+00:00"))
                minutes = round((t1 - t0).total_seconds() / 60)
            row["results"][i] = {"ok": job["conclusion"] == "success",
                                 "conclusion": job["conclusion"],
                                 "minutes": minutes, "url": job["html_url"]}
    version = lambda v: [int(x) if x.isdigit() else x for x in re.split(r"[.-]", v)]
    rows = sorted(paths.values(), key=lambda p: (version(p["to"]), version(p["from"])), reverse=True)
    return {
        "file": file,
        "what": what,
        "url": f"https://github.com/{REPO}/actions/workflows/{file}",
        "nights": [{"date": r["run_started_at"][:10], "label": r["run_started_at"][5:10],
                    "url": r["html_url"],
                    "ok": r["conclusion"] == "success"} for r in runs],
        "paths": rows,
    }


def main():
    nights = int(sys.argv[sys.argv.index("--nights") + 1]) if "--nights" in sys.argv else 7
    try:
        data = {"generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "workflows": [workflow(f, what, nights) for f, what in WORKFLOWS]}
    except Exception as e:  # network, rate limit, API change: keep the snapshot
        print(f"fetch_ci: {e}; keeping {os.path.relpath(OUT, SITE)}", file=sys.stderr)
        return 0
    with open(OUT, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
    total = sum(len(w["paths"]) for w in data["workflows"])
    print(f"fetch_ci: {total} upgrade paths over {nights} nights → {os.path.relpath(OUT, SITE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
