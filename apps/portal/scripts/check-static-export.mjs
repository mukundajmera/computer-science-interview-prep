import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import {
  DEFAULT_GITHUB_PAGES_BASE_PATH,
  normalizeBasePath,
} from "../site-config.mjs";

const portalRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(portalRoot, "../..");
const outDir = path.join(portalRoot, "out");
const quizSourceDir = path.join(repoRoot, "quizzes");
const quizAnswersDir = path.join(repoRoot, "quizzes", "answers");
const prerenderManifestPath = path.join(
  portalRoot,
  ".next/prerender-manifest.json"
);
const routesManifestPath = path.join(portalRoot, ".next/routes-manifest.json");
const appPathRoutesManifestPath = path.join(
  portalRoot,
  ".next/app-path-routes-manifest.json"
);
const basePath = normalizeBasePath(
  process.env.BASE_PATH ?? process.env.GITHUB_PAGES_BASE_PATH ?? DEFAULT_GITHUB_PAGES_BASE_PATH
);
const attributeUrlPattern = /\b(?:href|src)=\\?["']([^"'\\]+)\\?["']/g;

const representativePages = [
  "index.html",
  "coding/sliding-window/index.html",
  "coding/bfs-dfs/index.html",
  "coding/dynamic-programming/index.html",
  "coding/greedy/index.html",
  "coding/backtracking/index.html",
  "coding/heap-priority-queue/index.html",
  "coding/trie/index.html",
  "coding/union-find/index.html",
  "theory/big-data-structures/merkle-tree/index.html",
  "theory/big-data-structures/trie/index.html",
  "hld-concepts/caching/index.html",
  "hld/url-shortener/index.html",
  "genai/lld/embedding-service/index.html",
  "interview/lld/parking-lot/index.html",
  "interview/coding/bfs-dfs-pack/index.html",
  "interview/coding/dynamic-programming-pack/index.html",
  "interview/coding/greedy-pack/index.html",
  "interview/coding/backtracking-pack/index.html",
  "interview/coding/heap-priority-queue-pack/index.html",
  "interview/coding/trie-pack/index.html",
  "interview/coding/union-find-pack/index.html",
  "reveal/solution/lld/parking-lot/index.html",
  "reveal/solution/coding/bfs-dfs-pack/index.html",
  "reveal/solution/coding/dynamic-programming-pack/index.html",
  "reveal/solution/coding/greedy-pack/index.html",
  "reveal/solution/coding/backtracking-pack/index.html",
  "reveal/solution/coding/heap-priority-queue-pack/index.html",
  "reveal/solution/coding/trie-pack/index.html",
  "reveal/solution/coding/union-find-pack/index.html",
  "quizzes/design-patterns/index.html",
  "quizzes/sliding-window/index.html",
  "quizzes/bfs-dfs/index.html",
  "quizzes/dynamic-programming/index.html",
  "quizzes/greedy/index.html",
  "quizzes/backtracking/index.html",
  "quizzes/heap-priority-queue/index.html",
  "quizzes/trie/index.html",
  "quizzes/union-find/index.html",
  "reveal/quiz-answer/design-patterns/index.html",
  "reveal/quiz-answer/sliding-window/index.html",
  "reveal/quiz-answer/bfs-dfs/index.html",
  "reveal/quiz-answer/dynamic-programming/index.html",
  "reveal/quiz-answer/greedy/index.html",
  "reveal/quiz-answer/backtracking/index.html",
  "reveal/quiz-answer/heap-priority-queue/index.html",
  "reveal/quiz-answer/trie/index.html",
  "reveal/quiz-answer/union-find/index.html",
  "resources/study-plans/1-week-plan/index.html",
];

function walkIndexFiles(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) return walkIndexFiles(fullPath);
    return entry.isFile() && entry.name === "index.html" ? [fullPath] : [];
  });
}

function listRoutePaths(prefix, rootDir = outDir) {
  const root = path.join(rootDir, prefix);
  if (!fs.existsSync(root)) return [];

  return walkIndexFiles(root)
    .map((filePath) => {
      const relativeFile = path.relative(rootDir, filePath).split(path.sep).join("/");
      return `/${relativeFile.replace(/\/index\.html$/, "")}`;
    })
    .filter((route) => route !== `/${prefix}`);
}

export function listQuizAnswerSourceSlugs(rootDir = quizAnswersDir) {
  if (!fs.existsSync(rootDir)) return [];

  return fs
    .readdirSync(rootDir, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith("-answers.md"))
    .map((entry) => entry.name.replace(/-answers\.md$/, ""))
    .sort((a, b) => a.localeCompare(b));
}

