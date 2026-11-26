import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";

const portalRoot = fileURLToPath(new URL("..", import.meta.url));
const repoRoot = path.resolve(portalRoot, "../..");

test("Next config enables static export with GitHub Pages path support", () => {
  const configPath = path.join(portalRoot, "next.config.mjs");
  const source = fs.readFileSync(configPath, "utf-8");

  assert.match(source, /output:\s*["']export["']/);
  assert.match(source, /GITHUB_PAGES/);
  assert.match(source, /resolveGitHubPagesBasePath/);
  assert.match(source, /basePath/);
  assert.match(source, /assetPrefix/);
  assert.match(source, /trailingSlash:\s*true/);
});

test("Next config normalizes GitHub Pages base path override", async () => {
  const configPath = path.join(portalRoot, "next.config.mjs");
  const originalGitHubPages = process.env.GITHUB_PAGES;
  const originalBasePath = process.env.GITHUB_PAGES_BASE_PATH;

  process.env.GITHUB_PAGES = "true";
  process.env.GITHUB_PAGES_BASE_PATH = "/custom-portal/";

  try {
    const imported = await import(`${pathToFileURL(configPath).href}?base-path-test`);

    assert.equal(imported.default.basePath, "/custom-portal");
    assert.equal(imported.default.assetPrefix, "/custom-portal/");
  } finally {
    if (originalGitHubPages === undefined) {
      delete process.env.GITHUB_PAGES;
    } else {
      process.env.GITHUB_PAGES = originalGitHubPages;
    }

    if (originalBasePath === undefined) {
      delete process.env.GITHUB_PAGES_BASE_PATH;
    } else {
      process.env.GITHUB_PAGES_BASE_PATH = originalBasePath;
    }
  }
});

test("GitHub Pages workflow builds and deploys exported portal artifact", () => {
  const workflowPath = path.join(repoRoot, ".github/workflows/portal-pages.yml");
  const source = fs.readFileSync(workflowPath, "utf-8");

  assert.match(source, /cancel-in-progress:\s*true/);
  assert.match(source, /actions\/checkout@[a-f0-9]{40}\s*# v4/);
  assert.match(source, /actions\/setup-node@[a-f0-9]{40}\s*# v4/);
  assert.match(source, /actions\/configure-pages@[a-f0-9]{40}\s*# v5/);
  assert.match(source, /actions\/upload-pages-artifact@[a-f0-9]{40}\s*# v4/);
  assert.match(source, /actions\/deploy-pages@[a-f0-9]{40}\s*# v4/);
  assert.doesNotMatch(source, /uses:\s+actions\/[^\s@]+@v\d+/);
  assert.match(source, /npm --prefix apps\/portal run build/);
  assert.match(source, /npm --prefix apps\/portal run check:export/);
  assert.match(source, /apps\/portal\/out/);
  assert.match(source, /SHOULD_DEPLOY:/);
  assert.match(source, /vars\.ENABLE_GITHUB_PAGES_DEPLOYMENT == 'true'/);
  assert.match(source, /workflow_dispatch/);
  assert.match(source, /github\.ref == 'refs\/heads\/main'/);
  assert.match(source, /if:\s*env\.SHOULD_DEPLOY == 'true'/);
  assert.match(source, /deploy:\n\s+name: Deploy static portal\n\s+if: vars\.ENABLE_GITHUB_PAGES_DEPLOYMENT == 'true'/);
  assert.match(source, /build:\n\s+name: Build static portal\n\s+runs-on: ubuntu-latest\n\s+permissions:\n\s+contents: read/);
  assert.match(source, /deploy:\n\s+name: Deploy static portal[\s\S]*permissions:\n\s+contents: read\n\s+pages: write\n\s+id-token: write/);
  assert.doesNotMatch(source, /permissions:\n\s+contents: read\n\s+pages: write\n\s+id-token: write\n\nconcurrency:/);
  const contributorGuidance = fs.readFileSync(path.join(repoRoot, "apps/portal/AGENTS.md"), "utf-8");
  assert.match(contributorGuidance, /private source repository does not make the published Pages site private/i);
  assert.match(contributorGuidance, /explicitly approve the intended audience/i);
  assert.match(contributorGuidance, /does not configure or privatize the Pages site/i);
});

test("repo smoke workflow pins third-party actions and checks portal export", () => {
  const workflowPath = path.join(repoRoot, ".github/workflows/repo-smoke.yml");
  if (!fs.existsSync(workflowPath)) return;

  const source = fs.readFileSync(workflowPath, "utf-8");

  assert.match(source, /actions\/checkout@[a-f0-9]{40}\s*# v4/g);
  assert.match(source, /actions\/setup-python@[a-f0-9]{40}\s*# v5/g);
  assert.match(source, /actions\/setup-node@[a-f0-9]{40}\s*# v4/);
  assert.match(source, /actions\/setup-java@[a-f0-9]{40}\s*# v4/g);
  assert.doesNotMatch(source, /uses:\s+actions\/[^\s@]+@v\d+/);
  assert.match(source, /npm --prefix apps\/portal run check:export/);
});

test("static export start script serves the exported out directory", () => {
  const packagePath = path.join(portalRoot, "package.json");
  const packageJson = JSON.parse(fs.readFileSync(packagePath, "utf-8"));
  const previewScriptPath = path.join(portalRoot, "scripts/serve-static.mjs");
  const exportCheckPath = path.join(portalRoot, "scripts/check-static-export.mjs");
  const siteConfigPath = path.join(portalRoot, "site-config.mjs");
  const previewSource = fs.readFileSync(previewScriptPath, "utf-8");
  const exportCheckSource = fs.readFileSync(exportCheckPath, "utf-8");

  assert.equal(packageJson.scripts.build, "GITHUB_PAGES=true next build");
  assert.equal(packageJson.scripts["build:local"], "next build");
  assert.equal(packageJson.scripts.start, "node scripts/serve-static.mjs");
  assert.equal(packageJson.scripts["check:export"], "node scripts/check-static-export.mjs");
  assert.doesNotMatch(packageJson.scripts.start, /next start/);
  assert.equal(fs.existsSync(previewScriptPath), true);
  assert.equal(fs.existsSync(exportCheckPath), true);
  assert.equal(fs.existsSync(siteConfigPath), true);
  assert.match(previewSource, /GITHUB_PAGES_BASE_PATH/);
  assert.match(previewSource, /Bad request/);
  assert.match(previewSource, /try\s*{/);
  assert.match(exportCheckSource, /GITHUB_PAGES_BASE_PATH/);
  assert.match(exportCheckSource, /routes-manifest\.json/);
  assert.match(exportCheckSource, /app-path-routes-manifest\.json/);
  assert.match(exportCheckSource, /path\.relative\(outDir, filePath\)/);
  assert.match(exportCheckSource, /\?:href\|src/);
  assert.match(exportCheckSource, /decodeURIComponent/);
  assert.match(exportCheckSource, /validateRevealRoutePairs/);
  assert.match(exportCheckSource, /listRoutePaths\("interview", rootDir\)/);
  assert.match(exportCheckSource, /listQuizAnswerSourceSlugs/);
  assert.match(exportCheckSource, /\/reveal\/solution\//);
  assert.match(exportCheckSource, /reveal\/quiz-answer/);
  assert.match(exportCheckSource, /\/quizzes\//);
  assert.match(exportCheckSource, /reveal\/solution\/lld\/parking-lot\/index\.html/);
  assert.match(exportCheckSource, /reveal\/solution\/coding\/bfs-dfs-pack\/index\.html/);
  assert.match(exportCheckSource, /reveal\/solution\/coding\/dynamic-programming-pack\/index\.html/);
  assert.match(exportCheckSource, /reveal\/solution\/coding\/greedy-pack\/index\.html/);
  assert.match(exportCheckSource, /reveal\/solution\/coding\/backtracking-pack\/index\.html/);
  assert.match(exportCheckSource, /reveal\/solution\/coding\/heap-priority-queue-pack\/index\.html/);
  assert.match(exportCheckSource, /reveal\/solution\/coding\/trie-pack\/index\.html/);
  assert.match(exportCheckSource, /reveal\/solution\/coding\/union-find-pack\/index\.html/);
  assert.match(exportCheckSource, /reveal\/quiz-answer\/design-patterns\/index\.html/);
  assert.match(exportCheckSource, /reveal\/quiz-answer\/sliding-window\/index\.html/);
  assert.match(exportCheckSource, /reveal\/quiz-answer\/bfs-dfs\/index\.html/);
  assert.match(exportCheckSource, /reveal\/quiz-answer\/dynamic-programming\/index\.html/);
  assert.match(exportCheckSource, /reveal\/quiz-answer\/greedy\/index\.html/);
  assert.match(exportCheckSource, /reveal\/quiz-answer\/backtracking\/index\.html/);
  assert.match(exportCheckSource, /reveal\/quiz-answer\/heap-priority-queue\/index\.html/);
  assert.match(exportCheckSource, /reveal\/quiz-answer\/trie\/index\.html/);
  assert.match(exportCheckSource, /reveal\/quiz-answer\/union-find\/index\.html/);
  assert.match(exportCheckSource, /coding\/sliding-window\/index\.html/);
  assert.match(exportCheckSource, /coding\/bfs-dfs\/index\.html/);
  assert.match(exportCheckSource, /coding\/dynamic-programming\/index\.html/);
  assert.match(exportCheckSource, /coding\/greedy\/index\.html/);
  assert.match(exportCheckSource, /coding\/backtracking\/index\.html/);
  assert.match(exportCheckSource, /coding\/heap-priority-queue\/index\.html/);
  assert.match(exportCheckSource, /coding\/trie\/index\.html/);
  assert.match(exportCheckSource, /coding\/union-find\/index\.html/);
  assert.match(exportCheckSource, /theory\/big-data-structures\/merkle-tree\/index\.html/);
  assert.match(exportCheckSource, /theory\/big-data-structures\/trie\/index\.html/);
  assert.match(exportCheckSource, /interview\/coding\/bfs-dfs-pack\/index\.html/);
  assert.match(exportCheckSource, /interview\/coding\/dynamic-programming-pack\/index\.html/);
  assert.match(exportCheckSource, /interview\/coding\/greedy-pack\/index\.html/);
  assert.match(exportCheckSource, /interview\/coding\/backtracking-pack\/index\.html/);
  assert.match(exportCheckSource, /interview\/coding\/heap-priority-queue-pack\/index\.html/);
  assert.match(exportCheckSource, /interview\/coding\/trie-pack\/index\.html/);
  assert.match(exportCheckSource, /interview\/coding\/union-find-pack\/index\.html/);
  assert.match(exportCheckSource, /quizzes\/sliding-window\/index\.html/);
  assert.match(exportCheckSource, /quizzes\/bfs-dfs\/index\.html/);
  assert.match(exportCheckSource, /quizzes\/dynamic-programming\/index\.html/);
  assert.match(exportCheckSource, /quizzes\/greedy\/index\.html/);
  assert.match(exportCheckSource, /quizzes\/backtracking\/index\.html/);
  assert.match(exportCheckSource, /quizzes\/heap-priority-queue\/index\.html/);
  assert.match(exportCheckSource, /quizzes\/trie\/index\.html/);
  assert.match(exportCheckSource, /quizzes\/union-find\/index\.html/);
  assert.doesNotMatch(exportCheckSource, /startsWith\("\/_next\/"\)/);
});

test("static export checks expected quiz-answer reveal routes from answer files", async () => {
  const answersRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-quiz-answers-test-"));
  fs.writeFileSync(path.join(answersRoot, "dynamic-programming-answers.md"), "# Answers\n");
  fs.writeFileSync(path.join(answersRoot, "bfs-dfs-answers.md"), "# Answers\n");
  fs.writeFileSync(path.join(answersRoot, "README.md"), "# Ignore\n");
  fs.mkdirSync(path.join(answersRoot, "nested-answers.md"));

  const exportCheckPath = path.join(portalRoot, "scripts/check-static-export.mjs");
  const { listQuizAnswerSourceSlugs } = await import(
    `${pathToFileURL(exportCheckPath).href}?quiz-answer-source-test`
  );

  assert.deepEqual(listQuizAnswerSourceSlugs(answersRoot), [
    "bfs-dfs",
    "dynamic-programming",
  ]);
});

test("static export reports orphan answer files before route validation", async () => {
  const answersRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-orphan-answers-test-"));
  const quizzesRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-orphan-quizzes-test-"));
  const outputRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-orphan-output-test-"));
  const exportCheckPath = path.join(portalRoot, "scripts/check-static-export.mjs");
  const { validateRevealRoutePairs } = await import(
    `${pathToFileURL(exportCheckPath).href}?orphan-answer-test`
  );

  fs.writeFileSync(path.join(answersRoot, "orphan-answers.md"), "# Answers\n");

  assert.throws(
    () => validateRevealRoutePairs(outputRoot, answersRoot, quizzesRoot),
    /Quiz answer files without matching quiz source:\norphan-answers\.md/
  );
});

test("static export reveal-pair validation fails when source-backed reveal pages are absent", async () => {
  const answersRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-reveal-answer-test-"));
  const quizzesRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-reveal-quiz-test-"));
  const outputRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-reveal-output-test-"));
  const exportCheckPath = path.join(portalRoot, "scripts/check-static-export.mjs");
  const { validateRevealRoutePairs } = await import(
    `${pathToFileURL(exportCheckPath).href}?reveal-pair-test`
  );

  fs.writeFileSync(path.join(answersRoot, "source-backed-answers.md"), "# Answers\n");
  fs.writeFileSync(path.join(quizzesRoot, "source-backed-quiz.md"), "# Quiz\n");
  fs.mkdirSync(path.join(outputRoot, "quizzes", "source-backed"), {
    recursive: true,
  });
  fs.writeFileSync(
    path.join(outputRoot, "quizzes", "source-backed", "index.html"),
    "<!doctype html>\n"
  );

  assert.throws(
    () => validateRevealRoutePairs(outputRoot, answersRoot, quizzesRoot),
    /\/reveal\/quiz-answer\/source-backed/
  );

  fs.mkdirSync(path.join(outputRoot, "reveal", "quiz-answer", "source-backed"), {
    recursive: true,
  });
  fs.writeFileSync(
    path.join(outputRoot, "reveal", "quiz-answer", "source-backed", "index.html"),
    "<!doctype html>\n"
  );

  assert.doesNotThrow(() =>
    validateRevealRoutePairs(outputRoot, answersRoot, quizzesRoot)
  );
});

test("static export URL checks reject directories without index pages", async () => {
  const outputRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-export-url-test-"));
  const lonelyDirectory = path.join(outputRoot, "reveal", "solution", "lld");
  const validDirectory = path.join(outputRoot, "interview", "lld", "parking-lot");
  fs.mkdirSync(lonelyDirectory, { recursive: true });
  fs.mkdirSync(validDirectory, { recursive: true });
  fs.writeFileSync(path.join(validDirectory, "index.html"), "<!doctype html>\n");
  fs.writeFileSync(path.join(outputRoot, "asset.html"), "<!doctype html>\n");

  const exportCheckPath = path.join(portalRoot, "scripts/check-static-export.mjs");
  const { existsForUrl } = await import(
    `${pathToFileURL(exportCheckPath).href}?url-check-test`
  );

  assert.equal(existsForUrl("/reveal/solution/lld/", outputRoot), false);
  assert.equal(existsForUrl("/interview/lld/parking-lot/", outputRoot), true);
  assert.equal(existsForUrl("/asset", outputRoot), true);
});
