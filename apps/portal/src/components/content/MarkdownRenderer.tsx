/** Renders pre-processed HTML from markdown */
export function MarkdownRenderer({ html }: { html: string }) {
  return (
    <article
      className="prose prose-slate max-w-none prose-headings:scroll-mt-20 prose-a:text-blue-600 prose-code:rounded prose-code:bg-gray-100 prose-code:px-1 prose-code:py-0.5 prose-pre:bg-gray-900"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
