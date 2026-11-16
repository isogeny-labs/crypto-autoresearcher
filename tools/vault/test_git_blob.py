"""Committed blob reads obey the vault filter and fail closed."""
from __future__ import annotations

import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.vault.git_blob import GitBlobError, show_bytes, show_text


class GitBlobTests(unittest.TestCase):
    def test_plaintext_vaulted_and_failed_smudge(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            plain = repo / "plain.txt"
            plain.write_text("plain\n")
            subprocess.run(["git", "-C", str(repo), "add", "plain.txt"], check=True)
            self.assertEqual(show_text(repo, ":", "plain.txt"), None)
            self.assertEqual(show_text(repo, "HEAD", "plain.txt"), None)

            script = repo / "filter.py"
            script.write_text(
                "import sys\n"
                "data = sys.stdin.buffer.read()\n"
                "if sys.argv[1] == 'clean':\n"
                "    sys.stdout.buffer.write(b'VLT1' + data)\n"
                "elif data.startswith(b'VLT1'):\n"
                "    sys.stdout.buffer.write(data[4:])\n"
                "else:\n"
                "    sys.exit(1)\n"
            )
            prefix = f"{shlex.quote(sys.executable)} {shlex.quote(str(script))}"
            for direction in ("clean", "smudge"):
                subprocess.run(["git", "-C", str(repo), "config", f"filter.vault.{direction}",
                                f"{prefix} {direction}"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "test"], check=True)
            (repo / ".gitattributes").write_text("secret.txt filter=vault\n")
            (repo / "secret.txt").write_text("secret record\n")
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True)
            self.assertEqual(show_text(repo, "HEAD", "plain.txt"), "plain\n")
            self.assertEqual(show_bytes(repo, "HEAD", "secret.txt"), b"secret record\n")
            self.assertEqual(show_text(repo, "HEAD", "secret.txt"), "secret record\n")
            self.assertIsNone(show_text(repo, "HEAD", "absent.txt"))
            subprocess.run(["git", "-C", str(repo), "config", "filter.vault.smudge", "false"], check=True)
            with self.assertRaisesRegex(GitBlobError, "could not decrypt"):
                show_text(repo, "HEAD", "secret.txt")


if __name__ == "__main__":
    unittest.main()
