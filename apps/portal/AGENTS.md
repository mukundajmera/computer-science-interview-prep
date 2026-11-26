# AGENTS Guidance — apps/portal

## Scope
Applies to the Next.js learning portal under `apps/portal/`.

## Tech Stack
- **Framework:** Next.js 14 (App Router), TypeScript 5, React 18.
- **Styling:** Tailwind CSS 3, `@tailwindcss/typography` for prose rendering.
- **Markdown pipeline:** `unified` → `remark-parse` → `remark-gfm` → `remark-rehype` → `rehype-sanitize` → `rehype-stringify`, with `gray-matter` for frontmatter.
- **No backend:** Content is read from the repository's Markdown files at build time; progress tracking uses browser `localStorage`.

## Directory Layout

```
apps/portal/
├── src/
│   ├── app/              # Next.js App Router routes (one folder per section)
│   │   ├── theory/       # 00-theory
│   │   ├── patterns/     # 01-design-patterns
│   │   ├── lld/          # 02-lld-projects
│   │   ├── hld-concepts/ # 03-hld-concepts
│   │   ├── hld/          # 04-hld-projects
│   │   ├── genai/        # 06-genai-systems
│   │   ├── case-studies/ # case-studies
│   │   ├── progress/     # User progress dashboard
│   │   ├── layout.tsx    # Root layout (nav, footer)
│   │   └── page.tsx      # Home / landing page
│   ├── components/
│   │   ├── layout/       # Navigation bar, sidebar, footer
│   │   ├── content/      # Markdown rendering, topic page layout
│   │   └── progress/     # Progress tracker UI
│   ├── content/
│   │   ├── registry.ts   # Auto-discovery registry (scans content dirs at build time)
│   │   ├── loader.ts     # Build-time Markdown file reader
│   │   └── types.ts      # TypeScript types for content objects
│   └── lib/
│       ├── sections.ts   # Portal section navigation contract
│       └── utils.ts      # Shared utility functions and compatibility exports
├── package.json
├── next.config.mjs
├── tailwind.config.ts
├── tsconfig.json
└── postcss.config.mjs
```

## Content ↔ UI Map
For the full mapping of content directories to portal routes, categories, and
coverage status, see [`resources/CONTENT-UI-MAP.md`](../../resources/CONTENT-UI-MAP.md).
That document also contains extension guidelines for adding new categories and
a mismatch log from the latest coherence audit.

## How the Portal Reads Content
1. `registry.ts` **auto-discovers** topics by scanning content directories at build time using `listDirs()` and `listMarkdownFiles()`.
2. `loader.ts` reads the Markdown file at build time, extracts frontmatter via `gray-matter`, and converts the body to HTML via the `unified` pipeline.
3. Route handlers in `src/app/<section>/` call the loader and pass the result to page components.
4. **No content is duplicated.** The portal is a read-only view over the canonical Markdown in the repo.

## When to Update the Portal

