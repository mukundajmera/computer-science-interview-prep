"use client";

import { useProgress } from "./use-progress";

export function MarkCompleteButton({ contentId }: { contentId: string }) {
  const { isCompleted, toggleComplete } = useProgress();
  const done = isCompleted(contentId);

  return (
    <button
      onClick={() => toggleComplete(contentId)}
      aria-pressed={done}
      className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
        done
          ? "bg-green-100 text-green-800 hover:bg-green-200"
          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
      }`}
    >
      {done ? "✅ Completed" : "☐ Mark Complete"}
    </button>
  );
}
