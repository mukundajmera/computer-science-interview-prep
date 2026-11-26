import { listInterviewProblems } from "@/content/interviews";
import { listQuizEntries } from "@/content/quizzes";
import { buildRegistry } from "@/content/registry";
import { listResourceEntries } from "@/content/resources";
import type { ContentRegistry } from "@/content/types";
import { PORTAL_SECTIONS, type PortalSection } from "@/lib/sections";

export interface PortalSectionSummary extends PortalSection {
  summary: string;
}

interface SectionSummaryInput {
  registry: ContentRegistry;
  quizCount: number;
  resourceCount: number;
  interviewCount: number;
  sections?: PortalSection[];
}

function formatCount(count: number, singular: string, plural = `${singular}s`) {
  return `${count} ${count === 1 ? singular : plural}`;
}

function countUnique(values: string[]) {
  return new Set(values).size;
}

export function createSectionSummaries({
  registry,
  quizCount,
  resourceCount,
  interviewCount,
  sections = PORTAL_SECTIONS,
}: SectionSummaryInput): PortalSectionSummary[] {
  const genaiCount =
    registry.genaiConcepts.length +
    registry.genaiLLD.length +
    registry.genaiHLD.length;

  const summaries = new Map<
    string,
    Pick<PortalSectionSummary, "description" | "summary">
  >([
    [
      "/theory",
      {
        description: `Auto-discovered from ${formatCount(
          countUnique(registry.theory.map((article) => article.topicArea)),
          "topic area"
        )}`,
        summary: formatCount(registry.theory.length, "article"),
      },
    ],
    [
      "/patterns",
      {
        description: `Auto-discovered from ${formatCount(
          countUnique(registry.patterns.map((pattern) => pattern.patternCategory)),
          "pattern group"
        )}`,
        summary: formatCount(registry.patterns.length, "pattern"),
      },
    ],
    [
      "/coding",
      {
        description: "Auto-discovered from coding problem folders",
        summary: formatCount(registry.codingTopics.length, "topic"),
      },
    ],
    [
      "/lld",
      {
        description: "Auto-discovered from LLD project folders",
        summary: formatCount(registry.lldProjects.length, "project"),
      },
    ],
    [
      "/hld-concepts",
      {
        description: "Auto-discovered from HLD concept folders",
        summary: formatCount(registry.hldConcepts.length, "concept"),
      },
    ],
    [
      "/hld",
      {
        description: "Auto-discovered from HLD project folders",
        summary: formatCount(registry.hldProjects.length, "project"),
      },
    ],
    [
      "/genai",
      {
        description: `${formatCount(registry.genaiConcepts.length, "concept")}, ${formatCount(
          registry.genaiLLD.length,
          "LLD project"
        )}, ${formatCount(registry.genaiHLD.length, "HLD project")}`,
        summary: formatCount(genaiCount, "module"),
      },
    ],
    [
      "/case-studies",
      {
        description: "Auto-discovered from case-study folders",
        summary: formatCount(registry.caseStudies.length, "study", "studies"),
      },
    ],
    [
      "/interview",
      {
        description: "Guided practice sessions",
        summary: formatCount(interviewCount, "drill"),
      },
    ],
    [
      "/quizzes",
      {
        description: "Auto-discovered from quiz markdown files",
        summary: formatCount(quizCount, "quiz", "quizzes"),
      },
    ],
    [
      "/resources",
      {
        description: "Auto-discovered learner resources",
        summary: formatCount(resourceCount, "resource"),
      },
    ],
  ]);

  return sections.map((section) => ({
    ...section,
    ...(summaries.get(section.href) ?? {
      description: section.description,
      summary: "Auto-discovered",
    }),
  }));
}

export function buildSectionSummaries(): PortalSectionSummary[] {
  return createSectionSummaries({
    registry: buildRegistry(),
    quizCount: listQuizEntries().length,
    resourceCount: listResourceEntries().length,
    interviewCount: listInterviewProblems().length,
  });
}
