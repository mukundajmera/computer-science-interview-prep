# 🗂️ Site Backlog

> **Purpose:** Ordered work items that turn the plan in [`SITE-HOSTING-DECISION.md`](SITE-HOSTING-DECISION.md) into small, separately reviewable changes to `apps/portal/`.
> **Rule:** run the items in order. Items 4 to 6 each add a dependency and change the Markdown pipeline or `package.json`, so running them in parallel causes merge conflicts.

## Status

| ID | Item | Needs decision | Depends on | Status |
|----|------|----------------|------------|--------|
| SITE-01 | Deploy readiness: test the root-path build, fix stale workflow text, owner runbook, link check and size budget | D2 to go live | none | ✅ |
| SITE-02 | Theme: design tokens, class-based dark mode, toggle, no theme flash; fixes the white-body dark-text bug | none | SITE-01 | 🔜 |
| SITE-03 | Reading layout: line length, type scale, on-page contents, heading anchors, previous/next | none | SITE-02 | 🔜 |
| SITE-04 | Build-time syntax highlighting (leaves `mermaid` blocks untouched) | D3 | SITE-02 | 🔜 |
| SITE-05 | Mermaid rendering in pages (lazy, themed, source fallback) | D3 | SITE-02, SITE-04 | 🔜 |
| SITE-06 | Full-text search with Pagefind and a Ctrl/Cmd+K dialog | D3 | SITE-02 | 🔜 |
| SITE-07 | Mobile pass at 360, 390 and 768 px | none | SITE-03 | 🔜 |
| SITE-08 | Progress export/import and section percentages | none | none | 🔜 |
| SITE-09 | SEO and sharing: sitemap, robots, page metadata, 404 | needs site URL (D1 or the Pages URL) | SITE-01 | 🔜 |
| SITE-10 | Re-baseline the size budget after the features land; drop the embedded search list | none | SITE-01 to SITE-09 | 🔜 |
| SITE-11 | Login runbook for a separate private site (no workflow in this repository) | D1, D4, D6 | SITE-01 | 🔜 |
| SITE-12 | Progress sync behind login (deferred, backend needed) | D4 | SITE-08, SITE-11 | ⏸️ deferred |

Status markers: ✅ complete, 🔜 not started, ⏸️ deferred until a decision is made.

## Definitions of done (shared)

- `npm --prefix apps/portal run test`, `run lint`, `GITHUB_PAGES=true npm --prefix apps/portal run build` and `run check:export` all pass.
- `python3 scripts/check_markdown_links.py` and `python3 scripts/check_content_inventory.py` pass when Markdown changed.
- `apps/portal/AGENTS.md` and `resources/CONTENT-UI-MAP.md` updated if a route, section or content rule changed.
- No curriculum content is copied into the portal; it still reads the Markdown at build time.
- New dependencies are limited to those named in the item.

## Items

### SITE-01 Deploy readiness
- The base path is already configurable through `GITHUB_PAGES_BASE_PATH` (an empty string builds for a domain root; `check:export` and the static server read the same variable). Add tests for the empty value and document it. Do not add a new variable.
- Replace the "private repo" wording in `.github/workflows/portal-pages.yml` with current text. Do not change when the deploy job runs.
- Add `apps/portal/docs/DEPLOY.md`: the owner steps to enable GitHub Pages (repository variable `ENABLE_GITHUB_PAGES_DEPLOYMENT`, Pages source set to GitHub Actions), how to set the custom domain in Settings > Pages and enforce HTTPS (a CNAME file is ignored with a custom Actions deploy), and how to roll back.
- Record the baseline: page count, `out/` size, and the largest JavaScript bundle, in `DEPLOY.md`.
- Add the built-site gates now so every later item is checked: every internal link and asset in `out/` resolves, and a per-route JavaScript size budget (baseline plus 15 percent). The accessibility contract tests already run through `npm run test`.

### SITE-02 Theme
- Move colors into CSS variables, set Tailwind `darkMode: "class"`, add a light / dark / system toggle, save the choice in `localStorage` (wrapped for failure), and set the class before first paint.
- Make layout, nav, search, cards and prose follow the tokens. The start and learning-path pages use `dark:` classes that are broken today (light text on the forced white body); check them in both themes and fix.
- Test: contrast pairs meet WCAG AA for body text and links in both themes.

### SITE-03 Reading layout
- Prose column of 65 to 75 characters, 17 to 18 px body, 1.65+ line height.
- On-page contents with current-section highlight, heading anchor links, previous/next links inside a section.
- Wide tables scroll inside their own box.

### SITE-04 Syntax highlighting
- Add a build-time highlighter (recommended: `rehype-pretty-code` with `shiki`) to the Markdown pipeline. Languages: Java, Python, SQL, JSON, shell, YAML, TypeScript.
- Update the sanitize schema so highlighted markup survives. Light and dark themes follow SITE-02.
- Skip the `mermaid` language: leave `<code class="language-mermaid">` untouched so SITE-05 can find the source. Add a test.

### SITE-05 Mermaid rendering
- Render fenced `mermaid` blocks in the browser, loading Mermaid only on pages that contain one. Strict security level, theme follows SITE-02, source shown if rendering fails.
- Pages that link a `.mmd` file keep the link.
- Test with fixtures for flowchart, sequence and a deliberately broken diagram.

### SITE-06 Full-text search
- Run Pagefind over the exported site as a build step; add it to the Pages workflow and make `check:export` accept the generated index folder.
- Run Pagefind as a `postbuild` step in `package.json` so both workflows that build the portal get it.
- The client loads the index from the base path (`<basePath>/pagefind/`) with an import webpack leaves alone; test under the default base path and at the root.
- Mark the article with `data-pagefind-body` so nav and footer text is not indexed.
- Ctrl/Cmd+K dialog with snippets and keyboard navigation. Keep the title search only as a fallback loaded when the index is missing (for example in `next dev`), so its route list is no longer embedded in every page.

### SITE-07 Mobile pass
- Fix horizontal overflow, tap targets under 44 px, and nav/contents reachability at 360, 390 and 768 px. Add a contract test next to the existing accessibility contract test.

### SITE-08 Progress export/import
- Export and import the progress JSON as a file, validated against the versioned schema. Show percent complete on section cards. Still `localStorage` only.

### SITE-09 SEO and sharing
- `sitemap.xml`, `robots.txt`, per-page title, description, canonical URL and social tags, and a `404` page. Site URL comes from one config value.

### SITE-10 Re-baseline the budget
- After SITE-02 to SITE-09, measure again, set the final per-route budget, and confirm the embedded search list is gone. The link check and first budget come from SITE-01.

### SITE-11 Login runbook for a separate private site
- No deploy workflow is added to this public repository: anything it deployed would be public content. The private site's workflow lives in the private repository.
- Add `apps/portal/docs/AUTH-RUNBOOK.md`: owner steps for DNS on Cloudflare, attaching a custom domain, creating the Access application, enabling one-time PIN, writing the allow rule, and testing from a private window. State plainly that the public repository content is already public and that the private site must be built from a separate private repository.
- No account changes are made by the item itself; only this document is added.

### SITE-12 Progress sync behind login (deferred)
- Only start after D4 is decided and progress export/import has proven insufficient.
