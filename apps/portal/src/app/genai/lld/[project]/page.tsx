import { notFound } from "next/navigation";
import { buildRegistry } from "@/content/registry";
import { loadMarkdownSections } from "@/content/markdown-sections";
import { ContentArticlePage } from "@/components/content/ContentArticlePage";

interface Props {
  params: { project: string };
}

export function generateStaticParams() {
  const { genaiLLD } = buildRegistry();
  return genaiLLD.map((p) => ({
    project: p.id.replace("genai-lld-", ""),
  }));
}

export default async function GenAILLDPage({ params }: Props) {
  const { genaiLLD } = buildRegistry();
  const project = genaiLLD.find(
    (p) => p.id === `genai-lld-${params.project}`
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
