#!/usr/bin/env python3
"""Scan tracked file paths for credential-like artifact names."""

from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


SECRET_SUFFIXES = {
    ".env",
    ".key",
    ".pem",
    ".p12",
    ".pfx",
    ".p8",
    ".jks",
    ".keystore",
    ".kdb",
    ".sso",
    ".db",
    ".dump",
    ".sqlite",
    ".sqlite3",
    ".ovpn",
    ".tfstate",
    ".tfvars",
}

SECRET_BASENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".npmrc",
    "auth.json",
    "cookies.txt",
    "cookie.txt",
    "credentials",
    "credentials.json",
    "session.json",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "known_hosts",
    "netrc",
    ".netrc",
    ".bash_history",
    ".zsh_history",
    ".python_history",
    "shell-history.zsh",
}

SECRET_DIR_PARTS = {
    ".aws",
    ".docker",
    ".kube",
    ".oci",
    ".ssh",
    "wallet",
    "wallets",
}

IGNORED_TEXT_SUFFIXES = {".md", ".txt", ".rst"}


@dataclass(frozen=True)
class Finding:
    path: str
    reason: str


def git_ls_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "unknown error"
        raise RuntimeError(f"git ls-files failed: {detail}")
    return sorted(path for path in result.stdout.split("\0") if path)


def load_allowlist(path: Path | None) -> list[str]:
    if path is None:
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            entries.append(stripped)
    return entries


def is_allowlisted(path: str, allowlist: Sequence[str]) -> bool:
    return any(path == entry or segment_glob_match(path, entry) for entry in allowlist)


def segment_glob_match(path: str, pattern: str) -> bool:
    if not any(char in pattern for char in "*?["):
        return False

    def match_parts(path_parts: list[str], pattern_parts: list[str]) -> bool:
        if not pattern_parts:
            return not path_parts
        current = pattern_parts[0]
        if current == "**":
            return match_parts(path_parts, pattern_parts[1:]) or (
                bool(path_parts) and match_parts(path_parts[1:], pattern_parts)
            )
        if not path_parts:
            return False
        return fnmatch.fnmatchcase(path_parts[0], current) and match_parts(
            path_parts[1:], pattern_parts[1:]
        )

    return match_parts(path.split("/"), pattern.split("/"))


def classify_path(path: str) -> str | None:
    pure = Path(path)
    name = pure.name
    lower_name = name.lower()
    suffix = pure.suffix.lower()
    parts = {part.lower() for part in pure.parts}

    if lower_name in SECRET_BASENAMES:
        return f"secret basename {lower_name}"
    if lower_name.startswith("session.") or lower_name.startswith("cookies."):
        return f"secret basename {lower_name}"
    if lower_name.startswith("client_secret") and suffix == ".json":
        return "google client secret json"
    if suffix in IGNORED_TEXT_SUFFIXES:
        return None
    if suffix in SECRET_SUFFIXES:
        return f"secret suffix {suffix}"
    if parts & SECRET_DIR_PARTS:
        return "secret directory component"
    if lower_name.endswith(".env"):
        return "secret env filename"
    return None


def scan_paths(paths: Sequence[str], allowlist: Sequence[str]) -> list[Finding]:
    findings = []
    for path in sorted(paths):
        if is_allowlisted(path, allowlist):
            continue
        reason = classify_path(path)
        if reason is not None:
            findings.append(Finding(path, reason))
    return findings


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan tracked file paths for credential-like artifact names."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument(
        "--allowlist",
        type=Path,
        help="Optional file with exact or glob path patterns to suppress.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = args.root.resolve()
    try:
        tracked = git_ls_files(root)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 2

    allowlist = load_allowlist(args.allowlist)
    findings = scan_paths(tracked, allowlist)
    for finding in findings:
        print(f"secret-artifact: {finding.path} ({finding.reason})")
    print(f"checked {len(tracked)} tracked files")
    if findings:
        print(f"found {len(findings)} tracked secret artifact path{'s' if len(findings) != 1 else ''}")
        return 1
    print("tracked-secret-artifacts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
