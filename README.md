# ericvoss.com

A personal home page and a writing feed. Jekyll 4, no theme gem, no
JavaScript; built and deployed by GitHub Actions (`.github/workflows/deploy.yml`).

| Page | Source | URL |
|---|---|---|
| Home | `index.md` (intro), `_layouts/home.html` | `/` |
| Writing | `writing.html`, posts in `_writing/` | `/writing/`, `/writing/<slug>/` |

```sh
make post TITLE="Some title"   # start an unpublished post in _writing/
make serve                     # preview at localhost:4000, drafts included
make check                     # build + html-proofer, what CI runs
```
