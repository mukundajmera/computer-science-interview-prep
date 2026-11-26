import { ContentList } from "@/components/content/ContentList";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";
import { listResourceCategories, listResourceEntries } from "@/content/resources";

export default function ResourcesPage() {
  const categories = listResourceCategories();
  const resources = listResourceEntries();

  return (
    <div>
      <PageHeader
        title="🧭 Resources"
        description="Study plans, cheatsheets, interview tips, and templates for focused practice."
      />

      {categories.map((category) => {
        const items = resources.filter(
          (resource) => resource.categorySlug === category.slug
        );

        return (
          <ContentSection
            key={category.slug}
            title={category.label}
            description={category.description}
          >
            <ContentList items={items} />
          </ContentSection>
        );
      })}
    </div>
  );
}
