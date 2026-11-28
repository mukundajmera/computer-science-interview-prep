# 🌐 Site, Hosting and Login: Decision Doc

> **Purpose:** Decide how the learning portal in `apps/portal/` should look, where it should be hosted, and how any part of it can sit behind a login. This is a plan, not a rebuild. Checked on 2026-11-28; pricing and limits change, so re-check before paying for anything.
> **Tasks that follow from this doc:** [`SITE-BACKLOG.md`](SITE-BACKLOG.md).

---

## 🎯 Recommendation in five lines

1. **Host the public site on GitHub Pages now.** It is free for public repositories and the workflow already exists; it only needs switching on (decision D2).
2. **Fix the reading experience before spending on hosting.** The biggest gaps are Mermaid diagrams that show as raw code on many pages, no dark theme for the main layout, and title-only search.
3. **Keep the curriculum public.** The repository is public, so a login would not protect its content. It would only hurt reach and search ranking.
4. **If you want a login area, use Cloudflare Access in front of a second hostname.** It is free up to 50 users and needs no code in the portal. Put only content that is not in this repository there.
5. **Do not put paid or third-party licensed material on any host**, public or protected. Hosting it behind a login is still distributing it.

---

## 1. What exists today (from the code)

| Area | Current state | Evidence |
|---|---|---|
| Build | Next.js 14 static export, trailing slashes, GitHub Pages base path `/computer-science-interview-prep` | `apps/portal/next.config.mjs`, `site-config.mjs` |
| CI | `Portal Pages` builds, tests, lints, exports and checks the export on pull requests, pushes to `main` and manual runs. Deploy to Pages runs only when the repository variable `ENABLE_GITHUB_PAGES_DEPLOYMENT` is `true` | `.github/workflows/portal-pages.yml` |
| Stale text | The workflow comment still says the repository is private | same file |
| Search | A substring match over route titles, sections and descriptions, 8 results. It does not search page text. The whole route list is built in the root layout and passed to the client, so it is embedded in every exported page | `src/content/search-index.ts`, `SearchBox.tsx` |
| Mermaid | Not rendered. About 284 Markdown files contain a `mermaid` fenced block, and the portal has no Mermaid handling, so readers see source text | grep of the repo and of `apps/portal/src` |
| Code blocks | No syntax highlighting | no highlighter in `package.json` |
| Dark mode | Tailwind has no `darkMode` setting (so it follows the device), and `globals.css` forces a white body. `dark:` classes appear only in the start and learning-path pages, so on a device in dark mode those pages can show light text on a white background. The layout, nav and prose have no dark styles and there is no toggle | grep of `src` |
| Mobile | A `MobileNav` component exists. Not audited for tables, code overflow or tap size | `src/components/layout/` |
| Progress | Per-browser `localStorage`, with a versioned schema. No export, no sync | `src/lib/progress-schema.ts` |
| SEO | A root title and description, plus their own metadata on four static pages (start, start-here, learning paths, flashcards). Content pages inherit the root title. No sitemap, robots file or 404 page found | `src/app/layout.tsx` |
| Learning aids | Start-here, learning paths, level assessment, quizzes, flashcards, interview mode, resources: already present | `src/app/` |

Not measured here: built site size, page count, Lighthouse scores. The first backlog tasks capture those numbers.

---

## 2. What the site should look like

Design goal: a calm reading site first, a tool second. Keep what exists; close the gaps below in this order of reader impact.

### 2.1 Reading (highest impact)
- **Content width and type:** 65 to 75 characters per line, 17 to 18 px body text, 1.65+ line height, clear heading scale, wide tables scroll inside their own box.
- **On-page table of contents** with highlight of the current section on long pages, plus heading anchors that can be linked.
- **Previous / next** links inside a section, so a reader can move through a topic without going back to an index.
- **Code blocks:** build-time syntax highlighting for Java, Python, SQL, JSON and shell; light and dark themes; horizontal scroll, never page overflow.
- **Mermaid diagrams rendered in the page**, loaded only on pages that contain one, themed for light and dark, with the source shown if rendering fails.

### 2.2 Navigation and search
- **Full-text search** across all pages, opened with Ctrl/Cmd+K, results show a snippet. Recommended library: Pagefind, a static search index built after the site export, with no server (verified on its home page). Keep the current title search as fallback.
- Keep the existing section nav, breadcrumbs, learning paths and start-here page. Add "continue where you left off".

