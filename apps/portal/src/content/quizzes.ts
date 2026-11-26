import { fileExists, listMarkdownFiles } from "@/content/loader";
import { isBlockedBySourceProvenance } from "@/content/source-provenance";
import { slugToTitle } from "@/lib/utils";

export interface QuizEntry {
  id: string;
  slug: string;
  title: string;
  href: string;
  markdownFile: string;
  answerMarkdownFile: string | null;
  hasAnswers: boolean;
  icon: string;
  actionLabel: string;
}

let cachedQuizEntries: QuizEntry[] | null = null;

export function listQuizEntries(): QuizEntry[] {
  if (cachedQuizEntries) return cachedQuizEntries;

  cachedQuizEntries = listMarkdownFiles("quizzes")
    .filter((file) => file.endsWith("-quiz.md"))
    .filter((file) => !isBlockedBySourceProvenance(`quizzes/${file}`))
    .map((file) => {
      const slug = file.replace(/-quiz\.md$/, "");
      const answerMarkdownFile = `quizzes/answers/${slug}-answers.md`;
      const hasAnswers =
        fileExists(answerMarkdownFile) &&
        !isBlockedBySourceProvenance(answerMarkdownFile);
      return {
        id: `quiz-${slug}`,
        slug,
        title: `${slugToTitle(slug)} Quiz`,
        href: `/quizzes/${slug}`,
        markdownFile: `quizzes/${file}`,
        answerMarkdownFile: hasAnswers ? answerMarkdownFile : null,
        hasAnswers,
        icon: "📋",
        actionLabel: "Take quiz",
      };
    });

  return cachedQuizEntries;
}

export function listQuizSlugs(): string[] {
  return listQuizEntries().map((quiz) => quiz.slug);
}

export function listQuizAnswerSlugs(): string[] {
  return listQuizEntries()
    .filter((quiz) => quiz.hasAnswers)
    .map((quiz) => quiz.slug);
}

export function getQuizEntry(slug: string): QuizEntry | null {
  return listQuizEntries().find((quiz) => quiz.slug === slug) ?? null;
}
