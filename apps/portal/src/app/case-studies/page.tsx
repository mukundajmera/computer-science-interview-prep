import { buildRegistry } from "@/content/registry";
import { ContentList } from "@/components/content/ContentList";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";

export default function CaseStudiesPage() {
  const { caseStudies } = buildRegistry();

  return (
    <div>
      <PageHeader
        title="📊 Case Studies"
        description="Real company architecture deep-dives"
      />

      <ContentSection>
        <ContentList items={caseStudies} />
      </ContentSection>
    </div>
  );
}
