import { buildRegistry } from "@/content/registry";
import { loadFile } from "@/content/loader";
import { renderPortalMarkdown } from "@/content/portal-markdown";
import { MarkdownRenderer } from "@/components/content/MarkdownRenderer";
import { ContentList } from "@/components/content/ContentList";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";

export default async function CodingPage() {
  const { codingTopics } = buildRegistry();

  const overviewRaw = loadFile("05-coding-problems/README.md");
  const overviewHtml = overviewRaw
    ? (await renderPortalMarkdown(
        overviewRaw,
        "05-coding-problems/README.md",
        "/coding"
      )).html
    : "";

  return (
    <div>
      <PageHeader
        title="🔁 Coding Patterns"
        description="Algorithm pattern packs used in coding rounds that often accompany system design interviews."
      />

      {overviewHtml && (
        <ContentSection>
          <MarkdownRenderer html={overviewHtml} />
        </ContentSection>
      )}

      <ContentSection title="Available Pattern Packs" className="mt-8">
        <ContentList items={codingTopics} />
      </ContentSection>
    </div>
  );
}
