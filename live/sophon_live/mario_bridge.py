"""Opt-in isolated development adapter; importing this module opens nothing.

The regular Live client protocol is unchanged. This adapter owns generated
business history only, not speech readiness, native cancellation or audibility.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import ssl
import sys
from urllib.parse import urlsplit
import uuid

from .mario_reply import parse_mario_reply
from .mario_runtime import MarioRequest, MarioRuntime


def _directory(value: object) -> Path:
    if not isinstance(value, str) or not value.startswith("/"):
        raise ValueError("An absolute isolated Linux directory is required.")
    path = Path(value)
    if any(parent.is_symlink() for parent in (path, *path.parents)):
        raise ValueError("Linked development bindings are forbidden.")
    if path.resolve(strict=True) != path or not path.is_dir():
        raise ValueError("Missing or noncanonical development directory.")
    return path


@dataclass(frozen=True, repr=False)
class DevBindings:
    development_root: Path
    mario_root: Path
    assets_root: Path
    runtime_root: Path
    fixtures_root: Path
    sessions_root: Path
    logs_root: Path
    reports_root: Path
    model: dict = field(repr=False)
    ca_bundle: str = field(repr=False)
    config: dict = field(repr=False)

    @classmethod
    def from_config(cls, config: dict) -> DevBindings:
        try:
            b = config["development_integration"]
            if (b["plan_id"] != "2026-11-25-sophon-mario-development-integration"
                    or b["activation_authorized"] is not False or b["normal_observe_enabled"] is not False):
                raise ValueError("Only non-activating isolated Mario development is supported.")
            root = _directory(b["development_root"])
            mario, runtime = _directory(b["mario_library_root"]), _directory(b["runtime_root"])
            source = _directory(config["remote_source_root"])
            reference = _directory(config["mario_reference_root"])
            assets = _directory(b["mario_assets_root"])
            if (mario != root / "Mario" or runtime != root / "runtime" or source != root / "sophon-realtime"
                    or b["sophon_source_root"] != str(source) or assets != mario / "script-system"
                    or root.is_relative_to(reference) or reference.is_relative_to(root)):
                raise ValueError("Unsafe isolated development roots.")
            dirs = [_directory(b[key + "_root"]) for key in ("fixtures", "sessions", "logs", "reports")]
            if any(path != runtime / name for path, name in zip(dirs, ("fixtures", "sessions", "logs", "reports"))):
                raise ValueError("Runtime resources must stay in their bound isolated directories.")
            ownership_path = Path(b["resource_ownership_receipt"])
            if ownership_path != runtime / "reports/p1-source-copy/ownership.json" or ownership_path.is_symlink():
                raise ValueError("Invalid resource ownership receipt.")
            ownership = json.loads(ownership_path.read_text(encoding="utf-8"))
            if ownership["token"] != b["ownership_token"]:
                raise ValueError("Development ownership differs.")
            for rel, identity in ownership["directories"].items():
                path = root / rel
                if not path.resolve(strict=True).is_relative_to(root) or path.is_symlink():
                    raise ValueError("Ownership path escaped development root.")
                st = path.stat()
                if (st.st_dev, st.st_ino) != (identity["dev"], identity["ino"]):
                    raise ValueError("Owned resource identity changed.")
            manifest_path = Path(b["source_manifest"])
            if manifest_path != runtime / "reports/p1-source-copy/manifest.json" or manifest_path.is_symlink():
                raise ValueError("Invalid source manifest binding.")
            data = manifest_path.read_bytes()
            if hashlib.sha256(data).hexdigest() != b["source_manifest_sha256"]:
                raise ValueError("Source manifest changed.")
            manifest = json.loads(data)
            for entry in manifest["files"]:
                if entry["destination_relative"].startswith("script-system/"):
                    path = mario / entry["destination_relative"]
                    if (path.is_symlink() or not path.resolve(strict=True).is_relative_to(assets)
                            or hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]):
                        raise ValueError("Immutable Mario assets changed.")
            budget = b["model_budget"]
            expected = {"max_total_requests": 6, "max_output_tokens_per_request": 1536,
                        "timeout_seconds_per_request": 30, "concurrency": 1, "automatic_retries": 0, "max_loop_rounds": 3}
            if any(type(budget[k]) is not int or budget[k] != v for k, v in expected.items()):
                raise ValueError("The shared model workload limits must not change.")
            model = dict(b["model"])
            url = urlsplit(model["base_url"])
            if (url.scheme not in ("http", "https") or not url.hostname or url.username or url.password
                    or url.query or url.fragment or url.path.rstrip("/") != "/v1" or not model["model_id"]):
                raise ValueError("Explicit safe model binding required.")
            tls = b["tls"]
            if tls["verify"] is not True:
                raise ValueError("TLS verification cannot be disabled.")
            return cls(root, mario, assets, runtime, *dirs, model, tls["ca_bundle"], dict(config))
        except (KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
            raise ValueError("Missing or unsafe isolated Mario configuration.") from None


def load_business_package(root: Path):
    """Load a real regular package by bound spec, without changing sys.path."""
    package_dir = root / "mario_business"
    expected = package_dir / "__init__.py"
    for name, module in tuple(sys.modules.items()):
        if name == "mario_business" or name.startswith("mario_business."):
            location = getattr(module, "__file__", None)
            if location is None or not Path(location).resolve().is_relative_to(package_dir.resolve()):
                raise ValueError("Mario package name is already bound to a different source.")
    if "mario_business" in sys.modules:
        return sys.modules["mario_business"]
    if not expected.is_file() or expected.is_symlink():
        raise ValueError("Bound Mario library package is missing.")
    spec = importlib.util.spec_from_file_location("mario_business", expected, submodule_search_locations=[str(package_dir)])
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load bound Mario library package.")
    module = importlib.util.module_from_spec(spec)
    before = set(sys.modules)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        for name in set(sys.modules) - before:
            if name == "mario_business" or name.startswith("mario_business."):
                del sys.modules[name]
        raise
    return module


class MarioFactory:
    """One real library/state manager and shared client gate; unique UID per Live."""

    @classmethod
    async def open(cls, bindings: DevBindings, *, transport=None, resource_root: Path | None = None):
        if not isinstance(bindings, DevBindings):
            raise ValueError("Safe isolated bindings are required.")
        # Revalidate disk identities on explicit open, not merely at config load.
        if DevBindings.from_config(bindings.config) != bindings:
            raise ValueError("Bindings differ from their verified external configuration.")
        load_business_package(bindings.mario_root)
        library_type = importlib.import_module("mario_business.library").BusinessLibrary
        llm_module = importlib.import_module("mario_business.llm.llm_client")
        import httpx
        if resource_root is None:
            resources = bindings.sessions_root / ("library_" + uuid.uuid4().hex)
            resources.mkdir()
            budget_path = bindings.reports_root / "mario-qwen-budget.json"
            log_path = bindings.logs_root / (resources.name + ".jsonl")
        else:
            if not isinstance(transport, httpx.MockTransport):
                raise ValueError("A separate fixture budget is permitted only with mocked HTTP.")
            resources = resource_root.resolve(strict=True)
            if resource_root.is_symlink() or not resources.is_relative_to(bindings.fixtures_root):
                raise ValueError("Test resources must be in owned fixtures.")
            budget_path = resources / "budget.json"
            log_path = resources / "events.jsonl"
        verify = ssl.create_default_context(cafile=bindings.ca_bundle)
        headers = {}
        key_env = bindings.model.get("api_key_env")
        if key_env:
            if not os.environ.get(key_env):
                raise ValueError("Required model credential environment is missing.")
            headers["Authorization"] = "Bearer " + os.environ[key_env]
        http = httpx.AsyncClient(base_url=bindings.model["base_url"].rstrip("/") + "/", headers=headers,
                                 verify=verify, transport=transport, timeout=30, follow_redirects=False, trust_env=False)
        client = llm_module.LLMClient(client=http, model=bindings.model["model_id"], budget=llm_module.RequestBudget(budget_path))
        factory = cls()
        factory.bindings = bindings
        factory.bridges = set()
        factory.closed = False
        factory._close_task = None
        try:
            factory.library = await library_type.open(assets_root=bindings.assets_root, store_path=resources / "business.db",
                                                       log_path=log_path, client=client, validator=parse_mario_reply)
        except BaseException:
            await client.close()
            raise
        return factory

    async def create(self, session_id, emit):
        if self.closed:
            raise RuntimeError("Mario factory is closed.")
        uid = await self.library.create_session()
        bridge = SessionBridge(self, uid, session_id, emit)
        self.bridges.add(bridge)
        return bridge

    async def _close(self):
        try:
            for bridge in list(self.bridges):
                await bridge.close()
        finally:
            await self.library.close()

    async def close(self):
        if self._close_task is None:
            self.closed = True
            for bridge in self.bridges:
                bridge.closed = True
                bridge.invalidate()
            self._close_task = asyncio.create_task(self._close(), name="mario-factory-close")
        interrupted = False
        while not self._close_task.done():
            try:
                await asyncio.shield(self._close_task)
            except asyncio.CancelledError:
                interrupted = True
        self._close_task.result()
        if interrupted:
            raise asyncio.CancelledError


class SessionBridge:
    def __init__(self, factory, uid, session_id, emit):
        self.factory, self.uid, self.emit = factory, uid, emit
        self.epoch = 0
        self.closed = False
        self.drivers = set()
        self._delivery = None
        self.runtime = MarioRuntime(session_id, self._business, self._emit)
        self._close_task = None

    @property
    def busy(self):
        return any(not task.done() for task in self.drivers)

    def valid(self, epoch, revision):
        state = self.factory.library.manager.get_session(self.uid)
        return not self.closed and epoch == self.epoch and state is not None and state.revision == revision

    def invalidate(self):
        # Synchronous fence BEFORE cancellation or callback/queued timer can run.
        self.epoch += 1
        self.runtime.invalidate()
        for task in tuple(self.drivers):
            task.cancel()

    def submit(self, event, *, turn_id):
        if self.closed:
            raise RuntimeError("Mario session bridge is closed.")
        self.invalidate()
        epoch = self.epoch
        task = asyncio.create_task(self._drive(event, turn_id, epoch), name="mario-live-driver")
        self.drivers.add(task)
        task.add_done_callback(self._driver_done)
        return epoch

    def _driver_done(self, task):
        self.drivers.discard(task)
        if not task.cancelled():
            task.exception()  # callback failures never retry or escape unobserved

    async def _drive(self, event, turn_id, epoch):
        if epoch != self.epoch or self.closed:
            return
        await self.runtime.handle(event, turn_id=turn_id)

    async def _business(self, request: MarioRequest):
        epoch = self.epoch
        self._delivery = None
        active = lambda: not self.closed and self.epoch == epoch and self.runtime.is_active(request)
        try:
            result = await self.factory.library.run(self.uid, request.task, active=active)
        except Exception:
            outcome = self.factory.library.last_outcomes.get(self.uid)
            if active() and outcome is not None:
                self._delivery = (epoch, outcome.revision, request.delegation_id)
            raise
        self._delivery = (epoch, result.revision, request.delegation_id)
        return result.text

    async def _emit(self, event):
        delivery = self._delivery
        if delivery is not None and self.valid(delivery[0], delivery[1]):
            await self.emit(event, *delivery)

    async def drain(self):
        while self.drivers:
            tasks = tuple(self.drivers)
            await asyncio.gather(*tasks, return_exceptions=True)
            # gather of already-finished tasks may not suspend on Python 3.12.
            # Retire synchronously rather than spin ahead of done callbacks.
            for task in tasks:
                if task.done():
                    self._driver_done(task)

    async def _close(self):
        self.closed = True
        self.invalidate()
        await self.drain()
        await self.runtime.close()
        await self.factory.library.release_session(self.uid)
        self.factory.bridges.discard(self)

    async def close(self):
        if self._close_task is None:
            # Fence immediately, before the cleanup task is scheduled.
            self.closed = True
            self.invalidate()
            self._close_task = asyncio.create_task(self._close(), name="mario-bridge-close")
        interrupted = False
        while not self._close_task.done():
            try:
                await asyncio.shield(self._close_task)
            except asyncio.CancelledError:
                interrupted = True
        self._close_task.result()
        if interrupted:
            raise asyncio.CancelledError
