# Deploying the portal to GitHub Pages

Owner runbook for turning the Pages site on, pointing a custom domain at it, and rolling back. The workflow is `.github/workflows/portal-pages.yml`; it builds and tests on every push and pull request, and only publishes after the opt-in below.

## 1. Turn the deploy on

1. In the repository, go to **Settings > Pages** and set **Source** to **GitHub Actions**.
2. Go to **Settings > Secrets and variables > Actions > Variables** and create a repository variable named `ENABLE_GITHUB_PAGES_DEPLOYMENT` with the value `true`.
3. Push to `main` (or run the workflow manually from the Actions tab). The `deploy` job runs only when the variable is `true` and the event is a push to `main` or a manual run from `main`.

While the variable is unset or anything other than `true`, the workflow still builds and runs `check:export` on every event, so pull requests stay gated without publishing anything.

## 2. Base path

The site builds for `https://<owner>.github.io/computer-science-interview-prep/` by default. The base path comes from the `GITHUB_PAGES_BASE_PATH` environment variable:

- Unset: `/computer-science-interview-prep` (the repository name).
- Empty string (`GITHUB_PAGES_BASE_PATH=""`): builds for a domain root, which is what a custom domain needs.
- Any other value: normalized and used as-is, for example `/custom-portal/`.

The build, the export check and the static preview server all read the same variable, so one setting keeps them consistent. There is no second variable to set.

## 3. Custom domain and HTTPS

1. Buy or pick the domain, then in **Settings > Pages** enter it under **Custom domain** and save. Because the deploy uses a custom Actions workflow, a `CNAME` file in the repository is ignored; the domain must be set in the Pages settings, not committed.
2. Point the domain's DNS at GitHub (the Pages settings page shows the records to create) and wait for the DNS check to pass.
3. Once the DNS check passes, tick **Enforce HTTPS** on the same page.
4. Build with an empty base path so the exported URLs are root-relative: `GITHUB_PAGES_BASE_PATH="" GITHUB_PAGES=true npm --prefix apps/portal run build`. Set the variable in the workflow or the build environment the same way before switching the domain over.

## 4. What the export check gates

`npm --prefix apps/portal run check:export` runs after every build, locally and in the workflow. It fails the build when:

- a representative page, manifest route or reveal/quiz pair is missing from `out/`;
- any internal `href` or `src` in any exported page does not resolve to a file in `out/`;
- a root-relative link would break under the Pages base path;
- any route's total referenced JavaScript exceeds the per-route budget.

## 5. Size budget

Each exported page's referenced `_next` JavaScript chunks are summed, and the route fails when its total exceeds **530,000 bytes**. The budget is the measured worst route on the 2026-11-28 baseline build plus 15 percent headroom, rounded up to the next 1,000 bytes: 460,186 bytes (`progress/index.html`, the heaviest of 777 routes) times 1.15 is 529,214, so 530,000. SITE-10 re-baselines this number after the theme, reading-layout and search work lands, so treat 530,000 as a tripwire against regressions, not a target.

## 6. Baseline (2026-11-28)

Measured from a real build on this machine:

```
GITHUB_PAGES=true npm --prefix apps/portal run build
find apps/portal/out -name index.html | wc -l
du -sb apps/portal/out
find apps/portal/out/_next -name '*.js' -exec du -b {} + | sort -rn | head -1
```

| Metric | Value |
|---|---|
| Exported pages (`index.html` files in `out/`) | 777 |
| Total `out/` size | 328,669,470 bytes (317 MB) |
| Largest single JavaScript chunk | 172,834 bytes (`_next/static/chunks/fd9d1056-0513bfa1d30c24ee.js`) |
| Heaviest per-route JavaScript total | 460,186 bytes (`progress/index.html`) |

Both base-path modes were verified from this checkout: the default build and `GITHUB_PAGES_BASE_PATH=""` each build cleanly and pass `check:export`.

## 7. Rollback

- **Turn the site off:** set `ENABLE_GITHUB_PAGES_DEPLOYMENT` to anything other than `true` (or delete the variable). No deploy job runs after that; the last published site stays up but stops updating. To unpublish entirely, use **Settings > Pages > unpublish** (GitHub shows this option for a live site).
- **Revert a bad publish:** revert the offending commit on `main` and push. The workflow rebuilds and redeploys the previous good state. If the bad deploy must come down faster than a revert, unpublish from Pages settings first, then revert and republish.
- **Custom domain rollback:** remove the domain in **Settings > Pages**, then rebuild with the default base path (unset `GITHUB_PAGES_BASE_PATH`) so links point back under `/computer-science-interview-prep/`.
