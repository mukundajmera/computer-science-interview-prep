import { notFound } from "next/navigation";
import { buildRegistry } from "@/content/registry";
import { loadMarkdownSections } from "@/content/markdown-sections";
import { ContentArticlePage } from "@/components/content/ContentArticlePage";

interface Props {
  params: { concept: string };
}

export function generateStaticParams() {
  const { hldConcepts } = buildRegistry();
  return hldConcepts.map((c) => ({
    concept: c.id.replace("hld-concept-", ""),
  }));
}

export default async function HLDConceptPage({ params }: Props) {
  const { hldConcepts } = buildRegistry();
  const concept = hldConcepts.find(
    (c) => c.id === `hld-concept-${params.concept}`
  );
  if (!concept) notFound();

  const docEntries = [
    { key: "theory", label: "Theory" },
    { key: "interviewQA", label: "Interview Q&A" },
  ] as const;
  const tabs = await loadMarkdownSections(concept.docs, docEntries, concept.href);

  return (
    <ContentArticlePage
      title={concept.title}
      difficulty={concept.difficulty}
      contentId={concept.id}
      sections={tabs}
    />
  );
}
