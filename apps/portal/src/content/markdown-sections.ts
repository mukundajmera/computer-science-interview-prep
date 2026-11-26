import { loadFile } from "@/content/loader";
import { renderPortalMarkdown } from "@/content/portal-markdown";
import { isBlockedBySourceProvenance } from "@/content/source-provenance";

export interface MarkdownSection {
  label?: string;
  html: string;
}

interface MarkdownSectionEntry<TDocs extends object> {
  key: keyof TDocs;
  label: string;
}

export async function loadMarkdownSections<TDocs extends object>(
  docs: TDocs,
  entries: readonly MarkdownSectionEntry<TDocs>[],
  currentRoute: string
): Promise<MarkdownSection[]> {
  const sections: Array<MarkdownSection | null> = await Promise.all(
    entries.map(async ({ key, label }) => {
      const markdownPath = docs[key];
      if (typeof markdownPath !== "string" || !markdownPath) return null;
      if (isBlockedBySourceProvenance(markdownPath)) return null;

      const raw = loadFile(markdownPath);
      if (!raw) return null;

      const { html } = await renderPortalMarkdown(raw, markdownPath, currentRoute);
      return { label, html };
    })
  );

  return sections.filter((section): section is MarkdownSection => section !== null);
}
