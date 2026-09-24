import contextlib
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from bump_py_version.cli import bump_version, check_uv_lock


class UvLockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        previous = os.getcwd()
        os.chdir(self.temp.name)
        self.addCleanup(os.chdir, previous)
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.write_config("true")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "Initial")

    def git(self, *args):
        return subprocess.run(["git", *args], check=True, capture_output=True, text=True)

    def write_config(self, value):
        Path("pyproject.toml").write_text(
            '[project]\nname = "example"\nversion = "1.0.0"\n'
            f'[tool.bump_version]\nuv_lock = {value}\n'
        )

    def test_disabled_or_absent_does_not_check_uv_or_git(self):
        for config in ('[tool.bump_version]\nuv_lock = false\n', "[project]\n"):
            Path("pyproject.toml").write_text(config)
            with patch("bump_py_version.cli.subprocess.run") as run, patch("bump_py_version.cli.shutil.which") as which:
                self.assertFalse(check_uv_lock())
                run.assert_not_called()
                which.assert_not_called()
        Path("pyproject.toml").unlink()
        self.assertFalse(check_uv_lock())

    def test_ignored_lockfile_stops_before_edits(self):
        Path(".gitignore").write_text("uv.lock\n")
        self.git("add", ".gitignore")
        self.git("commit", "--quiet", "-m", "Ignore lockfile")
        before = Path("pyproject.toml").read_text()
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit):
            bump_version("v1.0.1")
        self.assertIn("Remove uv.lock from .gitignore", output.getvalue())
        self.assertEqual(Path("pyproject.toml").read_text(), before)

    def test_missing_uv_stops_before_edits(self):
        before = Path("pyproject.toml").read_text()
        with patch("bump_py_version.cli.shutil.which", return_value=None), contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            bump_version("v1.0.1")
        self.assertEqual(Path("pyproject.toml").read_text(), before)

    def test_lock_runs_after_version_edit_and_before_staging(self):
        commands = []

        def run(command):
            commands.append(command)
            if command == "uv lock":
                self.assertIn('version = "1.0.1"', Path("pyproject.toml").read_text())
                Path("uv.lock").write_text('version = 1\n')
            elif command == "git add .":
                self.git("add", ".")
                self.assertEqual(self.git("show", ":uv.lock").stdout, 'version = 1\n')

        with patch("bump_py_version.cli.shutil.which", return_value="/fake/uv"), patch("bump_py_version.cli.run_command", side_effect=run):
            bump_version("v1.0.1")
        self.assertEqual(commands[:2], ["uv lock", "git add ."])

    def test_failed_lock_stops_release(self):
        real_run = subprocess.run
        commands = []

        def run(command, **kwargs):
            commands.append(command)
            if command == "uv lock":
                raise subprocess.CalledProcessError(1, command)
            return real_run(command, **kwargs)

        with patch("bump_py_version.cli.shutil.which", return_value="/fake/uv"), patch("bump_py_version.cli.subprocess.run", side_effect=run), contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            bump_version("v1.0.1")
        self.assertEqual(commands[-1], "uv lock")
        self.assertIn('version = "1.0.1"', Path("pyproject.toml").read_text())
        self.assertEqual(self.git("diff", "--cached").stdout, "")


if __name__ == "__main__":
    unittest.main()
