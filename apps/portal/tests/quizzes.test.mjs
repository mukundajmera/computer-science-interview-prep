import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";
import ts from "typescript";

async function importQuizzesModule() {
  const outputRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-quizzes-test-"));

  fs.writeFileSync(
    path.join(outputRoot, "loader.mjs"),
    `export function listMarkdownFiles() {
      return [
        "graphs-quiz.md",
        "missing-answer-quiz.md",
        "blocked-answer-quiz.md",
        "blocked-quiz-quiz.md",
        "README.md"
      ];
    }
    export function fileExists(relativePath) {
      return [
        "quizzes/answers/graphs-answers.md",
        "quizzes/answers/blocked-answer-answers.md",
      ].includes(relativePath);
    }\n`
  );
  fs.writeFileSync(
    path.join(outputRoot, "source-provenance.mjs"),
    `export function isBlockedBySourceProvenance(relativePath) {
      return globalThis.__BLOCKED_QUIZ_SOURCES__?.has(relativePath) ?? false;
    }\n`
  );
  fs.writeFileSync(
    path.join(outputRoot, "utils.mjs"),
    `export function slugToTitle(slug) {
      return slug.split("-").map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
    }\n`
  );

  const modulePath = fileURLToPath(
    new URL("../src/content/quizzes.ts", import.meta.url)
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
    .replace(/from ["']@\/content\/loader["']/g, 'from "./loader.mjs"')
    .replace(
      /from ["']@\/content\/source-provenance["']/g,
      'from "./source-provenance.mjs"'
    )
    .replace(/from ["']@\/lib\/utils["']/g, 'from "./utils.mjs"');
  const outputPath = path.join(outputRoot, "quizzes.mjs");
  fs.writeFileSync(outputPath, outputSource);

  return import(pathToFileURL(outputPath).href);
}

test("quiz discovery tracks answer-key availability separately from quiz pages", async () => {
  globalThis.__BLOCKED_QUIZ_SOURCES__ = new Set([
    "quizzes/blocked-quiz-quiz.md",
    "quizzes/answers/blocked-answer-answers.md",
  ]);
  const {
    getQuizEntry,
    listQuizAnswerSlugs,
    listQuizEntries,
    listQuizSlugs,
  } = await importQuizzesModule();

  assert.deepEqual(listQuizSlugs(), [
    "graphs",
    "missing-answer",
    "blocked-answer",
  ]);
  assert.deepEqual(listQuizAnswerSlugs(), ["graphs"]);

  assert.deepEqual(
    listQuizEntries().map((quiz) => [
      quiz.slug,
      quiz.hasAnswers,
      quiz.answerMarkdownFile,
    ]),
    [
      ["graphs", true, "quizzes/answers/graphs-answers.md"],
      ["missing-answer", false, null],
      ["blocked-answer", false, null],
    ]
  );
  assert.equal(getQuizEntry("blocked-quiz"), null);
  assert.equal(getQuizEntry("missing-answer")?.hasAnswers, false);
  assert.equal(getQuizEntry("unknown"), null);
  delete globalThis.__BLOCKED_QUIZ_SOURCES__;
});
