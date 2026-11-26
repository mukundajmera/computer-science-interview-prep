import { buildRegistry } from "@/content/registry";
import { slugToTitle } from "@/lib/utils";
import { ContentList } from "@/components/content/ContentList";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";
import { notFound } from "next/navigation";

interface Props {
  params: { category: string };
}

export function generateStaticParams() {
  return [
    { category: "creational" },
    { category: "structural" },
    { category: "behavioral" },
  ];
}

export default function PatternCategoryPage({ params }: Props) {
  const { patterns } = buildRegistry();
  const items = patterns.filter(
    (p) => p.patternCategory === params.category
  );
  if (items.length === 0) notFound();

  return (
    <div>
      <PageHeader title={`${slugToTitle(params.category)} Patterns`} />
      <ContentSection>
        <ContentList items={items} />
      </ContentSection>
    </div>
  );
}
