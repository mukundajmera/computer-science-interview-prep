import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  DEFAULT_GITHUB_PAGES_BASE_PATH,
  normalizeBasePath,
} from "../site-config.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.resolve(scriptDir, "../out");
const port = Number.parseInt(process.env.PORT ?? "3000", 10);
const host = process.env.HOST ?? "127.0.0.1";
const defaultBasePath = DEFAULT_GITHUB_PAGES_BASE_PATH;
const configuredBasePath = normalizeBasePath(
  process.env.BASE_PATH ?? process.env.GITHUB_PAGES_BASE_PATH ?? defaultBasePath
);

const contentTypes = new Map([
  [".css", "text/css; charset=utf-8"],
  [".html", "text/html; charset=utf-8"],
  [".ico", "image/x-icon"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".map", "application/json; charset=utf-8"],
  [".svg", "image/svg+xml; charset=utf-8"],
  [".txt", "text/plain; charset=utf-8"],
]);

function stripBasePath(pathname) {
  for (const basePath of [configuredBasePath, defaultBasePath]) {
    if (!basePath || basePath === "/") continue;
    if (pathname === basePath) return "/";
    if (pathname.startsWith(`${basePath}/`)) {
      return pathname.slice(basePath.length) || "/";
    }
  }
  return pathname;
}

function resolveRequestPath(urlPathname) {
  let pathname;
  try {
    pathname = decodeURIComponent(stripBasePath(urlPathname));
  } catch {
    return null;
  }

  if (pathname.includes("\0")) return null;

  const relativePath = pathname.replace(/^\/+/, "");
  const absolutePath = path.resolve(outDir, relativePath);
  const relativeToOut = path.relative(outDir, absolutePath);

  if (relativeToOut.startsWith("..") || path.isAbsolute(relativeToOut)) {
    return null;
  }

  return absolutePath;
}

function findStaticFile(requestPath) {
  if (!requestPath) return null;

  if (fs.existsSync(requestPath) && fs.statSync(requestPath).isFile()) {
    return requestPath;
  }

  const indexPath = path.join(requestPath, "index.html");
  if (fs.existsSync(indexPath) && fs.statSync(indexPath).isFile()) {
    return indexPath;
  }

  return null;
}

function sendFile(response, filePath, statusCode = 200) {
  const extension = path.extname(filePath);
  const contentType = contentTypes.get(extension) ?? "application/octet-stream";

  response.writeHead(statusCode, {
    "Content-Type": contentType,
  });
  fs.createReadStream(filePath).pipe(response);
}

if (!fs.existsSync(outDir)) {
  console.error("Static export not found. Run `npm run build` first.");
  process.exit(1);
}

const server = http.createServer((request, response) => {
  let url;
  try {
    url = new URL(request.url ?? "/", `http://${request.headers.host ?? host}`);
  } catch {
    response.writeHead(400, { "Content-Type": "text/plain; charset=utf-8" });
    response.end("Bad request");
    return;
  }

  const requestPath = resolveRequestPath(url.pathname);
  const staticFile = findStaticFile(requestPath);

  if (staticFile) {
    sendFile(response, staticFile);
    return;
  }

  const notFoundPath = path.join(outDir, "404.html");
  if (fs.existsSync(notFoundPath)) {
    sendFile(response, notFoundPath, 404);
    return;
  }

  response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
  response.end("Not found");
});

server.listen(port, host, () => {
  console.log(`Serving ${outDir} at http://${host}:${port}`);
  console.log(`GitHub Pages path also works at http://${host}:${port}${defaultBasePath}/`);
});
