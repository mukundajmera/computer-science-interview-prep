import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_hld_project_readiness.py"


def write_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_project(root: Path, slug: str, design: str, include_strong: bool = True) -> None:
    base = root / "04-hld-projects" / slug
    write_file(base / "PROBLEM.md", "# Problem\n\n- [STRONG-ANSWER](./STRONG-ANSWER.md)\n")
    write_file(base / "APPROACH.md", "# Approach\n")
    write_file(base / "DESIGN.md", design)
    write_file(base / "RUBRIC.md", "# Rubric\n")
    write_file(base / "PITFALLS.md", "# Pitfalls\n")
    write_file(base / "FOLLOW-UPS.md", "# Follow-ups\n")
    if include_strong:
        write_file(base / "STRONG-ANSWER.md", "# Strong Answer\n\nA 60-90 second answer.\n")


class HldProjectReadinessCheckerTest(unittest.TestCase):
    def run_script(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_reports_placeholder_terms_and_missing_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project(
                root,
                "online-auction",
                "# Design\n\n## Architecture\n\nG --> S[Domain Service]\n\n- `DomainRecord`\n- `ReadModel`\n",
            )

            result = self.run_script(root, "--only", "online-auction")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("placeholder-term", result.stdout)
        self.assertIn("missing-api", result.stdout)
        self.assertIn("missing-data-model", result.stdout)
        self.assertIn("missing-capacity", result.stdout)
        self.assertIn("missing-failure-path", result.stdout)

    def test_passes_for_interview_ready_project_design(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project(
                root,
                "payment-system",
                """# Design

## APIs

POST /api/v1/payments
GET /api/v1/payments/{id}

## Data Model

| Table | Key fields | Indexes | Retention |
|---|---|---|---|
| payments | id, merchant_id, state | primary key id, index merchant_id | 18 months |

## Capacity

Peak throughput is 15K TPS and p95 latency should stay below 800ms.

## Failure Handling

Retries use idempotency keys, timeout recovery, replay jobs, and rollback by compensating event.
""",
            )

            result = self.run_script(root, "--only", "payment-system")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("hld-project-readiness: ok", result.stdout)

    def test_json_output_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_project(root, "live-comments", "# Design\n\nDomainRecord\n", include_strong=False)

            result = self.run_script(root, "--only", "live-comments", "--format", "json")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["summary"]["hld_projects"], 1)
        self.assertGreater(payload["summary"]["findings"], 0)
        self.assertEqual(payload["findings"][0]["slug"], "live-comments")

    def test_reports_missing_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = self.run_script(root, "--only", "ghost-project")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing-project", result.stdout)


if __name__ == "__main__":
    unittest.main()
