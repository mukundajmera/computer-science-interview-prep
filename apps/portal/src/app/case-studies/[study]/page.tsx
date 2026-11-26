import { notFound } from "next/navigation";
import { buildRegistry } from "@/content/registry";
import { loadFile } from "@/content/loader";
import { renderPortalMarkdown } from "@/content/portal-markdown";
import { ContentArticlePage } from "@/components/content/ContentArticlePage";

interface Props {
  params: { study: string };
}

export function generateStaticParams() {
  const { caseStudies } = buildRegistry();
  return caseStudies.map((s) => ({
    study: s.id.replace("case-study-", ""),
  }));
}

export default async function CaseStudyPage({ params }: Props) {
  const { caseStudies } = buildRegistry();
  const study = caseStudies.find(
    (s) => s.id === `case-study-${params.study}`
  );
  if (!study) notFound();

  const raw = loadFile(study.markdownFile);
  if (!raw) {
    return (
      <ContentArticlePage
        title={study.title}
        difficulty={study.difficulty}
        sections={[]}
        emptyText="Content coming soon."
      />
    );
  }

  const { html } = await renderPortalMarkdown(raw, study.markdownFile, study.href);

  return (
    <ContentArticlePage
      title={study.title}
      difficulty={study.difficulty}
      contentId={study.id}
      sections={[{ html }]}
    />
  );
}
