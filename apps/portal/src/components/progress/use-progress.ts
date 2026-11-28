"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import {
  emptyProgressState,
  mergeProgressStates,
  normalizeProgressState,
  parseProgressExportFile,
  parseProgressState,
  STORAGE_KEY,
  type ParseProgressExportResult,
  type ProgressState,
} from "../../lib/progress-schema";

function loadProgress(knownIds?: readonly string[]): ProgressState {
  if (typeof window === "undefined") return emptyProgressState();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return parseProgressState(raw, { knownIds });
  } catch {
    console.warn("sdp-progress: corrupt data in localStorage, resetting");
  }
  return emptyProgressState();
}

function saveProgress(state: ProgressState) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    console.warn("sdp-progress: storage failure, unable to save");
  }
}

export function useProgress(knownIds?: readonly string[]) {
  const normalizeOptions = useMemo(() => ({ knownIds }), [knownIds]);
  const [progress, setProgress] = useState<ProgressState>(emptyProgressState());

  const loadAndSet = useCallback(() => {
    const next = loadProgress(knownIds);
    setProgress(next);
  }, [knownIds]);

  useEffect(() => {
    loadAndSet();
    const handleStorage = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY) {
        loadAndSet();
      }
    };
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, [loadAndSet]);

  const isCompleted = useCallback((id: string) => !!progress.completed[id], [progress]);

  const toggleComplete = useCallback((id: string) => {
    setProgress((prev) => {
      const next = { ...prev, completed: { ...prev.completed } };
      if (next.completed[id]) {
        delete next.completed[id];
      } else {
        next.completed[id] = new Date().toISOString();
      }
      const normalized = normalizeProgressState(next, normalizeOptions);
      saveProgress(normalized);
      return normalized;
    });
  }, [normalizeOptions]);

  const removeLegacy = useCallback((id: string) => {
    setProgress((prev) => {
      const next = {
        ...prev,
        completed: { ...prev.completed },
        legacyCompleted: { ...prev.legacyCompleted },
      };
      delete next.legacyCompleted[id];
      const normalized = normalizeProgressState(next, normalizeOptions);
      saveProgress(normalized);
      return normalized;
    });
  }, [normalizeOptions]);

  const validateProgressFile = useCallback(
    (rawJson: string): ParseProgressExportResult =>
      parseProgressExportFile(rawJson, normalizeOptions),
    [normalizeOptions]
  );

  const importProgress = useCallback(
    (rawJson: string, mode: "merge" | "replace"): ParseProgressExportResult => {
      const parsed = parseProgressExportFile(rawJson, normalizeOptions);
      if (!parsed.ok) return parsed;
      const next =
        mode === "merge" ? mergeProgressStates(progress, parsed.state) : parsed.state;
      const normalized = normalizeProgressState(next, normalizeOptions);
      setProgress(normalized);
      saveProgress(normalized);
      return { ok: true, state: normalized };
    },
    [normalizeOptions, progress]
  );

  const completedCount = Object.keys(progress.completed).length;

  return { progress, isCompleted, toggleComplete, removeLegacy, validateProgressFile, importProgress, completedCount };
}
