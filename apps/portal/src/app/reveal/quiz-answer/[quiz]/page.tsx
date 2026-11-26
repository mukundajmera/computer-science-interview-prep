import { notFound } from "next/navigation";
import { MarkdownRenderer } from "@/components/content/MarkdownRenderer";
import { listQuizAnswerSlugs } from "@/content/quizzes";
import { renderStaticRevealMarkdown } from "@/content/static-reveal";

interface Props {
  params: { quiz: string };
}

export function generateStaticParams() {
  return listQuizAnswerSlugs().map((quiz) => ({ quiz }));
}

export default async function StaticQuizAnswerRevealPage({ params }: Props) {
  const html = await renderStaticRevealMarkdown(
    {
      kind: "quiz-answer",
      slug: params.quiz,
    },
    `/reveal/quiz-answer/${params.quiz}`
  );
  if (!html) notFound();

  return (
    <article data-reveal-content="">
      <MarkdownRenderer html={html} />
    </article>
  );
}
