import path from "path";
import { CODING_SUPPORT_DIRS } from "@/content/coding-policy";
import { isPublicResourceCategorySlug } from "@/content/resource-policy";
import {
  isBlockedBySourceProvenance,
  isBlockedPortalRoutePath,
} from "@/content/source-provenance";
import { fileExists } from "@/content/loader";

interface SolutionRouteEntry {
  type: string;
  slug: string;
  solutionPath: string;
}

interface ResourceHrefOptions {
  solutionEntries?: SolutionRouteEntry[];
}

const EXTERNAL_OR_SPECIAL_HREF = /^(?:[a-z][a-z0-9+.-]*:|\/\/|#)/i;
const SECTION_DOC_SEGMENT = /^[A-Z0-9][A-Z0-9-]*$/;
const SOURCE_REPOSITORY_URL =
  "https://github.com/mukundajmera/computer-science-interview-prep";
const SOURCE_REPOSITORY_BRANCH = "main";
const PORTAL_ROUTE_ROOTS = new Set([
  "case-studies",
  "coding",
  "genai",
  "hld",
  "hld-concepts",
  "interview",
  "lld",
  "patterns",
  "progress",
  "quizzes",
  "resources",
  "theory",
]);
const SOURCE_REPOSITORY_ROOTS = new Set([
  "00-theory",
  "01-design-patterns",
  "02-lld-projects",
  "03-hld-concepts",
  "04-hld-projects",
  "05-coding-problems",
  "06-genai-systems",
  "case-studies",
  "diagrams",
  "flashcards",
  "quizzes",
  "resources",
  "solutions",
]);
const FORBIDDEN_PORTAL_SOURCE_PATHS = [
  "resources/source-intake",
  "temp_upload",
];
const DESIGN_PATTERN_DOCS = new Set(["README", "THEORY"]);
const LLD_PROJECT_DOC_NAMES = [
  "README",
  "PROBLEM",
  "DESIGN",
  "APPROACH",
  "CODE-WALKTHROUGH",
  "RUBRIC",
  "PITFALLS",
  "FOLLOW-UPS",
];
const LLD_PROJECT_DOCS = new Set(LLD_PROJECT_DOC_NAMES);
const HLD_PROJECT_DOCS = new Set([
  ...LLD_PROJECT_DOC_NAMES,
  "COMPARISON",
  "STRONG-ANSWER",
]);
const HLD_CONCEPT_DOCS = new Set(["README", "THEORY", "INTERVIEW-QA"]);
const GENAI_PROJECT_DOCS = new Set(["README", "PROBLEM", "DESIGN", "APPROACH"]);
const BLOCKED_PORTAL_LINK_HREF = "#";

function splitHref(href: string): { pathname: string; suffix: string } {
  const hashIndex = href.indexOf("#");
  const queryIndex = href.indexOf("?");
  const indexes = [hashIndex, queryIndex].filter((index) => index >= 0);
  const splitIndex = indexes.length > 0 ? Math.min(...indexes) : -1;

  if (splitIndex === -1) {
    return { pathname: href, suffix: "" };
  }

  return {
    pathname: href.slice(0, splitIndex),
    suffix: href.slice(splitIndex),
  };
}

function normalizeRepoPath(sourceMarkdownFile: string, hrefPathname: string): string {
  const sourceDir = path.posix.dirname(sourceMarkdownFile);
  const rawPath = hrefPathname.startsWith("/")
    ? hrefPathname.slice(1)
    : path.posix.join(sourceDir, hrefPathname);

  return path.posix
    .normalize(rawPath)
    .replace(/\/+$/, "");
}

function rootDocRoute(segment: string): string | null {
  if (segment === "README") return "/";
  if (segment === "CONCEPTS") return "/theory";
  if (segment === "QUICK-START") return "/resources";
  return null;
}

function isSectionDoc(segment: string | undefined): boolean {
  return Boolean(segment && SECTION_DOC_SEGMENT.test(segment));
}

function stripMarkdownExtension(repoPath: string): string {
  return repoPath.replace(/\.md$/i, "");
}

function hasPathExtension(repoPath: string): boolean {
  return path.posix.extname(repoPath) !== "";
}

function hasSourceRepositoryRoot(repoPath: string): boolean {
  const [root] = repoPath.split("/").filter(Boolean);
  return Boolean(root && SOURCE_REPOSITORY_ROOTS.has(root));
}

function isForbiddenPortalSourcePath(repoPath: string): boolean {
  const normalizedPath = stripMarkdownExtension(repoPath).replace(/\/+$/, "");
  return FORBIDDEN_PORTAL_SOURCE_PATHS.some(
    (forbiddenPath) =>
      normalizedPath === forbiddenPath ||
      normalizedPath.startsWith(`${forbiddenPath}/`)
  );
}

function forbiddenResourcePath(repoPath: string): string | null {
  const normalizedPath = stripMarkdownExtension(repoPath)
    .replace(/^\/+/, "")
    .replace(/\/+$/, "");
  const [root, category] = normalizedPath.split("/").filter(Boolean);

  if (root !== "resources" || !category || category === "README") {
    return null;
  }

  return isPublicResourceCategorySlug(category) ? null : normalizedPath;
}

function assertAllowedPortalSourcePath(repoPath: string): void {
  const forbiddenPath =
    forbiddenResourcePath(repoPath) ??
    (isForbiddenPortalSourcePath(repoPath) ? repoPath : null);

  if (forbiddenPath) {
    throw new Error(`Forbidden portal content link: ${forbiddenPath}`);
  }
}

function githubSourceHref(repoPath: string, originalPathname: string): string {
  const mode =
    originalPathname.endsWith("/") || !hasPathExtension(repoPath)
      ? "tree"
      : "blob";
  const encodedPath = repoPath.split("/").map(encodeURIComponent).join("/");
  return `${SOURCE_REPOSITORY_URL}/${mode}/${SOURCE_REPOSITORY_BRANCH}/${encodedPath}`;
}

function normalizePortalRoute(route: string): string {
  const normalized = route.replace(/\/+$/, "") || "/";
  return normalized.startsWith("/") ? normalized : `/${normalized}`;
}

function isPortalRoutePathname(pathname: string): boolean {
  if (!pathname.startsWith("/") || hasPathExtension(pathname)) {
    return false;
  }

  const normalized = normalizePortalRoute(pathname);
  if (normalized === "/") return true;

  const [root] = normalized.split("/").filter(Boolean);
  return PORTAL_ROUTE_ROOTS.has(root);
}

function solutionRoute(
  segments: string[],
  solutionEntries: SolutionRouteEntry[]
): string | null {
  const solutionPath = `${segments.join("/")}.md`;
  const entry = solutionEntries.find(
    (candidate) => candidate.solutionPath === solutionPath
  );

  return entry ? `/interview/${entry.type}/${entry.slug}` : null;
}

function repoPathToPortalRoute(
  repoPath: string,
  solutionEntries: SolutionRouteEntry[]
): string | null {
  const routePath = stripMarkdownExtension(repoPath);
  const segments = routePath.split("/").filter(Boolean);
  const [root, second, third, fourth] = segments;

  if (!root) return null;

  const rootRoute = segments.length === 1 ? rootDocRoute(root) : null;
  if (rootRoute) return rootRoute;

  if (root === "00-theory") {
    if (segments.length === 1) return "/theory";
    if (segments.length === 2) {
      return second === "README" ? "/theory" : `/theory/${second}`;
    }
    if (segments.length === 3) return `/theory/${second}/${third}`;
    return null;
  }

  if (root === "01-design-patterns") {
    if (segments.length === 1) return "/patterns";
    if (segments.length === 2) {
      return second === "README" ? "/patterns" : `/patterns/${second}`;
    }
    if (segments.length === 3) return `/patterns/${second}/${third}`;
    if (segments.length === 4 && DESIGN_PATTERN_DOCS.has(fourth)) {
      return `/patterns/${second}/${third}`;
    }
    return null;
  }

  if (root === "02-lld-projects") {
    if (segments.length === 1) return "/lld";
    if (segments.length === 2) {
      return isSectionDoc(second) ? "/lld" : `/lld/${second}`;
    }
    if (segments.length === 3 && LLD_PROJECT_DOCS.has(third)) {
      return `/lld/${second}`;
    }
    return null;
  }

  if (root === "03-hld-concepts") {
    if (segments.length === 1) return "/hld-concepts";
    if (segments.length === 2) {
      if (second === "README") return "/hld-concepts";
      // Root-level docs such as TECHNOLOGY-SELECTION.md have no portal route.
      return isSectionDoc(second) ? null : `/hld-concepts/${second}`;
    }
    if (segments.length === 3 && HLD_CONCEPT_DOCS.has(third)) {
      return `/hld-concepts/${second}`;
    }
    return null;
  }

  if (root === "04-hld-projects") {
    if (segments.length === 1) return "/hld";
    if (segments.length === 2) {
      return isSectionDoc(second) ? "/hld" : `/hld/${second}`;
    }
    if (segments.length === 3 && HLD_PROJECT_DOCS.has(third)) {
      return `/hld/${second}`;
    }
    return null;
  }

  if (root === "05-coding-problems") {
    if (segments.length === 1) return "/coding";
    if (second && CODING_SUPPORT_DIRS.has(second)) return null;
    if (segments.length === 2) {
      return isSectionDoc(second) ? "/coding" : `/coding/${second}`;
    }
    if (segments.length === 3 && third === "README") {
      return `/coding/${second}`;
    }
    return null;
  }

  if (root === "06-genai-systems") {
    if (segments.length === 1) return "/genai";
    if (second === "00-concepts") {
      if (!third || isSectionDoc(third)) return "/genai";
      if (segments.length === 3) return `/genai/concepts/${third}`;
      if (segments.length === 4 && fourth === "README") {
        return `/genai/concepts/${third}`;
      }
      return null;
    }
    if (second === "01-llm-lld-projects") {
      if (!third || isSectionDoc(third)) return "/genai";
      if (segments.length === 3) return `/genai/lld/${third}`;
      if (segments.length === 4 && GENAI_PROJECT_DOCS.has(fourth)) {
        return `/genai/lld/${third}`;
      }
      return null;
    }
    if (second === "02-llm-hld-projects") {
      if (!third || isSectionDoc(third)) return "/genai";
      if (segments.length === 3) return `/genai/hld/${third}`;
      if (segments.length === 4 && GENAI_PROJECT_DOCS.has(fourth)) {
        return `/genai/hld/${third}`;
      }
      return null;
    }
    return "/genai";
  }

  if (root === "case-studies") {
    if (segments.length === 1) return "/case-studies";
    if (segments.length === 2) {
      return second === "README" ? "/case-studies" : `/case-studies/${second}`;
    }
    return null;
  }

  if (root === "quizzes") {
    if (!second || second === "answers") return "/quizzes";
    if (segments.length === 2) {
      const quizSlug = second.replace(/-(?:quiz|answers)$/i, "");
      return fileExists(`quizzes/${quizSlug}-quiz.md`)
        ? `/quizzes/${quizSlug}`
        : null;
    }
    return null;
  }

  if (root === "resources") {
    if (!second || second === "README") return "/resources";
    if (!isPublicResourceCategorySlug(second)) return null;
    if (!third || third === "README") return `/resources/${second}`;
    if (segments.length !== 3) return null;
    if (hasPathExtension(repoPath) && !/\.md$/i.test(repoPath)) return null;
    return `/resources/${second}/${third}`;
  }

  if (root === "solutions") {
    return solutionRoute(segments, solutionEntries);
  }

  if (root === "flashcards") {
    return null;
  }

  return null;
}

function resourceRouteForMarkdown(markdownFile: string): string {
  const segments = markdownFile.replace(/\.md$/i, "").split("/");
  return `/resources/${segments[1]}/${segments[2]}`;
}

function toRelativePortalHref(currentRoute: string, targetRoute: string): string {
  const from = normalizePortalRoute(currentRoute);
  const to = normalizePortalRoute(targetRoute);
  const relative = path.posix.relative(from, to);
  return relative === "" ? "./" : `${relative}/`;
}

export function rewriteResourceHref(
  href: string,
  sourceMarkdownFile: string,
  options: ResourceHrefOptions = {}
): string {
  return rewritePortalHref(
    href,
    sourceMarkdownFile,
    resourceRouteForMarkdown(sourceMarkdownFile),
    options
  );
}

export function rewritePortalHref(
  href: string,
  sourceMarkdownFile: string,
  currentRoute: string,
  options: ResourceHrefOptions = {}
): string {
  if (!href || EXTERNAL_OR_SPECIAL_HREF.test(href)) return href;

  const { pathname, suffix } = splitHref(href);
  if (!pathname) return href;

  assertAllowedPortalSourcePath(pathname);

  if (isPortalRoutePathname(pathname)) {
    if (isBlockedPortalRoutePath(pathname)) return BLOCKED_PORTAL_LINK_HREF;
    return `${toRelativePortalHref(currentRoute, pathname)}${suffix}`;
  }

  const repoPath = normalizeRepoPath(sourceMarkdownFile, pathname);
  if (repoPath.startsWith("../")) return href;
  assertAllowedPortalSourcePath(repoPath);
  if (isBlockedBySourceProvenance(repoPath)) return BLOCKED_PORTAL_LINK_HREF;

  const targetRoute = repoPathToPortalRoute(
    repoPath,
    options.solutionEntries ?? []
  );
  if (!targetRoute) {
    return hasSourceRepositoryRoot(repoPath)
      ? `${githubSourceHref(repoPath, pathname)}${suffix}`
      : href;
  }

  return `${toRelativePortalHref(
    currentRoute,
    targetRoute
  )}${suffix}`;
}

export function createPortalHrefRewriter(
  sourceMarkdownFile: string,
  currentRoute: string,
  options: ResourceHrefOptions = {}
): (href: string) => string {
  return (href) => rewritePortalHref(href, sourceMarkdownFile, currentRoute, options);
}

export function createResourceHrefRewriter(
  sourceMarkdownFile: string,
  options: ResourceHrefOptions = {}
): (href: string) => string {
  return (href) => rewriteResourceHref(href, sourceMarkdownFile, options);
}
