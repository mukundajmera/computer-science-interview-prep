import type { ContentItem, ContentRegistry } from "./types";
import type { InterviewProblem } from "@/components/interview/interview-data";
import { isPublicResourceCategorySlug } from "@/content/resource-policy";
import { PORTAL_SECTIONS, type PortalSection } from "@/lib/sections";

export type RouteSource =
  | "home"
  | "section"
  | "content"
  | "resource"
  | "quiz"
  | "interview"
  | "reveal";

export interface RouteManifestEntry {
  href: string;
  title: string;
  section: string;
  source: RouteSource;
  id?: string;
  description?: string;
  difficulty?: string;
  status?: string;
}

export interface RouteManifest {
  routes: RouteManifestEntry[];
  counts: {
    total: number;
    bySection: Record<string, number>;
  };
}

export interface RouteManifestInput {
  registry: ContentRegistry;
  quizSlugs: string[];
  quizAnswerSlugs?: string[];
  interviewProblems: InterviewProblem[];
  resourceEntries?: Array<{
    id: string;
    title: string;
    href: string;
    category: string;
  }>;
  sections?: PortalSection[];
}

const CONTENT_GROUPS: Array<{
  section: string;
  select: (registry: ContentRegistry) => ContentItem[];
}> = [
  { section: "Theory", select: (registry) => registry.theory },
  { section: "Design Patterns", select: (registry) => registry.patterns },
  { section: "Coding Patterns", select: (registry) => registry.codingTopics },
  { section: "LLD Projects", select: (registry) => registry.lldProjects },
  { section: "HLD Concepts", select: (registry) => registry.hldConcepts },
  { section: "HLD Projects", select: (registry) => registry.hldProjects },
  {
    section: "GenAI Systems",
    select: (registry) => [
      ...registry.genaiConcepts,
      ...registry.genaiLLD,
      ...registry.genaiHLD,
    ],
  },
  { section: "Case Studies", select: (registry) => registry.caseStudies },
];
const ROUTE_SEGMENT_PATTERN = /^[A-Za-z0-9][A-Za-z0-9-]*$/;
const PUBLIC_ROUTE_ROOTS = new Set([
  "case-studies",
  "coding",
  "flashcards",
  "genai",
  "hld",
  "hld-concepts",
  "interview",
  "learning-paths",
  "lld",
  "patterns",
  "progress",
  "quizzes",
  "resources",
  "reveal",
  "start",
  "theory",
]);

function assertSafeRoute(href: string) {
  if (
    !href.startsWith("/") ||
    href.includes("//") ||
    (href.length > 1 && href.endsWith("/")) ||
    href.includes("?") ||
    href.includes("#") ||
    href.includes("\\") ||
    /^[a-z][a-z0-9+.-]*:/i.test(href)
  ) {
    throw new Error(`Unsafe portal route: ${href}`);
  }

  if (href === "/") return;

  const segments = href.split("/").filter(Boolean);
  const [root] = segments;
  if (!root || !PUBLIC_ROUTE_ROOTS.has(root)) {
    throw new Error(`Unsafe portal route: ${href}`);
  }
  if (
    root === "resources" &&
    segments.length > 1 &&
    !isPublicResourceCategorySlug(segments[1])
  ) {
    throw new Error(`Unsafe portal route: ${href}`);
  }

  for (const segment of segments) {
    let decodedSegment: string;
    try {
      decodedSegment = decodeURIComponent(segment);
    } catch {
      throw new Error(`Unsafe portal route: ${href}`);
    }

    if (
      decodedSegment !== segment ||
      decodedSegment === "." ||
      decodedSegment === ".." ||
      !ROUTE_SEGMENT_PATTERN.test(decodedSegment)
    ) {
      throw new Error(`Unsafe portal route: ${href}`);
    }
  }
}

function addRoute(
  routes: RouteManifestEntry[],
  seen: Set<string>,
  route: RouteManifestEntry
) {
  assertSafeRoute(route.href);

  if (seen.has(route.href)) {
    throw new Error(`Duplicate portal route: ${route.href}`);
  }
  seen.add(route.href);
  routes.push(route);
}