### 2.3 Dark mode and mobile
- Light, dark and "follow system" with a toggle, saved per browser, no flash of the wrong theme on load. Use design tokens (CSS variables) so every component follows.
- Mobile checks at 360, 390 and 768 px: no sideways page scroll, 44 px tap targets, nav and contents reachable with one thumb.

### 2.4 Progress tracking
- Keep `localStorage` (no accounts, no privacy cost). Add **export and import as a JSON file** so a reader can move devices, and show percent complete on section cards.
- Syncing across devices would need a login and a small backend. Deferred; see 4.4.

### 2.5 Sharing and discovery
- Sitemap, robots file, per-page title, description, canonical URL and social preview tags, a proper 404 page. These matter more once a custom domain exists.

### 2.6 Quality gates
- CI checks on the built site: internal links resolve, a size budget per page, accessibility contract tests (a test file for this already exists).

---

## 3. Hosting options (static site)

All options host the same `apps/portal/out` folder. Prices and limits below were read from the vendors' pages on 2026-11-28 unless marked unverified.

| Option | Cost | Custom domain | Deploy from GitHub | Notes |
|---|---|---|---|---|
| **GitHub Pages** | $0 for public repositories. Soft limits: 1 GB site, 100 GB/month bandwidth, 10 builds/hour (the build limit does not apply to a custom Actions workflow) | Yes (domain cost separate, unverified) | Already wired through Actions | Not meant for a commercial business site. **No login.** Private publishing needs an organization account on GitHub Enterprise Cloud, which is not realistic here |
| **Cloudflare Pages** | $0 on the free plan: 500 builds/month, 20,000 files, 25 MiB per file, 100 custom domains. Static asset requests are free and unlimited | Yes. For login protection the DNS must be on Cloudflare | Git integration or an Actions workflow | Pairs with Cloudflare Access for login. Whether Cloudflare now steers new projects to Workers static assets was **not verified**: check the dashboard before creating the project |
| **Vercel** | Hobby is $0 but the terms say Hobby is for personal or non-commercial use. 100 GB fast data transfer | Yes | Native GitHub app | "Vercel Authentication" is included on Hobby (verified). Password protection is $20/month per project on Pro, not on Hobby. Who can pass Vercel Authentication on Hobby was **not verified** |
| **Hostinger shared hosting** | The Premium plan showed $1.99/month as a promo and $10.99/month on renewal. Plan term not checked | Yes, free domain for the first year on that plan | Not confirmed on the page I read | Costs money for something the free options do well. Only worth it if you already pay for it. Login there would be basic auth set by file, which was **not verified** |

**Recommendation:** the public site stays on GitHub Pages (zero cost, zero new accounts, already built) and needs no login. A login area is a *second, separate site* built from private material (section 4), not a move of the public one. Cloudflare Pages is only the host for that second site.

**Custom domain:** worth having once the site is stable (shorter link, survives a host change). It also removes the repository name from the URL. The base path is already configurable (`GITHUB_PAGES_BASE_PATH`, empty string for a domain root); task SITE-01 documents and tests that. The custom domain itself is set in repository Settings > Pages, because the deploy uses a custom Actions workflow. Domain price is unverified; a typical `.dev` or `.com` is roughly ten to twenty dollars a year, which you should confirm at purchase.

---

## 4. Login-protected hosting

### 4.1 Start from the real constraint
The repository is public. Everything committed to it is already readable by anyone, so putting the same pages behind a login protects nothing and costs readers and search traffic. Login only makes sense for **material that is not in this repository**, or for features that need an identity.

### 4.2 What stays public, what can sit behind login

| Stays public (in this repo and on the public site) | Can sit behind login (kept outside this repo) |
|---|---|
| All curriculum, code, quizzes, flashcards, diagrams | Your own private notes and mock-interview logs |
| Study plans, templates, cheatsheets | Personal progress sync (later) |
| Anything original that you are happy to share | Drafts you are not ready to publish |
| **Never anywhere:** paid course files, copied question lists, third-party licensed material, secrets | |

Anything committed here, even briefly, is public permanently, so private material lives in a separate private repository and is built into a separate site. The public build must never read from it. The deploy workflow for that private site lives in the private repository, not here.

