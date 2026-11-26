export const DEFAULT_GITHUB_PAGES_REPOSITORY = "computer-science-interview-prep";
export const DEFAULT_GITHUB_PAGES_BASE_PATH = `/${DEFAULT_GITHUB_PAGES_REPOSITORY}`;

export function normalizeBasePath(value) {
  const normalized = (value ?? "").replace(/^\/+|\/+$/g, "");
  return normalized ? `/${normalized}` : "";
}

export function resolveGitHubPagesBasePath(env = process.env) {
  return normalizeBasePath(
    env.GITHUB_PAGES_BASE_PATH ?? DEFAULT_GITHUB_PAGES_REPOSITORY
  );
}
