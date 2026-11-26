import Link from "next/link";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { SearchBox } from "@/components/layout/SearchBox";
import { SectionNav } from "@/components/layout/SectionNav";
import { ProgressBadge } from "@/components/progress/ProgressBadge";
import { MobileNav } from "@/components/layout/MobileNav";
import type { PortalSectionSummary } from "@/content/section-summaries";
import type { SearchEntry } from "@/content/search-index";

export function AppShell({
  children,
  searchEntries,
  sections,
  routeHrefs,
  totalItems,
}: {
  children: React.ReactNode;
  searchEntries: SearchEntry[];
  sections: PortalSectionSummary[];
  routeHrefs: string[];
  totalItems: number;
}) {
  return (
    <>
      <header className="sticky top-0 z-30 border-b bg-white/95 backdrop-blur">
        <div className="mx-auto flex min-h-14 max-w-screen-2xl flex-wrap items-center gap-3 px-4 py-2">
          <MobileNav sections={sections} />
          <Link
            href="/"
            aria-label="System Design Prep home"
            className="flex min-w-fit items-center gap-2 font-bold"
          >
            🎯 <span className="hidden sm:inline">System Design Prep</span>
          </Link>
          <div className="min-w-0 flex-1 flex justify-end gap-4 items-center">
            <Link href="/progress" className="hidden sm:inline text-sm font-medium text-gray-600 hover:text-gray-900">Progress</Link>
            <Link href="/flashcards" className="hidden sm:inline text-sm font-medium text-gray-600 hover:text-gray-900">Flashcards</Link>
            <Link href="/resources" className="hidden sm:inline text-sm font-medium text-gray-600 hover:text-gray-900">Resources</Link>
            <ProgressBadge totalItems={totalItems} />
            <div className="w-full max-w-xs ml-4">
              <SearchBox entries={searchEntries} />
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-screen-2xl">
        <aside className="sticky top-14 hidden h-[calc(100vh-3.5rem)] w-56 shrink-0 overflow-y-auto border-r p-4 md:block">
          <SectionNav sections={sections} />
        </aside>

        <main className="min-w-0 flex-1 px-4 sm:px-6 py-4">
          <Breadcrumb routeHrefs={routeHrefs} />
          <div className="mt-4 prose-table:block prose-table:overflow-x-auto sm:prose-pre:max-w-none prose-pre:max-w-[calc(100vw-2rem)]">
            {children}
          </div>
          <style>{`
            .prose pre { overflow-x: auto; }
            @media (max-width: 640px) {
              .flex.gap-2 { flex-wrap: wrap; }
            }
          `}</style>
        </main>
      </div>
    </>
  );
}
