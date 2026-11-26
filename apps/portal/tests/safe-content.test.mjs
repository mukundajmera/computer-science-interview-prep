import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";
import ts from "typescript";

async function importTypeScriptModule(relativePath) {
  const outputRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-ts-test-"));
  const modulePaths = [
    "../src/content/safe-content.ts",
    "../src/content/reveal-markdown.ts",
  ];

  for (const candidate of modulePaths) {
    const modulePath = fileURLToPath(new URL(candidate, import.meta.url));
    if (!fs.existsSync(modulePath)) continue;

    const source = fs
      .readFileSync(modulePath, "utf-8")
      .replace('from "./safe-content";', 'from "./safe-content.mjs";');
    const transpiled = ts.transpileModule(source, {
      compilerOptions: {
        esModuleInterop: true,
        module: ts.ModuleKind.ES2022,
        target: ts.ScriptTarget.ES2022,
      },
    });
    const outputPath = path.join(
      outputRoot,
      path.basename(candidate).replace(/\.ts$/, ".mjs")
    );
    fs.writeFileSync(outputPath, transpiled.outputText);
  }

  const entryPath = path.join(
    outputRoot,
    path.basename(relativePath).replace(/\.ts$/, ".mjs")
  );
  return import(pathToFileURL(entryPath).href);
}

const { resolvePathWithinRoot, resolveRevealMarkdownPath } =
  await importTypeScriptModule("../src/content/safe-content.ts");
const { renderRevealMarkdown } = await importTypeScriptModule(
  "../src/content/reveal-markdown.ts"
);

function makeFixtureRoot() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "portal-safe-content-"));
  fs.mkdirSync(path.join(root, "solutions"), { recursive: true });
  fs.mkdirSync(path.join(root, "quizzes", "answers"), { recursive: true });
  for (const resourceRoot of [
    "study-plans",
    "cheatsheets",
    "interview-tips",
    "templates",
    "internal",
  ]) {
    fs.mkdirSync(path.join(root, "resources", resourceRoot), { recursive: true });
    fs.writeFileSync(
      path.join(root, "resources", resourceRoot, "known.md"),
      `# ${resourceRoot}\n`
    );
  }
  fs.writeFileSync(path.join(root, "solutions", "known.md"), "# Known\n");
  fs.writeFileSync(path.join(root, "quizzes", "answers", "known-answers.md"), "# Answers\n");
  fs.writeFileSync(path.join(root, "package.json"), "{}\n");
  fs.writeFileSync(path.join(root, ".env"), "SECRET=value\n");
  return root;
}

test("resolvePathWithinRoot allows markdown inside an approved root", () => {
  const root = makeFixtureRoot();

  const resolved = resolvePathWithinRoot(root, "solutions/known.md", {
    allowedRoots: ["solutions", "quizzes/answers"],
    requireMarkdown: true,
  });

  assert.equal(resolved, fs.realpathSync.native(path.join(root, "solutions", "known.md")));
});

test("resolvePathWithinRoot rejects traversal, encoded traversal, absolute paths, dotfiles, and non-markdown", () => {
  const root = makeFixtureRoot();
  const options = {
    allowedRoots: ["solutions", "quizzes/answers"],
    requireMarkdown: true,
  };

  for (const candidate of [
    "../README.md",
    "%2e%2e/README.md",
    "..\\README.md",
    "/etc/passwd",
    ".env",
    "package.json",
    "solutions/../package.json",
  ]) {
    assert.equal(resolvePathWithinRoot(root, candidate, options), null, candidate);
  }
});

test("default content boundary allows only public resource categories", () => {
  const root = makeFixtureRoot();

  for (const category of [
    "study-plans",
    "cheatsheets",
    "interview-tips",
    "templates",
  ]) {
    assert.equal(
      resolvePathWithinRoot(root, `resources/${category}/known.md`, {
        requireMarkdown: true,
      }),
      fs.realpathSync.native(path.join(root, "resources", category, "known.md")),
      category
    );
  }

  assert.equal(
    resolvePathWithinRoot(root, "resources/internal/known.md", {
      requireMarkdown: true,
    }),
    null
  );
  assert.equal(
    resolvePathWithinRoot(root, "resources/README.md", {
      requireMarkdown: true,
    }),
    null
  );
});

test("resolvePathWithinRoot rejects symlink escapes from an approved root", (t) => {
  const root = makeFixtureRoot();
  const external = fs.mkdtempSync(path.join(os.tmpdir(), "portal-safe-external-"));
  fs.writeFileSync(path.join(external, "secret.md"), "# Secret\n");
  const linkPath = path.join(root, "solutions", "escape.md");

  try {
    fs.symlinkSync(path.join(external, "secret.md"), linkPath);
  } catch (error) {
    t.skip(`symlink creation unavailable: ${error.message}`);
    return;
  }

  const resolved = resolvePathWithinRoot(root, "solutions/escape.md", {
    allowedRoots: ["solutions"],
    requireMarkdown: true,
  });

  assert.equal(resolved, null);
});

test("resolveRevealMarkdownPath resolves only server-owned solution and quiz answer ids", () => {
  const root = makeFixtureRoot();
  const options = {
    repoRoot: root,
    solutionEntries: [
      {
        type: "hld",
        slug: "url-shortener",
        solutionPath: "solutions/known.md",
      },
    ],
    quizSlugs: ["known"],
  };

  assert.equal(
    resolveRevealMarkdownPath(
      {
        kind: "solution",
        type: "hld",
        slug: "url-shortener",
      },
      options
    ),
    "solutions/known.md"
  );
  assert.equal(
    resolveRevealMarkdownPath(
      {
        kind: "quiz-answer",
        slug: "known",
      },
      options
    ),
    "quizzes/answers/known-answers.md"
  );
});

