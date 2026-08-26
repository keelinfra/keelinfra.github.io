#!/usr/bin/env python3
"""Post-build checks for the built site in public/.

1. Internal links: every href/src starting with "/" resolves to a built file.
2. Fragments: every internal link with #fragment points at an existing id.
3. Inbound contract: every URL in tests/inbound-urls.txt exists (paths other
   repos, READMEs and mailtos depend on — breaking one breaks links in the wild).
4. External budget: no external stylesheets/scripts/fonts anywhere. External
   images are allowed only from github.com (live CI badges are evidence).

Usage: scripts/check_site.py [public_dir]
"""
import os, re, sys
from html.parser import HTMLParser

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SITE, "public")
CONTRACT = os.path.join(SITE, "tests", "inbound-urls.txt")
OWN_HOSTS = ("https://keelinfra.io", "http://keelinfra.io")
IMG_ALLOWED_EXTERNAL = ("https://github.com/",)


class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []      # (attr, value)
        self.external = []   # (tag, url)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        for attr in ("href", "src"):
            v = a.get(attr)
            if not v:
                continue
            if v.startswith(("mailto:", "data:", "#")):
                if v.startswith("#"):
                    self.links.append(("#self", v))
                continue
            if v.startswith(OWN_HOSTS):
                for h in OWN_HOSTS:
                    if v.startswith(h):
                        v = v[len(h):] or "/"
                        break
            if v.startswith("http://") or v.startswith("https://"):
                if tag in ("link", "script"):
                    self.external.append((tag, v))
                elif tag == "img" and not v.startswith(IMG_ALLOWED_EXTERNAL):
                    self.external.append((tag, v))
                continue
            self.links.append((tag, v))


def path_to_file(path):
    path = path.split("?")[0]
    if path.endswith("/"):
        return os.path.join(PUBLIC, path.lstrip("/"), "index.html")
    p = os.path.join(PUBLIC, path.lstrip("/"))
    if os.path.isdir(p):
        return os.path.join(p, "index.html")
    return p


def main():
    pages = {}
    for root, _, files in os.walk(PUBLIC):
        for f in files:
            if f.endswith(".html"):
                full = os.path.join(root, f)
                s = Scan()
                with open(full, encoding="utf-8") as fh:
                    s.feed(fh.read())
                pages[full] = s

    errors = []

    for full, s in pages.items():
        rel = os.path.relpath(full, PUBLIC)
        for tag, url in s.external:
            errors.append(f"{rel}: external {tag} request: {url}")
        for tag, link in s.links:
            frag = None
            target = link
            if "#" in link:
                target, frag = link.split("#", 1)
            if tag == "#self" or target == "":
                if frag and frag not in s.ids:
                    errors.append(f"{rel}: missing local anchor #{frag}")
                continue
            if not target.startswith("/"):
                errors.append(f"{rel}: non-root-relative internal link: {link}")
                continue
            tf = path_to_file(target)
            if not os.path.isfile(tf):
                errors.append(f"{rel}: broken internal link: {link}")
                continue
            if frag:
                tscan = pages.get(tf)
                if tscan and frag not in tscan.ids:
                    errors.append(f"{rel}: link {link} — no id '{frag}' in target")

    with open(CONTRACT, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            target, frag = (line.split("#", 1) + [None])[:2] if "#" in line else (line, None)
            tf = path_to_file(target or "/")
            if not os.path.isfile(tf):
                errors.append(f"CONTRACT: {line} — file missing ({os.path.relpath(tf, PUBLIC)})")
            elif frag:
                s = pages.get(tf)
                if s is None or frag not in s.ids:
                    errors.append(f"CONTRACT: {line} — id '{frag}' missing")

    if errors:
        print(f"check_site: {len(errors)} problem(s)")
        for e in sorted(errors):
            print("  -", e)
        sys.exit(1)
    print(f"check_site: OK ({len(pages)} pages, contract intact, no external requests)")


if __name__ == "__main__":
    main()
