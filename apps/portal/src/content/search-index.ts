import { listInterviewProblems } from "@/content/interviews";
import { listQuizAnswerSlugs, listQuizSlugs } from "@/content/quizzes";
import { buildRegistry } from "@/content/registry";
import {
  listResourceCategoryEntries,
  listResourceEntries,
} from "@/content/resources";
import { createRouteManifest } from "@/content/route-manifest";

export interface SearchEntry {
  href: string;
  title: string;
  section: string;
  description: string;
  searchText: string;
}

let cachedSearchIndex: SearchEntry[] | null = null;

export function buildSearchIndex(): SearchEntry[] {
  if (cachedSearchIndex) return cachedSearchIndex;

  const manifest = createRouteManifest({
    registry: buildRegistry(),
    resourceEntries: [
      ...listResourceCategoryEntries(),
      ...listResourceEntries(),
    ],
    quizSlugs: listQuizSlugs(),
    quizAnswerSlugs: listQuizAnswerSlugs(),
    interviewProblems: listInterviewProblems(),
  });

  cachedSearchIndex = manifest.routes
    .filter((route) => route.source !== "reveal")
    .map((route) => {
      const description =
        route.description ?? route.difficulty ?? route.status ?? "";
      return {
        href: route.href,
        title: route.title,
        section: route.section,
        description,
        searchText: [route.title, route.section, description, route.href]
          .join(" ")
          .toLowerCase(),
      };
    });

  return cachedSearchIndex;
}
