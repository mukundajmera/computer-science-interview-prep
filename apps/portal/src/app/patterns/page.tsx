import { buildRegistry } from "@/content/registry";
import { ContentList } from "@/components/content/ContentList";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";
import { slugToTitle } from "@/lib/utils";

export default function PatternsPage() {
  const { patterns } = buildRegistry();

  const grouped = patterns.reduce(
    (acc, item) => {
      if (!acc[item.patternCategory]) acc[item.patternCategory] = [];
      acc[item.patternCategory].push(item);
      return acc;
    },
    {} as Record<string, typeof patterns>
  );

  const order = ["creational", "structural", "behavioral"] as const;

  return (
    <div>
      <PageHeader
        title="🎨 Design Patterns"
        description={`${patterns.length} GoF patterns in Java & Python`}
      />

      {order.map((cat) => {
        const items = grouped[cat] ?? [];
        return (
          <ContentSection key={cat} title={slugToTitle(cat)}>
            <ContentList items={items} />
          </ContentSection>
        );
      })}
    </div>
  );
}
