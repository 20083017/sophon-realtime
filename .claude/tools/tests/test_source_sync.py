"""Offline source-sync contract tests; no SSH or model services are contacted."""
import base64
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1] / "sophon-source-sync.py"


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(TOOL.is_file(), "source-sync implementation is missing")
        spec = importlib.util.spec_from_file_location("sophon_source_sync", TOOL)
        self.s = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.s
        spec.loader.exec_module(self.s)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.local = self.base / "local"
        self.remote = self.base / "sophon-realtime"
        self.local.mkdir()
        self.remote.mkdir()
        self.reference = self.base / "Mario"
        self.reference.mkdir()
        subprocess.run(["git", "init", "-q", str(self.local)], check=True)
        self.config = {
            "ssh_alias": "fixture-alias", "expected_host": "fixture.invalid",
            "expected_user": "fixture", "expected_port": 22,
            "remote_source_root": "/fixture/sophon-realtime",
            "mario_reference_root": "/fixture/Mario",
            "connect_timeout": 10, "command_timeout": 120,
        }
        outer = self

        class LocalTransport:
            """Replace only the external hop; execute real remote filesystem code."""
            def call(self, action, payload):
                return outer.s.worker(action, dict(payload, root=str(outer.remote),
                                                   reference_root=str(outer.reference)))

        self.transport = LocalTransport()

    def write(self, rel, data=b"print('hello')\n", remote=False):
        p = (self.remote if remote else self.local) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return p

    def preview(self, selected=None, replacements=()):
        return self.s.create_preview(self.local, self.config,
                                     selected or {"app.py": 0o644},
                                     self.transport, replacements)

    def test_required_exclusions_cannot_be_explicitly_included(self):
        selected = {"app.py": 0o644}
        self.write("app.py")
        for path in (".claude/agents/x.md", ".CLAUDE/secret", "CLAUDE.md",
                     "AGENTS.md", ".worktree-policy.yaml"):
            self.write(path)
            selected[path] = 0o644
        manifest = self.preview(selected)
        self.assertEqual([e["path"] for e in manifest["entries"]], ["app.py"])
        self.s.upload(self.local, self.config, manifest, self.transport)
        self.assertEqual(sorted(p.name for p in self.remote.iterdir()), ["app.py"])

    def test_windows_separator_exclusion_and_required_audio_fixture(self):
        self.write("flash/examples/hello.wav", b"fixture")
        entries = self.s.build_entries(self.local, {
            ".CLAUDE\\rules\\x.md": 0o644, "agents.MD": 0o644,
            "flash/examples/hello.wav": 0o644})
        self.assertEqual([e["path"] for e in entries], ["flash/examples/hello.wav"])

    def test_private_generated_and_model_content_excluded(self):
        self.write("app.py")
        paths = [".git/config", "doc/check/CURRENT.md", ".env", "sub/.env.prod",
                 "tag/.venv/x.py", "logs/x.log", "__pycache__/x.pyc",
                 "tag/model/weights.bin", "weights.safetensors", "private.pem"]
        entries = self.s.build_entries(self.local, dict.fromkeys(paths+["app.py"], 0o644))
        self.assertEqual([e["path"] for e in entries], ["app.py"])

    def test_traversal_absolute_and_windows_special_paths_rejected(self):
        for path in ("../escape", "a/../escape", "/absolute", "C:\\escape",
                     "a//b", "a/./b", "name:stream", "a\nfile", "con", "x. "):
            with self.subTest(path=path), self.assertRaises(self.s.SyncError):
                self.s.normalize_relative(path)

    def test_case_collisions_rejected(self):
        self.write("app.py")
        with self.assertRaises(self.s.SyncError):
            self.s.build_entries(self.local, {"app.py": 0o644, "APP.py": 0o644})

    def test_local_link_escape_rejected(self):
        outside = self.write("outside.py")
        link = self.local / "linked.py"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("symlink creation unavailable")
        with self.assertRaises(self.s.SyncError):
            self.s.build_entries(self.local, {"linked.py": 0o644})

    def test_preview_is_read_only_and_upload_verifies_contents(self):
        self.write("nested/app.py", b"content")
        manifest = self.preview({"nested/app.py": 0o644})
        self.assertEqual(list(self.remote.iterdir()), [])
        result = self.s.upload(self.local, self.config, manifest, self.transport)
        self.assertEqual(result["uploaded"], 1)
        self.assertEqual((self.remote/"nested/app.py").read_bytes(), b"content")
        self.assertEqual(self.s.verify(self.config, manifest, self.transport)["verified"], 1)

    def test_unchanged_file_and_unrelated_remote_files_preserved(self):
        self.write("app.py")
        self.write("app.py", remote=True)
        self.write("CLAUDE.md", b"remote-only", remote=True)
        self.write("other.txt", b"keep", remote=True)
        result = self.s.upload(self.local, self.config, self.preview(), self.transport)
        self.assertEqual(result["uploaded"], 0)
        self.assertEqual((self.remote/"CLAUDE.md").read_bytes(), b"remote-only")
        self.assertEqual((self.remote/"other.txt").read_bytes(), b"keep")

    def test_existing_conflict_requires_explicit_replacement(self):
        self.write("app.py", b"new")
        self.write("app.py", b"old", remote=True)
        manifest = self.preview()
        self.assertEqual(manifest["conflicts"], ["app.py"])
        with self.assertRaises(self.s.SyncError):
            self.s.upload(self.local, self.config, manifest, self.transport)
        self.assertEqual((self.remote/"app.py").read_bytes(), b"old")
        self.s.upload(self.local, self.config, self.preview(replacements=["app.py"]), self.transport)
        self.assertEqual((self.remote/"app.py").read_bytes(), b"new")
        self.assertFalse(list(self.remote.glob(".sophon-sync-*")))

    def test_source_drift_blocks_upload_before_any_write(self):
        self.write("app.py")
        manifest = self.preview()
        self.write("app.py", b"changed")
        with self.assertRaises(self.s.SyncError):
            self.s.upload(self.local, self.config, manifest, self.transport)
        self.assertEqual(list(self.remote.iterdir()), [])

    def test_remote_drift_blocks_upload(self):
        self.write("app.py")
        manifest = self.preview()
        self.write("app.py", b"concurrent", remote=True)
        with self.assertRaises(self.s.SyncError):
            self.s.upload(self.local, self.config, manifest, self.transport)
        self.assertEqual((self.remote/"app.py").read_bytes(), b"concurrent")

    def test_changed_config_and_tampered_excluded_manifest_rejected(self):
        self.write("app.py")
        manifest = self.preview()
        with self.assertRaises(self.s.SyncError):
            self.s.upload(self.local, dict(self.config, ssh_alias="different"), manifest, self.transport)
        manifest["entries"][0]["path"] = "AGENTS.md"
        with self.assertRaises(self.s.SyncError):
            self.s.verify(self.config, manifest, self.transport)

    def test_verify_detects_hash_mismatch(self):
        self.write("app.py")
        manifest = self.preview()
        self.s.upload(self.local, self.config, manifest, self.transport)
        self.write("app.py", b"corrupted", remote=True)
        with self.assertRaises(self.s.SyncError):
            self.s.verify(self.config, manifest, self.transport)

    def test_interrupted_transfer_reports_partial_without_deleting_other_files(self):
        self.write("a.py"); self.write("b.py")
        manifest = self.preview({"a.py": 0o644, "b.py": 0o644})
        real = self.transport.call
        def interrupted(action, payload):
            if action == "put" and payload["entry"]["path"] == "b.py":
                raise self.s.SyncError("connection lost")
            return real(action, payload)
        with patch.object(self.transport, "call", side_effect=interrupted):
            with self.assertRaisesRegex(self.s.SyncError, "1.*verified"):
                self.s.upload(self.local, self.config, manifest, self.transport)
        self.assertTrue((self.remote/"a.py").is_file())
        self.assertFalse((self.remote/"b.py").exists())

    def test_remote_worker_rechecks_identity_and_hash_before_replace(self):
        self.write("app.py", b"new")
        entry = self.s.build_entries(self.local, {"app.py": 0o644})[0]
        self.write("app.py", b"other", remote=True)
        payload = dict(root=str(self.remote), entry=entry, expected=None,
                       data=base64.b64encode(b"new").decode(), reference_root=str(self.reference))
        with self.assertRaises(self.s.SyncError):
            self.s.worker("put", payload)
        self.assertEqual((self.remote/"app.py").read_bytes(), b"other")
        payload["expected"] = self.s.file_identity(self.remote/"app.py")
        payload["data"] = base64.b64encode(b"wrong").decode()
        with self.assertRaises(self.s.SyncError):
            self.s.worker("put", payload)
        self.assertEqual((self.remote/"app.py").read_bytes(), b"other")

    def test_executable_mode_is_preserved_on_posix(self):
        if os.name == "nt": self.skipTest("POSIX permissions require POSIX runner")
        self.write("start.sh", b"#!/bin/sh\n")
        manifest = self.preview({"start.sh": 0o755})
        self.s.upload(self.local, self.config, manifest, self.transport)
        self.assertEqual((self.remote/"start.sh").stat().st_mode & 0o777, 0o755)

    def test_remote_link_cannot_write_outside_destination(self):
        outside = self.base/"outside"; outside.mkdir()
        try:
            (self.remote/"nested").symlink_to(outside, target_is_directory=True)
        except OSError: self.skipTest("symlink creation unavailable")
        self.write("nested/app.py")
        with self.assertRaises(self.s.SyncError):
            self.preview({"nested/app.py": 0o644})
        self.assertEqual(list(outside.iterdir()), [])

    def test_git_selection_keeps_modes_and_requires_explicit_untracked_files(self):
        subprocess.run(["git", "init", "-q", str(self.local)], check=True)
        self.write("tracked.py"); self.write("new.py"); self.write("CLAUDE.md")
        subprocess.run(["git", "-C", str(self.local), "add", "tracked.py"], check=True)
        selected = self.s.git_selection(self.local, ["new.py", "CLAUDE.md"])
        self.assertEqual(set(selected), {"tracked.py", "new.py", "CLAUDE.md"})
        entries = self.s.build_entries(self.local, selected)
        self.assertEqual({e["path"] for e in entries}, {"tracked.py", "new.py"})

    def test_connection_failure_has_no_success_result(self):
        self.write("app.py")
        with patch.object(self.transport, "call", side_effect=self.s.SyncError("ssh failed")):
            with self.assertRaises(self.s.SyncError): self.preview()

    def test_worker_rejects_unknown_operation(self):
        with self.assertRaises(self.s.SyncError):
            self.s.worker("install", {"root": str(self.remote)})

    def test_serialized_remote_program_runs_without_repository_imports(self):
        self.write("app.py")
        entry = self.s.build_entries(self.local, {"app.py": 0o644})[0]
        request = {"action": "inspect", "root": str(self.remote), "entries": [entry],
                   "reference_root": str(self.reference)}
        result = subprocess.run([sys.executable, "-c", self.s.remote_program()],
                                input=json.dumps(request), text=True, capture_output=True,
                                timeout=20, cwd=self.base)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"files": {"app.py": None}})

    def test_remote_failure_keeps_previous_file_and_recovery_copy(self):
        self.write("app.py", b"new")
        self.write("app.py", b"old", remote=True)
        manifest = self.preview(replacements=["app.py"])
        with patch.object(self.s.os, "replace", side_effect=OSError("simulated failure")):
            with self.assertRaisesRegex(self.s.SyncError, "recovery staging retained"):
                self.s.upload(self.local, self.config, manifest, self.transport)
        self.assertEqual((self.remote/"app.py").read_bytes(), b"old")
        copies = list(self.remote.glob(".sophon-sync-*/previous"))
        self.assertEqual(len(copies), 1)
        self.assertEqual(copies[0].read_bytes(), b"old")
        self.assertFalse((self.remote/".sophon-sync-lock").exists())

    def test_windows_junction_parent_is_rejected(self):
        if os.name != "nt": self.skipTest("Windows junction test")
        outside = self.base/"outside"; outside.mkdir()
        junction = self.remote/"nested"
        # Literal paths passed as parameters; no cross-shell destructive command.
        command = "New-Item -ItemType Junction -Path $args[0] -Target $args[1] | Out-Null"
        result = subprocess.run(["powershell", "-NoProfile", "-Command",
                                 "& { " + command + " } '" + str(junction).replace("'", "''")
                                 + "' '" + str(outside).replace("'", "''") + "'"],
                                capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.addCleanup(lambda: os.rmdir(junction) if junction.exists() else None)
        self.write("nested/app.py")
        with self.assertRaises(self.s.SyncError): self.preview({"nested/app.py": 0o644})
        self.assertEqual(list(outside.iterdir()), [])

    def test_ssh_identity_mismatch_rejected_without_connection(self):
        resolved = subprocess.CompletedProcess([], 0, "hostname wrong.invalid\nuser fixture\nport 22\n", "")
        with patch.object(self.s.subprocess, "run", return_value=resolved) as run:
            with self.assertRaisesRegex(self.s.SyncError, "identity differs"):
                self.s.SSHTransport(self.config)
        self.assertEqual(run.call_count, 1)
        self.assertIn("-G", run.call_args.args[0])

    def test_ssh_timeout_retains_strict_options_and_reports_uncertainty(self):
        resolved = subprocess.CompletedProcess([], 0, "hostname fixture.invalid\nuser fixture\nport 22\n", "")
        with patch.object(self.s.subprocess, "run", return_value=resolved):
            transport = self.s.SSHTransport(self.config)
        with patch.object(self.s.subprocess, "run", side_effect=subprocess.TimeoutExpired("ssh", 120)) as run:
            with self.assertRaisesRegex(self.s.SyncError, "completion may be partial"):
                transport.call("inspect", {"entries": []})
        argv = run.call_args.args[0]
        self.assertIn("StrictHostKeyChecking=yes", argv)
        self.assertIn("BatchMode=yes", argv)
        self.assertIn("ForwardAgent=no", argv)
        self.assertNotIn("shell", run.call_args.kwargs)
        self.assertEqual(run.call_args.kwargs["timeout"], 120)

    def test_cli_preview_upload_verify_with_real_local_filesystem(self):
        subprocess.run(["git", "init", "-q", str(self.local)], check=True)
        self.write("app.py")
        self.write("AGENTS.md")
        config = self.base/"session.json"
        config.write_text(json.dumps(self.config), encoding="utf-8")
        manifest = self.base/"manifest.json"
        common = ["--config", str(config), "--root", str(self.local), "--manifest", str(manifest)]
        with patch.object(self.s, "SSHTransport", return_value=self.transport), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(self.s.main(["preview", *common, "--include", "app.py", "--include", "AGENTS.md"]), 0)
            self.assertEqual(list(self.remote.iterdir()), [])
            self.assertEqual(self.s.main(["upload", *common]), 0)
            self.assertEqual(self.s.main(["verify", *common]), 0)
        self.assertEqual(sorted(p.name for p in self.remote.iterdir()), ["app.py"])

    def test_config_cannot_select_mario_or_live_inside_checkout(self):
        config = self.base/"session.json"
        config.write_text(json.dumps(dict(self.config, mario_reference_root="/fixture")), encoding="utf-8")
        with self.assertRaises(self.s.SyncError): self.s.load_config(config, self.local)
        local_config = self.local/"session.json"
        local_config.write_text(json.dumps(self.config), encoding="utf-8")
        with self.assertRaises(self.s.SyncError): self.s.load_config(local_config, self.local)

    def test_cli_rejects_checkout_subdirectory_as_source_root(self):
        subroot = self.local/".claude"
        self.write(".claude/private.py")
        config = self.base/"config.json"
        config.write_text(json.dumps(self.config), encoding="utf-8")
        with patch.object(self.s, "SSHTransport", return_value=self.transport) as transport, contextlib.redirect_stderr(io.StringIO()):
            code = self.s.main(["preview", "--root", str(subroot), "--config", str(config),
                                "--manifest", str(self.base/"manifest.json"), "--include", "private.py"])
        self.assertNotEqual(code, 0)
        transport.assert_not_called()

    def test_cli_rejects_linked_root_before_resolving_it(self):
        link = self.base/"alias"
        if os.name == "nt":
            cmd = "New-Item -ItemType Junction -Path '"+str(link).replace("'", "''")+"' -Target '"+str(self.local).replace("'", "''")+"' | Out-Null"
            subprocess.run(["powershell", "-NoProfile", "-Command", cmd], check=True, capture_output=True)
            self.addCleanup(lambda: os.rmdir(link) if link.exists() else None)
        else:
            link.symlink_to(self.local, target_is_directory=True)
        config = self.base/"config.json"
        config.write_text(json.dumps(self.config), encoding="utf-8")
        self.write("app.py")
        with patch.object(self.s, "SSHTransport", return_value=self.transport) as transport, contextlib.redirect_stderr(io.StringIO()):
            code = self.s.main(["preview", "--root", str(link), "--config", str(config),
                                "--manifest", str(self.base/"manifest.json"), "--include", "app.py"])
        self.assertNotEqual(code, 0)
        transport.assert_not_called()

    def test_double_slash_remote_root_is_rejected(self):
        config = self.base/"config.json"
        config.write_text(json.dumps(dict(self.config, remote_source_root="//fixture/sophon-realtime")), encoding="utf-8")
        with self.assertRaises(self.s.SyncError): self.s.load_config(config, self.local)

    def test_remote_worker_enforces_reference_separation(self):
        self.write("app.py")
        entries = self.s.build_entries(self.local, {"app.py": 0o644})
        for ref in (self.remote, self.base):
            with self.subTest(ref=ref), self.assertRaises(self.s.SyncError):
                self.s.worker("inspect", {"root": str(self.remote), "reference_root": str(ref), "entries": entries})

    def test_index_mode_drift_is_detected_before_upload(self):
        self.write("start.sh")
        subprocess.run(["git", "-C", str(self.local), "add", "start.sh"], check=True)
        subprocess.run(["git", "-C", str(self.local), "update-index", "--chmod=-x", "start.sh"], check=True)
        manifest = self.preview({"start.sh": 0o644})
        subprocess.run(["git", "-C", str(self.local), "update-index", "--chmod=+x", "start.sh"], check=True)
        with self.assertRaises(self.s.SyncError):
            self.s.upload(self.local, self.config, manifest, self.transport)
        self.assertEqual(list(self.remote.iterdir()), [])

    def test_source_drift_after_a_verified_write_prevents_success(self):
        self.write("a.py"); self.write("b.py")
        manifest = self.preview({"a.py": 0o644, "b.py": 0o644})
        real = self.transport.call
        def changing(action, payload):
            result = real(action, payload)
            if action == "put" and payload["entry"]["path"] == "b.py":
                self.write("a.py", b"changed after transfer")
            return result
        with patch.object(self.transport, "call", side_effect=changing):
            with self.assertRaises(self.s.SyncError):
                self.s.upload(self.local, self.config, manifest, self.transport)

    def test_changed_target_during_backup_is_not_overwritten(self):
        self.write("app.py", b"new"); self.write("app.py", b"old", remote=True)
        manifest = self.preview(replacements=["app.py"])
        real = self.s.shutil.copy2
        def changing(*args, **kwargs):
            result = real(*args, **kwargs)
            self.write("app.py", b"concurrent writer", remote=True)
            return result
        if os.name != "nt": self.skipTest("portable worker path regression; POSIX handle path tested separately")
        with patch.object(self.s.shutil, "copy2", side_effect=changing):
            with self.assertRaises(self.s.SyncError):
                self.s.upload(self.local, self.config, manifest, self.transport)
        self.assertEqual((self.remote/"app.py").read_bytes(), b"concurrent writer")


if __name__ == "__main__":
    unittest.main()
