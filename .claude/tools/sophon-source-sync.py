#!/usr/bin/env python3
"""Preview, upload and verify source over bounded OpenSSH calls. Standard library only."""
from __future__ import annotations

import argparse
import base64
import hashlib
import inspect
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import zlib

MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_FILES = 10000
EXCLUDED_ROOTS = {".claude", ".worktree-policy.yaml", "agents.md", "claude.md", ".git"}
EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
                 ".ruff_cache", "node_modules", "logs", "log", "out", "outputs",
                 "model", "models", "checkpoints", ".sophon-sync-lock"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".log", ".safetensors", ".ckpt", ".pt", ".pth", ".pem", ".key"}


class SyncError(Exception):
    """A bounded failure that must not be reported as a successful transfer."""


def normalize_relative(value):
    if not isinstance(value, str) or not value or len(value) > 4096:
        raise SyncError("invalid relative path")
    value = value.replace("\\", "/")
    parts = value.split("/")
    if any(not p or p in (".", "..") or p[-1:] in (" ", ".") for p in parts):
        raise SyncError("empty, absolute or traversal path component")
    if any(ord(c) < 32 or ord(c) == 127 or c in ':*?"<>|' for c in value):
        raise SyncError("unsupported path characters")
    if any(re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", p) for p in parts):
        raise SyncError("reserved path component")
    return "/".join(parts)


def is_excluded(rel):
    parts = normalize_relative(rel).casefold().split("/")
    if parts[0] in EXCLUDED_ROOTS or parts[:2] in (["doc", "plan"], ["doc", "check"]):
        return True
    if any(p in EXCLUDED_DIRS or p.startswith((".venv-", ".sophon-sync-")) for p in parts):
        return True
    if any(p == ".env" or p.startswith(".env.") or p in ("id_rsa", "id_ed25519", ".ssh") for p in parts):
        return True
    return PurePosixPath(parts[-1]).suffix in EXCLUDED_SUFFIXES


def reject_links(path):
    # Inspect ancestors too: a junction/symlink parent must not change the target root.
    for part in (path, *path.parents):
        if part.is_symlink() or getattr(part, "is_junction", lambda: False)():
            raise SyncError("linked path is outside the supported sync boundary")


def safe_path(root, rel):
    root = Path(root).absolute()
    reject_links(root)
    path = root.joinpath(*normalize_relative(rel).split("/"))
    reject_links(path)
    if not path.resolve().is_relative_to(root.resolve()):
        raise SyncError("path escapes source/destination root")
    return path


def file_identity(path):
    reject_links(path)
    try:
        st = path.stat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(st.st_mode) or st.st_size > MAX_FILE_BYTES:
        raise SyncError("non-regular or oversized source/destination file")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    after = path.stat()
    if (st.st_size, st.st_mtime_ns, st.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise SyncError("file changed while hashing")
    return {"size": st.st_size, "sha256": digest.hexdigest(),
            "mode": 0o644 if os.name == "nt" else stat.S_IMODE(st.st_mode)}


def validate_identity(identity, source=False):
    if not isinstance(identity, dict) or set(identity) != {"size", "sha256", "mode"}:
        raise SyncError("invalid file identity")
    if type(identity["size"]) is not int or not 0 <= identity["size"] <= MAX_FILE_BYTES:
        raise SyncError("invalid file size")
    if not isinstance(identity["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", identity["sha256"]):
        raise SyncError("invalid file hash")
    mode = identity["mode"]
    if type(mode) is not int or not 0 <= mode <= 0o777 or (source and mode not in (0o644, 0o755)):
        raise SyncError("invalid file mode")


def entry_identity(entry):
    if not isinstance(entry, dict) or set(entry) != {"path", "size", "sha256", "mode"}:
        raise SyncError("invalid manifest entry")
    rel = normalize_relative(entry["path"])
    if rel != entry["path"] or is_excluded(rel):
        raise SyncError("excluded or noncanonical manifest path")
    ident = {k: entry[k] for k in ("size", "sha256", "mode")}
    validate_identity(ident, source=True)
    return ident


def open_directory(path):
    """Pin each POSIX ancestor, refusing links instead of following path names."""
    path = Path(path)
    if not path.is_absolute():
        raise SyncError("directory must be absolute")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open("/", flags)
    try:
        for part in path.parts[1:]:
            new_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = new_fd
        return fd
    except Exception:
        os.close(fd)
        raise


def open_parent(root_fd, rel, create=False):
    fd = os.dup(root_fd)
    try:
        for part in normalize_relative(rel).split("/")[:-1]:
            if create:
                try:
                    os.mkdir(part, dir_fd=fd)
                except FileExistsError:
                    pass
            new_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = new_fd
        return fd
    except Exception:
        os.close(fd)
        raise


def identity_at(parent_fd, name):
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
    except FileNotFoundError:
        return None
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_FILE_BYTES:
            raise SyncError("non-regular or oversized remote file")
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
        after = os.fstat(stream.fileno())
        if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
            raise SyncError("remote file changed while hashing")
        return {"size": before.st_size, "sha256": digest.hexdigest(), "mode": stat.S_IMODE(before.st_mode)}


def posix_inspect(root, entries):
    try:
        root_fd = open_directory(root)
    except FileNotFoundError:
        return {e["path"]: None for e in entries}
    try:
        result = {}
        for entry in entries:
            try:
                parent_fd = open_parent(root_fd, entry["path"])
            except FileNotFoundError:
                result[entry["path"]] = None
                continue
            try:
                result[entry["path"]] = identity_at(parent_fd, entry["path"].split("/")[-1])
            finally:
                os.close(parent_fd)
        return result
    finally:
        os.close(root_fd)


def posix_put(root, entry, expected, data):
    """Linux writes use pinned no-follow directories; external writers must be quiesced."""
    root_parent_fd = open_directory(root.parent)
    try:
        try:
            os.mkdir(root.name, dir_fd=root_parent_fd)
        except FileExistsError:
            pass
        root_fd = os.open(root.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_parent_fd)
    finally:
        os.close(root_parent_fd)
    stage_fd = parent_fd = None
    stage = None
    locked = False
    leaf = entry["path"].split("/")[-1]
    wanted = entry_identity(entry)
    try:
        try:
            os.mkdir(".sophon-sync-lock", dir_fd=root_fd)
            locked = True
        except FileExistsError as exc:
            raise SyncError("sync already active or interrupted; inspect existing lock") from exc
        parent_fd = open_parent(root_fd, entry["path"], create=True)
        if identity_at(parent_fd, leaf) != expected:
            raise SyncError("remote changed before replacement")
        stage = ".sophon-sync-" + os.urandom(12).hex()
        os.mkdir(stage, mode=0o700, dir_fd=root_fd)
        stage_fd = os.open(stage, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
        fd = os.open("incoming", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=stage_fd)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), wanted["mode"])
            os.fsync(stream.fileno())
        if expected is not None:
            source_fd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
            with os.fdopen(source_fd, "rb") as source:
                if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                    raise SyncError("replacement source is no longer regular")
                backup_fd = os.open("previous", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=stage_fd)
                with os.fdopen(backup_fd, "wb") as backup:
                    remaining = MAX_FILE_BYTES + 1
                    while remaining:
                        chunk = source.read(min(1024 * 1024, remaining))
                        if not chunk:
                            break
                        backup.write(chunk)
                        remaining -= len(chunk)
                    if remaining == 0:
                        raise SyncError("replacement source grew beyond limit")
                    backup.flush()
                    os.fchmod(backup.fileno(), expected["mode"])
                    os.fsync(backup.fileno())
            if identity_at(stage_fd, "previous") != expected:
                raise SyncError("remote changed while preserving recovery copy")
        # Recheck both the pathname's directory identity and file after backup.
        check_root_fd = open_directory(root)
        try:
            if (os.fstat(check_root_fd).st_dev, os.fstat(check_root_fd).st_ino) != (os.fstat(root_fd).st_dev, os.fstat(root_fd).st_ino):
                raise SyncError("destination root changed")
            check_parent_fd = open_parent(check_root_fd, entry["path"])
            try:
                if (os.fstat(check_parent_fd).st_dev, os.fstat(check_parent_fd).st_ino) != (os.fstat(parent_fd).st_dev, os.fstat(parent_fd).st_ino):
                    raise SyncError("destination parent changed")
            finally:
                os.close(check_parent_fd)
        finally:
            os.close(check_root_fd)
        if identity_at(parent_fd, leaf) != expected:
            raise SyncError("remote changed during transfer")
        os.replace("incoming", leaf, src_dir_fd=stage_fd, dst_dir_fd=parent_fd)
        actual = identity_at(parent_fd, leaf)
        if actual != wanted:
            raise SyncError("post-transfer identity mismatch")
        if expected is not None:
            os.unlink("previous", dir_fd=stage_fd)
        os.close(stage_fd)
        stage_fd = None
        os.rmdir(stage, dir_fd=root_fd)
        stage = None
        return {"file": actual}
    except Exception as exc:
        recovery = f"; recovery staging retained at {root / stage}" if stage else ""
        raise SyncError(f"transfer failed: {exc}{recovery}") from exc
    finally:
        if parent_fd is not None:
            os.close(parent_fd)
        if stage_fd is not None:
            os.close(stage_fd)
        try:
            if locked:
                os.rmdir(".sophon-sync-lock", dir_fd=root_fd)
        finally:
            os.close(root_fd)


def worker(action, payload):
    """Remote filesystem operations, also executed directly by offline tests."""
    root = Path(payload["root"])
    if not root.is_absolute() or root.name != "sophon-realtime":
        raise SyncError("destination must be an absolute dedicated sophon-realtime directory")
    reject_links(root)
    reference = Path(payload.get("reference_root", ""))
    if not reference.is_absolute() or not reference.is_dir():
        raise SyncError("configured reference root must be an existing absolute directory")
    reject_links(reference)
    resolved_root, resolved_reference = root.resolve(), reference.resolve()
    if resolved_root.is_relative_to(resolved_reference) or resolved_reference.is_relative_to(resolved_root):
        raise SyncError("destination overlaps Mario reference")
    if os.name == "posix":
        # Pin all reference ancestors as well, not just lexical path components.
        reference_fd = open_directory(reference)
        os.close(reference_fd)
    if not root.parent.is_dir() or (root.exists() and not root.is_dir()):
        raise SyncError("destination parent must already exist")
    if action == "inspect":
        entries = payload["entries"]
        if not isinstance(entries, list) or len(entries) > MAX_FILES:
            raise SyncError("invalid inspection size")
        result = {}
        for entry in entries:
            entry_identity(entry)
            rel = entry["path"]
            if rel.casefold() in {k.casefold() for k in result}:
                raise SyncError("duplicate destination path")
            result[rel] = None
        if os.name == "posix":
            try:
                return {"files": posix_inspect(root, entries)}
            except OSError as exc:
                raise SyncError("remote inspection refused an invalid or linked path") from exc
        for rel in result:
            result[rel] = file_identity(safe_path(root, rel))
        return {"files": result}
    if action != "put":
        raise SyncError("unsupported remote operation")
    entry = payload["entry"]
    wanted = entry_identity(entry)
    expected = payload["expected"]
    if expected is not None:
        validate_identity(expected)
    encoded = payload["data"]
    if not isinstance(encoded, str) or len(encoded) > (MAX_FILE_BYTES + 2) // 3 * 4:
        raise SyncError("oversized transfer payload")
    try:
        data = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as exc:
        raise SyncError("invalid transfer encoding") from exc
    if len(data) != wanted["size"] or hashlib.sha256(data).hexdigest() != wanted["sha256"]:
        raise SyncError("transfer hash mismatch before mutation")
    if os.name == "posix":
        return posix_put(root, entry, expected, data)
    path = safe_path(root, entry["path"])
    if file_identity(path) != expected:
        raise SyncError("remote file changed since preview")
    root.mkdir(exist_ok=True)
    lock = root / ".sophon-sync-lock"
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise SyncError("sync already active or interrupted; inspect the existing lock before recovery") from exc
    stage = None
    try:
        path = safe_path(root, entry["path"])
        if file_identity(path) != expected:
            raise SyncError("remote file changed before replacement")
        stage = Path(tempfile.mkdtemp(prefix=".sophon-sync-", dir=root))
        incoming = stage / "incoming"
        with incoming.open("xb") as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        incoming.chmod(wanted["mode"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path = safe_path(root, entry["path"])
        if file_identity(path) != expected:
            raise SyncError("remote file changed during transfer")
        if expected is not None:
            shutil.copy2(path, stage / "previous")
        path = safe_path(root, entry["path"])
        if file_identity(path) != expected:
            raise SyncError("remote changed while preserving recovery copy")
        os.replace(incoming, path)
        actual = file_identity(path)
        if actual != wanted:
            raise SyncError("post-transfer identity mismatch")
        backup = stage / "previous"
        if backup.exists():
            backup.unlink()
        stage.rmdir()
        stage = None
        return {"file": actual}
    except Exception as exc:
        recovery = f"; recovery staging retained at {stage}" if stage else ""
        raise SyncError(f"transfer failed: {exc}{recovery}") from exc
    finally:
        lock.rmdir()


def build_entries(root, selected):
    if len(selected) > MAX_FILES:
        raise SyncError("too many selected files")
    entries, seen = [], set()
    for raw, mode in sorted(selected.items()):
        rel = normalize_relative(raw)
        if is_excluded(rel):
            continue
        if rel.casefold() in seen:
            raise SyncError("case-colliding source paths")
        seen.add(rel.casefold())
        ident = file_identity(safe_path(root, rel))
        if ident is None:
            raise SyncError(f"selected file is missing: {rel}")
        ident["mode"] = mode
        validate_identity(ident, source=True)
        entries.append(dict(path=rel, **ident))
    if not entries:
        raise SyncError("no transferable source files selected")
    return entries


def repository_root(root):
    root = Path(root).absolute()
    reject_links(root)
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                            capture_output=True, text=True, check=True, timeout=15)
    if root.resolve() != Path(result.stdout.strip()).resolve():
        raise SyncError("source root must equal the Git worktree top level")
    return root.resolve()


def git_selection(root, includes):
    root = repository_root(root)
    result = subprocess.run(["git", "-C", str(root), "ls-files", "--stage", "-z"],
                            capture_output=True, check=True, timeout=30)
    selected = {}
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        meta, raw_path = raw.split(b"\t", 1)
        mode, _, stage = meta.decode("ascii").split()
        rel = raw_path.decode("utf-8")
        if is_excluded(rel):
            continue
        if stage != "0" or mode not in ("100644", "100755"):
            raise SyncError("unmerged, linked or nested repository entry needs explicit handling")
        # Source sync never propagates local deletions to the server.
        if not safe_path(root, rel).exists():
            continue
        selected[rel] = 0o755 if mode == "100755" else 0o644
    for raw in includes:
        rel = normalize_relative(raw)
        # Exact new-file selection only; no directory-wide inclusion.
        selected.setdefault(rel, 0o755 if rel.endswith(".sh") else 0o644)
    return selected


def config_digest(config):
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()


def inspect_remote(entries, transport):
    result = transport.call("inspect", {"entries": entries})
    identities = result.get("files")
    if not isinstance(identities, dict) or set(identities) != {e["path"] for e in entries}:
        raise SyncError("incomplete remote inspection")
    for ident in identities.values():
        if ident is not None:
            validate_identity(ident)
    return identities


def create_preview(root, config, selected, transport, replacements=()):
    entries = build_entries(root, selected)
    remote = inspect_remote(entries, transport)
    replace = sorted({normalize_relative(p) for p in replacements})
    if not set(replace) <= {e["path"] for e in entries}:
        raise SyncError("replacement selection must be a transferable manifest path")
    conflicts = [e["path"] for e in entries if remote[e["path"]] not in (None, entry_identity(e))
                 and e["path"] not in replace]
    return {"version": 1, "root": str(Path(root).resolve()), "config_sha256": config_digest(config),
            "entries": entries, "remote": remote, "replace": replace, "conflicts": conflicts}


def validate_manifest(config, manifest):
    if not isinstance(manifest, dict) or manifest.get("version") != 1:
        raise SyncError("unsupported manifest")
    if manifest.get("config_sha256") != config_digest(config):
        raise SyncError("configuration changed; create a new preview")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not 0 < len(entries) <= MAX_FILES:
        raise SyncError("invalid manifest file count")
    seen = set()
    for entry in entries:
        entry_identity(entry)
        key = entry["path"].casefold()
        if key in seen:
            raise SyncError("duplicate manifest path")
        seen.add(key)
    if not isinstance(manifest.get("remote"), dict) or set(manifest["remote"]) != {e["path"] for e in entries}:
        raise SyncError("invalid preview identities")
    for ident in manifest["remote"].values():
        if ident is not None:
            validate_identity(ident)
    replace = manifest.get("replace")
    if not isinstance(replace, list) or any(p not in manifest["remote"] for p in replace):
        raise SyncError("invalid replacement selection")
    return entries


def upload(root, config, manifest, transport):
    entries = validate_manifest(config, manifest)
    if str(Path(root).resolve()) != manifest.get("root"):
        raise SyncError("manifest belongs to a different checkout")
    check_source(root, entries)
    for entry in entries:
        rel = entry["path"]
        actual = file_identity(safe_path(root, rel))
        wanted = entry_identity(entry)
        if actual is None or any(actual[k] != wanted[k] for k in ("size", "sha256")):
            raise SyncError("source changed since preview; create a new preview")
        old = manifest["remote"][rel]
        if old not in (None, wanted) and rel not in manifest["replace"]:
            raise SyncError("remote conflict requires explicit preview replacement selection")
    current = inspect_remote(entries, transport)
    if current != manifest["remote"]:
        raise SyncError("remote changed since preview; reconcile and create a new preview")
    uploaded = 0
    try:
        for entry in entries:
            wanted = entry_identity(entry)
            rel = entry["path"]
            if current[rel] == wanted:
                continue
            data = safe_path(root, rel).read_bytes()
            if len(data) != wanted["size"] or hashlib.sha256(data).hexdigest() != wanted["sha256"]:
                raise SyncError("source changed during upload")
            result = transport.call("put", {"entry": entry, "expected": current[rel],
                                            "data": base64.b64encode(data).decode("ascii")})
            if result.get("file") != wanted:
                raise SyncError("remote write verification mismatch")
            uploaded += 1
        result = verify(config, manifest, transport)
        check_source(root, entries)
        return dict(result, uploaded=uploaded)
    except Exception as exc:
        raise SyncError(f"upload incomplete: {uploaded} writes verified before failure; {exc}") from exc


def check_source(root, entries):
    paths = [e["path"] for e in entries]
    selected = git_selection(root, paths)
    current = build_entries(root, {rel: selected[rel] for rel in paths})
    if current != sorted(entries, key=lambda e: e["path"]):
        raise SyncError("source content or Git executable mode changed since preview")


def verify(config, manifest, transport):
    entries = validate_manifest(config, manifest)
    actual = inspect_remote(entries, transport)
    mismatches = [e["path"] for e in entries if actual[e["path"]] != entry_identity(e)]
    if mismatches:
        raise SyncError("remote verification mismatch: " + ", ".join(mismatches[:10]))
    return {"verified": len(entries)}


def load_config(path, root):
    path = Path(path).expanduser().resolve()
    if path.is_relative_to(root.resolve()):
        raise SyncError("session configuration must be outside the checkout")
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise SyncError("invalid configuration object")
    for key in ("ssh_alias", "expected_host", "expected_user"):
        value = config.get(key)
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.@-]*", value):
            raise SyncError(f"missing or invalid {key}")
    for key, default, maximum in (("expected_port", 22, 65535), ("connect_timeout", 10, 60), ("command_timeout", 120, 600)):
        value = config.setdefault(key, default)
        if type(value) is not int or not 1 <= value <= maximum:
            raise SyncError(f"invalid {key}")
    for key in ("remote_source_root", "mario_reference_root"):
        value = config.get(key)
        if not isinstance(value, str) or not value.startswith("/") or value.startswith("//") or value == "/" or "\\" in value:
            raise SyncError(f"invalid absolute POSIX {key}")
        if str(PurePosixPath(value)) != value or any(p in (".", "..") for p in value.split("/")[1:]) or any(ord(c) < 32 for c in value):
            raise SyncError(f"noncanonical {key}")
    target, reference = (PurePosixPath(config[k]) for k in ("remote_source_root", "mario_reference_root"))
    if target.name != "sophon-realtime" or target.is_relative_to(reference) or reference.is_relative_to(target):
        raise SyncError("source target must be a dedicated sophon-realtime directory separate from Mario")
    return config


def remote_program():
    # Send transient code through SSH's command, not a .claude directory upload.
    constants = "\n".join(f"{n} = {globals()[n]!r}" for n in
                          ("MAX_FILE_BYTES", "MAX_FILES", "EXCLUDED_ROOTS", "EXCLUDED_DIRS", "EXCLUDED_SUFFIXES"))
    functions = (SyncError, normalize_relative, is_excluded, reject_links, safe_path,
                 file_identity, validate_identity, entry_identity, open_directory,
                 open_parent, identity_at, posix_inspect, posix_put, worker)
    source = ("from pathlib import Path, PurePosixPath\nimport os, re, stat, json, sys, base64, hashlib, shutil, tempfile\n"
              + constants + "\n" + "\n".join(inspect.getsource(f) for f in functions)
              + "\ntry:\n p=json.load(sys.stdin); print(json.dumps(worker(p.pop('action'),p)))\n"
              + "except Exception as e:\n print(json.dumps({'error':str(e)})); sys.exit(1)\n")
    encoded = base64.b64encode(zlib.compress(source.encode())).decode("ascii")
    return "import base64,zlib;exec(zlib.decompress(base64.b64decode(" + repr(encoded) + ")))"


class SSHTransport:
    def __init__(self, config):
        self.config = config
        self.options = ["-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
                        "-o", "ForwardAgent=no", "-o", "ForwardX11=no", "-o", "ClearAllForwardings=yes",
                        "-o", "ControlMaster=no", "-o", "ControlPath=none", "-o", "ControlPersist=no",
                        "-o", "RemoteCommand=none", "-o", "PermitLocalCommand=no",
                        "-o", f"ConnectTimeout={config['connect_timeout']}",
                        "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=2"]
        resolved = subprocess.run(["ssh", "-G", *self.options, config["ssh_alias"]],
                                  capture_output=True, text=True, timeout=15, check=True)
        fields = dict(line.split(None, 1) for line in resolved.stdout.splitlines() if " " in line)
        expected = {"hostname": config["expected_host"], "user": config["expected_user"],
                    "port": str(config["expected_port"])}
        if any(fields.get(k) != value for k, value in expected.items()):
            raise SyncError("SSH alias identity differs from configured host/user/port")

    def call(self, action, payload):
        command = "python3 -c " + shlex.quote(remote_program())
        request = dict(payload, action=action, root=self.config["remote_source_root"],
                       reference_root=self.config["mario_reference_root"])
        try:
            result = subprocess.run(["ssh", *self.options, self.config["ssh_alias"], command],
                                    input=json.dumps(request), capture_output=True, text=True,
                                    timeout=self.config["command_timeout"])
        except subprocess.TimeoutExpired as exc:
            raise SyncError("SSH command timed out; remote completion may be partial, inspect before retry") from exc
        try:
            response = json.loads(result.stdout)
        except ValueError as exc:
            raise SyncError("SSH/Python failed or returned invalid output; no target fallback") from exc
        if not isinstance(response, dict) or result.returncode or "error" in response:
            raise SyncError(response.get("error", "SSH failed") if isinstance(response, dict) else "invalid SSH response")
        return response


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("preview", "upload", "verify"))
    parser.add_argument("--config", default=os.environ.get("SOPHON_SESSION_CONFIG"),
                        help="user-local JSON outside checkout, or SOPHON_SESSION_CONFIG")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--manifest", type=Path, required=True, help="local manifest outside checkout")
    parser.add_argument("--include", action="append", default=[], help="exact new source file, preview only")
    parser.add_argument("--replace", action="append", default=[], help="known remote file to replace, preview only")
    args = parser.parse_args(argv)
    try:
        root = repository_root(args.root)
        if not root.is_dir() or not args.config:
            raise SyncError("existing source root and user-local config are required")
        manifest_path = args.manifest.expanduser().absolute()
        reject_links(manifest_path)
        if manifest_path.resolve().is_relative_to(root):
            raise SyncError("manifest must be outside checkout")
        config = load_config(args.config, root)
        if args.action != "preview" and (args.include or args.replace):
            raise SyncError("selection flags apply only to preview")
        transport = SSHTransport(config)
        if args.action == "preview":
            if manifest_path.exists():
                raise SyncError("preview output already exists; choose a new manifest path")
            manifest = create_preview(root, config, git_selection(root, args.include), transport, args.replace)
            with manifest_path.open("x", encoding="utf-8") as out:
                json.dump(manifest, out, indent=2)
                out.write("\n")
            counts = {"add": 0, "unchanged": 0, "replace": 0, "conflict": len(manifest["conflicts"])}
            for entry in manifest["entries"]:
                old = manifest["remote"][entry["path"]]
                if old is None: counts["add"] += 1
                elif old == entry_identity(entry): counts["unchanged"] += 1
                elif entry["path"] in manifest["replace"]: counts["replace"] += 1
            print(json.dumps(dict(counts, manifest=str(manifest_path))))
            return 2 if manifest["conflicts"] else 0
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        result = upload(root, config, manifest, transport) if args.action == "upload" else verify(config, manifest, transport)
        print(json.dumps(result))
        return 0
    except (SyncError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f"source-sync: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
