import fs from "fs";
import path from "path";

export const REPO_ROOT = process.env.REPO_ROOT
  ? path.resolve(process.env.REPO_ROOT)
  : path.resolve(process.cwd(), "../..");

const DEFAULT_ALLOWED_ROOTS = [
  "00-theory",
  "01-design-patterns",
  "02-lld-projects",
  "03-hld-concepts",
  "04-hld-projects",
  "05-coding-problems",
  "06-genai-systems",
  "case-studies",
  "resources/study-plans",
  "resources/cheatsheets",
  "resources/interview-tips",
  "resources/templates",
  "quizzes",
  "solutions",
];

const REVEAL_ALLOWED_ROOTS = ["solutions", "quizzes/answers"];
const SLUG_PATTERN = /^[a-z0-9][a-z0-9-]*$/;

export type RevealMarkdownRequest =
  | {
      kind: "solution";
      type: string;
      slug: string;
    }
  | {
      kind: "quiz-answer";
      slug: string;
    };

export interface SolutionEntry {
  type: string;
  slug: string;
  solutionPath: string;
}

export interface ResolvePathOptions {
  allowedRoots?: string[];
  requireMarkdown?: boolean;
  mustExist?: boolean;
}

export interface ResolveRevealOptions {
  repoRoot?: string;
  solutionEntries?: SolutionEntry[];
  quizSlugs?: string[];
}

function decodePathInput(input: string): string | null {
  let decoded = input;
  for (let i = 0; i < 3; i += 1) {
    try {
      const next = decodeURIComponent(decoded);
      if (next === decoded) return next;
      decoded = next;
    } catch {
      return null;
    }
  }
  return decoded;
}

function isWithin(parent: string, child: string): boolean {
  const relative = path.relative(parent, child);
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative));
}

function toPosixRelative(candidate: string): string | null {
  const decoded = decodePathInput(candidate);
  if (!decoded || decoded.includes("\0") || decoded.includes("\\")) return null;
  if (path.posix.isAbsolute(decoded) || path.win32.isAbsolute(decoded)) return null;

  const normalized = path.posix.normalize(decoded);
  if (normalized === "." || normalized.startsWith("../")) return null;

  const segments = normalized.split("/");
  if (
    segments.some(
      (segment) => segment === "" || segment === "." || segment === ".." || segment.startsWith(".")
    )
  ) {
    return null;
  }

  return normalized;
}

function isUnderAllowedRoot(relativePath: string, allowedRoots: string[]): boolean {
  return allowedRoots.some((root) => {
    const normalizedRoot = path.posix.normalize(root);
    return relativePath === normalizedRoot || relativePath.startsWith(`${normalizedRoot}/`);
  });
}

function toPosixFromRoot(root: string, absolutePath: string): string {
  return path.relative(root, absolutePath).split(path.sep).join("/");
}

export function resolvePathWithinRoot(
  root: string,
  relativePath: string,
  options: ResolvePathOptions = {}
): string | null {
  const allowedRoots = options.allowedRoots ?? DEFAULT_ALLOWED_ROOTS;
  const requireMarkdown = options.requireMarkdown ?? false;
  const mustExist = options.mustExist ?? false;

  const safeRelative = toPosixRelative(relativePath);
  if (!safeRelative) return null;
  if (requireMarkdown && path.posix.extname(safeRelative) !== ".md") return null;
  if (!isUnderAllowedRoot(safeRelative, allowedRoots)) return null;
  if (!fs.existsSync(root)) return null;

  const realRoot = fs.realpathSync.native(root);
  const absolutePath = path.resolve(realRoot, ...safeRelative.split("/"));
  if (!isWithin(realRoot, absolutePath)) return null;

  if (!fs.existsSync(absolutePath)) return mustExist ? null : absolutePath;

  const realPath = fs.realpathSync.native(absolutePath);
  if (!isWithin(realRoot, realPath)) return null;

  const realRelative = toPosixFromRoot(realRoot, realPath);
  if (!isUnderAllowedRoot(realRelative, allowedRoots)) return null;

  return realPath;
}

export function resolveRepoMarkdownPath(
  relativePath: string,
  options: Pick<ResolvePathOptions, "allowedRoots"> = {}
): string | null {
  return resolvePathWithinRoot(REPO_ROOT, relativePath, {
    allowedRoots: options.allowedRoots ?? DEFAULT_ALLOWED_ROOTS,
    requireMarkdown: true,
    mustExist: true,
  });
}

export function resolveRepoDirectoryPath(
  relativePath: string,
  options: Pick<ResolvePathOptions, "allowedRoots"> = {}
): string | null {
  return resolvePathWithinRoot(REPO_ROOT, relativePath, {
    allowedRoots: options.allowedRoots ?? DEFAULT_ALLOWED_ROOTS,
    mustExist: true,
  });
}

export function resolveRevealMarkdownPath(
  request: unknown,
  options: ResolveRevealOptions = {}
): string | null {
  if (!request || typeof request !== "object") return null;

  const repoRoot = options.repoRoot ?? REPO_ROOT;
  const solutionEntries = options.solutionEntries ?? [];
  const quizSlugs = options.quizSlugs ?? [];
  const candidate = request as Partial<RevealMarkdownRequest>;

  let relativePath: string | null = null;
  if (candidate.kind === "solution") {
    if (
      typeof candidate.type !== "string" ||
      typeof candidate.slug !== "string" ||
      !SLUG_PATTERN.test(candidate.type) ||
      !SLUG_PATTERN.test(candidate.slug)
    ) {
      return null;
    }

    const entry = solutionEntries.find(
      (problem) => problem.type === candidate.type && problem.slug === candidate.slug
    );
    relativePath = entry?.solutionPath ?? null;
  } else if (candidate.kind === "quiz-answer") {
    if (typeof candidate.slug !== "string" || !SLUG_PATTERN.test(candidate.slug)) {
      return null;
    }
    if (!quizSlugs.includes(candidate.slug)) return null;
    relativePath = `quizzes/answers/${candidate.slug}-answers.md`;
  }

  if (!relativePath) return null;

  const resolved = resolvePathWithinRoot(repoRoot, relativePath, {
    allowedRoots: REVEAL_ALLOWED_ROOTS,
    requireMarkdown: true,
    mustExist: true,
  });
  if (!resolved) return null;

  return toPosixFromRoot(fs.realpathSync.native(repoRoot), resolved);
}
