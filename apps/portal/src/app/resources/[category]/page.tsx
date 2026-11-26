import { notFound } from "next/navigation";
import { ContentList } from "@/components/content/ContentList";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";
import {
  getResourceCategory,
  listResourceCategories,
  listResourceEntries,
} from "@/content/resources";

interface Props {
  params: {
    category: string;
  };
}

export function generateStaticParams() {
  return listResourceCategories().map((category) => ({
    category: category.slug,
  }));
}

export default function ResourceCategoryPage({ params }: Props) {
  const category = getResourceCategory(params.category);
  if (!category) notFound();

  const items = listResourceEntries().filter(
    (resource) => resource.categorySlug === category.slug
  );

  return (
    <div>
      <PageHeader title={category.label} description={category.description} />

      <ContentSection>
        <ContentList items={items} />
      </ContentSection>
    </div>
  );
}
