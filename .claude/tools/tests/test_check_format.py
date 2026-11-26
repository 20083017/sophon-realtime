"""Exercise syntax-helper failures against an isolated fixture directory."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest


class SyntaxHelperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.script = self.root/".claude/hooks/check-format.sh"
        self.script.parent.mkdir(parents=True)
        shutil.copyfile(Path(__file__).resolve().parents[2]/"hooks/check-format.sh", self.script)
        self.bash = "C:/Program Files/Git/bin/bash.exe" if os.name == "nt" else shutil.which("bash")
        if not self.bash or not Path(self.bash).exists(): self.skipTest("Bash unavailable")

    def run_helper(self, *args):
        return subprocess.run([self.bash, str(self.script), *args], cwd=self.root,
                              capture_output=True, text=True, timeout=20)

    def test_missing_explicit_file_fails(self):
        result = self.run_helper("missing.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("checks passed", result.stdout)

    def test_failed_git_enumeration_is_not_a_success(self):
        result = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("checks passed", result.stdout)

    def test_empty_discovery_reports_no_checks(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root/".gitignore").write_text(".claude/\n", encoding="utf-8")
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No", result.stdout)
        self.assertNotIn("checks passed", result.stdout)

    def test_valid_and_invalid_python_are_distinguished(self):
        path=self.root/"app.py"
        path.write_text("x = 1\n", encoding="utf-8")
        self.assertEqual(self.run_helper("app.py").returncode, 0)
        path.write_text("if (\n", encoding="utf-8")
        self.assertNotEqual(self.run_helper("app.py").returncode, 0)
