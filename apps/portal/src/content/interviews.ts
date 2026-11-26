import {
  INTERVIEW_PROBLEMS as CURATED_INTERVIEW_PROBLEMS,
  type InterviewProblem,
} from "@/components/interview/interview-data";
import { listMarkdownFiles } from "@/content/loader";
import { isBlockedBySourceProvenance } from "@/content/source-provenance";

const CODING_PACK_ORDER = [
  "two-pointers",
  "sliding-window",
  "binary-search",
  "bfs-dfs",
  "dynamic-programming",
  "greedy",
  "backtracking",
  "heap-priority-queue",
  "trie",
  "union-find",
];

const CODING_PACK_TITLES: Record<string, string> = {
  "bfs-dfs": "BFS/DFS",
  "heap-priority-queue": "Heap / Priority Queue",
  "union-find": "Union-Find",
};

const CODING_PACK_DIFFICULTY: Record<
  string,
  InterviewProblem["difficulty"]
> = {
  "dynamic-programming": "advanced",
};

let cachedInterviewProblems: InterviewProblem[] | null = null;

function titleFromSlug(slug: string): string {
  return (
    CODING_PACK_TITLES[slug] ??
    slug
      .split("-")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ")
  );
}

function codingPackSortKey(slug: string): number {
  const index = CODING_PACK_ORDER.indexOf(slug);
  return index === -1 ? Number.MAX_SAFE_INTEGER : index;
}

export function listCodingInterviewProblems(): InterviewProblem[] {
  return listMarkdownFiles("solutions")
    .filter((file) => /^coding-[a-z0-9-]+\.md$/.test(file))
    .filter((file) => !isBlockedBySourceProvenance(`solutions/${file}`))
    .map((file) => {
      const slug = file.replace(/^coding-/, "").replace(/\.md$/, "");
      return {
        slug: `${slug}-pack`,
        title: `${titleFromSlug(slug)} Pack`,
        type: "coding" as const,
        difficulty: CODING_PACK_DIFFICULTY[slug] ?? "intermediate",
        solutionPath: `solutions/${file}`,
      };
    })
    .sort(
      (left, right) =>
        codingPackSortKey(left.slug.replace(/-pack$/, "")) -
          codingPackSortKey(right.slug.replace(/-pack$/, "")) ||
        left.slug.localeCompare(right.slug)
    );
}


export function listLldInterviewProblems(): InterviewProblem[] {
  return listMarkdownFiles("solutions")
    .filter((file) => /^lld-[a-z0-9-]+\.md$/.test(file))
    .filter((file) => !isBlockedBySourceProvenance(`solutions/${file}`))
    .map((file) => {
      const slug = file.replace(/^lld-/, "").replace(/\.md$/, "");
      const curated = CURATED_INTERVIEW_PROBLEMS.find(
        (p) => p.type === "lld" && p.slug === slug
      );
      return {
        slug,
        title: curated ? curated.title : titleFromSlug(slug),
        type: "lld" as const,
        difficulty: curated ? curated.difficulty : "advanced",
        solutionPath: `solutions/${file}`,
      };
    })
    .sort((a, b) => a.title.localeCompare(b.title));
}

export function listInterviewProblems(): InterviewProblem[] {
  if (cachedInterviewProblems) return cachedInterviewProblems;

  const curatedProblems = CURATED_INTERVIEW_PROBLEMS.filter(
    (problem) =>
      problem.type !== "coding" &&
      !isBlockedBySourceProvenance(problem.solutionPath)
  );
  
  const nonLldCurated = curatedProblems.filter(p => p.type !== "lld");
  
  const firstLldProblemIndex = curatedProblems.findIndex(
    (problem) => problem.type === "lld"
  );
  
  const insertAt =
    firstLldProblemIndex === -1
      ? nonLldCurated.length
      : firstLldProblemIndex;

  cachedInterviewProblems = [
    ...nonLldCurated.slice(0, insertAt),
    ...listLldInterviewProblems(),
    ...listCodingInterviewProblems(),
    ...nonLldCurated.slice(insertAt),
  ];

  return cachedInterviewProblems;
}
