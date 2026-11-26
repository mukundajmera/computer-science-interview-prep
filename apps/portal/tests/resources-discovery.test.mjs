import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";
import ts from "typescript";

async function importResourcesModule() {
  const outputRoot = fs.mkdtempSync(
    path.join(os.tmpdir(), "portal-resources-discovery-test-")
  );

  fs.writeFileSync(
    path.join(outputRoot, "loader.mjs"),
    `export function listDirs(relativePath, options = {}) {
      globalThis.__RESOURCE_CALLS__.push(["listDirs", relativePath, options]);
      return globalThis.__RESOURCE_DIRS__;
    }
    export function fileExists(relativePath, options = {}) {
      globalThis.__RESOURCE_CALLS__.push(["fileExists", relativePath, options]);
      return globalThis.__RESOURCE_EXISTS__.has(relativePath);
    }
    export function listMarkdownFiles(relativePath, options = {}) {
      globalThis.__RESOURCE_CALLS__.push(["listMarkdownFiles", relativePath, options]);
      return globalThis.__RESOURCE_FILES__[relativePath] ?? [];
    }\n`
  );
  fs.writeFileSync(
    path.join(outputRoot, "utils.mjs"),
    `export function slugToTitle(slug) {
      return slug.split("-").map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
    }\n`
  );
  fs.writeFileSync(
    path.join(outputRoot, "source-provenance.mjs"),
    `export function isBlockedBySourceProvenance(relativePath) {
      return globalThis.__BLOCKED_SOURCE_PATHS__?.has(relativePath) ?? false;
    }\n`
  );

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

  writeTranspiled("../src/content/resource-policy.ts", "resource-policy.mjs");
  writeTranspiled("../src/content/resources.ts", "resources.mjs", [
    [/from ["']@\/content\/loader["']/g, 'from "./loader.mjs"'],
    [/from ["']@\/content\/resource-policy["']/g, 'from "./resource-policy.mjs"'],
    [/from ["']@\/content\/source-provenance["']/g, 'from "./source-provenance.mjs"'],
    [/from ["']@\/lib\/utils["']/g, 'from "./utils.mjs"'],
  ]);

  return import(pathToFileURL(path.join(outputRoot, "resources.mjs")).href);
}

test("resources discover only allowlisted public README-backed categories", async () => {
  globalThis.__RESOURCE_DIRS__ = [
    "source-intake",
    "templates",
    "interview-tips",
    "practice-labs",
    "missing-readme",
    "study-plans",
  ];
  globalThis.__RESOURCE_EXISTS__ = new Set([
    "resources/study-plans/README.md",
    "resources/templates/README.md",
    "resources/interview-tips/README.md",
    "resources/practice-labs/README.md",
  ]);
  globalThis.__RESOURCE_FILES__ = {
    "resources/study-plans": ["README.md", "1-week-plan.md"],
    "resources/templates": ["README.md", "lld-template.md"],
    "resources/interview-tips": [
      "README.md",
      "interview-framework.md",
      "salary-negotiation.md",
    ],
    "resources/practice-labs": ["README.md", "lab-one.md"],
  };
  globalThis.__BLOCKED_SOURCE_PATHS__ = new Set([
    "resources/interview-tips/interview-framework.md",
  ]);
  globalThis.__RESOURCE_CALLS__ = [];

  const {
    getResourceCategory,
    listResourceCategories,
    listResourceEntries,
  } = await importResourcesModule();

  assert.deepEqual(
    listResourceCategories().map((category) => [
      category.slug,
      category.label,
      category.description,
    ]),
    [
      [
        "study-plans",
        "Study Plans",
        "Time-boxed paths through the curriculum",
      ],
      [
        "interview-tips",
        "Interview Tips",
        "Communication, round strategy, and checklists",
      ],
      [
        "templates",
        "Templates",
        "Practice worksheets and reusable answer structures",
      ],
    ]
  );
  assert.equal(getResourceCategory("source-intake"), null);
  assert.equal(getResourceCategory("practice-labs"), null);
  assert.equal(getResourceCategory("missing-readme"), null);

  assert.deepEqual(
    listResourceEntries().map((entry) => entry.href),
    [
      "/resources/study-plans/1-week-plan",
      "/resources/interview-tips/salary-negotiation",
      "/resources/templates/lld-template",
    ]
  );
  assert.deepEqual(globalThis.__RESOURCE_CALLS__[0], [
    "listDirs",
    "resources",
    { allowedRoots: ["resources"] },
  ]);
  assert.equal(
    globalThis.__RESOURCE_CALLS__.some(
      ([fn, relativePath]) =>
        fn === "listMarkdownFiles" && relativePath === "resources/practice-labs"
    ),
    false
  );

  delete globalThis.__RESOURCE_DIRS__;
  delete globalThis.__RESOURCE_EXISTS__;
  delete globalThis.__RESOURCE_FILES__;
  delete globalThis.__BLOCKED_SOURCE_PATHS__;
  delete globalThis.__RESOURCE_CALLS__;
});
