import { loadFile } from "@/content/loader";
import { listInterviewProblems } from "@/content/interviews";
import { renderPortalMarkdown } from "@/content/portal-markdown";
import { listQuizAnswerSlugs } from "@/content/quizzes";
import { renderRevealMarkdown } from "@/content/reveal-markdown";
import type { RevealMarkdownRequest } from "@/content/safe-content";

export async function renderStaticRevealMarkdown(
  request: RevealMarkdownRequest,
  currentRoute: string
): Promise<string | null> {
  const interviewProblems = listInterviewProblems();

  return renderRevealMarkdown(request, {
    solutionEntries: interviewProblems,
    quizSlugs: listQuizAnswerSlugs(),
    loadFile,
    renderMarkdown: (markdown, markdownFile) =>
      renderPortalMarkdown(markdown, markdownFile, currentRoute, {
        solutionEntries: interviewProblems,
      }),
  });
}
