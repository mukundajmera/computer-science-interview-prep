import { ProgressDashboard } from "@/components/progress/ProgressDashboard";
import { buildRegistry } from "@/content/registry";
import { PORTAL_SECTIONS } from "@/lib/sections";

export default function ProgressPage() {
  const registry = buildRegistry();
  const registryMap: Record<string, { id: string; title: string; category: string }> = {};
  
  [
    ...registry.theory,
    ...registry.patterns,
    ...registry.lldProjects,
    ...registry.hldConcepts,
    ...registry.hldProjects,
    ...registry.genaiConcepts,
    ...registry.genaiLLD,
    ...registry.genaiHLD,
    ...registry.codingTopics,
    ...registry.caseStudies,
  ].forEach(item => {
    registryMap[item.id] = { id: item.id, title: item.title, category: item.category };
  });

  return <ProgressDashboard knownIds={Object.keys(registryMap)} registryMap={registryMap} sections={PORTAL_SECTIONS} />;
}
