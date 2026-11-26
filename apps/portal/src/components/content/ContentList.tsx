import Link from "next/link";
import type { Difficulty } from "@/content/types";
import { DifficultyBadge } from "@/components/content/DifficultyBadge";

export interface ContentListItem {
  id: string;
  href: string;
  title: string;
  difficulty?: Difficulty;
  status?: string;
  disabled?: boolean;
  description?: string;
  meta?: string;
  icon?: string;
  actionLabel?: string;
}

interface ContentListProps {
  items: ContentListItem[];
  columns?: "one" | "two";
  emptyText?: string;
  variant?: "compact" | "comfortable";
}

export function ContentList({
  items,
  columns = "two",
  emptyText = "No items available yet.",
  variant = "compact",
}: ContentListProps) {
  if (items.length === 0) {
    return <p className="text-gray-500">{emptyText}</p>;
  }

  const gridClass = columns === "two" ? "grid gap-2 sm:grid-cols-2" : "space-y-2";
  const spacingClass = variant === "comfortable" ? "p-4" : "p-3";
  const hoverClass = variant === "comfortable" ? "hover:shadow-md" : "hover:bg-gray-50";

  return (
    <div className={gridClass}>
      {items.map((item) => {
        const content = (
          <>
            <span className="flex min-w-0 items-center gap-3">
              {item.icon ? (
                <span className="shrink-0 text-2xl" aria-hidden="true">
                  {item.icon}
                </span>
              ) : null}
              <span className="min-w-0">
                <span className="block font-medium">{item.title}</span>
                {item.meta ? (
                  <span className="mt-1 inline-block rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                    {item.meta}
                  </span>
                ) : null}
                {item.description ? (
                  <span className="mt-1 block text-sm text-gray-500">
                    {item.description}
                  </span>
                ) : null}
              </span>
            </span>
            {item.difficulty ? (
              <DifficultyBadge difficulty={item.difficulty} />
            ) : item.status ? (
              <span className="shrink-0 text-xs uppercase tracking-wide text-gray-500">
                {item.status}
              </span>
            ) : item.actionLabel ? (
              <span className="shrink-0 text-sm text-gray-500">
                {item.actionLabel}
              </span>
            ) : null}
          </>
        );

        if (item.disabled) {
          return (
            <div
              key={item.id}
              aria-disabled="true"
              className={`flex items-center justify-between gap-3 rounded-lg border border-dashed text-gray-500 ${spacingClass}`}
            >
              {content}
            </div>
          );
        }

        return (
          <Link
            key={item.id}
            href={item.href}
            className={`flex items-center justify-between gap-3 rounded-lg border transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 ${spacingClass} ${hoverClass}`}
          >
            {content}
          </Link>
        );
      })}
    </div>
  );
}
