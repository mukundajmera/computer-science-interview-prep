import { resolveGitHubPagesBasePath } from "./site-config.mjs";

const isGitHubPages = process.env.GITHUB_PAGES === "true";
const pagesBasePath = isGitHubPages ? resolveGitHubPagesBasePath() : "";

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  ...(isGitHubPages
    ? {
        basePath: pagesBasePath,
        assetPrefix: `${pagesBasePath}/`,
      }
    : {}),
};

export default nextConfig;
