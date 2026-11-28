import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath, pathToFileURL } from "node:url";
import ts from "typescript";

async function importTypeScriptModule(relativePath) {
  const outputRoot = fs.mkdtempSync(path.join(os.tmpdir(), "portal-navigation-test-"));
  const modulePath = fileURLToPath(new URL(relativePath, import.meta.url));
  const source = fs.readFileSync(modulePath, "utf-8");
  const transpiled = ts.transpileModule(source, {
    compilerOptions: {
      esModuleInterop: true,
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  });
  const outputPath = path.join(
    outputRoot,
    path.basename(relativePath).replace(/\.ts$/, ".mjs")
  );
  fs.writeFileSync(outputPath, transpiled.outputText);
  return import(pathToFileURL(outputPath).href);
}

const { isActiveSectionRoute } = await importTypeScriptModule(
  "../src/lib/navigation.ts"
);

test("isActiveSectionRoute matches only exact routes or path boundaries", () => {
  assert.equal(isActiveSectionRoute("/hld", "/hld"), true);
  assert.equal(isActiveSectionRoute("/hld/url-shortener", "/hld"), true);
  assert.equal(isActiveSectionRoute("/hld-concepts", "/hld"), false);
  assert.equal(isActiveSectionRoute("/hld-concepts/caching", "/hld"), false);
});

test("breadcrumb and section nav use route-aware matching", () => {
  const sectionNavPath = fileURLToPath(
    new URL("../src/components/layout/SectionNav.tsx", import.meta.url)
  );
  const breadcrumbPath = fileURLToPath(
    new URL("../src/components/layout/Breadcrumb.tsx", import.meta.url)
  );
  const appShellPath = fileURLToPath(
    new URL("../src/components/layout/AppShell.tsx", import.meta.url)
  );

  const sectionNavSource = fs.readFileSync(sectionNavPath, "utf-8");
  const breadcrumbSource = fs.readFileSync(breadcrumbPath, "utf-8");
  const appShellSource = fs.readFileSync(appShellPath, "utf-8");
  const layoutSource = fs.readFileSync(
    fileURLToPath(new URL("../src/app/layout.tsx", import.meta.url)),
    "utf-8"
  );

  assert.match(sectionNavSource, /isActiveSectionRoute\(pathname,\s*section\.href\)/);
  assert.match(sectionNavSource, /sidebarSections\.map/);
  assert.doesNotMatch(sectionNavSource, /pathname\.startsWith\(section\.href\)/);
  assert.match(layoutSource, /buildSectionSummaries\(\)/);
  assert.match(appShellSource, /<SectionNav sections=\{sections\}/);
  assert.match(layoutSource, /const routeHrefs = searchEntries\.map/);
  assert.match(appShellSource, /<Breadcrumb routeHrefs=\{routeHrefs\}/);
  assert.match(breadcrumbSource, /knownRoutes\.has\(href\)/);
});
