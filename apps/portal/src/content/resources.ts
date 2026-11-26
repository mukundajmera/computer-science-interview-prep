import { fileExists, listDirs, listMarkdownFiles } from "@/content/loader";
import {
  compareResourceCategorySlugs,
  getResourceCategoryDetails,
  isPublicResourceCategorySlug,
} from "@/content/resource-policy";
import { isBlockedBySourceProvenance } from "@/content/source-provenance";
import { slugToTitle } from "@/lib/utils";

export interface ResourceCategory {
  slug: string;
  label: string;
  description: string;
}

export interface ResourceEntry {
  id: string;
  title: string;
  href: string;
  categorySlug: string;
  category: string;
  markdownFile: string;
}

let cachedResourceCategories: ResourceCategory[] | null = null;
let cachedResourceCategoryEntries: ResourceEntry[] | null = null;
let cachedResourceEntries: ResourceEntry[] | null = null;

function categoryAllowedRoots(slug: string): string[] {
  return [`resources/${slug}`];
}

function categoryFor(slug: string): ResourceCategory | null {
  return listResourceCategories().find((category) => category.slug === slug) ?? null;
}

export function listResourceCategories(): ResourceCategory[] {
  if (cachedResourceCategories) return cachedResourceCategories;

  cachedResourceCategories = listDirs("resources", { allowedRoots: ["resources"] })
    .filter((slug) => isPublicResourceCategorySlug(slug))
    .filter((slug) =>
      fileExists(`resources/${slug}/README.md`, {
        allowedRoots: categoryAllowedRoots(slug),
      })
    )
    .sort(compareResourceCategorySlugs)
    .map((slug) => {
      const details = getResourceCategoryDetails(slug);
      return {
        slug,
        label: details.label,
        description: details.description,
      };
    });

  return cachedResourceCategories;
}

export function getResourceCategory(slug: string): ResourceCategory | null {
  return categoryFor(slug);
}

export function listResourceCategoryEntries(): ResourceEntry[] {
  if (cachedResourceCategoryEntries) return cachedResourceCategoryEntries;

  cachedResourceCategoryEntries = listResourceCategories().map((category) => ({
    id: `resource-category-${category.slug}`,
    title: category.label,
    href: `/resources/${category.slug}`,
    categorySlug: category.slug,
    category: "Resources",
    markdownFile: `resources/${category.slug}/README.md`,
  }));

  return cachedResourceCategoryEntries;
}

export function listResourceEntries(): ResourceEntry[] {
  if (cachedResourceEntries) return cachedResourceEntries;

  cachedResourceEntries = listResourceCategories().flatMap((category) =>
    listMarkdownFiles(`resources/${category.slug}`, {
      allowedRoots: categoryAllowedRoots(category.slug),
    })
      .filter((file) => file !== "README.md")
      .filter((file) => !isBlockedBySourceProvenance(`resources/${category.slug}/${file}`))
      .map((file) => {
        const slug = file.replace(/\.md$/, "");
        return {
          id: `resource-${category.slug}-${slug}`,
          title: slugToTitle(slug),
          href: `/resources/${category.slug}/${slug}`,
          categorySlug: category.slug,
          category: category.label,
          markdownFile: `resources/${category.slug}/${file}`,
        };
      })
  );

  return cachedResourceEntries;
}

export function getResourceEntry(
  categorySlug: string,
  resourceSlug: string
): ResourceEntry | null {
  const category = categoryFor(categorySlug);
  if (!category) return null;

  return (
    listResourceEntries().find(
      (entry) =>
        entry.categorySlug === category.slug &&
        entry.markdownFile === `resources/${category.slug}/${resourceSlug}.md`
    ) ?? null
  );
}

export function getResourceEntryAllowedRoots(entry: ResourceEntry): string[] {
  return categoryAllowedRoots(entry.categorySlug);
}
