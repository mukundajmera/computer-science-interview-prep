import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

const notFoundUrl = new URL("../src/app/not-found.tsx", import.meta.url);
const readSource = () => fs.readFileSync(notFoundUrl, "utf-8");

test("not-found.tsx exists", () => {
  assert.ok(fs.existsSync(notFoundUrl), "src/app/not-found.tsx is missing");
});

test("not-found.tsx has a default export function", () => {
  assert.match(readSource(), /export default function \w+/);
});

test("not-found.tsx is a server component (no use client directive)", () => {
  assert.doesNotMatch(readSource(), /["']use client["']/);
});

test("not-found.tsx builds links from PORTAL_SECTIONS", () => {
  assert.match(
    readSource(),
    /import\s*\{\s*PORTAL_SECTIONS\s*\}\s*from\s*["']@\/lib\/sections["']/
  );
});

test("not-found.tsx has no hard-coded routes besides the home link", () => {
  const source = readSource();
  const hardCodedHrefs = [...source.matchAll(/href="(\/[^"]*)"/g)].map(
    (match) => match[1]
  );
  for (const href of hardCodedHrefs) {
    assert.equal(href, "/", `unexpected hard-coded route ${href}`);
  }
  assert.ok(
    hardCodedHrefs.includes("/"),
    "expected one home link with literal href=\"/\""
  );
});
