import { notFound } from "next/navigation";
import { MarkdownRenderer } from "@/components/content/MarkdownRenderer";
import { listInterviewProblems } from "@/content/interviews";
import { renderStaticRevealMarkdown } from "@/content/static-reveal";

interface Props {
  params: { type: string; slug: string };
}

export function generateStaticParams() {
  return listInterviewProblems().map((problem) => ({
    type: problem.type,
    slug: problem.slug,
  }));
}

export default async function StaticSolutionRevealPage({ params }: Props) {
  const problem = listInterviewProblems().find(
    (candidate) => candidate.type === params.type && candidate.slug === params.slug
  );
  if (!problem) notFound();

  const html = await renderStaticRevealMarkdown(
    {
      kind: "solution",
      type: problem.type,
      slug: problem.slug,
    },
    `/reveal/solution/${problem.type}/${problem.slug}`
  );
  if (!html) notFound();

  return (
    <article data-reveal-content="">
      <MarkdownRenderer html={html} />
    </article>
  );
}
