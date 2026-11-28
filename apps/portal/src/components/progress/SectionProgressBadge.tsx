"use client";

import { useProgress } from "./use-progress";

interface SectionProgressBadgeProps {
  itemIds: string[];
}

/** Percent of a section's items the visitor has completed. Reads the
 * browser's localStorage, so it renders 0% until mounted and then fills in;
 * that keeps the server-rendered markup and first client render identical. */
export function SectionProgressBadge({ itemIds }: SectionProgressBadgeProps) {
  const { progress } = useProgress();
  if (itemIds.length === 0) return null;

  const completed = itemIds.filter((id) => progress.completed[id]).length;
  const pct = Math.round((completed / itemIds.length) * 100);

  return (
    <span
      className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700"
      title={`${completed} of ${itemIds.length} completed`}
    >
      {pct}% done
    </span>
  );
}