| Content event | Portal action required |
|---------------|----------------------|
| New topic or project added under an existing section | **No action needed** — auto-discovered from the content folder. Optionally update the `DIFFICULTY` map in `registry.ts` if the default difficulty needs adjustment. |
| New quiz added | **No action needed** — place `<topic>-quiz.md` in `quizzes/` and it's auto-discovered. |
| New interview problem added | Add an entry to the `INTERVIEW_PROBLEMS` array in `src/components/interview/interview-data.ts` and add a solution file in `solutions/`. |
| Topic renamed or folder moved within the same section | **No action needed** — auto-discovery picks up the change. Verify the route in `src/app/` and update any internal links that referenced the old path. |
| New top-level section added (e.g., a new numbered folder) | Create a route folder under `src/app/`, add nav entry in `src/lib/sections.ts` `PORTAL_SECTIONS`, and add auto-discovery logic in `registry.ts`. See [Extension Guidelines](../../resources/CONTENT-UI-MAP.md#extension-guidelines). |
| Difficulty metadata changed | Update the `DIFFICULTY` map in `registry.ts` if the portal needs a different difficulty than the default. |
| Content-only edit (text/code inside an existing Markdown file) | **No portal change needed** — content is read at build time |

## Adding a New Route / Section
1. Create `src/app/<section-name>/page.tsx` (and optionally `[slug]/page.tsx` for dynamic routes).
2. Import and call `loader.ts` to fetch content for the section.
3. Add a navigation entry to the `PORTAL_SECTIONS` array in `src/lib/sections.ts`; `src/lib/utils.ts` re-exports it as `SECTIONS` for compatibility.
4. Add route-manifest coverage in `src/content/route-manifest.ts` and auto-discovery logic in `registry.ts` for the new section's content directory (following the pattern used by existing sections).

> For a full step-by-step checklist, see the Extension Guidelines in
> [`resources/CONTENT-UI-MAP.md`](../../resources/CONTENT-UI-MAP.md#extension-guidelines).

## Coding Standards
- Follow existing patterns: use Server Components by default; use `'use client'` only where browser APIs are required (e.g., `localStorage` in progress tracker).
- Keep components small and composable; co-locate styles via Tailwind utility classes.
- No additional npm dependencies without maintainer approval.
- Use TypeScript strict mode; avoid `any` types.

## Validation
```bash
cd apps/portal
npm ci             # Reproducible install from package-lock.json
npm run lint       # ESLint check
npm run build      # GitHub Pages static export build (catches type errors and broken imports)
npm run build:local # Local Next.js production build without GitHub Pages base path
npm run check:export # Validate generated static export routes and reveal pages
npm run dev        # Dev server for manual testing at http://localhost:3000
```

Use Node.js 20.x with the committed `package-lock.json`; CI and GitHub Pages workflows pin Node 20.

### GitHub Pages Deployment Opt-In
- The `Portal Pages` workflow always tests and builds the static export.
- Deployment is disabled by default because the repository may not have Pages enabled (and is currently private).
- **Treat opt-in as public publication.** A private source repository does not make the published Pages site private: it is public by default when the plan supports Pages. Private site visibility is limited to eligible GitHub Enterprise Cloud organizations and must be configured separately; a private source repo also requires an eligible GitHub plan.
- Before enabling deployment, the repository owner must explicitly approve the intended audience, confirm that all exported Markdown/content is safe for that audience, verify plan eligibility and the site's visibility in GitHub settings, and enable GitHub Pages with **GitHub Actions** as the source. Then set repository variable `ENABLE_GITHUB_PAGES_DEPLOYMENT=true` to publish. Leave it unset/false for build-only validation. This variable gates this workflow only; it does not configure or privatize the Pages site.

## Stability Guarantees — What NOT to Touch
- **Route paths** (`/theory`, `/patterns`, `/coding`, `/lld`, `/hld-concepts`, `/hld`, `/genai`, `/case-studies`, `/interview`, `/quizzes`, `/resources`, `/progress`) are stable; do not rename without coordinating with cross-links and bookmarks.
- **`PORTAL_SECTIONS` array** in `src/lib/sections.ts` determines the navigation; adding entries is fine, but removing or reordering requires coordination. `src/lib/utils.ts` keeps the legacy `SECTIONS` export.
- **`route-manifest.ts`** is the public-route contract for search, static export checks, and duplicate-route protection; every new route family must be represented there.
- **`registry.ts` schema** (the shape of content entries) is a contract between content and rendering; schema changes require updating all existing entries.
- **`loader.ts` Markdown pipeline** plugins are deliberately minimal; do not add heavy remark/rehype plugins without verifying build performance.
- **`localStorage` keys** used by the progress tracker must remain backward-compatible so learners don't lose their progress data.

## Progress ID Policy
- Treat registry `id` values and public route slugs as stable persistence keys.
- Keep the `sdp-progress` localStorage key stable; migrate the stored value in place.
- Before any folder/slug/registry ID rename, add an entry to the progress alias map, preserve unknown IDs as legacy progress, and verify migration idempotency with `npm run test`.
- `/progress` must exclude unmapped legacy IDs from completion counts while still surfacing them for manual cleanup or future alias recovery.

## Gotchas
- The portal's `next.config.mjs` may reference paths outside `apps/portal/` to read repo Markdown; do not move or rename top-level content directories without updating the config.
- Mermaid diagrams are stored as `.mmd` source; the portal does not render Mermaid at runtime. Link diagram sources as learning artifacts, and render temporary `/tmp` assets only for validation or external export.
- The portal has its own `.gitignore` and `node_modules/`; do not commit `node_modules` or `.next/` build output.
