import { notFound } from "next/navigation";
import { buildRegistry } from "@/content/registry";
import { loadMarkdownSections } from "@/content/markdown-sections";
import { ContentArticlePage } from "@/components/content/ContentArticlePage";

interface Props {
  params: { project: string };
}

export function generateStaticParams() {
  const { hldProjects } = buildRegistry();
  return hldProjects.map((p) => ({
    project: p.id.replace("hld-", ""),
  }));
}

export default async function HLDProjectPage({ params }: Props) {
  const { hldProjects } = buildRegistry();
  const project = hldProjects.find(
    (p) => p.id === `hld-${params.project}`
  );
  if (!project) notFound();

  const docEntries = [
    { key: "problem", label: "Problem" },
    { key: "design", label: "Design" },
    { key: "approach", label: "Approach" },
  ] as const;
  const tabs = await loadMarkdownSections(project.docs, docEntries, project.href);

  const depthEntries = [
    { key: "rubric", label: "📊 Scoring Rubric" },
    { key: "pitfalls", label: "⚠️ Common Pitfalls" },
    { key: "followUps", label: "🔄 Follow-Up Variants" },
    { key: "comparison", label: "🆚 Comparison with Similar Systems" },
    { key: "strongAnswer", label: "✅ Strong Answer Outline" },
  ] as const;
  const depthTabs = await loadMarkdownSections(
    project.docs,
    depthEntries,
    project.href
  );

  return (
    <ContentArticlePage
      title={project.title}
      difficulty={project.difficulty}
      contentId={project.id}
      sections={tabs}
      moreSections={depthTabs}
    />
  );
}