function slugToLabel(slug: string): string {
  return slug
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function uniqueSorted(values: string[]): string[] {
  return Array.from(new Set(values)).sort((a, b) => a.localeCompare(b));
}

function addGroupingRoutes(
  routes: RouteManifestEntry[],
  seen: Set<string>,
  input: RouteManifestInput
) {
  for (const topicArea of uniqueSorted(
    input.registry.theory.map((article) => article.topicArea)
  )) {
    addRoute(routes, seen, {
      href: `/theory/${topicArea}`,
      title: slugToLabel(topicArea),
      section: "Theory",
      source: "section",
      description: "Theory topic area",
    });
  }

  for (const category of uniqueSorted(
    input.registry.patterns.map((pattern) => pattern.patternCategory)
  )) {
    addRoute(routes, seen, {
      href: `/patterns/${category}`,
      title: `${slugToLabel(category)} Patterns`,
      section: "Design Patterns",
      source: "section",
      description: "Design pattern category",
    });
  }
}

export function createRouteManifest(input: RouteManifestInput): RouteManifest {
  const sections = input.sections ?? PORTAL_SECTIONS;
  const routes: RouteManifestEntry[] = [];
  const seen = new Set<string>();

  addRoute(routes, seen, {
    href: "/",
    title: "System Design Interview Prep",
    section: "Home",
    source: "home",
    description: "All curriculum sections",
  });

  for (const section of sections) {
    addRoute(routes, seen, {
      href: section.href,
      title: section.label,
      section: section.label,
      source: "section",
      description: section.description,
    });
  }

  addGroupingRoutes(routes, seen, input);

  for (const group of CONTENT_GROUPS) {
    for (const item of group.select(input.registry)) {
      addRoute(routes, seen, {
        href: item.href,
        title: item.title,
        section: group.section,
        source: "content",
        id: item.id,
        difficulty: item.difficulty,
        status: item.status,
      });
    }
  }

  for (const resource of input.resourceEntries ?? []) {
    addRoute(routes, seen, {
      href: resource.href,
      title: resource.title,
      section: "Resources",
      source: "resource",
      id: resource.id,
      description: resource.category,
    });
  }

  for (const slug of input.quizSlugs) {
    addRoute(routes, seen, {
      href: `/quizzes/${slug}`,
      title: `${slug
        .split("-")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ")} Quiz`,
      section: "Quizzes",
      source: "quiz",
      id: `quiz-${slug}`,
    });
  }

  for (const problem of input.interviewProblems) {
    addRoute(routes, seen, {
      href: `/interview/${problem.type}/${problem.slug}`,
      title: problem.title,
      section: "Interview Mode",
      source: "interview",
      id: `interview-${problem.type}-${problem.slug}`,
      difficulty: problem.difficulty,
    });
    addRoute(routes, seen, {
      href: `/reveal/solution/${problem.type}/${problem.slug}`,
      title: `${problem.title} Coach Answer`,
      section: "Reveal",
      source: "reveal",
      id: `reveal-solution-${problem.type}-${problem.slug}`,
      description: "Static reveal route for interview coach answer",
    });
  }

  for (const slug of input.quizAnswerSlugs ?? []) {
    addRoute(routes, seen, {
      href: `/reveal/quiz-answer/${slug}`,
      title: `${slugToLabel(slug)} Answer Key`,
      section: "Reveal",
      source: "reveal",
      id: `reveal-quiz-answer-${slug}`,
      description: "Static reveal route for quiz answer key",
    });
  }

  return {
    routes,
    counts: {
      total: routes.length,
      bySection: routes.reduce<Record<string, number>>((acc, route) => {
        if (
          route.source === "home" ||
          route.source === "section" ||
          route.source === "reveal"
        ) {
          return acc;
        }
        acc[route.section] = (acc[route.section] ?? 0) + 1;
        return acc;
      }, {}),
    },
  };
}
