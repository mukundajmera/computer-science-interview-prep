import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";
import ts from "typescript";

async function importSectionSummaries() {
  const outputRoot = fs.mkdtempSync(
    path.join(os.tmpdir(), "portal-section-summaries-test-")
  );
  const modulePath = fileURLToPath(
    new URL("../src/content/section-summaries.ts", import.meta.url)
  );

  const stubs = {
    "interviews.mjs": "export function listInterviewProblems() { return [{ slug: 'one' }, { slug: 'two' }]; }\n",
    "quizzes.mjs": "export function listQuizEntries() { return [{ slug: 'graphs' }]; }\n",
    "registry.mjs": "export function buildRegistry() { return globalThis.__SECTION_SUMMARY_REGISTRY__; }\n",
    "resources.mjs": "export function listResourceEntries() { return [{ id: 'study-plan' }, { id: 'cheatsheet' }]; }\n",
    "sections.mjs": `export const PORTAL_SECTIONS = [
      { label: "Theory", href: "/theory", emoji: "T", description: "Static theory" },
      { label: "Design Patterns", href: "/patterns", emoji: "P", description: "23 GoF patterns" },
      { label: "Coding Patterns", href: "/coding", emoji: "C", description: "Static coding" },
      { label: "Interview Mode", href: "/interview", emoji: "I", description: "Static interview" },
      { label: "Quizzes", href: "/quizzes", emoji: "Q", description: "Static quizzes" },
      { label: "Resources", href: "/resources", emoji: "R", description: "Static resources" },
    ];\n`,
  };

  for (const [filename, source] of Object.entries(stubs)) {
    fs.writeFileSync(path.join(outputRoot, filename), source);
  }

  const source = fs.readFileSync(modulePath, "utf-8");
  const transpiled = ts.transpileModule(source, {
    compilerOptions: {
      esModuleInterop: true,
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  });

  const outputSource = transpiled.outputText
    .replace(/from ["']@\/content\/interviews["']/g, 'from "./interviews.mjs"')
    .replace(/from ["']@\/content\/quizzes["']/g, 'from "./quizzes.mjs"')
    .replace(/from ["']@\/content\/registry["']/g, 'from "./registry.mjs"')
    .replace(/from ["']@\/content\/resources["']/g, 'from "./resources.mjs"')
    .replace(/from ["']@\/lib\/sections["']/g, 'from "./sections.mjs"');

  const outputPath = path.join(outputRoot, "section-summaries.mjs");
  fs.writeFileSync(outputPath, outputSource);
  return import(pathToFileURL(outputPath).href);
}

function registryFixture() {
  return {
    theory: [
      { topicArea: "oop" },
      { topicArea: "networking" },
      { topicArea: "networking" },
    ],
    patterns: [
      { patternCategory: "creational" },
      { patternCategory: "structural" },
    ],
    lldProjects: [{}, {}, {}],
    hldConcepts: [{}],
    hldProjects: [{}],
    genaiConcepts: [{}, {}],
    genaiLLD: [{}],
    genaiHLD: [{}],
    codingTopics: [{}, {}],
    caseStudies: [{}],
  };
}

test("section summaries derive visible UI counts from discovered content", async () => {
  const { createSectionSummaries } = await importSectionSummaries();

  const sections = createSectionSummaries({
    registry: registryFixture(),
    quizCount: 4,
    resourceCount: 7,
    interviewCount: 6,
    sections: [
      { label: "Theory", href: "/theory", emoji: "T", description: "Static theory" },
      {
        label: "Design Patterns",
        href: "/patterns",
        emoji: "P",
        description: "23 GoF patterns",
      },
      { label: "GenAI Systems", href: "/genai", emoji: "G", description: "Static GenAI" },
      { label: "Quizzes", href: "/quizzes", emoji: "Q", description: "Static quizzes" },
      { label: "Custom", href: "/custom", emoji: "X", description: "Manual section" },
    ],
  });

  assert.deepEqual(
    sections.map((section) => [section.href, section.summary]),
    [
      ["/theory", "3 articles"],
      ["/patterns", "2 patterns"],
      ["/genai", "4 modules"],
      ["/quizzes", "4 quizzes"],
      ["/custom", "Auto-discovered"],
    ]
  );
  assert.equal(
    sections.find((section) => section.href === "/patterns")?.description,
    "Auto-discovered from 2 pattern groups"
  );
  assert.equal(
    sections.find((section) => section.href === "/genai")?.description,
    "2 concepts, 1 LLD project, 1 HLD project"
  );
});

test("buildSectionSummaries uses the registry and list helpers instead of static copy", async () => {
  const { buildSectionSummaries } = await importSectionSummaries();
  globalThis.__SECTION_SUMMARY_REGISTRY__ = registryFixture();

  const sections = buildSectionSummaries();

  assert.equal(sections.find((section) => section.href === "/patterns")?.summary, "2 patterns");
  assert.equal(sections.find((section) => section.href === "/quizzes")?.summary, "1 quiz");
  assert.equal(sections.find((section) => section.href === "/resources")?.summary, "2 resources");
  assert.equal(sections.find((section) => section.href === "/interview")?.summary, "2 drills");
  assert.notEqual(
    sections.find((section) => section.href === "/patterns")?.description,
    "23 GoF patterns"
  );

  delete globalThis.__SECTION_SUMMARY_REGISTRY__;
});
