#!/usr/bin/env python3
"""Sync repo-sourced docs pages from keelinfra/keycloak into content/docs/keycloak/.

Generated pages are pure mirrors of files in the product repo, transformed for the
site (front matter, link rewrites, YAML fencing). Hand-edits to generated files are
rejected by `--check`, which CI runs on every build: the fix always lands in the
product repo, never on the site.

Usage:
  scripts/sync_docs.py [--source DIR] [--check]

Without --source, tries $KEELINFRA_KEYCLOAK_DIR, then ../keycloak relative to the
site repo, then a shallow clone of github.com/keelinfra/keycloak.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(SITE, "content", "docs", "keycloak")
REPO_URL = "https://github.com/keelinfra/keycloak"

# Relative links inside repo markdown → site or GitHub targets.
LINK_MAP = {
    "UPGRADES.md": "/docs/keycloak/upgrades/",
    "SECURITY.md": "/docs/keycloak/security/",
    "LICENSE": f"{REPO_URL}/blob/main/LICENSE",
    "examples/ha-3node.yml": "/docs/keycloak/example-ha-3node/",
    "examples/single-node.yml": "/docs/keycloak/example-single-node/",
    # Directory link with no site page — it resolved to /docs/keycloak/upgrades/lts/.
    "lts/": f"{REPO_URL}/tree/main/lts",
}


def front_matter(title, weight, description, source_path, sha):
    return (
        "+++\n"
        f'title = "{title}"\n'
        f'description = "{description}"\n'
        f"weight = {weight}\n"
        "[extra]\n"
        f'source_repo_path = "{source_path}"\n'
        f'source_sha = "{sha}"\n'
        "+++\n\n"
        f"<!-- GENERATED from keelinfra/keycloak@{sha} ({source_path}) by scripts/sync_docs.py — edit it THERE, not here. -->\n\n"
    )


def rewrite_links(md):
    def repl(m):
        text, target = m.group(1), m.group(2)
        return f"[{text}]({LINK_MAP.get(target, target)})"
    return re.sub(r"\[([^\]]+)\]\(([^)#\s]+)\)", repl, md)


def strip_heading(md):
    """Drop the first H1 (title moves to front matter) and any badge/picture header."""
    md = re.sub(r"<a href[^>]*>\s*<picture>.*?</picture>\s*</a>\s*", "", md, flags=re.S)
    md = re.sub(r"^\[!\[[^\n]*\n?", "", md, flags=re.M)  # badge lines
    md = re.sub(r"^# [^\n]+\n+", "", md.lstrip(), count=1)
    return md.strip() + "\n"


def gen_markdown_page(src_dir, rel, title, weight, description, sha):
    with open(os.path.join(src_dir, rel)) as f:
        body = rewrite_links(strip_heading(f.read()))
    return front_matter(title, weight, description, rel, sha) + body


def gen_example_page(src_dir, rel, title, weight, description, intro, sha):
    with open(os.path.join(src_dir, rel)) as f:
        yml = f.read().rstrip()
    body = f"{intro}\n\n```yaml\n{yml}\n```\n"
    return front_matter(title, weight, description, rel, sha) + body


def generate(src_dir, sha):
    return {
        "upgrades.md": gen_markdown_page(
            src_dir, "UPGRADES.md", "Upgrades", 5,
            "Supported upgrade paths, strategies, and measured service windows — every path is executed end-to-end before it is listed, and re-proven nightly in CI.",
            sha),
        "security.md": gen_markdown_page(
            src_dir, "SECURITY.md", "Security policy", 7,
            "How to report vulnerabilities privately, what is in scope, and how upstream CVEs are handled.",
            sha),
        "example-ha-3node.md": gen_example_page(
            src_dir, "examples/ha-3node.yml", "Example: 3-node HA cluster", 8,
            "The annotated cluster definition for a 3-node HA install.",
            "The complete cluster definition for a production 3-node HA install — this is the only "
            "file you edit. Run `./configure -c examples/ha-3node.yml` against it.",
            sha),
        "example-single-node.md": gen_example_page(
            src_dir, "examples/single-node.yml", "Example: single node", 9,
            "The annotated cluster definition for a single-node install.",
            "The complete cluster definition for a single-node install (no HA — evaluation, dev, or "
            "small internal setups). Run `./configure -c examples/single-node.yml` against it.",
            sha),
    }


def resolve_source(arg):
    if arg:
        return arg, None
    env = os.environ.get("KEELINFRA_KEYCLOAK_DIR")
    if env and os.path.isdir(env):
        return env, None
    sibling = os.path.normpath(os.path.join(SITE, "..", "keycloak"))
    if os.path.isfile(os.path.join(sibling, "UPGRADES.md")):
        return sibling, None
    tmp = tempfile.mkdtemp(prefix="keelinfra-sync-")
    subprocess.run(["git", "clone", "--depth", "1", REPO_URL, tmp],
                   check=True, capture_output=True)
    return tmp, tmp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", help="path to a keelinfra/keycloak checkout")
    ap.add_argument("--check", action="store_true",
                    help="verify committed pages match a fresh generation; exit 1 on drift")
    args = ap.parse_args()

    src_dir, cleanup = resolve_source(args.source)
    try:
        sha = subprocess.run(["git", "-C", src_dir, "rev-parse", "--short", "HEAD"],
                             check=True, capture_output=True, text=True).stdout.strip()
        pages = generate(src_dir, sha)

        if args.check:
            drift = []
            for name, want in pages.items():
                path = os.path.join(DEST, name)
                have = open(path).read() if os.path.isfile(path) else None
                if have is None:
                    drift.append(f"{name}: missing")
                elif have != want:
                    # Same content at a different SHA isn't drift — normalize the stamp.
                    norm = re.sub(r"@[0-9a-f]{7,}", "@SHA", have)
                    normw = re.sub(r"@[0-9a-f]{7,}", "@SHA", want)
                    norm = re.sub(r'source_sha = "[0-9a-f]+"', 'source_sha = "SHA"', norm)
                    normw = re.sub(r'source_sha = "[0-9a-f]+"', 'source_sha = "SHA"', normw)
                    if norm != normw:
                        drift.append(f"{name}: content drift")
            if drift:
                print("DOCS DRIFT — content/docs/keycloak/ does not match keelinfra/keycloak@" + sha)
                for d in drift:
                    print("  -", d)
                print("Fix: run scripts/sync_docs.py (never hand-edit generated pages).")
                sys.exit(1)
            print(f"docs in sync with keelinfra/keycloak@{sha}")
            return

        os.makedirs(DEST, exist_ok=True)
        for name, content in pages.items():
            with open(os.path.join(DEST, name), "w") as f:
                f.write(content)
            print("wrote", os.path.relpath(os.path.join(DEST, name), SITE))
    finally:
        if cleanup:
            shutil.rmtree(cleanup, ignore_errors=True)


if __name__ == "__main__":
    main()
