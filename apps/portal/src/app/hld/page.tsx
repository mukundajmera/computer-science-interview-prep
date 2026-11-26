import { buildRegistry } from "@/content/registry";
import { ContentList } from "@/components/content/ContentList";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";

export default function HLDProjectsPage() {
  const { hldProjects } = buildRegistry();
  const completeProjects = hldProjects.filter((p) => p.status === "complete");
  const comingSoonProjects = hldProjects.filter((p) => p.status !== "complete");

  return (
    <div>
      <PageHeader
        title="🌐 HLD Projects"
        description={`${completeProjects.length} complete system designs`}
      />

      <ContentSection>
        <ContentList items={completeProjects} />
      </ContentSection>

      {comingSoonProjects.length > 0 ? (
        <ContentSection title="Coming Soon" className="mt-8">
          <ContentList
            items={comingSoonProjects.map((project) => ({
              ...project,
              difficulty: undefined,
              disabled: true,
              status: "Coming Soon",
            }))}
          />
        </ContentSection>
      ) : null}
    </div>
  );
}
