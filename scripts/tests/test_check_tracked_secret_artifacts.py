import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_tracked_secret_artifacts.py"


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_file(path: Path, content: str = "placeholder\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def init_repo(root: Path, files: dict[str, str]) -> None:
    run(["git", "init", "-q"], root)
    run(["git", "config", "user.email", "test@example.com"], root)
    run(["git", "config", "user.name", "Test User"], root)
    for relative_path, content in files.items():
        write_file(root / relative_path, content)
    run(["git", "add", "-f", "."], root)
    commit = run(["git", "commit", "-q", "-m", "fixture"], root)
    if commit.returncode != 0:
        raise AssertionError(commit.stdout + commit.stderr)


class TrackedSecretArtifactCheckerTest(unittest.TestCase):
    def test_reports_tracked_secret_artifact_paths_without_printing_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(
                root,
                {
                    ".env": "TOP_SECRET_VALUE=do-not-print\n",
                    "certs/service.pem": "-----BEGIN PRIVATE KEY-----\ndo-not-print\n",
                    "docs/token-guide.md": "Educational token discussion is okay.\n",
                },
            )

            result = run([sys.executable, str(SCRIPT)], root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("secret-artifact", result.stdout)
        self.assertIn(".env", result.stdout)
        self.assertIn("certs/service.pem", result.stdout)
        self.assertNotIn("TOP_SECRET_VALUE", result.stdout)
        self.assertNotIn("do-not-print", result.stdout)
        self.assertNotIn("docs/token-guide.md", result.stdout)

    def test_reports_common_secret_artifact_families(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(
                root,
                {
                    ".npmrc": "PRIVATE_VALUE=do-not-print\n",
                    "auth.json": '{"token":"do-not-print"}\n',
                    "certs/service.jks": "do-not-print\n",
                    "certs/service.key": "do-not-print\n",
                    "certs/service.p12": "do-not-print\n",
                    "certs/service.pfx": "do-not-print\n",
                    "cookies.txt": "do-not-print\n",
                    "dumps/local.sqlite": "do-not-print\n",
                    "dumps/prod.dump": "do-not-print\n",
                    "session.json": '{"session":"do-not-print"}\n',
                    "snapshots/shell-history.zsh": "do-not-print\n",
                    "wallet/tnsnames.ora": "do-not-print\n",
                },
            )

            result = run([sys.executable, str(SCRIPT)], root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for expected_path in [
            ".npmrc",
            "auth.json",
            "certs/service.jks",
            "certs/service.key",
            "certs/service.p12",
            "certs/service.pfx",
            "cookies.txt",
            "dumps/local.sqlite",
            "dumps/prod.dump",
            "session.json",
            "snapshots/shell-history.zsh",
            "wallet/tnsnames.ora",
        ]:
            self.assertIn(expected_path, result.stdout)
        self.assertNotIn("PRIVATE_VALUE", result.stdout)
        self.assertNotIn("do-not-print", result.stdout)

    def test_allowlist_suppresses_exact_and_globbed_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(
                root,
                {
                    "fixtures/example.env": "not real\n",
                    "fixtures/certs/example.pem": "not real\n",
                },
            )
            allowlist = root / "secret-allowlist.txt"
            allowlist.write_text(
                "\n".join(
                    [
                        "# intentional educational fixtures",
                        "fixtures/example.env",
                        "fixtures/certs/*.pem",
                    ]
                ),
                encoding="utf-8",
            )

            result = run(
                [sys.executable, str(SCRIPT), "--allowlist", str(allowlist)],
                root,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("tracked-secret-artifacts: ok", result.stdout)

    def test_partial_allowlist_still_reports_unallowlisted_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(
                root,
                {
                    "fixtures/example.env": "do-not-print\n",
                    "fixtures/nested/prod.pem": "do-not-print\n",
                    "real/service.pem": "do-not-print\n",
                },
            )
            allowlist = root / "secret-allowlist.txt"
            allowlist.write_text("fixtures/*\n", encoding="utf-8")

            result = run(
                [sys.executable, str(SCRIPT), "--allowlist", str(allowlist)],
                root,
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("fixtures/nested/prod.pem", result.stdout)
        self.assertIn("real/service.pem", result.stdout)
        self.assertIn("found 2", result.stdout)
        self.assertNotIn("fixtures/example.env", result.stdout)
        self.assertNotIn("do-not-print", result.stdout)

    def test_double_star_allowlist_can_suppress_nested_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(
                root,
                {
                    "fixtures/nested/prod.pem": "do-not-print\n",
                },
            )
            allowlist = root / "secret-allowlist.txt"
            allowlist.write_text("fixtures/**\n", encoding="utf-8")

            result = run(
                [sys.executable, str(SCRIPT), "--allowlist", str(allowlist)],
                root,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("tracked-secret-artifacts: ok", result.stdout)

    def test_ignores_untracked_files_and_educational_markdown_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(
                root,
                {
                    "examples/cookies/parser.py": "cookie parser example\n",
                    "examples/sessions/session_store.py": "session store example\n",
                    "docs/session-management.md": "session concepts\n",
                    "docs/api-key-rotation.md": "key rotation concepts\n",
                },
            )
            write_file(root / "local.env", "LOCAL_SECRET=do-not-print\n")

            result = run([sys.executable, str(SCRIPT)], root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("tracked-secret-artifacts: ok", result.stdout)
        self.assertNotIn("local.env", result.stdout)

    def test_reports_common_cloud_and_infra_credential_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(
                root,
                {
                    ".aws/credentials": "do-not-print\n",
                    ".docker/config.json": "do-not-print\n",
                    ".kube/config": "do-not-print\n",
                    "certs/AuthKey_ABC123.p8": "do-not-print\n",
                    "client_secret_123.apps.googleusercontent.com.json": "do-not-print\n",
                    "infra/terraform.tfstate": "do-not-print\n",
                    "infra/terraform.tfvars": "do-not-print\n",
                    "vpn/client.ovpn": "do-not-print\n",
                },
            )

            result = run([sys.executable, str(SCRIPT)], root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for expected_path in [
            ".aws/credentials",
            ".docker/config.json",
            ".kube/config",
            "certs/AuthKey_ABC123.p8",
            "client_secret_123.apps.googleusercontent.com.json",
            "infra/terraform.tfstate",
            "infra/terraform.tfvars",
            "vpn/client.ovpn",
        ]:
            self.assertIn(expected_path, result.stdout)
        self.assertNotIn("do-not-print", result.stdout)

    def test_output_is_path_only_and_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(
                root,
                {
                    "z/service.pem": "do-not-print\n",
                    "a/.env": "do-not-print\n",
                    "m/auth.json": "do-not-print\n",
                },
            )

            result = run([sys.executable, str(SCRIPT)], root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        finding_lines = [
            line
            for line in result.stdout.splitlines()
            if line.startswith("secret-artifact:")
        ]
        self.assertEqual(
            finding_lines,
            [
                "secret-artifact: a/.env (secret basename .env)",
                "secret-artifact: m/auth.json (secret basename auth.json)",
                "secret-artifact: z/service.pem (secret suffix .pem)",
            ],
        )
        self.assertNotIn("do-not-print", result.stdout)

    def test_fails_cleanly_outside_git_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_file(root / "README.md", "not a git repo\n")

            result = run([sys.executable, str(SCRIPT)], root)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("git ls-files failed", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
