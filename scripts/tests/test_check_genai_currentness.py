import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_genai_currentness.py"


def write_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def ledger_doc(*rows: str) -> str:
    return "\n".join(
        [
            "# GenAI Currentness Ledger",
            "",
            "| path | claim_type | claim_summary | source_standard | primary_source | verified_on | review_due | status | notes |",
            "|---|---|---|---|---|---|---|---|---|",
            *rows,
            "",
        ]
    )


def interview_data(solution_path: str) -> str:
    return f"""
export const INTERVIEW_PROBLEMS = [
  {{
    slug: "doc-rag",
    title: "Doc RAG",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "{solution_path}",
  }},
];
"""


class GenAICurrentnessCheckerTest(unittest.TestCase):
    def run_script(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def write_minimal_hld(self, root: Path) -> None:
        write_file(
            root / "06-genai-systems/02-llm-hld-projects/doc-rag/PROBLEM.md",
            "# Doc RAG\n\nUse GPT-4 class reasoning for complex synthesis.\n",
        )

    def test_passes_with_dated_ledger_and_genai_hld_solution_parity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimal_hld(root)
            verified_on = date.today()
            review_due = verified_on + timedelta(days=90)
            write_file(
                root / "resources/GENAI-CURRENTNESS-LEDGER.md",
                ledger_doc(
                    f"| `06-genai-systems/02-llm-hld-projects/doc-rag/PROBLEM.md` | `model-surface` | GPT-class example is illustrative | official provider docs when exact models matter | https://developers.openai.com/api/docs/models | {verified_on.isoformat()} | {review_due.isoformat()} | watchlist | Keep generic unless refreshed. |",
                ),
            )
            write_file(
                root / "apps/portal/src/components/interview/interview-data.ts",
                interview_data("solutions/genai-hld-doc-rag.md"),
            )
            write_file(
                root / "solutions/genai-hld-doc-rag.md",
                "# Coach Answer: Doc RAG - GenAI HLD\n\nSay: route through retrieval first.\n",
            )
            write_file(
                root / "solutions/README.md",
                "| Doc RAG | GenAI HLD | ⭐⭐⭐ | [genai-hld-doc-rag.md](genai-hld-doc-rag.md) | Yes |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("summary: genai-volatile-claim-groups=1 genai-hld-interviews=1", result.stdout)
        self.assertIn("genai-currentness: ok", result.stdout)

    def test_reports_missing_currentness_and_interview_solution_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimal_hld(root)
            write_file(
                root / "resources/GENAI-CURRENTNESS-LEDGER.md",
                ledger_doc(),
            )
            write_file(
                root / "apps/portal/src/components/interview/interview-data.ts",
                "export const INTERVIEW_PROBLEMS = [];\n",
            )
            write_file(root / "solutions/README.md", "# Solutions\n")

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing-genai-currentness-row", result.stdout)
        self.assertIn("missing-genai-hld-interview-entry: doc-rag", result.stdout)
        self.assertIn("missing-genai-hld-solution-file: doc-rag", result.stdout)
        self.assertIn("missing-solutions-readme-row: doc-rag", result.stdout)

    def test_requires_rows_for_each_claim_type_in_same_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_file(
                root / "06-genai-systems/02-llm-hld-projects/doc-rag/PROBLEM.md",
                "# Doc RAG\n\nUse GPT-4 class reasoning and pricing estimates during capacity sizing.\n",
            )
            write_file(
                root / "resources/GENAI-CURRENTNESS-LEDGER.md",
                ledger_doc(
                    "| 06-genai-systems/02-llm-hld-projects/doc-rag/PROBLEM.md | model-surface | GPT-class example is illustrative | official provider docs when exact models matter | https://developers.openai.com/api/docs/models | 2026-06-14 | 2026-09-14 | watchlist | Keep generic unless refreshed. |",
                ),
            )
            write_file(
                root / "apps/portal/src/components/interview/interview-data.ts",
                interview_data("solutions/genai-hld-doc-rag.md"),
            )
            write_file(
                root / "solutions/genai-hld-doc-rag.md",
                "# Coach Answer: Doc RAG - GenAI HLD\n\nSay: route through retrieval first.\n",
            )
            write_file(
                root / "solutions/README.md",
                "| Doc RAG | GenAI HLD | ⭐⭐⭐ | [genai-hld-doc-rag.md](genai-hld-doc-rag.md) | Yes |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "missing-genai-currentness-row: "
            "06-genai-systems/02-llm-hld-projects/doc-rag/PROBLEM.md#pricing-cost",
            result.stdout,
        )

    def test_inline_dated_caveat_satisfies_volatile_claim_without_ledger_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_file(
                root / "06-genai-systems/02-llm-hld-projects/doc-rag/PROBLEM.md",
                "# Doc RAG\n\nAs of 2026-06-14, GPT-4 class examples are illustrative only.\n",
            )
            write_file(root / "resources/GENAI-CURRENTNESS-LEDGER.md", ledger_doc())
            write_file(
                root / "apps/portal/src/components/interview/interview-data.ts",
                interview_data("solutions/genai-hld-doc-rag.md"),
            )
            write_file(
                root / "solutions/genai-hld-doc-rag.md",
                "# Coach Answer: Doc RAG - GenAI HLD\n\nSay: route through retrieval first.\n",
            )
            write_file(
                root / "solutions/README.md",
                "| Doc RAG | GenAI HLD | ⭐⭐⭐ | [genai-hld-doc-rag.md](genai-hld-doc-rag.md) | Yes |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("summary: genai-volatile-claim-groups=0 genai-hld-interviews=1", result.stdout)

    def test_inline_dated_caveat_does_not_exempt_other_lines_in_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_file(
                root / "06-genai-systems/02-llm-hld-projects/doc-rag/PROBLEM.md",
                "# Doc RAG\n\n"
                "As of 2026-06-14, GPT-4 class examples are illustrative only.\n\n"
                "Pricing estimates still need ledger coverage.\n",
            )
            write_file(root / "resources/GENAI-CURRENTNESS-LEDGER.md", ledger_doc())
            write_file(
                root / "apps/portal/src/components/interview/interview-data.ts",
                interview_data("solutions/genai-hld-doc-rag.md"),
            )
            write_file(
                root / "solutions/genai-hld-doc-rag.md",
                "# Coach Answer: Doc RAG - GenAI HLD\n\nSay: route through retrieval first.\n",
            )
            write_file(
                root / "solutions/README.md",
                "| Doc RAG | GenAI HLD | ⭐⭐⭐ | [genai-hld-doc-rag.md](genai-hld-doc-rag.md) | Yes |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "missing-genai-currentness-row: "
            "06-genai-systems/02-llm-hld-projects/doc-rag/PROBLEM.md#pricing-cost",
            result.stdout,
        )

    def test_scans_genai_hld_solution_files_for_currentness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimal_hld(root)
            write_file(
                root / "resources/GENAI-CURRENTNESS-LEDGER.md",
                ledger_doc(
                    "| 06-genai-systems/02-llm-hld-projects/doc-rag/PROBLEM.md | model-surface | GPT-class example is illustrative | official provider docs when exact models matter | https://developers.openai.com/api/docs/models | 2026-06-14 | 2026-09-14 | watchlist | Keep generic unless refreshed. |",
                ),
            )
            write_file(
                root / "apps/portal/src/components/interview/interview-data.ts",
                interview_data("solutions/genai-hld-doc-rag.md"),
            )
            write_file(
                root / "solutions/genai-hld-doc-rag.md",
                "# Coach Answer: Doc RAG - GenAI HLD\n\nUse OpenAI for model routing.\n\nSay: route through retrieval first.\n",
            )
            write_file(
                root / "solutions/README.md",
                "| Doc RAG | GenAI HLD | ⭐⭐⭐ | [genai-hld-doc-rag.md](genai-hld-doc-rag.md) | Yes |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "missing-genai-currentness-row: solutions/genai-hld-doc-rag.md#model-surface",
            result.stdout,
        )

    def test_refresh_needed_and_expired_rows_do_not_satisfy_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimal_hld(root)
            write_file(
                root / "resources/GENAI-CURRENTNESS-LEDGER.md",
                ledger_doc(
                    "| 06-genai-systems/02-llm-hld-projects/doc-rag/PROBLEM.md | model-surface | GPT-class example is illustrative | official provider docs when exact models matter | https://developers.openai.com/api/docs/models | 2000-01-01 | 2000-02-01 | refresh-needed | Needs refresh. |",
                ),
            )
            write_file(
                root / "apps/portal/src/components/interview/interview-data.ts",
                interview_data("solutions/genai-hld-doc-rag.md"),
            )
            write_file(
                root / "solutions/genai-hld-doc-rag.md",
                "# Coach Answer: Doc RAG - GenAI HLD\n\nSay: route through retrieval first.\n",
            )
            write_file(
                root / "solutions/README.md",
                "| Doc RAG | GenAI HLD | ⭐⭐⭐ | [genai-hld-doc-rag.md](genai-hld-doc-rag.md) | Yes |\n",
            )

            result = self.run_script(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("unresolved-genai-currentness-status", result.stdout)
        self.assertIn("expired-genai-currentness-row", result.stdout)

    def test_json_output_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimal_hld(root)

            result = self.run_script(root, "--format", "json")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(set(payload), {"ok", "summary", "findings"})
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["summary"], {"genai-volatile-claim-groups": 1, "genai-hld-interviews": 1})
        self.assertTrue(
            any(finding["kind"] == "missing-genai-currentness-ledger" for finding in payload["findings"])
        )


if __name__ == "__main__":
    unittest.main()
