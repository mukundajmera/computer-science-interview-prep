import { notFound } from "next/navigation";
import { buildRegistry } from "@/content/registry";
import { loadFile } from "@/content/loader";
import { renderPortalMarkdown } from "@/content/portal-markdown";
import { ContentArticlePage } from "@/components/content/ContentArticlePage";

interface Props {
  params: { topic: string };
}

export function generateStaticParams() {
  const { codingTopics } = buildRegistry();
  return codingTopics.map((topic) => ({
    topic: topic.topic,
  }));
}

export default async function CodingTopicPage({ params }: Props) {
  const { codingTopics } = buildRegistry();
  const topic = codingTopics.find((item) => item.topic === params.topic);
  if (!topic) notFound();

  const raw = loadFile(topic.markdownFile);
  if (!raw) {
    return (
      <ContentArticlePage
        title={topic.title}
        difficulty={topic.difficulty}
        sections={[]}
        emptyText="Content coming soon."
      />
    );
  }

  const { html } = await renderPortalMarkdown(raw, topic.markdownFile, topic.href);

  return (
    <ContentArticlePage
      title={topic.title}
      difficulty={topic.difficulty}
      contentId={topic.id}
      sections={[{ html }]}
    />
  );
}
