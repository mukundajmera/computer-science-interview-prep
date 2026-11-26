import { notFound } from "next/navigation";
import { buildRegistry } from "@/content/registry";
import { loadMarkdownSections } from "@/content/markdown-sections";
import { ContentArticlePage } from "@/components/content/ContentArticlePage";

interface Props {
  params: { project: string };
}

export function generateStaticParams() {
  const { genaiHLD } = buildRegistry();
  return genaiHLD.map((p) => ({
    project: p.id.replace("genai-hld-", ""),
  }));
}

export default async function GenAIHLDPage({ params }: Props) {
  const { genaiHLD } = buildRegistry();
  const project = genaiHLD.find(
    (p) => p.id === `genai-hld-${params.project}`
  );
  if (!project) notFound();

  const tabs = await loadMarkdownSections(
    project.docs,
    [
      { key: "problem", label: "Problem" },
      { key: "design", label: "Design" },
      { key: "approach", label: "Approach" },
    ] as const,
    project.href
  );

  return (
    <ContentArticlePage
      title={project.title}
      difficulty={project.difficulty}
      contentId={project.id}
      sections={tabs}
      emptyText="Content coming soon."
    />
  );
}
