#!/usr/bin/env python3
"""Validate local Markdown links and heading anchors."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


SKIP_DIRS = {
    ".git",
    ".next",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "temp_upload",
}

SKIP_SUFFIXES = {
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".svg",
    ".webp",
}

EXTERNAL_SCHEMES = {
    "http",
    "https",
    "mailto",
    "tel",
}

INLINE_LINK_RE = re.compile(r"(!?)\[([^\]\n]+)\]\(([^)\n]+)\)")
REFERENCE_DEF_RE = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s+(\S+)", re.MULTILINE)
REFERENCE_USAGE_RE = re.compile(r"(!?)\[([^\]\n]+)\]\[([^\]\n]*)\]")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.MULTILINE)
HTML_ANCHOR_RE = re.compile(r"<a\s+[^>]*(?:id|name)=[\"']([^\"']+)[\"']", re.IGNORECASE)
HTML_ID_RE = re.compile(r"\sid=[\"']([^\"']+)[\"']", re.IGNORECASE)
FENCE_RE = re.compile(r"(^|\n)(```|~~~).*?(\n\2[ \t]*$)", re.MULTILINE | re.DOTALL)
INLINE_CODE_RE = re.compile(r"`+[^`\n]*`+")


@dataclass(frozen=True)
class Finding:
    kind: str
    source: Path
    line: int
    target: str
    message: str


@dataclass(frozen=True)
class MarkdownLink:
    target: str
    line: int


@dataclass(frozen=True)
class ReferenceUsage:
    label: str
    display: str
    line: int


def strip_code_fences(markdown: str) -> str:
    return FENCE_RE.sub(lambda match: "\n" * match.group(0).count("\n"), markdown)


def strip_link_code(markdown: str) -> str:
    without_fences = strip_code_fences(markdown)
    return INLINE_CODE_RE.sub(lambda match: " " * len(match.group(0)), without_fences)


def link_line(markdown: str, offset: int) -> int:
    return markdown.count("\n", 0, offset) + 1


def iter_markdown_links(markdown: str) -> Iterator[MarkdownLink]:
    link_source = strip_link_code(markdown)
    for match in INLINE_LINK_RE.finditer(link_source):
        yield MarkdownLink(match.group(3).strip(), link_line(link_source, match.start()))
    for match in REFERENCE_DEF_RE.finditer(link_source):
        yield MarkdownLink(match.group(2).strip(), link_line(link_source, match.start()))


def normalize_reference_label(label: str) -> str:
    return re.sub(r"\s+", " ", label.strip()).casefold()


def reference_definitions(markdown: str) -> set[str]:
    without_fences = strip_link_code(markdown)
    return {
        normalize_reference_label(match.group(1))
        for match in REFERENCE_DEF_RE.finditer(without_fences)
    }


def iter_reference_usages(markdown: str) -> Iterator[ReferenceUsage]:
    link_source = strip_link_code(markdown)
    for match in REFERENCE_USAGE_RE.finditer(link_source):
        label = match.group(3).strip() or match.group(2).strip()
        display = link_source[match.start() : match.end()]
        yield ReferenceUsage(label, display, link_line(link_source, match.start()))


def normalize_target(target: str) -> str:
    stripped = target.strip()
    if (stripped.startswith("<") and stripped.endswith(">")) or (
        stripped.startswith('"') and stripped.endswith('"')
    ):
        return stripped[1:-1].strip()
    return stripped


def is_external_or_special(target: str) -> bool:
    parsed = urllib.parse.urlparse(target)
    return parsed.scheme.lower() in EXTERNAL_SCHEMES or target.startswith("data:")


def slugify_heading(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = text.strip().lower()
    kept = []
    for char in text:
        if char.isalnum() or char in {" ", "-", "_", "\ufe0f"}:
            kept.append(char)
    return "".join(kept).replace(" ", "-")


def anchor_candidates(markdown: str) -> set[str]:
    anchors: set[str] = set()
    slug_counts: dict[str, int] = {}
    for match in HEADING_RE.finditer(strip_code_fences(markdown)):
        base_slug = slugify_heading(match.group(2))
        count = slug_counts.get(base_slug, 0)
        anchors.add(base_slug if count == 0 else f"{base_slug}-{count}")
        slug_counts[base_slug] = count + 1
    anchors.update(match.group(1) for match in HTML_ANCHOR_RE.finditer(markdown))
    anchors.update(match.group(1) for match in HTML_ID_RE.finditer(markdown))
    return anchors


def normalize_fragment(fragment: str) -> str:
    return urllib.parse.unquote(fragment).strip().lower()


def is_within(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def resolve_candidate(source: Path, link_path: str) -> Path:
    decoded = urllib.parse.unquote(link_path)
    if decoded == "":
        return source
    return (source.parent / decoded).resolve()


def repository_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def is_blocked_temp_upload_path(path: Path, root: Path) -> bool:
    try:
        parts = path.resolve().relative_to(root.resolve()).parts
    except ValueError:
        parts = path.parts
    return "temp_upload" in parts


def allowlist_key(source: Path, target: str, root: Path) -> str:
    return f"{repository_relative(source, root)}|{target}"


def load_allowlist(path: Path | None) -> set[str]:
    if path is None:
        return set()
    entries = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            entries.add(stripped)
    return entries


def target_exists(resolved: Path, root: Path) -> Path | None:
    if not is_within(root, resolved):
        return None
    if is_blocked_temp_upload_path(resolved, root):
        return None
    if resolved.exists() and is_within(root, resolved):
        return resolved
    if resolved.suffix == "":
        markdown = resolved.with_suffix(".md")
        if (
            markdown.exists()
            and is_within(root, markdown)
            and not is_blocked_temp_upload_path(markdown, root)
        ):
            return markdown
    return None


def check_target(source: Path, line: int, target: str, root: Path) -> Finding | None:
    normalized = normalize_target(target)
    if not normalized or is_external_or_special(normalized):
        return None

    parsed = urllib.parse.urlparse(normalized)
    if parsed.scheme or parsed.netloc:
        return None

    path_part = parsed.path
    fragment = normalize_fragment(parsed.fragment)
    decoded_path = urllib.parse.unquote(path_part)
    if decoded_path.startswith("~") or Path(decoded_path).is_absolute():
        return Finding("unsafe-path", source, line, normalized, "target path is outside the repository")
    if path_part and Path(path_part).suffix.lower() in SKIP_SUFFIXES:
        return None

    resolved = resolve_candidate(source, path_part)
    if not is_within(root, resolved):
        return Finding("unsafe-path", source, line, normalized, "target path is outside the repository")
    if is_blocked_temp_upload_path(source, root) or is_blocked_temp_upload_path(resolved, root):
        return Finding("blocked-source-path", source, line, normalized, "temp_upload payload paths are not scanned")

    existing = target_exists(resolved, root)
    if existing is None:
        if resolved.exists():
            return Finding("unsafe-path", source, line, normalized, "target path is outside the repository")
        if resolved.suffix == "" and resolved.with_suffix(".md").exists():
            return Finding("unsafe-path", source, line, normalized, "target path is outside the repository")
        return Finding("missing-file", source, line, normalized, "target file or directory does not exist")

    if fragment:
        if existing.is_dir():
            readme = existing / "README.md"
            if readme.exists() and not is_within(root, readme):
                return Finding("unsafe-path", source, line, normalized, "target path is outside the repository")
            existing = readme
        if not existing.is_file():
            return Finding("missing-anchor", source, line, normalized, "target has no Markdown file for anchor")
        if not is_within(root, existing):
            return Finding("unsafe-path", source, line, normalized, "target path is outside the repository")
        try:
            target_markdown = existing.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return Finding(
                "invalid-encoding",
                source,
                line,
                normalized,
                "target file is not valid UTF-8",
            )
        anchors = anchor_candidates(target_markdown)
        if fragment not in anchors:
            return Finding("missing-anchor", source, line, normalized, "heading anchor does not exist")

    return None


def is_skipped(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def collect_markdown_files(paths: Sequence[Path], root: Path) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if is_blocked_temp_upload_path(path, root):
            raise ValueError(f"refusing to scan temp_upload payload path: {path}")
        if is_skipped(path):
            continue
        if path.is_file() and path.suffix == ".md":
            files.append(path)
        elif path.is_dir():
            for markdown in path.rglob("*.md"):
                if not is_skipped(markdown):
                    files.append(markdown)
    return sorted(set(files))


def check_files(files: Iterable[Path], root: Path, allowlist: set[str]) -> list[Finding]:
    findings: list[Finding] = []
    for source in files:
        try:
            markdown = source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(
                Finding(
                    "invalid-encoding",
                    source,
                    0,
                    repository_relative(source, root),
                    "file is not valid UTF-8",
                )
            )
            continue
        definitions = reference_definitions(markdown)
        for usage in iter_reference_usages(markdown):
            if normalize_reference_label(usage.label) not in definitions:
                findings.append(
                    Finding(
                        "missing-reference",
                        source,
                        usage.line,
                        usage.display,
                        "reference label is not defined",
                    )
                )
        for link in iter_markdown_links(markdown):
            target = link.target
            if allowlist_key(source, normalize_target(target), root) in allowlist:
                continue
            finding = check_target(source, link.line, target, root)
            if finding is not None:
                findings.append(finding)
    return findings


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate local Markdown links and heading anchors."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Markdown files or directories to scan. Defaults to the current directory.",
    )
    parser.add_argument(
        "--allowlist",
        type=Path,
        help="Optional file containing source.md|target entries to suppress.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv or sys.argv[1:])
        root = Path.cwd().resolve()
        paths = args.paths or [root]
        files = collect_markdown_files(paths, root)
        allowlist = load_allowlist(args.allowlist)
        findings = check_files(files, root, allowlist)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    for finding in findings:
        print(
            f"{repository_relative(finding.source, root)}:{finding.line}: "
            f"{finding.kind}: {finding.target} ({finding.message})"
        )

    print(f"checked {len(files)} markdown file{'s' if len(files) != 1 else ''}")
    if findings:
        print(f"found {len(findings)} link issue{'s' if len(findings) != 1 else ''}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
