import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";
import ts from "typescript";

async function importTypeScriptModule(relativePath) {
  const outputRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-resource-links-test-"));

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
    const outputPath = path.join(outputRoot, outputName);
    fs.writeFileSync(outputPath, outputSource);
  }

  writeTranspiled("../src/content/resource-policy.ts", "resource-policy.mjs");
  writeTranspiled("../src/content/coding-policy.ts", "coding-policy.mjs");
  fs.writeFileSync(
    path.join(outputRoot, "loader.mjs"),
    `export function fileExists(relativePath) {
      return !(globalThis.__MISSING_PORTAL_FILES__?.has(relativePath) ?? false);
    }\n`
  );
  fs.writeFileSync(
    path.join(outputRoot, "source-provenance.mjs"),
    `export function isBlockedBySourceProvenance(relativePath) {
      return globalThis.__BLOCKED_SOURCE_PATHS__?.has(relativePath) ?? false;
    }
    export function isBlockedPortalRoutePath(pathname) {
      return globalThis.__BLOCKED_PORTAL_ROUTES__?.has(pathname.replace(/\\/+$/, "") || "/") ?? false;
    }\n`
  );
  const outputName = path.basename(relativePath).replace(/\.ts$/, ".mjs");
  writeTranspiled(relativePath, outputName, [
    [
      /from ["']@\/content\/coding-policy["']/g,
      'from "./coding-policy.mjs"',
    ],
    [
      /from ["']@\/content\/resource-policy["']/g,
      'from "./resource-policy.mjs"',
    ],
    [
      /from ["']@\/content\/source-provenance["']/g,
      'from "./source-provenance.mjs"',
    ],
    [
      /from ["']@\/content\/loader["']/g,
      'from "./loader.mjs"',
    ],
  ]);

  return import(pathToFileURL(path.join(outputRoot, outputName)).href);
}

const { rewritePortalHref, rewriteResourceHref } = await importTypeScriptModule(
  "../src/content/resource-links.ts"
);

const source = "resources/study-plans/1-week-plan.md";
const repositoryUrl = "https://github.com/mukundajmera/computer-science-interview-prep";

test("rewriteResourceHref maps repo-relative content links to basePath-safe portal links", () => {
  assert.equal(
    rewriteResourceHref("../../01-design-patterns/behavioral/strategy/", source),
    "../../../patterns/behavioral/strategy/"
  );
  assert.equal(
    rewriteResourceHref("../../02-lld-projects/parking-lot/", source),
    "../../../lld/parking-lot/"
  );
  assert.equal(
    rewriteResourceHref("../../03-hld-concepts/cap-theorem/THEORY.md", source),
    "../../../hld-concepts/cap-theorem/"
  );
  assert.equal(
    rewriteResourceHref("../../quizzes/hld-concepts-quiz.md", source),
    "../../../quizzes/hld-concepts/"
  );
  assert.equal(
    rewriteResourceHref("../../02-lld-projects/HOW-TO-APPROACH.md", source),
    "../../../lld/"
  );
  assert.equal(
    rewriteResourceHref("../../04-hld-projects/DESIGN-TEMPLATE.md", source),
    "../../../hld/"
  );
  assert.equal(
    rewriteResourceHref(
      "../../06-genai-systems/02-llm-hld-projects/GENAI-DESIGN-TEMPLATE.md",
      source
    ),
    "../../../genai/"
  );
  assert.equal(
    rewriteResourceHref("../../01-design-patterns/README.md", source),
    "../../../patterns/"
  );
  assert.equal(
    rewriteResourceHref("../../00-theory/README.md", source),
    "../../../theory/"
  );
  assert.equal(
    rewriteResourceHref("../../05-coding-problems/TOP-20.md", source),
    "../../../coding/"
  );
  assert.equal(rewriteResourceHref("../../README.md", source), "../../../");
  assert.equal(
    rewriteResourceHref("/02-lld-projects/parking-lot/README.md", source),
    "../../../lld/parking-lot/"
  );
});

test("rewriteResourceHref maps cross-resource links to public resource routes", () => {
  assert.equal(
    rewriteResourceHref("../templates/lld-template.md", source),
    "../../templates/lld-template/"
  );
  assert.equal(
    rewriteResourceHref("../cheatsheets/", source),
    "../../cheatsheets/"
  );
});

test("rewriteResourceHref preserves public resource non-Markdown assets as source links", () => {
  assert.equal(
    rewriteResourceHref("../templates/architecture-diagram.mmd", source),
    `${repositoryUrl}/blob/main/resources/templates/architecture-diagram.mmd`
  );
  assert.equal(
    rewriteResourceHref("../templates/export.csv", source),
    `${repositoryUrl}/blob/main/resources/templates/export.csv`
  );
  assert.equal(
    rewriteResourceHref("/resources/templates/export.csv", source),
    `${repositoryUrl}/blob/main/resources/templates/export.csv`
  );
  assert.equal(
    rewriteResourceHref("/resources/templates/architecture-diagram.mmd", source),
    `${repositoryUrl}/blob/main/resources/templates/architecture-diagram.mmd`
  );
});

test("rewriteResourceHref rejects non-public source-intake links", () => {
  assert.throws(
    () => rewriteResourceHref("../source-intake/temp-upload/README.md", source),
    /Forbidden portal content link/
  );
  assert.throws(
    () => rewriteResourceHref("/resources/source-intake/temp-upload/", source),
    /Forbidden portal content link/
  );
  assert.throws(
    () => rewriteResourceHref("../practice-labs/lab-one.md", source),
    /Forbidden portal content link/
  );
  assert.throws(
    () => rewriteResourceHref("/resources/practice-labs/lab-one/", source),
    /Forbidden portal content link/
  );
  assert.throws(
    () =>
      rewritePortalHref(
        "../../temp_upload/INTEGRATION-PLAN.md",
        source,
        "/resources/study-plans/1-week-plan"
      ),
    /Forbidden portal content link/
  );
});

test("rewritePortalHref turns blocked derivative-review links inert", () => {
  globalThis.__BLOCKED_SOURCE_PATHS__ = new Set([
    "00-theory/system-design-fundamentals/cap-theorem.md",
  ]);
  globalThis.__BLOCKED_PORTAL_ROUTES__ = new Set([
    "/theory/system-design-fundamentals/cap-theorem",
  ]);

  assert.equal(
    rewritePortalHref(
      "../../00-theory/system-design-fundamentals/cap-theorem.md",
      "03-hld-concepts/cap-theorem/THEORY.md",
      "/hld-concepts/cap-theorem"
    ),
    "#"
  );
  assert.equal(
    rewritePortalHref(
      "/theory/system-design-fundamentals/cap-theorem",
      "03-hld-concepts/cap-theorem/THEORY.md",
      "/hld-concepts/cap-theorem"
    ),
    "#"
  );

  delete globalThis.__BLOCKED_SOURCE_PATHS__;
  delete globalThis.__BLOCKED_PORTAL_ROUTES__;
});

test("rewriteResourceHref preserves external and same-document links", () => {
  assert.equal(
    rewriteResourceHref("https://example.com/a.md", source),
    "https://example.com/a.md"
  );
  assert.equal(rewriteResourceHref("#daily-checklist", source), "#daily-checklist");
});

test("rewriteResourceHref maps absolute portal links without domain-root paths", () => {
  assert.equal(rewriteResourceHref("/patterns", source), "../../../patterns/");
  assert.equal(
    rewriteResourceHref("/resources/study-plans/1-week-plan#daily-checklist", source),
    "./#daily-checklist"
  );
  assert.equal(
    rewritePortalHref("/theory", "README.md", "/"),
    "theory/"
  );
});

test("rewriteResourceHref maps solution files through interview problem metadata", () => {
  assert.equal(
    rewriteResourceHref("../../solutions/lld-parking-lot.md", source, {
      solutionEntries: [
        {
          type: "lld",
          slug: "parking-lot",
          solutionPath: "solutions/lld-parking-lot.md",
        },
      ],
    }),
    "../../../interview/lld/parking-lot/"
  );
});

test("rewritePortalHref preserves GitHub-only practice assets as source links", () => {
  const codingSource = "05-coding-problems/bfs-dfs/README.md";
  const codingRoute = "/coding/bfs-dfs";

  assert.equal(
    rewritePortalHref(
      "../../solutions/coding-bfs-dfs.md",
      codingSource,
      codingRoute
    ),
    `${repositoryUrl}/blob/main/solutions/coding-bfs-dfs.md`
  );
  assert.equal(
    rewritePortalHref(
      "../../flashcards/bfs-dfs.md",
      codingSource,
      codingRoute
    ),
    `${repositoryUrl}/blob/main/flashcards/bfs-dfs.md`
  );
  assert.equal(
    rewritePortalHref(
      "../../quizzes/bfs-dfs-quiz.md",
      codingSource,
      codingRoute
    ),
    "../../quizzes/bfs-dfs/"
  );
});

test("rewritePortalHref preserves non-routed coding support directories as source links", () => {
  const codingSource = "05-coding-problems/README.md";
  const codingRoute = "/coding";

  assert.equal(
    rewritePortalHref("./problem-bank/README.md", codingSource, codingRoute),
    `${repositoryUrl}/blob/main/05-coding-problems/problem-bank/README.md`
  );
  assert.equal(
    rewritePortalHref(
      "./problem-bank/IMPLEMENTATION-PLAN.md",
      codingSource,
      codingRoute
    ),
    `${repositoryUrl}/blob/main/05-coding-problems/problem-bank/IMPLEMENTATION-PLAN.md`
  );
  assert.equal(
    rewritePortalHref("./collections/README.md", codingSource, codingRoute),
    `${repositoryUrl}/blob/main/05-coding-problems/collections/README.md`
  );
  assert.equal(
    rewritePortalHref("./collections/", codingSource, codingRoute),
    `${repositoryUrl}/tree/main/05-coding-problems/collections`
  );
});

test("rewritePortalHref keeps missing quiz markdown as source links", () => {
  const codingSource = "05-coding-problems/trie/README.md";
  const codingRoute = "/coding/trie";
  globalThis.__MISSING_PORTAL_FILES__ = new Set(["quizzes/trie-quiz.md"]);

  assert.equal(
    rewritePortalHref("../../quizzes/trie-quiz.md", codingSource, codingRoute),
    `${repositoryUrl}/blob/main/quizzes/trie-quiz.md`
  );

  delete globalThis.__MISSING_PORTAL_FILES__;
});

test("rewritePortalHref preserves pattern implementation links as source tree URLs", () => {
  const patternSource = "01-design-patterns/creational/builder/THEORY.md";
  const patternRoute = "/patterns/creational/builder";

  assert.equal(
    rewritePortalHref("./java/v1-basic/", patternSource, patternRoute),
    `${repositoryUrl}/tree/main/01-design-patterns/creational/builder/java/v1-basic`
  );
  assert.equal(
    rewritePortalHref("./python/v1-basic/", patternSource, patternRoute),
    `${repositoryUrl}/tree/main/01-design-patterns/creational/builder/python/v1-basic`
  );
  assert.equal(
    rewritePortalHref("./README.md", patternSource, patternRoute),
    "./"
  );
});

test("rewritePortalHref preserves GenAI diagram artifacts as source blob URLs", () => {
  const genaiSource =
    "06-genai-systems/02-llm-hld-projects/semantic-retrieval-platform/DESIGN.md";
  const genaiRoute = "/genai/hld/semantic-retrieval-platform";

  assert.equal(
    rewritePortalHref("./diagrams/architecture.mmd", genaiSource, genaiRoute),
    `${repositoryUrl}/blob/main/06-genai-systems/02-llm-hld-projects/semantic-retrieval-platform/diagrams/architecture.mmd`
  );
  assert.equal(
    rewritePortalHref("./APPROACH.md", genaiSource, genaiRoute),
    "./"
  );
});
