"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { LearningPath } from "./LearningPathData";

export function LearningPathCard({ path }: { path: LearningPath }) {
  const STORAGE_KEY = `learning_path_progress_${path.id}`;
  const [completedItems, setCompletedItems] = useState<Record<string, boolean>>({});

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setCompletedItems(JSON.parse(saved));
      }
    } catch (e) {
      console.error("Failed to load progress from localStorage", e);
    }
  }, [STORAGE_KEY]);

  const toggleItem = (id: string) => {
    setCompletedItems((prev) => {
      const next = { ...prev, [id]: !prev[id] };
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch (e) {
        console.error("Failed to save progress to localStorage", e);
      }
      return next;
    });
  };

  const allItems = path.milestones.flatMap((m) => m.items);
  const completedCount = allItems.filter((i) => completedItems[i.id]).length;
  const progressPercent = allItems.length > 0 ? Math.round((completedCount / allItems.length) * 100) : 0;

  return (
    <div className="space-y-8 mb-12">
      {/* Active Track Header & Progress Card */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {path.title}
            </h2>
            <p className="mt-1 text-sm font-medium text-blue-600 dark:text-blue-400">
              {path.subtitle}
            </p>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 max-w-2xl">
              {path.description}
            </p>
          </div>
          <div className="rounded-lg bg-gray-50 p-4 text-center dark:bg-gray-800/60 min-w-[160px]">
            <div className="text-3xl font-extrabold text-blue-600 dark:text-blue-400">
              {progressPercent}%
            </div>
            <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {completedCount} / {allItems.length} Completed
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
          <div
            className="h-full bg-blue-600 transition-all duration-300 dark:bg-blue-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-gray-500 dark:text-gray-400 border-t border-gray-100 pt-3 dark:border-gray-800/80">
          <div>
            <span className="font-semibold text-gray-700 dark:text-gray-300">Target Role:</span>{" "}
            {path.targetRole}
          </div>
          <div>•</div>
          <div>
            <span className="font-semibold text-gray-700 dark:text-gray-300">Pacing:</span> ~
            {path.durationWeeks} weeks
          </div>
        </div>
      </div>

      {/* Milestones List */}
      <div className="space-y-6">
        {path.milestones.map((milestone, idx) => (
          <div
            key={idx}
            className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900"
          >
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
              {milestone.category}
            </h3>

            <div className="space-y-3">
              {milestone.items.map((item) => {
                const isDone = !!completedItems[item.id];
                return (
                  <div
                    key={item.id}
                    className={`flex items-start justify-between gap-4 rounded-lg border p-4 transition-all ${
                      isDone
                        ? "border-emerald-200 bg-emerald-50/40 dark:border-emerald-900/40 dark:bg-emerald-950/20"
                        : "border-gray-200 bg-gray-50/50 hover:border-gray-300 dark:border-gray-800 dark:bg-gray-800/40 dark:hover:border-gray-700"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={isDone}
                        onChange={() => toggleItem(item.id)}
                        className="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800"
                      />
                      <div>
                        <Link
                          href={item.href}
                          className={`text-base font-semibold hover:underline ${
                            isDone
                              ? "text-gray-500 line-through dark:text-gray-400"
                              : "text-gray-900 dark:text-gray-100"
                          }`}
                        >
                          {item.title}
                        </Link>
                        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                          {item.description}
                        </p>
                      </div>
                    </div>

                    <div className="shrink-0 text-right">
                      <span className="inline-block rounded-full bg-gray-200/70 px-2.5 py-0.5 text-xs font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-300">
                        ~{item.estimatedHours}h
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
