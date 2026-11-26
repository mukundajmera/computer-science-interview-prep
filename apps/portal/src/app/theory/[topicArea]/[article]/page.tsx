import { notFound } from "next/navigation";
import { buildRegistry } from "@/content/registry";
import { loadFile } from "@/content/loader";
import { renderPortalMarkdown } from "@/content/portal-markdown";
import { ContentArticlePage } from "@/components/content/ContentArticlePage";

interface Props {
  params: { topicArea: string; article: string };
}

export function generateStaticParams() {
  const { theory } = buildRegistry();
  return theory.map((a) => ({
    topicArea: a.topicArea,
    article: a.markdownFile.replace(/^.*\//, "").replace(/\.md$/, ""),
  }));
}

export default async function TheoryArticlePage({ params }: Props) {
  const { theory } = buildRegistry();
  const article = theory.find(
    (a) =>
      a.topicArea === params.topicArea &&
      a.markdownFile.endsWith(`${params.article}.md`)
  );
  if (!article) notFound();

  const raw = loadFile(article.markdownFile);
  if (!raw) notFound();

  const { html } = await renderPortalMarkdown(raw, article.markdownFile, article.href);

  return (
    <ContentArticlePage
      title={article.title}
      difficulty={article.difficulty}
      contentId={article.id}
      sections={[{ html }]}
    />
  );
}
