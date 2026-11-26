import { buildRegistry } from "@/content/registry";
import { ContentList } from "@/components/content/ContentList";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";

export default function GenAIPage() {
  const { genaiConcepts, genaiLLD, genaiHLD } = buildRegistry();

  return (
    <div>
      <PageHeader
        title="🤖 GenAI Systems"
        description="Generative AI / LLM system design"
      />

      <ContentSection title="Concepts">
        <ContentList items={genaiConcepts} />
      </ContentSection>

      <ContentSection title="LLD Components">
        <ContentList items={genaiLLD} />
      </ContentSection>

      <ContentSection title="HLD Systems">
        <ContentList items={genaiHLD} />
      </ContentSection>
    </div>
  );
}
