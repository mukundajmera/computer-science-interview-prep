import type { Metadata } from "next";
import "./globals.css";
import { buildSectionSummaries } from "@/content/section-summaries";
import { buildSearchIndex } from "@/content/search-index";
import { buildRegistry } from "@/content/registry";
import { AppShell } from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "System Design Prep",
  description:
    "The ultimate system-design and GenAI system-design preparation portal",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const searchEntries = buildSearchIndex();
  const sections = buildSectionSummaries();
  const routeHrefs = searchEntries.map((entry) => entry.href);

  const registry = buildRegistry();
  const totalItems = [
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
  ].length;

  return (
    <html lang="en">
      <body>
        <AppShell
          searchEntries={searchEntries}
          sections={sections}
          routeHrefs={routeHrefs}
          totalItems={totalItems}
        >
          {children}
        </AppShell>
      </body>
    </html>
  );
}
