/** Content category — determines page layout and routing */
export type ContentCategory =
  | "theory"
  | "pattern"
  | "lld-project"
  | "hld-concept"
  | "hld-project"
  | "genai-concept"
  | "genai-lld"
  | "genai-hld"
  | "coding-topic"
  | "case-study";

export type Difficulty = "beginner" | "intermediate" | "advanced";

export type ContentStatus = "complete" | "in-progress" | "coming-soon";

/** Base content item — every piece of content implements this */
export interface ContentItem {
  id: string;
  title: string;
  category: ContentCategory;
  difficulty: Difficulty;
  href: string;
  status: ContentStatus;
  /** Relative path from repo root to content directory */
  fsPath: string;
}

/** Theory article in 00-theory */
export interface TheoryArticle extends ContentItem {
  category: "theory";
  topicArea: string;
  markdownFile: string;
}

/** Design pattern in 01-design-patterns */
export interface DesignPattern extends ContentItem {
  category: "pattern";
  patternCategory: "creational" | "structural" | "behavioral";
  docs: {
    readme: string | null;
    theory: string | null;
  };
}

/** LLD project in 02-lld-projects */
export interface LLDProject extends ContentItem {
  category: "lld-project";
  docs: {
    problem: string | null;
    design: string | null;
    approach: string | null;
    walkthrough: string | null;
    rubric: string | null;
    pitfalls: string | null;
    followUps: string | null;
    strongAnswer: string | null;
  };
}

/** HLD concept in 03-hld-concepts */
export interface HLDConcept extends ContentItem {
  category: "hld-concept";
  docs: {
    theory: string | null;
    interviewQA: string | null;
  };
}

/** HLD project in 04-hld-projects */
export interface HLDProject extends ContentItem {
  category: "hld-project";
  docs: {
    problem: string | null;
    design: string | null;
    approach: string | null;
    rubric: string | null;
    pitfalls: string | null;
    followUps: string | null;
    comparison: string | null;
    strongAnswer: string | null;
  };
}

/** GenAI concept in 06-genai-systems/00-concepts */
export interface GenAIConcept extends ContentItem {
  category: "genai-concept";
  markdownFile: string;
}

/** GenAI LLD in 06-genai-systems/01-llm-lld-projects */
export interface GenAILLDProject extends ContentItem {
  category: "genai-lld";
  docs: {
    problem: string | null;
    design: string | null;
    approach: string | null;
  };
}

/** GenAI HLD in 06-genai-systems/02-llm-hld-projects */
export interface GenAIHLDProject extends ContentItem {
  category: "genai-hld";
  docs: {
    problem: string | null;
    design: string | null;
    approach: string | null;
  };
}

/** Coding topic in 05-coding-problems/<topic> */
export interface CodingTopic extends ContentItem {
  category: "coding-topic";
  topic: string;
  markdownFile: string;
}

/** Case study in case-studies/ */
export interface CaseStudy extends ContentItem {
  category: "case-study";
  markdownFile: string;
}

/** Full content registry built at build time */
export interface ContentRegistry {
  theory: TheoryArticle[];
  patterns: DesignPattern[];
  lldProjects: LLDProject[];
  hldConcepts: HLDConcept[];
  hldProjects: HLDProject[];
  genaiConcepts: GenAIConcept[];
  genaiLLD: GenAILLDProject[];
  genaiHLD: GenAIHLDProject[];
  codingTopics: CodingTopic[];
  caseStudies: CaseStudy[];
}
