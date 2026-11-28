import fs from "fs";
import path from "path";
import { CODING_SUPPORT_DIRS } from "@/content/coding-policy";
import { REPO_ROOT } from "@/content/safe-content";

const DERIVATIVE_REVIEW_LEDGER =
  "resources/source-intake/temp-upload/derivative-review-ledger.csv";
const BLOCKING_REVIEW_STATUSES = new Set(["blocked", "needs-review"]);

export interface BlockedSourcePath {
  path: string;
  isPrefix: boolean;
  reviewStatus: string;
}

let cachedBlockedSourcePaths: BlockedSourcePath[] | null = null;

function parseCsvLine(line: string): string[] {
  const cells: string[] = [];
  let current = "";
  let inQuotes = false;

  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    const next = line[index + 1];
    if (char === '"' && inQuotes && next === '"') {
      current += '"';
      index += 1;
      continue;
    }
    if (char === '"') {
      inQuotes = !inQuotes;
      continue;
    }
    if (char === "," && !inQuotes) {
      cells.push(current);
      current = "";
      continue;
    }
    current += char;
  }

  cells.push(current);
  return cells;
}

function normalizeSourcePath(candidate: string): string | null {
  if (!candidate || candidate.includes("\0") || candidate.includes("\\")) return null;
  if (path.posix.isAbsolute(candidate) || path.win32.isAbsolute(candidate)) return null;

  const normalized = path.posix.normalize(candidate.replace(/\/+$/, ""));
  if (normalized === "." || normalized.startsWith("../")) return null;

  const segments = normalized.split("/");
  if (segments.some((segment) => segment === "" || segment === "." || segment === "..")) {
    return null;
  }

  return normalized;
}

export function parseBlockedSourcePaths(csvText: string): BlockedSourcePath[] {
  const lines = csvText
    .split(/\r?\n/)
    .map((line) => line.trimEnd())
    .filter(Boolean);
  if (lines.length === 0) return [];

  const headers = parseCsvLine(lines[0]);
  const artifactPathIndex = headers.indexOf("artifact_path");
  const reviewStatusIndex = headers.indexOf("review_status");
  if (artifactPathIndex === -1 || reviewStatusIndex === -1) {
    throw new Error(
      "Derivative review ledger must include artifact_path and review_status columns"
    );
  }

  return lines.slice(1).flatMap((line) => {
    const cells = parseCsvLine(line);
    const reviewStatus = (cells[reviewStatusIndex] ?? "").trim().toLowerCase();
    if (!BLOCKING_REVIEW_STATUSES.has(reviewStatus)) return [];

    const rawPath = cells[artifactPathIndex] ?? "";
    const isPrefix = rawPath.endsWith("/");
    const normalizedPath = normalizeSourcePath(rawPath);
    if (!normalizedPath) {
      throw new Error(`Invalid blocked source path in derivative review ledger: ${rawPath}`);
    }

    return [
      {
        path: isPrefix ? `${normalizedPath.replace(/\/+$/, "")}/` : normalizedPath,
        isPrefix,
        reviewStatus,
      },
    ];
  });
}

export function isBlockedBySourceProvenance(
  relativePath: string,
  blockedPaths: BlockedSourcePath[] = getBlockedSourcePaths()
): boolean {
  const normalizedPath = normalizeSourcePath(relativePath);
  if (!normalizedPath) return true;

  return blockedPaths.some((blockedPath) => {
    if (blockedPath.isPrefix) {
      return normalizedPath.startsWith(blockedPath.path);
    }
    return normalizedPath === blockedPath.path;
  });
}

function routeFromSolutionPath(solutionSlug: string): string[] {
  if (solutionSlug.startsWith("coding-")) {
    const slug = `${solutionSlug.replace(/^coding-/, "")}-pack`;
    return [`/interview/coding/${slug}`, `/reveal/solution/coding/${slug}`];
  }
  if (solutionSlug.startsWith("lld-")) {
    const slug = solutionSlug.replace(/^lld-/, "");
    return [`/interview/lld/${slug}`, `/reveal/solution/lld/${slug}`];
  }
  if (solutionSlug.startsWith("hld-")) {
    const slug = solutionSlug.replace(/^hld-/, "");
    return [`/interview/hld/${slug}`, `/reveal/solution/hld/${slug}`];
  }
  if (solutionSlug.startsWith("genai-hld-")) {
    const slug = solutionSlug.replace(/^genai-hld-/, "");
    return [`/interview/genai-hld/${slug}`, `/reveal/solution/genai-hld/${slug}`];
  }
  if (solutionSlug.startsWith("behavioral-")) {
    return [
      `/interview/behavioral/${solutionSlug}`,
      `/reveal/solution/behavioral/${solutionSlug}`,
    ];
  }
  return [];
}

