"use client";

import { useRef } from "react";
import { useProgress } from "./use-progress";
import type { PortalSection } from "@/lib/sections";

interface Props {
  knownIds: string[];
  registryMap: Record<string, { id: string; title: string; category: string }>;
  sections: PortalSection[];
}

export function ProgressDashboard({ knownIds, registryMap, sections }: Props) {
  const { progress, completedCount, toggleComplete, removeLegacy, importProgress } = useProgress(knownIds);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const entries = Object.entries(progress.completed).sort(
    ([, a], [, b]) => new Date(b).getTime() - new Date(a).getTime()
  );
  const legacyEntries = Object.entries(progress.legacyCompleted).sort(
    ([, a], [, b]) => new Date(b).getTime() - new Date(a).getTime()
  );

  const totalKnown = knownIds.length;
  const overallPct = totalKnown > 0 ? Math.round((completedCount / totalKnown) * 100) : 0;

  const categoryToSectionLabel: Record<string, string> = {
    "theory": "Theory",
    "pattern": "Design Patterns",
    "lld-project": "LLD Projects",
    "hld-concept": "HLD Concepts",
    "hld-project": "HLD Projects",
    "genai-concept": "GenAI Systems",
    "genai-lld": "GenAI Systems",
    "genai-hld": "GenAI Systems",
    "coding-topic": "Coding Patterns",
    "case-study": "Case Studies",
  };

  const sectionStats: Record<string, { total: number; completed: number }> = {};
  sections.forEach(s => {
    sectionStats[s.label] = { total: 0, completed: 0 };
  });

  Object.values(registryMap).forEach(item => {
    const label = categoryToSectionLabel[item.category];
    if (label && sectionStats[label]) {
      sectionStats[label].total++;
      if (progress.completed[item.id]) {
        sectionStats[label].completed++;
      }
    }
  });

  const handleExport = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(progress, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "sdp-progress.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      if (importProgress(content)) {
        alert("Progress imported successfully!");
      } else {
        alert("Failed to import progress data.");
      }
    };
    reader.readAsText(file);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">📈 Progress Dashboard</h1>
          <p className="mt-1 text-gray-600">
            {completedCount} of {totalKnown} completed ({overallPct}%)
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={handleExport} className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">Export JSON</button>
          <button onClick={() => fileInputRef.current?.click()} className="rounded bg-gray-200 px-4 py-2 text-sm font-medium text-gray-800 hover:bg-gray-300">Import JSON</button>
          <input type="file" accept=".json" ref={fileInputRef} onChange={handleImport} className="hidden" />
        </div>
      </div>
      
      <div className="mt-4 h-4 w-full rounded-full bg-gray-200 overflow-hidden">
        <div className="h-full bg-blue-600 transition-all duration-500" style={{ width: `${overallPct}%` }} />
      </div>

      <div className="mt-8 grid gap-6 md:grid-cols-2">
        <section>
          <h2 className="text-xl font-semibold mb-4">By Section</h2>
          <div className="space-y-4">
            {sections.filter(s => sectionStats[s.label] && sectionStats[s.label].total > 0).map(s => {
              const stat = sectionStats[s.label];
              const pct = Math.round((stat.completed / stat.total) * 100);
              return (
                <div key={s.label} className="rounded-lg border p-4">
                  <div className="flex justify-between text-sm font-medium mb-2">
                    <span>{s.emoji} {s.label}</span>
                    <span>{stat.completed} / {stat.total} ({pct}%)</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-gray-100 overflow-hidden">
                    <div className="h-full bg-green-500 transition-all duration-500" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          {entries.length === 0 ? (
            <p className="text-gray-500">No topics completed yet.</p>
          ) : (
            <ul className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
              {entries.map(([id, timestamp]) => {
                const item = registryMap[id];
                return (
                  <li key={id} className="flex items-center justify-between rounded-lg border p-3 bg-white">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate" title={item?.title || id}>{item?.title || id}</p>
                      <p className="text-xs text-gray-500">{new Date(timestamp).toLocaleDateString()} • {item?.category || "Unknown"}</p>
                    </div>
                    <button onClick={() => toggleComplete(id)} aria-label={`Remove ${item?.title || id}`} className="ml-4 shrink-0 text-sm text-red-600 hover:text-red-800">Remove</button>
                  </li>
                );
              })}
            </ul>
          )}
        </section>
      </div>

      {legacyEntries.length > 0 && (
        <section className="mt-8 border-t pt-6">
          <h2 className="text-lg font-semibold">Legacy or Unmapped Progress</h2>
          <ul className="mt-3 space-y-2 max-h-64 overflow-y-auto">
            {legacyEntries.map(([id, timestamp]) => (
              <li key={id} className="flex items-center justify-between rounded-lg border border-amber-200 bg-amber-50 p-3">
                <div>
                  <span className="font-medium">{id}</span>
                  <span className="ml-2 text-xs text-amber-700">{new Date(timestamp).toLocaleDateString()}</span>
                </div>
                <button onClick={() => removeLegacy(id)} aria-label={`Remove ${id}`} className="text-sm text-red-600 hover:text-red-800">Remove</button>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