export function listQuizSourceSlugs(rootDir = quizSourceDir) {
  if (!fs.existsSync(rootDir)) return [];

  return fs
    .readdirSync(rootDir, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith("-quiz.md"))
    .map((entry) => entry.name.replace(/-quiz\.md$/, ""))
    .sort((a, b) => a.localeCompare(b));
}

function assertExists(relativePath) {
  const fullPath = path.join(outDir, relativePath);
  if (!fs.existsSync(fullPath)) {
    throw new Error(`Missing static export artifact: ${relativePath}`);
  }
}

function isFile(filePath) {
  try {
    return fs.statSync(filePath).isFile();
  } catch {
    return false;
  }
}

export function existsForUrl(urlPath, rootDir = outDir) {
  const cleanPath = urlPath.replace(/^\/+/, "").replace(/\/$/, "");
  const candidates = [cleanPath];

  try {
    const decodedPath = decodeURIComponent(cleanPath);
    if (decodedPath !== cleanPath) candidates.push(decodedPath);
  } catch {
    // Keep checking the raw URL path; malformed escapes should fail naturally.
  }

  return candidates.some((candidate) => {
    const filePath = path.resolve(rootDir, candidate);
    const relativeToOut = path.relative(rootDir, filePath);
    if (relativeToOut.startsWith("..") || path.isAbsolute(relativeToOut)) {
      return false;
    }

    return (
      isFile(filePath) ||
      isFile(`${filePath}.html`) ||
      isFile(path.join(filePath, "index.html"))
    );
  });
}