function sourcePathToRemovedPortalRoutes(relativePath: string): string[] {
  const routePath = relativePath.replace(/\.md$/i, "");
  const segments = routePath.split("/").filter(Boolean);
  const [root, second, third, fourth] = segments;
  const isPrefixPath = relativePath.endsWith("/");

  if (root === "00-theory" && segments.length === 3) {
    return [`/theory/${second}/${third}`];
  }
  if (
    root === "01-design-patterns" &&
    segments.length >= 3 &&
    ["README", "THEORY"].includes(fourth ?? "README")
  ) {
    return [`/patterns/${second}/${third}`];
  }
  if (root === "02-lld-projects" && segments.length >= 2) {
    return [`/lld/${second}`];
  }
  if (root === "03-hld-concepts" && segments.length >= 2) {
    return [`/hld-concepts/${second}`];
  }
  if (root === "04-hld-projects" && segments.length >= 2) {
    return [`/hld/${second}`];
  }
  if (
    root === "05-coding-problems" &&
    second &&
    !CODING_SUPPORT_DIRS.has(second) &&
    (isPrefixPath || (segments.length === 3 && third === "README"))
  ) {
    return [`/coding/${second}`];
  }
  if (root === "06-genai-systems" && second === "00-concepts" && segments.length === 4 && fourth === "README") {
    return [`/genai/concepts/${third}`];
  }
  if (root === "06-genai-systems" && second === "01-llm-lld-projects" && segments.length >= 3) {
    return [`/genai/lld/${third}`];
  }
  if (root === "06-genai-systems" && second === "02-llm-hld-projects" && segments.length >= 3) {
    return [`/genai/hld/${third}`];
  }
  if (root === "case-studies" && segments.length === 3 && third === "README") {
    return [`/case-studies/${second}`];
  }
  if (root === "quizzes" && segments.length === 2 && second.endsWith("-quiz")) {
    return [`/quizzes/${second.replace(/-quiz$/, "")}`];
  }
  if (root === "quizzes" && second === "answers" && segments.length === 3 && third.endsWith("-answers")) {
    return [`/reveal/quiz-answer/${third.replace(/-answers$/, "")}`];
  }
  if (root === "resources" && second && isPrefixPath && segments.length === 2) {
    return [`/resources/${second}`];
  }
  if (root === "resources" && segments.length === 3) {
    return [`/resources/${second}/${third}`];
  }
  if (root === "solutions" && second) {
    return routeFromSolutionPath(second);
  }

  return [];
}

export function isBlockedPortalRoutePath(
  pathname: string,
  blockedPaths: BlockedSourcePath[] = getBlockedSourcePaths()
): boolean {
  if (!pathname.startsWith("/")) return false;
  const normalizedRoute = pathname.replace(/\/+$/, "") || "/";

  return blockedPaths.some((blockedPath) => {
    return sourcePathToRemovedPortalRoutes(blockedPath.path).some((route) => {
      return blockedPath.isPrefix
        ? normalizedRoute === route || normalizedRoute.startsWith(`${route}/`)
        : normalizedRoute === route;
    });
  });
}

export function assertSourcePathAllowedForPortal(relativePath: string): void {
  if (isBlockedBySourceProvenance(relativePath)) {
    throw new Error(`Blocked source-derived content is not public: ${relativePath}`);
  }
}

export function filterAllowedPortalSourcePath<T extends string | null>(
  relativePath: T
): T | null {
  if (!relativePath) return relativePath;
  return isBlockedBySourceProvenance(relativePath) ? null : relativePath;
}

export function getBlockedSourcePaths(): BlockedSourcePath[] {
  if (cachedBlockedSourcePaths) return cachedBlockedSourcePaths;

  const ledgerPath = path.join(REPO_ROOT, DERIVATIVE_REVIEW_LEDGER);
  if (!fs.existsSync(ledgerPath)) {
    // The review ledger is a private, ignored artifact and is not published in
    // this public repository; scripts/check_assessment_coverage.py behaves the same.
    cachedBlockedSourcePaths = [];
    return cachedBlockedSourcePaths;
  }

  cachedBlockedSourcePaths = parseBlockedSourcePaths(
    fs.readFileSync(ledgerPath, "utf-8")
  );
  return cachedBlockedSourcePaths;
}
