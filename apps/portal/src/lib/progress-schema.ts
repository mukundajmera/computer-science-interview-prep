export const STORAGE_KEY = "sdp-progress";
export const CURRENT_PROGRESS_VERSION = 1;

export const PROGRESS_ID_ALIASES: Record<string, string> = {
  "theory-system-design-fundamentals-ml-generalization": "genai-concept-ml-generalization",
};

export interface ProgressState {
  version: typeof CURRENT_PROGRESS_VERSION;
  completed: Record<string, string>;
  legacyCompleted: Record<string, string>;
}

export interface NormalizeProgressOptions {
  aliases?: Record<string, string>;
  knownIds?: Iterable<string>;
}

export function emptyProgressState(): ProgressState {
  return {
    version: CURRENT_PROGRESS_VERSION,
    completed: {},
    legacyCompleted: {},
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function mergeTimestamp(target: Record<string, string>, id: string, timestamp: string) {
  const timestampTime = new Date(timestamp).getTime();
  if (!Number.isFinite(timestampTime)) return;
  const existing = target[id];
  const existingTime = existing ? new Date(existing).getTime() : Number.NEGATIVE_INFINITY;
  if (!existing || !Number.isFinite(existingTime) || timestampTime > existingTime) {
    target[id] = timestamp;
  }
}

function ingestCompleted(
  state: ProgressState,
  sourceId: string,
  timestamp: unknown,
  options: Required<Pick<NormalizeProgressOptions, "aliases">> & {
    knownIds: Set<string> | null;
    preserveLegacy: boolean;
  }
) {
  if (typeof timestamp !== "string") return;
  const canonicalId = options.aliases[sourceId] ?? sourceId;
  if (options.knownIds && !options.knownIds.has(canonicalId)) {
    mergeTimestamp(state.legacyCompleted, sourceId, timestamp);
    return;
  }
  if (options.preserveLegacy && canonicalId === sourceId) {
    mergeTimestamp(state.legacyCompleted, sourceId, timestamp);
    return;
  }
  mergeTimestamp(state.completed, canonicalId, timestamp);
}

export function normalizeProgressState(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  raw: any,
  options: NormalizeProgressOptions = {}
): ProgressState {
  const state = emptyProgressState();
  if (!isRecord(raw)) return state;

  const aliases = options.aliases ?? PROGRESS_ID_ALIASES;
  const knownIds = options.knownIds ? new Set(options.knownIds) : null;
  const normalizedOptions = { aliases, knownIds, preserveLegacy: false };

  if (raw.version === CURRENT_PROGRESS_VERSION) {
    if (isRecord(raw.completed)) {
      for (const [id, timestamp] of Object.entries(raw.completed)) {
        ingestCompleted(state, id, timestamp, normalizedOptions);
      }
    }
    if (isRecord(raw.legacyCompleted)) {
      for (const [id, timestamp] of Object.entries(raw.legacyCompleted)) {
        ingestCompleted(state, id, timestamp, { aliases, knownIds, preserveLegacy: true });
      }
    }
  } else {
    if (isRecord(raw)) {
      const possibleOldIds = Object.keys(raw).filter(k => k !== "completed" && k !== "legacyCompleted" && k !== "version");
      if (possibleOldIds.length > 0 && !raw.completed) {
        for (const [id, timestamp] of Object.entries(raw)) {
          ingestCompleted(state, id, timestamp, normalizedOptions);
        }
      } else {
        if (isRecord(raw.completed)) {
          for (const [id, timestamp] of Object.entries(raw.completed)) {
            ingestCompleted(state, id, timestamp, normalizedOptions);
          }
        }
        if (isRecord(raw.legacyCompleted)) {
          for (const [id, timestamp] of Object.entries(raw.legacyCompleted)) {
            ingestCompleted(state, id, timestamp, { aliases, knownIds, preserveLegacy: true });
          }
        }
      }
    }
  }
  return state;
}

export function parseProgressState(
  raw: string | null,
  options?: NormalizeProgressOptions
): ProgressState {
  if (!raw) return emptyProgressState();
  try {
    return normalizeProgressState(JSON.parse(raw), options);
  } catch {
    return emptyProgressState();
  }
}

if (process.env.NODE_ENV === "test") {
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-expect-error
  if (typeof import.meta.vitest !== "undefined") {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    const { it, expect } = import.meta.vitest;
    it("migration test: loads the v0 shape and yields v1", () => {
      const v0Shape = { "lld-parking-lot": "2024-01-01T00:00:00.000Z" };
      const result = normalizeProgressState(v0Shape, { knownIds: ["lld-parking-lot"] });
      expect(result).toEqual({
        version: 1,
        completed: { "lld-parking-lot": "2024-01-01T00:00:00.000Z" },
        legacyCompleted: {}
      });
    });
  }
}
