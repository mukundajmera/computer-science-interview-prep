import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_executable_sample_inventory.py"


def write_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_inventory(root: Path, rows: str) -> None:
    write_file(
        root / "resources" / "executable-sample-inventory.md",
        "# Executable Sample Inventory\n\n"
        "| Path | Status | Evidence |\n"
        "|------|--------|----------|\n"
        f"{rows}",
    )


class ExecutableSampleInventoryCheckerTest(unittest.TestCase):
    def run_script(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_passes_when_inventory_matches_discovered_samples(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_file(root / "03-hld-concepts" / "caching" / "python" / "v1-simple" / "simple_cache.py")
            write_file(root / "03-hld-concepts" / "caching" / "python" / "tests" / "test_cache.py")
            write_inventory(
                root,
                "| `03-hld-concepts/caching/python/v1-simple/simple_cache.py` | tested | Same-language test suite present. |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("summary: executable-samples=1", result.stdout)
        self.assertIn("executable-sample-inventory: ok", result.stdout)

    def test_reports_missing_rows_and_stale_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_file(root / "03-hld-concepts" / "dns" / "java" / "v1-simple" / "SimpleDnsResolver.java")
            write_file(root / "06-genai-systems" / "00-concepts" / "vector-databases" / "python" / "v1-basic" / "simple_vector_store.py")
            write_inventory(
                root,
                "| `03-hld-concepts/dns/java/v1-simple/SimpleDnsResolver.java` | tested | Same-language test suite present. |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("stale-status", result.stdout)
        self.assertIn("missing-inventory-row", result.stdout)

    def test_reports_invalid_duplicate_and_extra_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_file(root / "03-hld-concepts" / "api-gateway" / "python" / "v1-simple" / "simple_gateway.py")
            write_inventory(
                root,
                "| `03-hld-concepts/api-gateway/python/v1-simple/simple_gateway.py` | illustrative-only | No same-language test suite present. |\n"
                "| `03-hld-concepts/api-gateway/python/v1-simple/simple_gateway.py` | illustrative-only | No same-language test suite present. |\n"
                "| `03-hld-concepts/ghost/python/v1-simple/ghost.py` | unknown | Invalid. |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("duplicate-inventory-row", result.stdout)
        self.assertIn("invalid-status", result.stdout)
        self.assertIn("extra-inventory-row", result.stdout)

    def test_move_to_lld_can_override_expected_test_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_file(root / "03-hld-concepts" / "message-queues" / "python" / "v1-simple" / "simple_queue.py")
            write_inventory(
                root,
                "| `03-hld-concepts/message-queues/python/v1-simple/simple_queue.py` | move-to-lld | Should become an LLD project. |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_ignores_tests_init_and_theory_markdown_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_file(root / "00-theory" / "oop" / "README.md")
            write_file(root / "03-hld-concepts" / "caching" / "python" / "v1-simple" / "__init__.py")
            write_file(root / "03-hld-concepts" / "caching" / "python" / "tests" / "test_cache.py")
            write_inventory(root, "")

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("summary: executable-samples=0", result.stdout)


if __name__ == "__main__":
    unittest.main()
