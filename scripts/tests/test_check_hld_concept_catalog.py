import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_hld_concept_catalog.py"


def write_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_concept(root: Path, slug: str) -> None:
    write_file(root / "03-hld-concepts" / slug / "THEORY.md", f"# {slug}\n")
    write_file(root / "03-hld-concepts" / slug / "INTERVIEW-QA.md", f"# {slug} Q&A\n")


def readme(catalog_rows: str, mapping_rows: str, checklist_items: str) -> str:
    return (
        "# HLD Concepts\n\n"
        "## 📚 Concept Catalog\n\n"
        "| Concept | What It Solves | Related Concepts | Status |\n"
        "|---------|----------------|------------------|--------|\n"
        f"{catalog_rows}\n"
        "\n## 🔗 Concept → Project Mapping\n\n"
        "| Concept | Used In These Projects |\n"
        "|---------|------------------------|\n"
        f"{mapping_rows}\n"
        "\n## ✅ Completion Checklist\n\n"
        f"{checklist_items}\n"
    )


class HldConceptCatalogCheckerTest(unittest.TestCase):
    def run_script(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_passes_when_catalog_mapping_and_checklist_match_concept_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_concept(root, "caching")
            write_concept(root, "idempotency")
            write_file(
                root / "03-hld-concepts" / "README.md",
                readme(
                    "| [Caching](./caching/) | Reduce load | Redis | ✅ Complete |\n"
                    "| [Idempotency](./idempotency/) | Retry safety | APIs | ✅ Complete |\n",
                    "| [Caching](./caching/) | URL Shortener |\n"
                    "| [Idempotency](./idempotency/) | Payment System |\n",
                    "- [x] Caching\n- [x] Idempotency\n",
                ),
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("summary: hld-concepts=2", result.stdout)
        self.assertIn("hld-concept-catalog: ok", result.stdout)

    def test_reports_missing_catalog_mapping_and_checklist_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_concept(root, "caching")
            write_concept(root, "idempotency")
            write_file(
                root / "03-hld-concepts" / "README.md",
                readme(
                    "| [Caching](./caching/) | Reduce load | Redis | ✅ Complete |\n",
                    "| [Caching](./caching/) | URL Shortener |\n",
                    "- [x] Caching\n",
                ),
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing-catalog-row: idempotency", result.stdout)
        self.assertIn("missing-mapping-row: idempotency", result.stdout)
        self.assertIn("missing-checklist-item: idempotency", result.stdout)

    def test_reports_extra_stale_local_concept_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_concept(root, "caching")
            write_file(
                root / "03-hld-concepts" / "README.md",
                readme(
                    "| [Caching](./caching/) | Reduce load | Redis | ✅ Complete |\n"
                    "| [Ghost](./ghost-concept/) | Gone | None | ✅ Complete |\n",
                    "| [Caching](./caching/) | URL Shortener |\n"
                    "| [Ghost](./ghost-concept/) | Nowhere |\n",
                    "- [x] Caching\n",
                ),
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("extra-catalog-row: ghost-concept", result.stdout)
        self.assertIn("extra-mapping-row: ghost-concept", result.stdout)

    def test_reports_stale_unknown_checklist_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_concept(root, "caching")
            write_file(
                root / "03-hld-concepts" / "README.md",
                readme(
                    "| [Caching](./caching/) | Reduce load | Redis | ✅ Complete |\n"
                    "| [Indexing Strategies](../00-theory/database-concepts/indexing.md) | Query performance | Database design | ✅ Complete |\n",
                    "| [Caching](./caching/) | URL Shortener |\n",
                    "- [x] Caching\n- [x] Indexing Strategies\n- [x] SQL vs NoSQL\n",
                ),
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("extra-checklist-item: SQL vs NoSQL", result.stdout)
        self.assertNotIn("extra-checklist-item: Indexing Strategies", result.stdout)

    def test_rejects_ambiguous_complete_status_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_concept(root, "caching")
            write_file(
                root / "03-hld-concepts" / "README.md",
                readme(
                    "| [Caching](./caching/) | Reduce load | Redis | Not Complete |\n",
                    "| [Caching](./caching/) | URL Shortener |\n",
                    "- [x] Caching\n",
                ),
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("invalid-catalog-status: caching", result.stdout)

    def test_allows_external_non_concept_links_in_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_concept(root, "caching")
            write_file(
                root / "03-hld-concepts" / "README.md",
                readme(
                    "| [Caching](./caching/) | Reduce load | Redis | ✅ Complete |\n"
                    "| [Indexing Strategies](../00-theory/database-concepts/indexing.md) | Query performance | Database design | ✅ Complete |\n",
                    "| [Caching](./caching/) | URL Shortener |\n",
                    "- [x] Caching\n",
                ),
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("hld-concept-catalog: ok", result.stdout)

    def test_ignores_incomplete_concepts_and_accepts_theory_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_concept(root, "postgresql")
            write_file(root / "03-hld-concepts" / "draft-concept" / "THEORY.md", "# Draft\n")
            write_file(
                root / "03-hld-concepts" / "README.md",
                readme(
                    "| [PostgreSQL](./postgresql/THEORY.md) | Transactional SQL | Relational data | ✅ Complete |\n",
                    "| [PostgreSQL](./postgresql/THEORY.md) | Orders and workflows |\n",
                    "- [x] PostgreSQL\n",
                ),
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("summary: hld-concepts=1", result.stdout)
        self.assertIn("hld-concept-catalog: ok", result.stdout)

    def test_json_output_is_machine_readable_on_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_concept(root, "idempotency")
            write_file(
                root / "03-hld-concepts" / "README.md",
                readme("", "", ""),
            )

            result = self.run_script(root, "--format", "json")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(set(payload), {"ok", "summary", "findings"})
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["summary"], {"hld-concepts": 1})
        self.assertEqual(
            sorted(finding["kind"] for finding in payload["findings"]),
            ["missing-catalog-row", "missing-checklist-item", "missing-mapping-row"],
        )


if __name__ == "__main__":
    unittest.main()
