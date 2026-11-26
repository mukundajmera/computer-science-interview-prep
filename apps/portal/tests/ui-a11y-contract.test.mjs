import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import { fileURLToPath } from "node:url";

function readSource(relativePath) {
  return fs.readFileSync(fileURLToPath(new URL(relativePath, import.meta.url)), "utf-8");
}

test("RevealPanel exposes disclosure state and controlled content", () => {
  const source = readSource("../src/components/content/RevealPanel.tsx");

  assert.match(source, /useId/);
  assert.match(source, /type="button"/);
  assert.match(source, /aria-expanded=\{revealed\}/);
  assert.match(source, /aria-controls=\{contentId\}/);
  assert.match(source, /disabled=\{loading\}/);
  assert.match(source, /if \(loading\) return/);
  assert.match(source, /role="region"/);
  assert.match(source, /hidden=\{!revealed\}/);
  assert.match(source, /fetch\(revealHref\)/);
  assert.match(source, /DOMParser/);
  assert.match(source, /data-reveal-content/);
  assert.doesNotMatch(source, /html:\s*string/);
});

test("SearchBox exposes search result state and supports dismissal", () => {
  const source = readSource("../src/components/layout/SearchBox.tsx");

  assert.match(source, /role="search"/);
  assert.match(source, /aria-controls=\{hasSearchQuery \? listId : undefined\}/);
  assert.match(source, /aria-live="polite"/);
  assert.match(source, /event\.key === "Escape"/);
  assert.match(source, /<ul/);
  assert.match(source, /<li/);
  assert.match(source, /No results found\./);
  assert.doesNotMatch(source, /role="combobox"/);
  assert.doesNotMatch(source, /role="option"/);
});

test("search index remains the route source for search and breadcrumbs", () => {
  const source = readSource("../src/content/search-index.ts");

  assert.match(source, /createRouteManifest/);
  assert.match(source, /listResourceCategoryEntries/);
  assert.match(source, /listResourceEntries/);
  assert.match(source, /listInterviewProblems/);
  assert.match(source, /quizSlugs/);
});

test("InterviewStepper exposes step semantics and note association", () => {
  const source = readSource("../src/components/interview/InterviewStepper.tsx");

  assert.match(source, /aria-label=\{s\.title\}/);
  assert.match(source, /aria-current=\{i === currentStep \? "step" : undefined\}/);
  assert.match(source, /htmlFor="step-notes"/);
  assert.match(source, /id="step-notes"/);
});

test("MarkCompleteButton exposes completion toggle state", () => {
  const source = readSource("../src/components/progress/MarkCompleteButton.tsx");

  assert.match(source, /aria-pressed=\{done\}/);
});

test("ProgressDashboard remove buttons name the item affected", () => {
  const source = readSource("../src/components/progress/ProgressDashboard.tsx");

  assert.match(source, /aria-label=\{`Remove \$\{id\}`\}/);
});
