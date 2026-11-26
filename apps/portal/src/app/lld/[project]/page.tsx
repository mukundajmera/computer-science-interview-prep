import { notFound } from "next/navigation";
import { buildRegistry } from "@/content/registry";
import { loadMarkdownSections } from "@/content/markdown-sections";
import { ContentArticlePage } from "@/components/content/ContentArticlePage";

interface Props {
  params: { project: string };
}

export function generateStaticParams() {
  const { lldProjects } = buildRegistry();
  return lldProjects.map((p) => ({
    project: p.id.replace("lld-", ""),
  }));
}

export default async function LLDProjectPage({ params }: Props) {
  const { lldProjects } = buildRegistry();
  const project = lldProjects.find(
    (p) => p.id === `lld-${params.project}`
  );
  if (!project) notFound();

  const docEntries = [
    { key: "problem", label: "Problem" },
    { key: "design", label: "Design" },
    { key: "approach", label: "Approach" },
    { key: "walkthrough", label: "Code Walkthrough" },
  ] as const;
  const tabs = await loadMarkdownSections(project.docs, docEntries, project.href);

  const depthEntries = [
    { key: "rubric", label: "📊 Scoring Rubric" },
    { key: "pitfalls", label: "⚠️ Common Pitfalls" },
    { key: "followUps", label: "🔄 Follow-Up Variants" },
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
