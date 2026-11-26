/** Convert a slug like "parking-lot" to title case "Parking Lot" */
export function slugToTitle(slug: string): string {
  return slug
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

import { PORTAL_SECTIONS, type PortalSection } from "@/lib/sections";

export const SECTIONS = PORTAL_SECTIONS.map((section) => ({
  ...section,
  description: section.description.replace(/^\d+\s+/, ""),
}));

export type { PortalSection as SectionInfo };