### 4.3 Options for the login

| Option | Cost | Effort | Fit |
|---|---|---|---|
| **A. Cloudflare Access in front of a second hostname (recommended)** | Free for up to 50 users, then $7 per user per month pay-as-you-go | Low: DNS on Cloudflare, one Access application, an allow rule for your email | Works for any static host, no code in the portal. Login by one-time PIN sent to allowed emails, or by an identity provider you connect. A one-time PIN is no longer added automatically, so you enable it once |
| B. Vercel Authentication | Included on Hobby | Low | Ties access to Vercel accounts and is limited by the Hobby terms. Fine for a private preview, awkward for sharing |
| C. Host-level basic auth (shared hosting) | Hosting fee | Low | One shared password, no per-person revoke. Unverified for this host |
| D. GitHub Pages private | Needs Enterprise Cloud organization | High | Not realistic |
| E. Build login into the app | Your time | High | A backend, sessions and an attack surface for a study site. **Not recommended** |

**Pick A.** Two limits to plan for, both verified in Cloudflare's docs: Access protects a public hostname only when the DNS is on Cloudflare, and protecting preview deployments does **not** cover the production `*.pages.dev` address or a custom domain, so the production hostname must be a custom domain you attach the Access application to.

### 4.4 Optional later: progress sync
With option A, Access can identify the signed-in email, and a small Worker plus a key-value store could save progress per person. This adds a backend and a privacy duty, so it is deferred until progress export/import proves insufficient.

---

## 5. Decisions needed from the owner

| # | Decision | Recommended |
|---|---|---|
| D1 | Buy a custom domain? Budget and name | Yes, after the reading fixes ship. Confirm price at purchase |
| D2 | Switch on GitHub Pages (set the repository variable and choose "GitHub Actions" as the Pages source) | Yes, now |
| D3 | Allow four new portal packages: `rehype-pretty-code` and `shiki` (highlighting), `mermaid`, `pagefind`. The repository rule requires maintainer approval for new libraries | Yes, for those four only |
| D4 | Do you want a login area at all, and what would go in it? | Not yet. Public site first; add Access only when you have private material |
| D5 | Add visitor analytics? | No analytics by default; revisit if you want reach numbers |
| D6 | Create a Cloudflare account (needed only for D1/D4 path) | Later |

Nothing in this plan changes any hosting account. Account steps are written as owner steps in the runbook task.

---

## 6. Ordered task list

Full list with sizes, dependencies and status: [`SITE-BACKLOG.md`](SITE-BACKLOG.md).

1. Deploy readiness (document and test the root-path build, stale workflow text, owner runbook, link check and size budget)
2. Theme: tokens, dark mode, toggle
3. Reading layout: width, TOC, heading anchors, previous/next
4. Syntax highlighting
5. Mermaid rendering
6. Full-text search
7. Mobile pass
8. Progress export/import and section percentages
9. SEO and sharing files
10. CI quality gates on the built site
11. Login runbook for a separate private site (no workflow in this repository)

---

## 7. Unverified items

- Domain price and renewal.
- Whether Cloudflare recommends Workers static assets over Pages for new projects.
- Who can pass Vercel Authentication on a Hobby plan.
- Hostinger deploy-from-GitHub and login method.
- Built-site size, page count and performance scores (not measured; no build was run for this doc).
- All prices can change; check the vendor page on the day you pay.

## Sources checked on 2026-11-28

- GitHub Pages limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- GitHub plans: https://docs.github.com/en/get-started/learning-about-github/githubs-plans
- Cloudflare Zero Trust plans: https://www.cloudflare.com/plans/zero-trust-services/
- Cloudflare Access web apps: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/
- Cloudflare one-time PIN: https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/
- Cloudflare Pages limits: https://developers.cloudflare.com/pages/platform/limits/
- Cloudflare Pages pricing: https://developers.cloudflare.com/pages/functions/pricing/
- Cloudflare Pages preview deployments: https://developers.cloudflare.com/pages/configuration/preview-deployments/
- Vercel Hobby: https://vercel.com/docs/plans/hobby and terms: https://vercel.com/legal/terms
- Vercel deployment protection pricing: https://vercel.com/docs/deployment-protection/usage-and-pricing
- Hostinger web hosting: https://www.hostinger.com/web-hosting
- Pagefind: https://pagefind.app/
