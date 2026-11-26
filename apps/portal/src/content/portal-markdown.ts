import { renderMarkdown } from "@/content/loader";
import { createPortalHrefRewriter } from "@/content/resource-links";
import { assertSourcePathAllowedForPortal } from "@/content/source-provenance";

interface PortalMarkdownOptions {
  solutionEntries?: Array<{
    type: string;
    slug: string;
    solutionPath: string;
  }>;
}

export function renderPortalMarkdown(
  content: string,
  markdownFile: string,
  currentRoute: string,
  options: PortalMarkdownOptions = {}
) {
  assertSourcePathAllowedForPortal(markdownFile);
  return renderMarkdown(content, {
    rewriteHref: createPortalHrefRewriter(markdownFile, currentRoute, options),
  });
}
