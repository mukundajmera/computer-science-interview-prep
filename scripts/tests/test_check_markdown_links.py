import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_markdown_links.py"


class MarkdownLinkCheckerTest(unittest.TestCase):
    def test_reports_missing_files_and_missing_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "guide.md").write_text(
                "\n".join(
                    [
                        "# Guide",
                        "",
                        "[Valid file](./target.md)",
                        "[Valid anchor](./target.md#deep-dive)",
                        "[Missing file](./missing.md)",
                        "[Missing anchor](./target.md#not-present)",
                    ]
                ),
                encoding="utf-8",
            )
            (docs / "target.md").write_text(
                "\n".join(["# Target", "", "## Deep Dive", ""]),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(docs / "guide.md")],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing-file", result.stdout)
        self.assertIn("missing-anchor", result.stdout)
        self.assertIn("guide.md:5", result.stdout)
        self.assertIn("guide.md:6", result.stdout)
        self.assertIn("missing.md", result.stdout)
        self.assertIn("#not-present", result.stdout)
        self.assertNotIn("target.md#deep-dive", result.stdout)

    def test_accepts_valid_files_directories_and_github_style_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            nested = docs / "nested"
            nested.mkdir(parents=True)
            (docs / "guide.md").write_text(
                "\n".join(
                    [
                        "# 🚀 Quick Start",
                        "",
                        "[Self anchor](#-quick-start)",
                        "[Nested directory](./nested/)",
                        "[Nested README anchor](./nested/#api-design)",
                        "[External skipped](https://example.com/missing#anchor)",
                    ]
                ),
                encoding="utf-8",
            )
            (nested / "README.md").write_text("# API Design\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(docs / "guide.md")],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("checked 1 markdown file", result.stdout)

    def test_allowlist_suppresses_intentional_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            source = docs / "guide.md"
            source.write_text("[Known gap](./future.md)\n", encoding="utf-8")
            allowlist = root / "allowlist.txt"
            allowlist.write_text("docs/guide.md|./future.md\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--allowlist",
                    str(allowlist),
                    str(source),
                ],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_reference_style_links_validate_definitions_and_usages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            source = docs / "guide.md"
            source.write_text(
                "\n".join(
                    [
                        "# Guide",
                        "",
                        "[Valid reference][target-ref]",
                        "[Collapsed reference][]",
                        "[Missing reference][missing-ref]",
                        "[Bad target][bad-ref]",
                        "`Piece[8][8]`",
                        "`[a-zA-Z_][a-zA-Z0-9_]*`",
                        "",
                        "[target-ref]: ./target.md#deep-dive",
                        "[Collapsed reference]: ./target.md",
                        "[bad-ref]: ./missing.md",
                    ]
                ),
                encoding="utf-8",
            )
            (docs / "target.md").write_text(
                "\n".join(["# Target", "", "## Deep Dive", ""]),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source)],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing-reference", result.stdout)
        self.assertIn("[Missing reference][missing-ref]", result.stdout)
        self.assertIn("guide.md:5", result.stdout)
        self.assertIn("missing-file", result.stdout)
        self.assertIn("./missing.md", result.stdout)
        self.assertNotIn("[8][8]", result.stdout)
        self.assertNotIn("[a-zA-Z_][a-zA-Z0-9_]", result.stdout)
        self.assertNotIn("[Valid reference][target-ref]", result.stdout)
        self.assertNotIn("[Collapsed reference][]", result.stdout)

    def test_rejects_absolute_paths_and_symlink_escapes(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = Path(tmp)
            outside = Path(outside_tmp)
            (outside / "secret.md").write_text("# Secret\n", encoding="utf-8")
            docs = root / "docs"
            docs.mkdir()
            directory_with_readme = docs / "directory"
            directory_with_readme.mkdir()
            source = docs / "guide.md"
            direct_link_path = docs / "escape.md"
            readme_link_path = directory_with_readme / "README.md"
            try:
                direct_link_path.symlink_to(outside / "secret.md")
                readme_link_path.symlink_to(outside / "secret.md")
            except OSError as error:
                self.skipTest(f"symlink creation unavailable: {error}")
            source.write_text(
                "\n".join(
                    [
                        "[Absolute](/etc/passwd)",
                        "[Symlink escape](./escape.md#secret)",
                        "[Extensionless symlink fallback](./escape#secret)",
                        "[Directory README symlink escape](./directory/#secret)",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source)],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("unsafe-path", result.stdout)
        self.assertIn("/etc/passwd", result.stdout)
        self.assertIn("escape.md#secret", result.stdout)
        self.assertIn("escape#secret", result.stdout)
        self.assertIn("directory/#secret", result.stdout)

    def test_duplicate_headings_use_github_style_suffixes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "guide.md").write_text(
                "\n".join(["# Guide", "[Second API](./target.md#api-1)"]),
                encoding="utf-8",
            )
            (docs / "target.md").write_text(
                "\n".join(["# API", "## API", ""]),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(docs / "guide.md")],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_github_slugger_preserves_emoji_variation_selector_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "README.md"
            source.write_text(
                "\n".join(
                    [
                        "# Index",
                        "",
                        "[Component Map](#️-system-design-components-map)",
                        "",
                        "## 🗺️ System Design Components Map",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source)],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_root_scan_skips_and_explicit_input_rejects_temp_upload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Root\n", encoding="utf-8")
            blocked_dir = root / "temp_upload"
            blocked_dir.mkdir()
            (blocked_dir / "payload.md").write_text("[Broken](./missing.md)\n", encoding="utf-8")

            root_result = subprocess.run(
                [sys.executable, str(SCRIPT)],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            explicit_result = subprocess.run(
                [sys.executable, str(SCRIPT), str(blocked_dir / "payload.md")],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(root_result.returncode, 0, root_result.stdout + root_result.stderr)
        self.assertIn("checked 1 markdown file", root_result.stdout)
        self.assertNotIn("missing.md", root_result.stdout)
        self.assertEqual(explicit_result.returncode, 2, explicit_result.stdout + explicit_result.stderr)
        self.assertIn("refusing to scan temp_upload", explicit_result.stderr)

    def test_rejects_links_into_temp_upload_before_anchor_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            blocked_dir = root / "temp_upload"
            blocked_dir.mkdir()
            (blocked_dir / "payload.md").write_text("# Secret Anchor\n", encoding="utf-8")
            (docs / "guide.md").write_text(
                "[Blocked](../temp_upload/payload.md#secret-anchor)\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(docs / "guide.md")],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("blocked-source-path", result.stdout)
        self.assertNotIn("missing-anchor", result.stdout)

    def test_reports_invalid_encoding_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "cp1252.md").write_bytes(
                b"# Title\n\nNorth-South traffic\x97entering.\n"
            )
            (docs / "valid.md").write_text(
                "\n".join(
                    [
                        "# Valid",
                        "",
                        "[Anchor in undecodable](./cp1252.md#title)",
                        "[Missing](./missing.md)",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(docs)],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("docs/cp1252.md:0: invalid-encoding:", result.stdout)
        self.assertIn("docs/valid.md:3: invalid-encoding: ./cp1252.md#title", result.stdout)
        self.assertIn("not valid UTF-8", result.stdout)
        self.assertIn("docs/valid.md:4: missing-file: ./missing.md", result.stdout)
        self.assertIn("checked 2 markdown files", result.stdout)


if __name__ == "__main__":
    unittest.main()
