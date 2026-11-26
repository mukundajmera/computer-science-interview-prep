import { notFound } from "next/navigation";
import { buildRegistry } from "@/content/registry";
import { loadFile } from "@/content/loader";
import { renderPortalMarkdown } from "@/content/portal-markdown";
import { ContentArticlePage } from "@/components/content/ContentArticlePage";

interface Props {
  params: { category: string; pattern: string };
}

export function generateStaticParams() {
  const { patterns } = buildRegistry();
  return patterns.map((p) => ({
    category: p.patternCategory,
    pattern: p.id.replace(`pattern-${p.patternCategory}-`, ""),
  }));
}

export default async function PatternPage({ params }: Props) {
  const { patterns } = buildRegistry();
  const pattern = patterns.find(
    (p) =>
      p.patternCategory === params.category &&
      p.id === `pattern-${params.category}-${params.pattern}`
  );
  if (!pattern) notFound();

  // Prefer THEORY.md, fall back to README.md
  const mdPath = pattern.docs.theory ?? pattern.docs.readme;
  const raw = mdPath ? loadFile(mdPath) : null;
  const html = raw && mdPath
    ? (await renderPortalMarkdown(raw, mdPath, pattern.href)).html
    : null;

  return (
    <ContentArticlePage
      title={pattern.title}
      subtitle={`Category: ${pattern.patternCategory}`}
      difficulty={pattern.difficulty}
      contentId={pattern.id}
      sections={html ? [{ html }] : []}
      emptyText="No documentation available for this pattern yet."
    />
  );
}
