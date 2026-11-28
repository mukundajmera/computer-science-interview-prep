import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";
import ts from "typescript";

async function importTypeScriptModule(relativePath) {
  const outputRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-route-manifest-test-"));
  const modulePath = fileURLToPath(new URL(relativePath, import.meta.url));
  const source = fs.readFileSync(modulePath, "utf-8");

  const sectionsPath = fileURLToPath(new URL("../src/lib/sections.ts", import.meta.url));
  const sectionsTranspiled = ts.transpileModule(fs.readFileSync(sectionsPath, "utf-8"), {
    compilerOptions: {
      esModuleInterop: true,
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  });
  fs.writeFileSync(path.join(outputRoot, "sections.mjs"), sectionsTranspiled.outputText);
  const resourcePolicyPath = fileURLToPath(
    new URL("../src/content/resource-policy.ts", import.meta.url)
  );
  const resourcePolicyTranspiled = ts.transpileModule(
    fs.readFileSync(resourcePolicyPath, "utf-8"),
    {
      compilerOptions: {
        esModuleInterop: true,
        module: ts.ModuleKind.ES2022,
        target: ts.ScriptTarget.ES2022,
      },
    }
  );
  fs.writeFileSync(
    path.join(outputRoot, "resource-policy.mjs"),
    resourcePolicyTranspiled.outputText
  );

  const transpiled = ts.transpileModule(source, {
    compilerOptions: {
      esModuleInterop: true,
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  });
  const outputSource = transpiled.outputText
    .replace(/from ["']@\/lib\/sections["']/g, 'from "./sections.mjs"')
    .replace(
      /from ["']@\/content\/resource-policy["']/g,
      'from "./resource-policy.mjs"'
    );
  const outputPath = path.join(
    outputRoot,
    path.basename(relativePath).replace(/\.ts$/, ".mjs")
  );
  fs.writeFileSync(outputPath, outputSource);
  return import(pathToFileURL(outputPath).href);
}

const { createRouteManifest } = await importTypeScriptModule(
  "../src/content/route-manifest.ts"
);

function item(overrides) {
  return {
    id: overrides.id,
    title: overrides.title,
    category: overrides.category,
    difficulty: overrides.difficulty ?? "intermediate",
    href: overrides.href,
    status: overrides.status ?? "complete",
    fsPath: overrides.fsPath ?? "fixture",
  };
}

test("createRouteManifest preserves stable routes for content, quizzes, and interviews", () => {
  const manifest = createRouteManifest({
    registry: {
      theory: [
        {
          ...item({
            id: "theory-oop-solid",
            title: "SOLID",
            category: "theory",
            href: "/theory/oop/solid",
          }),
          topicArea: "oop",
          markdownFile: "00-theory/oop/solid.md",
        },
      ],
      patterns: [
        {
          ...item({
            id: "pattern-creational-factory",
            title: "Factory",
            category: "pattern",
            href: "/patterns/creational/factory",
          }),
          patternCategory: "creational",
          docs: {
            readme: null,
            theory: null,
          },
        },
      ],
      lldProjects: [
        item({
          id: "lld-parking-lot",
          title: "Parking Lot",
          category: "lld-project",
          href: "/lld/parking-lot",
        }),
      ],
      hldConcepts: [],
      hldProjects: [],
      genaiConcepts: [],
      genaiLLD: [
        {
          ...item({
            id: "genai-lld-embedding-service",
            title: "Embedding Service",
            category: "genai-lld",
            href: "/genai/lld/embedding-service",
          }),
          docs: {
            problem: null,
            design: null,
            approach: null,
          },
        },
      ],
      genaiHLD: [],
      codingTopics: [
        item({
          id: "coding-bfs-dfs",
          title: "BFS/DFS",
          category: "coding-topic",
          href: "/coding/bfs-dfs",
        }),
      ],
      caseStudies: [],
    },
    resourceEntries: [
      {
        id: "resource-study-plans-1-week-plan",
        title: "1 Week Plan",
        href: "/resources/study-plans/1-week-plan",
        category: "Study Plans",
      },
    ],
    quizSlugs: ["design-patterns", "missing-answer"],
    quizAnswerSlugs: ["design-patterns"],
    interviewProblems: [
      {
        slug: "parking-lot",
        title: "Parking Lot",
        type: "lld",
        difficulty: "beginner",
        solutionPath: "solutions/lld-parking-lot.md",
      },
      {
        slug: "bfs-dfs-pack",
        title: "BFS/DFS Pack",
        type: "coding",
        difficulty: "intermediate",
        solutionPath: "solutions/coding-bfs-dfs.md",
      },
    ],
  });

  assert.deepEqual(
    manifest.routes.map((route) => route.href),
    [
      "/",
      "/start",
      "/learning-paths",
      "/theory",
      "/patterns",
      "/coding",
      "/lld",
      "/hld-concepts",
      "/hld",
      "/genai",
      "/case-studies",
      "/interview",
      "/quizzes",
      "/flashcards",
      "/resources",
      "/progress",
      "/theory/oop",
      "/patterns/creational",
      "/theory/oop/solid",
      "/patterns/creational/factory",
      "/coding/bfs-dfs",
      "/lld/parking-lot",
      "/genai/lld/embedding-service",
      "/resources/study-plans/1-week-plan",
      "/quizzes/design-patterns",
      "/quizzes/missing-answer",
      "/interview/lld/parking-lot",
      "/reveal/solution/lld/parking-lot",
      "/interview/coding/bfs-dfs-pack",
      "/reveal/solution/coding/bfs-dfs-pack",
      "/reveal/quiz-answer/design-patterns",
    ]
  );
  assert.equal(manifest.counts.bySection["LLD Projects"], 1);
  assert.equal(manifest.counts.bySection["Design Patterns"], 1);
  assert.equal(manifest.counts.bySection["Coding Patterns"], 1);
  assert.equal(manifest.counts.bySection["GenAI Systems"], 1);
  assert.equal(manifest.counts.bySection["Interview Mode"], 2);
  assert.equal(manifest.counts.bySection.Resources, 1);
  assert.equal(manifest.counts.bySection.Quizzes, 2);
  assert.equal(manifest.counts.total, 31);

  const hrefs = new Set(manifest.routes.map((route) => route.href));
  assert.equal(hrefs.has("/interview/lld"), false);
  assert.equal(hrefs.has("/genai/lld"), false);
  assert.equal(hrefs.has("/reveal/quiz-answer/missing-answer"), false);
  assert.equal(
    manifest.routes.find((route) => route.href === "/reveal/solution/lld/parking-lot")?.source,
    "reveal"
  );
  assert.equal(
    manifest.routes.find((route) => route.href === "/interview/coding/bfs-dfs-pack")?.source,
    "interview"
  );
});

test("createRouteManifest rejects duplicate public routes", () => {
  assert.throws(
    () =>
      createRouteManifest({
        registry: {
          theory: [],
          patterns: [],
          lldProjects: [
            item({
              id: "lld-one",
              title: "One",
              category: "lld-project",
              href: "/lld/duplicate",
            }),
            item({
              id: "lld-two",
              title: "Two",
              category: "lld-project",
              href: "/lld/duplicate",
            }),
          ],
          hldConcepts: [],
          hldProjects: [],
          genaiConcepts: [],
          genaiLLD: [],
          genaiHLD: [],
          codingTopics: [],
          caseStudies: [],
        },
        quizSlugs: [],
        interviewProblems: [],
      }),
    /Duplicate portal route: \/lld\/duplicate/
  );
});

test("createRouteManifest rejects unsafe route inputs", () => {
  const baseInput = {
    registry: {
      theory: [],
      patterns: [],
      lldProjects: [],
      hldConcepts: [],
      hldProjects: [],
      genaiConcepts: [],
      genaiLLD: [],
      genaiHLD: [],
      codingTopics: [],
      caseStudies: [],
    },
    quizSlugs: [],
    interviewProblems: [],
  };

  for (const href of [
    "relative/path",
    "//evil.example/route",
    "https://evil.example/route",
    "/resources/study-plans/one?debug=1",
    "/resources/study-plans/one#debug",
    "/resources\\study-plans",
    "/resources/%2e%2e/secret",
    "/resources/../secret",
    "/resources/study_plans",
    "/resources/study-plans/",
    "/resources//study-plans",
    "/unknown/root",
  ]) {
    assert.throws(
      () =>
        createRouteManifest({
          ...baseInput,
          resourceEntries: [
            {
              id: "resource-bad",
              title: "Bad",
              href,
              category: "Resources",
            },
          ],
        }),
      /Unsafe portal route/,
      href
    );
  }

  assert.throws(
    () =>
      createRouteManifest({
        ...baseInput,
        resourceEntries: [
          {
            id: "resource-source-intake-temp-upload",
            title: "Source Intake",
            href: "/resources/source-intake/temp-upload",
            category: "Source Intake",
          },
        ],
      }),
    /Unsafe portal route/
  );

  assert.throws(
    () =>
      createRouteManifest({
        ...baseInput,
        quizSlugs: ["../secret"],
      }),
    /Unsafe portal route/
  );
  assert.throws(
    () =>
      createRouteManifest({
        ...baseInput,
        interviewProblems: [
          {
            slug: "parking%2flot",
            title: "Parking Lot",
            type: "lld",
            difficulty: "beginner",
            solutionPath: "solutions/lld-parking-lot.md",
          },
        ],
      }),
    /Unsafe portal route/
  );
});
