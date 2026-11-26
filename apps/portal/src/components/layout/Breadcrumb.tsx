"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { slugToTitle } from "@/lib/utils";

interface BreadcrumbProps {
  routeHrefs: string[];
}

export function Breadcrumb({ routeHrefs }: BreadcrumbProps) {
  const pathname = usePathname();
  if (pathname === "/") return null;

  const knownRoutes = new Set(["/", ...routeHrefs]);
  const segments = pathname.split("/").filter(Boolean);
  const crumbs = segments.map((seg, i) => {
    const href = "/" + segments.slice(0, i + 1).join("/");
    return {
      label: slugToTitle(seg),
      href,
      isCurrent: i === segments.length - 1,
      isRoute: knownRoutes.has(href),
    };
  });

  return (
    <nav
      aria-label="Breadcrumb"
      className="flex flex-wrap items-center gap-1 text-sm text-gray-500"
    >
      <Link href="/" className="hover:text-gray-700">
        Home
      </Link>
      {crumbs.map((crumb) => (
        <span key={crumb.href} className="flex items-center gap-1">
          <span>/</span>
          {!crumb.isCurrent && crumb.isRoute ? (
            <Link href={crumb.href} className="hover:text-gray-700">
              {crumb.label}
            </Link>
          ) : (
            <span aria-current={crumb.isCurrent ? "page" : undefined}>
              {crumb.label}
            </span>
          )}
        </span>
      ))}
    </nav>
  );
}
