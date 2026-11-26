import type { Difficulty } from "@/content/types";
import type { MarkdownSection } from "@/content/markdown-sections";
import { DifficultyBadge } from "@/components/content/DifficultyBadge";
import { MarkdownRenderer } from "@/components/content/MarkdownRenderer";
import { MarkCompleteButton } from "@/components/progress/MarkCompleteButton";

interface ContentArticlePageProps {
  title: string;
  subtitle?: string;
  difficulty: Difficulty;
  contentId?: string;
  sections: MarkdownSection[];
  emptyText?: string;
  moreSections?: MarkdownSection[];
  moreTitle?: string;
}

function MarkdownSectionList({ sections }: { sections: MarkdownSection[] }) {
  return (
    <div className="space-y-8">
      {sections.map((section, index) => (
        <section key={section.label ?? index}>
          {section.label ? (
            <h2 className="mb-3 text-lg font-semibold text-gray-700">
              {section.label}
            </h2>
          ) : null}
          <MarkdownRenderer html={section.html} />
        </section>
      ))}
    </div>
  );
}

export function ContentArticlePage({
  title,
  subtitle,
  difficulty,
  contentId,
  sections,
  emptyText = "No documentation available yet.",
  moreSections = [],
  moreTitle = "More",
}: ContentArticlePageProps) {
  return (
    <div>
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-bold">{title}</h1>
        <DifficultyBadge difficulty={difficulty} />
      </div>
      {subtitle ? (
        <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
      ) : null}

      {contentId ? (
        <div className="mt-4">
          <MarkCompleteButton contentId={contentId} />
        </div>
      ) : null}

      {sections.length > 0 ? (
        <div className="mt-6">
          <MarkdownSectionList sections={sections} />
        </div>
      ) : (
        <p className="mt-6 text-gray-500">{emptyText}</p>
      )}

      {moreSections.length > 0 ? (
        <div className="mt-10 border-t pt-8">
          <h2 className="mb-6 text-xl font-bold text-gray-800">{moreTitle}</h2>
          <MarkdownSectionList sections={moreSections} />
        </div>
      ) : null}
    </div>
  );
}
