import { slugToTitle } from "@/lib/utils";
import { CODING_SUPPORT_DIRS } from "@/content/coding-policy";
import { listDirs, listMarkdownFiles, fileExists } from "./loader";
import {
  filterAllowedPortalSourcePath,
  isBlockedBySourceProvenance,
} from "./source-provenance";
import type {
  ContentRegistry,
  TheoryArticle,
  DesignPattern,
  LLDProject,
  HLDConcept,
  HLDProject,
  GenAIConcept,
  GenAILLDProject,
  GenAIHLDProject,
  CodingTopic,
  CaseStudy,
  Difficulty,
} from "./types";

/** Difficulty lookup — items not listed default to "intermediate" */
const DIFFICULTY: Record<string, Difficulty> = {
  // LLD Projects - Beginner
  "parking-lot": "beginner",
  "connect-four": "beginner",
  "tic-tac-toe": "beginner",
  "vending-machine": "beginner",
  "snake-and-ladder": "beginner",
  "lru-cache": "beginner",
  "deck-of-cards": "beginner",
  "traffic-signal": "beginner",

  // LLD Projects - Intermediate
  "library-management": "intermediate",
  "amazon-locker": "intermediate",
  "elevator-system": "intermediate",
  "atm-system": "intermediate",
  "hotel-reservation": "intermediate",
  "hotel-management-system": "intermediate",
  "movie-ticket-booking": "intermediate",
  "online-shopping-cart": "intermediate",
  "restaurant-management": "intermediate",
  "car-rental": "intermediate",
  "inventory-management": "intermediate",
  "online-code-judge": "intermediate",
  "notification-service": "intermediate",
  "text-editor": "intermediate",
  "dynamic-config-service": "intermediate",
  "distributed-counter": "intermediate",
  "circuit-breaker": "intermediate",
  "in-memory-event-bus": "intermediate",
  "logging-framework": "intermediate",
  "task-management-system": "intermediate",
  "pub-sub-system": "intermediate",
  "food-delivery-platform": "intermediate",

  // LLD Projects - Advanced
  "chess-game": "advanced",
  "splitwise": "advanced",
  "rate-limiter": "advanced",
  "ride-sharing-system": "advanced",
  "file-system": "advanced",
  "linkedin-connection": "advanced",
  "stack-overflow": "advanced",
  "job-scheduler": "advanced",
  "web-crawler": "advanced",
  "ad-click-aggregator": "advanced",
  "payment-system": "advanced",
  "payment-gateway-router": "advanced",
  "market-alert-engine": "advanced",
  "key-value-store-lsm": "advanced",
  "finite-state-machine": "advanced",
  "message-queue": "advanced",
  "webhook-dispatcher": "advanced",
  "multi-policy-cache": "advanced",
  "youtube-top-k": "advanced",
  "instagram-core": "advanced",
  "price-tracking-service": "advanced",
  "social-post-search": "advanced",
  "live-comments": "advanced",
  "online-auction": "advanced",

  // HLD Projects - Beginner
  "url-shortener": "beginner",
  "pastebin": "beginner",

  // HLD Projects - Intermediate
  "web-crawler-hld": "intermediate",
  "news-feed-system": "intermediate",
  "chat-service": "intermediate",
  "notification-system": "intermediate",
  "distributed-cache": "intermediate",
  "proximity-service": "intermediate",
  "rate-limiter-hld": "intermediate",
  "leaderboard-system": "intermediate",

  // HLD Projects - Advanced
  "ride-sharing-hld": "advanced",
  "payment-system-hld": "advanced",
  "video-streaming": "advanced",
  "collaborative-doc-editor": "advanced",
  "distributed-cloud-storage-s3": "advanced",
  "distributed-messaging-queue": "advanced",
  "metric-monitoring-logging": "advanced",
  "digital-wallet": "advanced",
  "brokerage-platform": "advanced",
  "bot-detection-platform": "advanced",
  "content-moderation-platform": "advanced",

  // Theory Topics - Beginner
  "big-o-notation": "beginner",
  "acid-transactions": "beginner",
  "cap-theorem": "beginner",

  // Theory Topics - Intermediate
  "bloom-filter": "intermediate",
  "hyperloglog": "intermediate",
  "consistent-hashing": "intermediate",

  // Theory Topics - Advanced
  "advanced-hash-tables": "advanced",
  "raft-consensus": "advanced",
  "distributed-transactions-2pc-saga": "advanced",
  "merkle-tree": "advanced",
};

