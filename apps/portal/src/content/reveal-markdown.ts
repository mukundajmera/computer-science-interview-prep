import {
  resolveRevealMarkdownPath,
  type ResolveRevealOptions,
} from "./safe-content";

export interface RevealMarkdownDependencies extends ResolveRevealOptions {
  loadFile: (relativePath: string) => string | null;
  renderMarkdown: (
    markdown: string,
    relativePath: string
  ) => Promise<{ html: string }>;
}

export async function renderRevealMarkdown(
  request: unknown,
  dependencies: RevealMarkdownDependencies
): Promise<string | null> {
  const relativePath = resolveRevealMarkdownPath(request, dependencies);
  if (!relativePath) return null;

  const raw = dependencies.loadFile(relativePath);
  if (!raw) return null;

  const { html } = await dependencies.renderMarkdown(raw, relativePath);
  return html;
}
