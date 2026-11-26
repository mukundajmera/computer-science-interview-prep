import { buildRegistry } from "@/content/registry";
import { ContentList } from "@/components/content/ContentList";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";

export default function HLDConceptsPage() {
  const { hldConcepts } = buildRegistry();

  return (
    <div>
      <PageHeader
        title="⚙️ HLD Concepts"
        description={`${hldConcepts.length} system design building blocks`}
      />

      <ContentSection>
        <ContentList items={hldConcepts} />
      </ContentSection>
    </div>
  );
}
