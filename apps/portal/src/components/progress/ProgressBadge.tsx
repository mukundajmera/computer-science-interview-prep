"use client";

import { useProgress } from "./use-progress";

export function ProgressBadge({ totalItems }: { totalItems: number }) {
  const { completedCount } = useProgress();
  const pct = totalItems > 0 ? Math.round((completedCount / totalItems) * 100) : 0;

  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-800">
      {pct}% complete
    </span>
  );
}
