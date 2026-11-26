import { notFound } from "next/navigation";
import { loadFile } from "@/content/loader";
import { renderPortalMarkdown } from "@/content/portal-markdown";
import { getQuizEntry, listQuizSlugs } from "@/content/quizzes";
import { slugToTitle } from "@/lib/utils";
import { QuizViewer } from "@/components/interview/QuizViewer";
import { getStructuredQuiz } from "@/content/quiz-parser";

interface Props {
  params: { quiz: string };
}

export function generateStaticParams() {
  return listQuizSlugs().map((quiz) => ({ quiz }));
}

export default async function QuizPage({ params }: Props) {
  const quiz = getQuizEntry(params.quiz);
  if (!quiz) notFound();

  const quizRaw = loadFile(quiz.markdownFile);
  if (!quizRaw) notFound();

  const { html: quizHtml } = await renderPortalMarkdown(
    quizRaw,
    quiz.markdownFile,
    `/quizzes/${params.quiz}`
  );
  
  let structuredQuiz = null;
  if (quiz.hasAnswers) {
      // Intentionally do not catch error so the build fails if the answer count mismatches
      structuredQuiz = getStructuredQuiz(params.quiz);
  }

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold">
        📋 {slugToTitle(params.quiz)} Quiz
      </h1>
      <QuizViewer
        quizHtml={quizHtml}
        answersHref={quiz.hasAnswers ? `../../reveal/quiz-answer/${params.quiz}/` : null}
        structuredQuiz={structuredQuiz}
      />
    </div>
  );
}
