import { notFound } from "next/navigation";
import { buildRegistry } from "@/content/registry";
import { loadFile } from "@/content/loader";
import { renderPortalMarkdown } from "@/content/portal-markdown";
import { ContentArticlePage } from "@/components/content/ContentArticlePage";

interface Props {
  params: { concept: string };
}

export function generateStaticParams() {
  const { genaiConcepts } = buildRegistry();
  return genaiConcepts.map((c) => ({
    concept: c.id.replace("genai-concept-", ""),
  }));
}

export default async function GenAIConceptPage({ params }: Props) {
  const { genaiConcepts } = buildRegistry();
  const concept = genaiConcepts.find(
    (c) => c.id === `genai-concept-${params.concept}`
  );
  if (!concept) notFound();

  const raw = loadFile(concept.markdownFile);
  if (!raw) {
    return (
      <ContentArticlePage
        title={concept.title}
        difficulty={concept.difficulty}
        sections={[]}
        emptyText="Content coming soon."
      />
    );
  }

  const { html } = await renderPortalMarkdown(raw, concept.markdownFile, concept.href);

  return (
    <ContentArticlePage
      title={concept.title}
      difficulty={concept.difficulty}
      contentId={concept.id}
      sections={[{ html }]}
    />
  );
}
