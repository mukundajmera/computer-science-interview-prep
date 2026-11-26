const CATEGORY_SLUG_PATTERN = /^[a-z0-9][a-z0-9-]*$/;

const PUBLIC_RESOURCE_CATEGORIES = new Set([
  "study-plans",
  "cheatsheets",
  "interview-tips",
  "templates",
]);

const RESOURCE_CATEGORY_DETAILS: Record<
  string,
  { label: string; description: string; order: number }
> = {
  "study-plans": {
    label: "Study Plans",
    description: "Time-boxed paths through the curriculum",
    order: 10,
  },
  cheatsheets: {
    label: "Cheatsheets",
    description: "Compact interview references",
    order: 20,
  },
  "interview-tips": {
    label: "Interview Tips",
    description: "Communication, round strategy, and checklists",
    order: 30,
  },
  templates: {
    label: "Templates",
    description: "Practice worksheets and reusable answer structures",
    order: 40,
  },
};

function titleFromSlug(slug: string): string {
  return slug
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export function isPublicResourceCategorySlug(slug: string): boolean {
  return CATEGORY_SLUG_PATTERN.test(slug) && PUBLIC_RESOURCE_CATEGORIES.has(slug);
}

export function getResourceCategoryDetails(slug: string): {
  label: string;
  description: string;
  order: number;
} {
  return (
    RESOURCE_CATEGORY_DETAILS[slug] ?? {
      label: titleFromSlug(slug),
      description: "Auto-discovered learner resources",
      order: 100,
    }
  );
}

export function compareResourceCategorySlugs(a: string, b: string): number {
  const left = getResourceCategoryDetails(a);
  const right = getResourceCategoryDetails(b);

  return left.order - right.order || left.label.localeCompare(right.label);
}