function getDifficulty(id: string): Difficulty {
  return DIFFICULTY[id] ?? "intermediate";
}

function checkDoc(base: string, name: string): string | null {
  const p = `${base}/${name}`;
  return fileExists(p) ? filterAllowedPortalSourcePath(p) : null;
}

/** Memoized registry — computed once per process (build or dev server) */
let _cachedRegistry: ContentRegistry | null = null;

/** Build the full content registry by scanning the repo tree (memoized) */
export function buildRegistry(): ContentRegistry {
  if (_cachedRegistry) return _cachedRegistry;

  // --- 00-theory ---
  const theory: TheoryArticle[] = [];
  for (const area of listDirs("00-theory")) {
    for (const file of listMarkdownFiles(`00-theory/${area}`)) {
      const slug = file.replace(/\.md$/, "");
      const markdownFile = `00-theory/${area}/${file}`;
      if (isBlockedBySourceProvenance(markdownFile)) continue;
      theory.push({
        id: `theory-${area}-${slug}`,
        title: slugToTitle(slug),
        category: "theory",
        difficulty: "beginner",
        href: `/theory/${area}/${slug}`,
        status: "complete",
        fsPath: `00-theory/${area}`,
        topicArea: area,
        markdownFile,
      });
    }
  }

  // --- 01-design-patterns ---
  const patterns: DesignPattern[] = [];
  for (const cat of listDirs("01-design-patterns") as Array<
    "creational" | "structural" | "behavioral"
  >) {
    if (!["creational", "structural", "behavioral"].includes(cat)) continue;
    for (const pat of listDirs(`01-design-patterns/${cat}`)) {
      const base = `01-design-patterns/${cat}/${pat}`;
      patterns.push({
        id: `pattern-${cat}-${pat}`,
        title: slugToTitle(pat),
        category: "pattern",
        patternCategory: cat as "creational" | "structural" | "behavioral",
        difficulty: "intermediate",
        href: `/patterns/${cat}/${pat}`,
        status: "complete",
        fsPath: base,
        docs: {
          readme: checkDoc(base, "README.md"),
          theory: checkDoc(base, "THEORY.md"),
        },
      });
    }
  }

  // --- 02-lld-projects ---
  const lldProjects: LLDProject[] = [];
  for (const proj of listDirs("02-lld-projects")) {
    const base = `02-lld-projects/${proj}`;
    if (!checkDoc(base, "PROBLEM.md")) continue;
    lldProjects.push({
      id: `lld-${proj}`,
      title: slugToTitle(proj),
      category: "lld-project",
      difficulty: getDifficulty(proj),
      href: `/lld/${proj}`,
      status: "complete",
      fsPath: base,
      docs: {
        problem: checkDoc(base, "PROBLEM.md"),
        design: checkDoc(base, "DESIGN.md"),
        approach: checkDoc(base, "APPROACH.md"),
        walkthrough: checkDoc(base, "CODE-WALKTHROUGH.md"),
        rubric: checkDoc(base, "RUBRIC.md"),
        pitfalls: checkDoc(base, "PITFALLS.md"),
        followUps: checkDoc(base, "FOLLOW-UPS.md"),
        strongAnswer: checkDoc(base, "STRONG-ANSWER.md"),
      },
    });
  }

  // --- 03-hld-concepts ---
  const hldConcepts: HLDConcept[] = [];
  for (const concept of listDirs("03-hld-concepts")) {
    const base = `03-hld-concepts/${concept}`;
    const theory = checkDoc(base, "THEORY.md");
    const interviewQA = checkDoc(base, "INTERVIEW-QA.md");
    hldConcepts.push({
      id: `hld-concept-${concept}`,
      title: slugToTitle(concept),
      category: "hld-concept",
      difficulty: "intermediate",
      href: `/hld-concepts/${concept}`,
      status: theory && interviewQA ? "complete" : "coming-soon",
      fsPath: base,
      docs: {
        theory,
        interviewQA,
      },
    });
  }

  // --- 04-hld-projects ---
  const hldProjects: HLDProject[] = [];
  for (const proj of listDirs("04-hld-projects")) {
    const base = `04-hld-projects/${proj}`;
    const problem = checkDoc(base, "PROBLEM.md");
    const design = checkDoc(base, "DESIGN.md");
    const approach = checkDoc(base, "APPROACH.md");
    const rubric = checkDoc(base, "RUBRIC.md");
    const pitfalls = checkDoc(base, "PITFALLS.md");
    const followUps = checkDoc(base, "FOLLOW-UPS.md");
    const comparison = checkDoc(base, "COMPARISON.md");
    const strongAnswer = checkDoc(base, "STRONG-ANSWER.md");
    hldProjects.push({
      id: `hld-${proj}`,
      title: slugToTitle(proj),
      category: "hld-project",
      difficulty: getDifficulty(proj),
      href: `/hld/${proj}`,
      status: problem && design ? "complete" : "coming-soon",
      fsPath: base,
      docs: {
        problem,
        design,
        approach,
        rubric,
        pitfalls,
        followUps,
        comparison,
        strongAnswer,
      },
    });
  }

  // --- 06-genai-systems/00-concepts ---
  const genaiConcepts: GenAIConcept[] = [];
  for (const concept of listDirs("06-genai-systems/00-concepts")) {
    const base = `06-genai-systems/00-concepts/${concept}`;
    const readme = `${base}/README.md`;
    if (isBlockedBySourceProvenance(readme)) continue;
    genaiConcepts.push({
      id: `genai-concept-${concept}`,
      title: slugToTitle(concept),
      category: "genai-concept",
      difficulty: "advanced",
      href: `/genai/concepts/${concept}`,
      status: fileExists(readme) ? "complete" : "coming-soon",
      fsPath: base,
      markdownFile: readme,
    });
  }

  // --- 06-genai-systems/01-llm-lld-projects ---
  const genaiLLD: GenAILLDProject[] = [];
  for (const proj of listDirs("06-genai-systems/01-llm-lld-projects")) {
    const base = `06-genai-systems/01-llm-lld-projects/${proj}`;
    genaiLLD.push({
      id: `genai-lld-${proj}`,
      title: slugToTitle(proj),
      category: "genai-lld",
      difficulty: "advanced",
      href: `/genai/lld/${proj}`,
      status: checkDoc(base, "PROBLEM.md") ? "complete" : "coming-soon",
      fsPath: base,
      docs: {
        problem: checkDoc(base, "PROBLEM.md"),
        design: checkDoc(base, "DESIGN.md"),
        approach: checkDoc(base, "APPROACH.md"),
      },
    });
  }

  // --- 06-genai-systems/02-llm-hld-projects ---
  const genaiHLD: GenAIHLDProject[] = [];
  for (const proj of listDirs("06-genai-systems/02-llm-hld-projects")) {
    const base = `06-genai-systems/02-llm-hld-projects/${proj}`;
    genaiHLD.push({
      id: `genai-hld-${proj}`,
      title: slugToTitle(proj),
      category: "genai-hld",
      difficulty: "advanced",
      href: `/genai/hld/${proj}`,
      status: checkDoc(base, "PROBLEM.md") ? "complete" : "coming-soon",
      fsPath: base,
      docs: {
        problem: checkDoc(base, "PROBLEM.md"),
        design: checkDoc(base, "DESIGN.md"),
        approach: checkDoc(base, "APPROACH.md"),
      },
    });
  }

  // --- 05-coding-problems ---
  const codingTopics: CodingTopic[] = [];
  for (const topic of listDirs("05-coding-problems")) {
    if (CODING_SUPPORT_DIRS.has(topic)) continue;
    const base = `05-coding-problems/${topic}`;
    const readme = checkDoc(base, "README.md");
    if (isBlockedBySourceProvenance(`${base}/README.md`)) continue;
    codingTopics.push({
      id: `coding-${topic}`,
      title: slugToTitle(topic),
      category: "coding-topic",
      difficulty: "intermediate",
      href: `/coding/${topic}`,
      status: readme ? "complete" : "coming-soon",
      fsPath: base,
      topic,
      markdownFile: readme ?? `${base}/README.md`,
    });
  }

  // --- case-studies ---
  const caseStudies: CaseStudy[] = [];
  for (const study of listDirs("case-studies")) {
    const base = `case-studies/${study}`;
    const readme = `${base}/README.md`;
    if (isBlockedBySourceProvenance(readme)) continue;
    caseStudies.push({
      id: `case-study-${study}`,
      title: slugToTitle(study),
      category: "case-study",
      difficulty: "advanced",
      href: `/case-studies/${study}`,
      status: fileExists(readme) ? "complete" : "coming-soon",
      fsPath: base,
      markdownFile: readme,
    });
  }

  _cachedRegistry = {
    theory,
    patterns,
    lldProjects,
    hldConcepts,
    hldProjects,
    genaiConcepts,
    genaiLLD,
    genaiHLD,
    codingTopics,
    caseStudies,
  };

  return _cachedRegistry;
}
