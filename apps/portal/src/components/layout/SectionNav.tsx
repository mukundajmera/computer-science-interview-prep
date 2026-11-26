"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { isActiveSectionRoute } from "@/lib/navigation";
import type { PortalSectionSummary } from "@/content/section-summaries";

interface SectionNavProps {
  sections: PortalSectionSummary[];
}

export function SectionNav({ sections }: SectionNavProps) {
  const pathname = usePathname();

  const sidebarSections = sections.filter(
    (s) => !["/progress", "/flashcards", "/resources"].includes(s.href)
  );

  return (
    <nav className="flex flex-col gap-1">
      {sidebarSections.map((section) => {
        const active = isActiveSectionRoute(pathname, section.href);
        return (
          <Link
            key={section.href}
            href={section.href}
            className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
              active
                ? "bg-blue-50 font-semibold text-blue-700"
                : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            }`}
          >
            <span>{section.emoji}</span>
            <span className="min-w-0 flex-1 truncate">{section.label}</span>
            <span className="shrink-0 text-xs text-gray-400">
              {section.summary}
            </span>
          </Link>
        );
      })}
    </nav>
  );
}
