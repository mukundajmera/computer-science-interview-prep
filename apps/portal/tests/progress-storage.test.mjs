import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";
import ts from "typescript";

async function importTypeScriptModule(relativePath) {
  const outputRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-progress-test-"));
  const modulePath = fileURLToPath(new URL(relativePath, import.meta.url));
  const source = fs.readFileSync(modulePath, "utf-8");
  const transpiled = ts.transpileModule(source, {
    compilerOptions: {
      esModuleInterop: true,
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  });
  const outputPath = path.join(
    outputRoot,
    path.basename(relativePath).replace(/\.ts$/, ".mjs")
  );
  fs.writeFileSync(outputPath, transpiled.outputText);
  return import(pathToFileURL(outputPath).href);
}

const { normalizeProgressState, parseProgressState, STORAGE_KEY } =
  await importTypeScriptModule("../src/components/progress/progress-storage.ts");

test("progress storage key remains stable", () => {
  assert.equal(STORAGE_KEY, "sdp-progress");
});

test("normalizes old completed maps with aliases and preserves unknown ids", () => {
  const state = normalizeProgressState(
    {
      completed: {
        "old-lld-parking": "2026-01-01T00:00:00.000Z",
        "lld-parking-lot": "2026-01-02T00:00:00.000Z",
        "unknown-retired-id": "2026-01-03T00:00:00.000Z",
      },
    },
    {
      aliases: {
        "old-lld-parking": "lld-parking-lot",
      },
      knownIds: ["lld-parking-lot"],
    }
  );

  assert.deepEqual(state.completed, {
    "lld-parking-lot": "2026-01-02T00:00:00.000Z",
  });
  assert.deepEqual(state.legacyCompleted, {
    "unknown-retired-id": "2026-01-03T00:00:00.000Z",
  });
});

test("progress migration is idempotent", () => {
  const options = {
    aliases: {
      "old-genai-rag": "genai-hld-document-qa-rag",
    },
    knownIds: ["genai-hld-document-qa-rag"],
  };
  const once = normalizeProgressState(
    {
      completed: {
        "old-genai-rag": "2026-02-01T00:00:00.000Z",
        "retired-topic": "2026-02-02T00:00:00.000Z",
      },
    },
    options
  );
  const twice = normalizeProgressState(once, options);

  assert.deepEqual(twice, once);
});

test("existing legacy entries can recover when an alias targets a known id", () => {
  const state = normalizeProgressState(
    {
      legacyCompleted: {
        "old-progress-id": "2026-03-01T00:00:00.000Z",
      },
    },
    {
      aliases: {
        "old-progress-id": "hld-url-shortener",
      },
      knownIds: ["hld-url-shortener"],
    }
  );

  assert.deepEqual(state.completed, {
    "hld-url-shortener": "2026-03-01T00:00:00.000Z",
  });
  assert.deepEqual(state.legacyCompleted, {});
});

test("production aliases map ml-generalization with timestamp preservation and idempotence", () => {
  const knownIds = ["genai-concept-ml-generalization"];

  const once = normalizeProgressState(
    {
      completed: {
        "theory-system-design-fundamentals-ml-generalization": "2026-05-01T00:00:00.000Z",
      },
      legacyCompleted: {
        "some-unrelated-unknown-id": "2026-05-02T00:00:00.000Z",
      }
    },
    { knownIds }
  );

  assert.deepEqual(once.completed, {
    "genai-concept-ml-generalization": "2026-05-01T00:00:00.000Z",
  });
  assert.deepEqual(once.legacyCompleted, {
    "some-unrelated-unknown-id": "2026-05-02T00:00:00.000Z",
  });

  const twice = normalizeProgressState(once, { knownIds });
  assert.deepEqual(twice, once);
});

test("corrupt progress JSON is rejected by the parser", () => {
  assert.throws(() => parseProgressState("{not json"));
});

test("invalid progress timestamps are ignored during normalization", () => {
  const state = normalizeProgressState(
    {
      completed: {
        "lld-parking-lot": "not-a-date",
        "lld-tic-tac-toe": "2026-04-01T00:00:00.000Z",
      },
      legacyCompleted: {
        "retired-topic": "also-invalid",
      },
    },
    {
      knownIds: ["lld-parking-lot", "lld-tic-tac-toe"],
    }
  );

  assert.deepEqual(state.completed, {
    "lld-tic-tac-toe": "2026-04-01T00:00:00.000Z",
  });
  assert.deepEqual(state.legacyCompleted, {});
});
