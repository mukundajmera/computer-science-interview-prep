import { buildRegistry } from "@/content/registry";
import { ContentList } from "@/components/content/ContentList";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";
import { slugToTitle } from "@/lib/utils";

export default function TheoryPage() {
  const { theory } = buildRegistry();

  // Group by topic area
  const grouped = theory.reduce(
    (acc, item) => {
      if (!acc[item.topicArea]) acc[item.topicArea] = [];
      acc[item.topicArea].push(item);
      return acc;
    },
    {} as Record<string, typeof theory>
  );

  return (
    <div>
      <PageHeader
        title="📚 Theory"
        description="Core CS fundamentals for system design"
      />

      {Object.entries(grouped).map(([area, articles]) => (
        <ContentSection key={area} title={slugToTitle(area)}>
          <ContentList items={articles} columns="one" />
        </ContentSection>
      ))}
    </div>
  );
}
