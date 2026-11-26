import fs from "fs";
import matter from "gray-matter";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";
import { unified } from "unified";
import type { Element, Root, RootContent } from "hast";
import type { Plugin } from "unified";
import remarkParse from "remark-parse";
import remarkRehype from "remark-rehype";
import rehypeStringify from "rehype-stringify";
import {
  resolveRepoDirectoryPath,
  resolveRepoMarkdownPath,
} from "./safe-content";

interface RenderMarkdownOptions {
  rewriteHref?: (href: string) => string;
}

interface ContentPathOptions {
  allowedRoots?: string[];
}

function isElement(node: Root | RootContent): node is Element {
  return node.type === "element";
}

function rewriteLinkNodes(
  node: Root | RootContent,
  rewriteHref: (href: string) => string
) {
  if (
    isElement(node) &&
    node.tagName === "a" &&
    node.properties &&
    typeof node.properties.href === "string"
  ) {
    node.properties.href = rewriteHref(node.properties.href);
  }

  if ("children" in node) {
    for (const child of node.children) {
      rewriteLinkNodes(child, rewriteHref);
    }
  }
}

function rehypeRewriteLinks(rewriteHref: (href: string) => string): Plugin<[], Root> {
  return function attachRewriteLinks() {
    return function transform(tree: Root) {
      rewriteLinkNodes(tree, rewriteHref);
    };
  };
}

/** Read a file from the repo root, returning null if it doesn't exist */
export function loadFile(
  relativePath: string,
  options: ContentPathOptions = {}
): string | null {
  const fullPath = resolveRepoMarkdownPath(relativePath, options);
  return fullPath ? fs.readFileSync(fullPath, "utf-8") : null;
}

/** Check if a file exists relative to repo root */
export function fileExists(
  relativePath: string,
  options: ContentPathOptions = {}
): boolean {
  return resolveRepoMarkdownPath(relativePath, options) !== null;
}

/** List subdirectories of a path relative to repo root */
export function listDirs(
  relativePath: string,
  options: ContentPathOptions = {}
): string[] {
  const fullPath = resolveRepoDirectoryPath(relativePath, options);
  if (!fullPath) return [];
  return fs
    .readdirSync(fullPath, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith("."))
    .map((d) => d.name)
    .sort();
}

/** List markdown files in a directory */
export function listMarkdownFiles(
  relativePath: string,
  options: ContentPathOptions = {}
): string[] {
  const fullPath = resolveRepoDirectoryPath(relativePath, options);
  if (!fullPath) return [];
  return fs
    .readdirSync(fullPath)
    .filter((f) => f.endsWith(".md") && !f.startsWith("."))
    .sort();
}

/** Parse markdown to sanitized HTML string.
 *  Uses rehype-sanitize to prevent XSS — critical because the output
 *  is rendered downstream via dangerouslySetInnerHTML. */
export async function renderMarkdown(
  content: string,
  options: RenderMarkdownOptions = {}
): Promise<{ html: string; frontmatter: Record<string, unknown> }> {
  const { data, content: md } = matter(content);
  const processor = unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkRehype);

  if (options.rewriteHref) {
    processor.use(rehypeRewriteLinks(options.rewriteHref));
  }

  const result = await processor
    .use(rehypeSanitize)
    .use(rehypeStringify)
    .process(md);
  return { html: result.toString(), frontmatter: data };
}

/** Extract first H1 heading from markdown content */
export function extractTitle(content: string): string | null {
  const match = content.match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : null;
}
