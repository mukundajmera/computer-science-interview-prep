import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";
import ts from "typescript";

async function importInterviewsModule() {
  const outputRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-interviews-test-"));

  fs.writeFileSync(
    path.join(outputRoot, "interview-data.mjs"),
    `export const INTERVIEW_PROBLEMS = [
      {
        slug: "behavioral-big-three",
        title: "Behavioral Big Three",
        type: "behavioral",
        difficulty: "intermediate",
        solutionPath: "solutions/behavioral-big-three.md",
      },
      {
        slug: "parking-lot",
        title: "Parking Lot",
        type: "lld",
        difficulty: "beginner",
        solutionPath: "solutions/lld-parking-lot.md",
      },
      {
        slug: "legacy-static-coding",
        title: "Legacy Static Coding",
        type: "coding",
        difficulty: "intermediate",
        solutionPath: "solutions/coding-legacy.md",
      },
    ];\n`
  );
  fs.writeFileSync(
    path.join(outputRoot, "loader.mjs"),
    `export function listMarkdownFiles(relativePath) {
      if (relativePath !== "solutions") return [];
      return [
        "lld-parking-lot.md",
        "coding-bfs-dfs.md",
        "coding-dynamic-programming.md",
        "coding-greedy.md",
        "coding-backtracking.md",
        "coding-heap-priority-queue.md",
        "coding-trie.md",
        "coding-union-find.md",
        "coding-unreviewed.md",
        "coding-two-pointers.md",
        "coding-sliding-window.md",
        "coding-binary-search.md",
        "hld-url-shortener.md",
      ];
    }\n`,
  );
  fs.writeFileSync(
    path.join(outputRoot, "source-provenance.mjs"),
    `export function isBlockedBySourceProvenance(relativePath) {
      return globalThis.__BLOCKED_INTERVIEW_SOURCES__?.has(relativePath) ?? false;
    }\n`
  );

  const modulePath = fileURLToPath(
    new URL("../src/content/interviews.ts", import.meta.url)
  );
  const source = fs.readFileSync(modulePath, "utf-8");
  const transpiled = ts.transpileModule(source, {
    compilerOptions: {
      esModuleInterop: true,
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  });
  const outputSource = transpiled.outputText
    .replace(
      /from ["']@\/components\/interview\/interview-data["']/g,
      'from "./interview-data.mjs"'
    )
    .replace(/from ["']@\/content\/loader["']/g, 'from "./loader.mjs"')
    .replace(
      /from ["']@\/content\/source-provenance["']/g,
      'from "./source-provenance.mjs"'
    );
  const outputPath = path.join(outputRoot, "interviews.mjs");
  fs.writeFileSync(outputPath, outputSource);
  return import(pathToFileURL(outputPath).href);
}

test("Interview Mode discovers coding packs from solution markdown", async () => {
  globalThis.__BLOCKED_INTERVIEW_SOURCES__ = new Set([
    "solutions/coding-unreviewed.md",
  ]);
  const { listCodingInterviewProblems, listInterviewProblems } =
    await importInterviewsModule();

  assert.deepEqual(
    listCodingInterviewProblems().map((problem) => [
      problem.slug,
      problem.title,
      problem.difficulty,
      problem.solutionPath,
    ]),
    [
      [
        "two-pointers-pack",
        "Two Pointers Pack",
        "intermediate",
        "solutions/coding-two-pointers.md",
      ],
      [
        "sliding-window-pack",
        "Sliding Window Pack",
        "intermediate",
        "solutions/coding-sliding-window.md",
      ],
      [
        "binary-search-pack",
        "Binary Search Pack",
        "intermediate",
        "solutions/coding-binary-search.md",
      ],
      [
        "bfs-dfs-pack",
        "BFS/DFS Pack",
        "intermediate",
        "solutions/coding-bfs-dfs.md",
      ],
      [
        "dynamic-programming-pack",
        "Dynamic Programming Pack",
        "advanced",
        "solutions/coding-dynamic-programming.md",
      ],
      [
        "greedy-pack",
        "Greedy Pack",
        "intermediate",
        "solutions/coding-greedy.md",
      ],
      [
        "backtracking-pack",
        "Backtracking Pack",
        "intermediate",
        "solutions/coding-backtracking.md",
      ],
      [
        "heap-priority-queue-pack",
        "Heap / Priority Queue Pack",
        "intermediate",
        "solutions/coding-heap-priority-queue.md",
      ],
      [
        "trie-pack",
        "Trie Pack",
        "intermediate",
        "solutions/coding-trie.md",
      ],
      [
        "union-find-pack",
        "Union-Find Pack",
        "intermediate",
        "solutions/coding-union-find.md",
      ],
    ]
  );

  assert.deepEqual(
    listInterviewProblems().map((problem) => problem.slug),
    [
      "behavioral-big-three",
      "parking-lot",
      "two-pointers-pack",
      "sliding-window-pack",
      "binary-search-pack",
      "bfs-dfs-pack",
      "dynamic-programming-pack",
      "greedy-pack",
      "backtracking-pack",
      "heap-priority-queue-pack",
      "trie-pack",
      "union-find-pack",
    ]
  );

  assert.equal(
    listInterviewProblems().some((problem) => problem.slug === "unreviewed-pack"),
    false
  );
  delete globalThis.__BLOCKED_INTERVIEW_SOURCES__;
});
