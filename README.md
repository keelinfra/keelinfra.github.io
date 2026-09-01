# keelinfra.github.io

Source for [keelinfra.io](https://keelinfra.io) — built with [Zola](https://www.getzola.org/).

```bash
zola build   # -> public/
zola serve   # local preview at localhost:1111
```

`content/docs/keycloak/` is synced from [keelinfra/keycloak](https://github.com/keelinfra/keycloak)
by `scripts/sync_docs.py`. Don't hand-edit those files — CI checks for drift on every
build; the fix always lands in the product repo, never here.

Deploys automatically on push to `main` via GitHub Actions → GitHub Pages.