test("resolveRevealMarkdownPath rejects unknown ids and raw/path-like payloads", () => {
  const root = makeFixtureRoot();
  const options = {
    repoRoot: root,
    solutionEntries: [
      {
        type: "hld",
        slug: "url-shortener",
        solutionPath: "solutions/known.md",
      },
    ],
    quizSlugs: ["known"],
  };

  for (const request of [
    "../README.md",
    { kind: "solution", type: "hld", slug: "../url-shortener" },
    { kind: "solution", type: "hld", slug: "missing" },
    { kind: "quiz-answer", slug: "%2e%2e/design-patterns" },
    { kind: "quiz-answer", slug: "missing" },
    { kind: "unknown", slug: "design-patterns" },
  ]) {
    assert.equal(resolveRevealMarkdownPath(request, options), null, JSON.stringify(request));
  }
});

test("renderRevealMarkdown rejects forged requests before loading content", async () => {
  const root = makeFixtureRoot();
  const loadedPaths = [];
  const dependencies = {
    repoRoot: root,
    solutionEntries: [
      {
        type: "hld",
        slug: "url-shortener",
        solutionPath: "solutions/known.md",
      },
    ],
    quizSlugs: ["known"],
    loadFile(relativePath) {
      loadedPaths.push(relativePath);
      return fs.readFileSync(path.join(root, relativePath), "utf-8");
    },
    async renderMarkdown(markdown) {
      return { html: `<article>${markdown.trim()}</article>` };
    },
  };

  for (const request of [
    "../README.md",
    { kind: "solution", type: "hld", slug: "../url-shortener" },
    { kind: "solution", type: "hld", slug: "missing" },
    { kind: "quiz-answer", slug: "%2e%2e/design-patterns" },
    { kind: "quiz-answer", slug: "missing" },
  ]) {
    assert.equal(await renderRevealMarkdown(request, dependencies), null);
  }
  assert.deepEqual(loadedPaths, []);
});

test("renderRevealMarkdown renders known solution and quiz answer ids", async () => {
  const root = makeFixtureRoot();
  const loadedPaths = [];
  const renderedPaths = [];
  const dependencies = {
    repoRoot: root,
    solutionEntries: [
      {
        type: "hld",
        slug: "url-shortener",
        solutionPath: "solutions/known.md",
      },
    ],
    quizSlugs: ["known"],
    loadFile(relativePath) {
      loadedPaths.push(relativePath);
      return fs.readFileSync(path.join(root, relativePath), "utf-8");
    },
    async renderMarkdown(markdown, relativePath) {
      renderedPaths.push(relativePath);
      return { html: `<article>${markdown.trim()}</article>` };
    },
  };

  assert.equal(
    await renderRevealMarkdown(
      {
        kind: "solution",
        type: "hld",
        slug: "url-shortener",
      },
      dependencies
    ),
    "<article># Known</article>"
  );
  assert.equal(
    await renderRevealMarkdown(
      {
        kind: "quiz-answer",
        slug: "known",
      },
      dependencies
    ),
    "<article># Answers</article>"
  );
  assert.deepEqual(loadedPaths, ["solutions/known.md", "quizzes/answers/known-answers.md"]);
  assert.deepEqual(renderedPaths, ["solutions/known.md", "quizzes/answers/known-answers.md"]);
});

test("static reveal renderer keeps portal link rewriting enabled", () => {
  const sourcePath = fileURLToPath(new URL("../src/content/static-reveal.ts", import.meta.url));
  const source = fs.readFileSync(sourcePath, "utf-8");

  assert.match(source, /renderPortalMarkdown/);
  assert.match(source, /currentRoute/);
  assert.match(source, /listInterviewProblems/);
  assert.match(source, /solutionEntries:\s*interviewProblems/);
  assert.doesNotMatch(source, /renderMarkdown\s*}/);
});

test("reveal client components do not import server actions", () => {
  for (const component of [
    "../src/components/interview/SolutionReveal.tsx",
    "../src/components/interview/QuizViewer.tsx",
  ]) {
    const componentPath = fileURLToPath(new URL(component, import.meta.url));
    const source = fs.readFileSync(componentPath, "utf-8");

    assert.doesNotMatch(source, /@\/content\/actions/, component);
    assert.doesNotMatch(source, /fetchRevealMarkdown/, component);
  }
});

test("server action reveal boundary is removed for static export", () => {
  const actionsPath = fileURLToPath(new URL("../src/content/actions.ts", import.meta.url));

  assert.equal(fs.existsSync(actionsPath), false);
});

test("interview and quiz pages fetch reveal content from static routes", () => {
  const pagePaths = [
    "../src/app/interview/[type]/[project]/page.tsx",
    "../src/app/quizzes/[quiz]/page.tsx",
  ];

  for (const pagePath of pagePaths) {
    const sourcePath = fileURLToPath(new URL(pagePath, import.meta.url));
    const source = fs.readFileSync(sourcePath, "utf-8");

    assert.doesNotMatch(source, /renderStaticRevealMarkdown/, pagePath);
    assert.doesNotMatch(source, /solutionHtml|answersHtml/, pagePath);
    assert.match(source, /revealHref|answersHref/, pagePath);
  }
});
