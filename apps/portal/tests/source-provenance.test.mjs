import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";
import ts from "typescript";

async function importSourceProvenanceModule() {
  const outputRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-source-provenance-test-"));

  function writeTranspiled(inputRelativePath, outputName, replacements = []) {
    const modulePath = fileURLToPath(new URL(inputRelativePath, import.meta.url));
    const source = fs.readFileSync(modulePath, "utf-8");
    const transpiled = ts.transpileModule(source, {
      compilerOptions: {
        esModuleInterop: true,
        module: ts.ModuleKind.ES2022,
        target: ts.ScriptTarget.ES2022,
      },
    });
    let outputSource = transpiled.outputText;
    for (const [pattern, replacement] of replacements) {
      outputSource = outputSource.replace(pattern, replacement);
    }
    fs.writeFileSync(path.join(outputRoot, outputName), outputSource);
  }

  writeTranspiled("../src/content/safe-content.ts", "safe-content.mjs");
  writeTranspiled("../src/content/coding-policy.ts", "coding-policy.mjs");
  writeTranspiled("../src/content/source-provenance.ts", "source-provenance.mjs", [
    [/from ["']@\/content\/coding-policy["']/g, 'from "./coding-policy.mjs"'],
    [/from ["']@\/content\/safe-content["']/g, 'from "./safe-content.mjs"'],
  ]);

  return import(pathToFileURL(path.join(outputRoot, "source-provenance.mjs")).href);
}

test("source provenance parses blocked exact and prefix paths", async () => {
  const {
    isBlockedBySourceProvenance,
    isBlockedPortalRoutePath,
    parseBlockedSourcePaths,
  } = await importSourceProvenanceModule();

  const blockedPaths = parseBlockedSourcePaths(
    [
      "artifact_path,permission_status,allowed_use,review_status,notes",
      "00-theory/system-design-fundamentals/cap-theorem.md,needs-owner-review,metadata-only,needs-review,claimed by legacy plan",
      "03-hld-concepts/redis/python/,needs-owner-review,metadata-only,blocked,claimed code directory",
      "04-hld-projects/payment-system/DESIGN.md,approved,reference-only,approved,review complete",
      "",
    ].join("\n")
  );

  assert.deepEqual(blockedPaths, [
    {
      path: "00-theory/system-design-fundamentals/cap-theorem.md",
      isPrefix: false,
      reviewStatus: "needs-review",
    },
    {
      path: "03-hld-concepts/redis/python/",
      isPrefix: true,
      reviewStatus: "blocked",
    },
  ]);
  assert.equal(
    isBlockedBySourceProvenance(
      "00-theory/system-design-fundamentals/cap-theorem.md",
      blockedPaths
    ),
    true
  );
  assert.equal(
    isBlockedBySourceProvenance(
      "03-hld-concepts/redis/python/v1-simple/cache.py",
      blockedPaths
    ),
    true
  );
  assert.equal(
    isBlockedBySourceProvenance(
      "04-hld-projects/payment-system/DESIGN.md",
      blockedPaths
    ),
    false
  );
  assert.equal(
    isBlockedPortalRoutePath(
      "/theory/system-design-fundamentals/cap-theorem",
      blockedPaths
    ),
    true
  );
  assert.equal(
    isBlockedPortalRoutePath("/hld-concepts/redis", blockedPaths),
    true
  );
});

test("source provenance fails closed on malformed ledgers", async () => {
  const { parseBlockedSourcePaths } = await importSourceProvenanceModule();

  assert.throws(
    () =>
      parseBlockedSourcePaths(
        "artifact_path,notes\nsolutions/coding-bfs-dfs.md,x\n"
      ),
    /artifact_path and review_status/
  );
  assert.throws(
    () =>
      parseBlockedSourcePaths(
        "artifact_path,review_status\n../solutions/coding-bfs-dfs.md,needs-review\n"
      ),
    /Invalid blocked source path/
  );
});

test("source provenance maps blocked public source paths to portal routes", async () => {
  const { isBlockedPortalRoutePath, parseBlockedSourcePaths } =
    await importSourceProvenanceModule();
  const blockedPaths = parseBlockedSourcePaths(
    [
      "artifact_path,review_status",
      "solutions/coding-bfs-dfs.md,Needs-Review",
      "02-lld-projects/parking-lot/DESIGN.md,blocked",
      "03-hld-concepts/redis/THEORY.md,blocked",
      "04-hld-projects/payment-system/DESIGN.md,blocked",
      "06-genai-systems/01-llm-lld-projects/embedding-service/DESIGN.md,blocked",
      "06-genai-systems/02-llm-hld-projects/document-qa-rag/DESIGN.md,blocked",
      "01-design-patterns/creational/factory/THEORY.md,blocked",
      "quizzes/bfs-dfs-quiz.md,blocked",
      "quizzes/answers/bfs-dfs-answers.md,blocked",
      "resources/templates/lld-template.md,blocked",
      "resources/study-plans/,blocked",
      "05-coding-problems/trie/,blocked",
      "05-coding-problems/problem-bank/,blocked",
      "05-coding-problems/collections/README.md,blocked",
    ].join("\n")
  );

  for (const route of [
    "/interview/coding/bfs-dfs-pack",
    "/reveal/solution/coding/bfs-dfs-pack",
    "/lld/parking-lot",
    "/hld-concepts/redis",
    "/hld/payment-system",
    "/genai/lld/embedding-service",
    "/genai/hld/document-qa-rag",
    "/patterns/creational/factory",
    "/quizzes/bfs-dfs",
    "/reveal/quiz-answer/bfs-dfs",
    "/resources/templates/lld-template",
    "/resources/study-plans/1-week-plan",
    "/coding/trie",
  ]) {
    assert.equal(isBlockedPortalRoutePath(route, blockedPaths), true, route);
  }

  for (const nonRoute of ["/coding/problem-bank", "/coding/collections"]) {
    assert.equal(isBlockedPortalRoutePath(nonRoute, blockedPaths), false, nonRoute);
  }
});
