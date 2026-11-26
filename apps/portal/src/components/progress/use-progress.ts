"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import {
  emptyProgressState,
  normalizeProgressState,
  parseProgressState,
  STORAGE_KEY,
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

  const importProgress = useCallback((rawJson: string) => {
    try {
      const parsed = normalizeProgressState(JSON.parse(rawJson), normalizeOptions);
      setProgress(parsed);
      saveProgress(parsed);
      return true;
    } catch (e) {
      console.error("Invalid progress data", e);
      return false;
    }
  }, [normalizeOptions]);

  const completedCount = Object.keys(progress.completed).length;

  return { progress, isCompleted, toggleComplete, removeLegacy, importProgress, completedCount };
}
