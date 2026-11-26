import { notFound } from "next/navigation";
import { MarkdownRenderer } from "@/components/content/MarkdownRenderer";
import { loadFile } from "@/content/loader";
import { listInterviewProblems } from "@/content/interviews";
import { renderPortalMarkdown } from "@/content/portal-markdown";
import {
  getResourceEntry,
  getResourceEntryAllowedRoots,
  listResourceEntries,
} from "@/content/resources";

interface Props {
  params: {
    category: string;
    resource: string;
  };
}

export function generateStaticParams() {
  return listResourceEntries().map((entry) => ({
    category: entry.categorySlug,
    resource: entry.markdownFile.split("/").pop()?.replace(/\.md$/, "") ?? "",
  }));
}

export default async function ResourceDetailPage({ params }: Props) {
  const entry = getResourceEntry(params.category, params.resource);
  if (!entry) notFound();

  const raw = loadFile(entry.markdownFile, {
    allowedRoots: getResourceEntryAllowedRoots(entry),
  });
  if (!raw) notFound();

  const { html } = await renderPortalMarkdown(
    raw,
    entry.markdownFile,
    entry.href,
    {
      solutionEntries: listInterviewProblems(),
    }
  );

  return (
    <div>
      <div className="mb-5">
        <p className="text-sm font-medium text-blue-700">{entry.category}</p>
        <h1 className="mt-1 text-2xl font-bold">{entry.title}</h1>
      </div>
      <MarkdownRenderer html={html} />
    </div>
  );
}