function normalizeHref(filePath, href, rootDir = outDir) {
  const withoutFragment = href.split(/[?#]/)[0];
  if (!withoutFragment) return null;

  if (
    withoutFragment === basePath ||
    withoutFragment.startsWith(`${basePath}/`)
  ) {
    return withoutFragment.slice(basePath.length) || "/";
  }

  if (withoutFragment.startsWith("/")) return withoutFragment;

  const absolutePath = path.resolve(path.dirname(filePath), withoutFragment);
  return `/${path.relative(rootDir, absolutePath).split(path.sep).join("/")}`;
}

export function validateInternalLinks(rootDir = outDir) {
  const failures = [];
  const basePathFailures = [];

  for (const filePath of walkIndexFiles(rootDir)) {
    const relativeFile = path.relative(rootDir, filePath);
    if (relativeFile.startsWith("404/")) continue;

    const html = fs.readFileSync(filePath, "utf-8");
    for (const match of html.matchAll(attributeUrlPattern)) {
      const href = match[1];
      if (/^(?:[a-z][a-z0-9+.-]*:|\/\/|#)/i.test(href)) continue;
      if (
        basePath &&
        href.startsWith("/") &&
        href !== basePath &&
        !href.startsWith(`${basePath}/`)
      ) {
        basePathFailures.push(`${relativeFile} -> ${href}`);
      }

      const normalized = normalizeHref(filePath, href, rootDir);
      if (!normalized) continue;
      if (!existsForUrl(normalized, rootDir)) {
        failures.push(`${relativeFile} -> ${href} -> ${normalized}`);
      }
    }
  }

  if (failures.length > 0) {
    throw new Error(
      `Broken static export links:\n${failures.slice(0, 120).join("\n")}`
    );
  }

  if (basePathFailures.length > 0) {
    throw new Error(
      `Root-relative links are not GitHub Pages basePath safe:\n${basePathFailures
        .slice(0, 120)
        .join("\n")}`
    );
  }
}

// Largest per-route JavaScript payload measured on the 2026-11-28 build:
// 460,186 bytes (progress/index.html, 777 routes scanned). Budget is that
// baseline plus 15 percent, rounded up to the next 1,000 bytes. SITE-10
// re-baselines this after the theme, reading-layout and search work lands.
export const PER_ROUTE_JS_BUDGET_BYTES = 530000;

const nextAssetPrefix = "/_next/";

function isNextJavaScriptUrl(url) {
  const withoutQuery = url.split(/[?#]/)[0];
  return withoutQuery.includes(nextAssetPrefix) && withoutQuery.endsWith(".js");
}

// Sums the bytes of every distinct Next chunk a route's HTML references and
// fails when any route exceeds the budget. Reported per route so the owner
// sees exactly which page got heavier.
export function validateJsBudget(
  rootDir = outDir,
  budgetBytes = PER_ROUTE_JS_BUDGET_BYTES
) {
  const failures = [];

  for (const filePath of walkIndexFiles(rootDir)) {
    const relativeFile = path.relative(rootDir, filePath).split(path.sep).join("/");
    if (relativeFile.startsWith("404/")) continue;

    const html = fs.readFileSync(filePath, "utf-8");
    const seenChunks = new Set();
    let totalBytes = 0;

    for (const match of html.matchAll(attributeUrlPattern)) {
      const url = match[1];
      if (!isNextJavaScriptUrl(url)) continue;

      const normalized = normalizeHref(filePath, url, rootDir);
      if (!normalized || seenChunks.has(normalized)) continue;
      seenChunks.add(normalized);

      const chunkPath = path.resolve(rootDir, normalized.replace(/^\/+/, ""));
      if (isFile(chunkPath)) {
        totalBytes += fs.statSync(chunkPath).size;
      }
      // A missing chunk is already reported by validateInternalLinks.
    }

    if (totalBytes > budgetBytes) {
      failures.push(
        `${relativeFile}: ${totalBytes} bytes of JavaScript exceeds the ${budgetBytes} byte budget`
      );
    }
  }

  if (failures.length > 0) {
    throw new Error(
      `Per-route JavaScript size budget exceeded:\n${failures
        .slice(0, 120)
        .join("\n")}`
    );
  }
}

function readJsonManifest(manifestPath, label) {
  if (!fs.existsSync(manifestPath)) {
    throw new Error(`Missing Next ${label}; run next build first`);
  }

  return JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
}

function validateManifestRoutes() {
  const failures = [];

  if (fs.existsSync(prerenderManifestPath)) {
    const manifest = readJsonManifest(prerenderManifestPath, "prerender manifest");
    failures.push(
      ...Object.keys(manifest.routes ?? {}).filter((route) => !existsForUrl(route))
    );
  } else {
    const routesManifest = readJsonManifest(routesManifestPath, "routes manifest");
    const appPathRoutesManifest = readJsonManifest(
      appPathRoutesManifestPath,
      "app path routes manifest"
    );
    const staticRoutes = new Set(
      (routesManifest.staticRoutes ?? [])
        .map((entry) => entry.page)
        .filter((route) => route && route !== "/_not-found")
    );

    for (const route of Object.values(appPathRoutesManifest)) {
      if (!route || route.includes("[") || route === "/_not-found") continue;
      staticRoutes.add(route);
    }

    failures.push(
      ...Array.from(staticRoutes).filter((route) => !existsForUrl(route))
    );
  }

  if (failures.length > 0) {
    throw new Error(
      `Missing exported HTML for manifest routes:\n${failures
        .slice(0, 120)
        .join("\n")}`
    );
  }
}

export function validateRevealRoutePairs(
  rootDir = outDir,
  answerSourceDir = quizAnswersDir,
  quizRouteSourceDir = quizSourceDir
) {
  const expectedSolutionRevealRoutes = listRoutePaths("interview", rootDir).map(
    (route) => route.replace(/^\/interview\//, "/reveal/solution/")
  );
  const quizSlugs = new Set(listQuizSourceSlugs(quizRouteSourceDir));
  const quizAnswerSlugs = listQuizAnswerSourceSlugs(answerSourceDir);
  const orphanAnswerSlugs = quizAnswerSlugs.filter((slug) => !quizSlugs.has(slug));

  if (orphanAnswerSlugs.length > 0) {
    throw new Error(
      `Quiz answer files without matching quiz source:\n${orphanAnswerSlugs
        .slice(0, 120)
        .map((slug) => `${slug}-answers.md`)
        .join("\n")}`
    );
  }

  const expectedQuizAnswerRevealRoutes = quizAnswerSlugs.map(
    (slug) => `/reveal/quiz-answer/${slug}`
  );
  const expectedQuizRoutes = expectedQuizAnswerRevealRoutes.map((route) =>
    route.replace(/^\/reveal\/quiz-answer\//, "/quizzes/")
  );
  const failures = [
    ...expectedSolutionRevealRoutes.filter((route) => !existsForUrl(route, rootDir)),
    ...expectedQuizAnswerRevealRoutes.filter((route) => !existsForUrl(route, rootDir)),
    ...expectedQuizRoutes.filter((route) => !existsForUrl(route, rootDir)),
  ];

  if (failures.length > 0) {
    throw new Error(
      `Missing paired reveal, interview, or quiz pages:\n${failures
        .slice(0, 120)
        .join("\n")}`
    );
  }
}

function main() {
  assertExists("index.html");
  assertExists("_next");
  for (const page of representativePages) assertExists(page);
  validateManifestRoutes();
  validateRevealRoutePairs();
  validateInternalLinks();
  validateJsBudget();

  console.log("static-export: ok");
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
