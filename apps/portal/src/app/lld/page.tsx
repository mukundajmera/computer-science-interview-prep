import { buildRegistry } from "@/content/registry";
import { ContentList } from "@/components/content/ContentList";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";

export default function LLDPage() {
  const { lldProjects } = buildRegistry();

  const groups: Record<string, typeof lldProjects> = {
    Beginner: lldProjects.filter((p) => p.difficulty === "beginner"),
    Intermediate: lldProjects.filter((p) => p.difficulty === "intermediate"),
    Advanced: lldProjects.filter((p) => p.difficulty === "advanced"),
  };

  return (
    <div>
      <PageHeader
        title="🏗️ LLD Projects"
        description={`${lldProjects.length} low-level design projects with Java & Python`}
      />

      {Object.entries(groups).map(([level, items]) => (
        <ContentSection key={level} title={level}>
          <ContentList items={items} />
        </ContentSection>
      ))}
    </div>
  );
}
