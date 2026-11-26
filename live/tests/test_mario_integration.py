"""Real library and actual gateway, with HTTP/native engine/WebSocket I/O mocked.

Run full tests in the approved isolated Linux environment. No listener, ASR,
model, audio or native-engine connection is opened by this module.
"""
import asyncio
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from live.sophon_live.mario_bridge import DevBindings, MarioFactory, load_business_package


class BindingsTests(unittest.TestCase):
    def test_missing_config_fails_closed(self):
        with self.assertRaises(ValueError):
            DevBindings.from_config({})

    def test_import_collision_fails_without_path_hacks(self):
        import sys
        before = list(sys.path)
        with patch.dict(sys.modules, {"mario_business": SimpleNamespace(__file__="/not/the/bound/package.py")}):
            with self.assertRaises(ValueError):
                load_business_package(Path("/does/not/exist"))
        self.assertEqual(sys.path, before)


class MemoryWS:
    def __init__(self):
        self.events = []
        self.closed = False

    async def send(self, raw):
        self.events.append(json.loads(raw))

    async def close(self):
        self.closed = True


class MemoryEngine:
    def __init__(self):
        self.q = asyncio.Queue()
        self.results = []
        self.closed = False

    async def tool_result(self, call_id, content, speak=True):
        self.results.append((call_id, content, speak))
        return True

    async def close(self):
        self.closed = True


def completion(text="synthetic settled text", target=None, finish="stop"):
    actions = [] if target is None else [{"skill": "script_jump", "params": {"target_script": target}}]
    return {"choices": [{"message": {"content": json.dumps({"response": text, "actions": actions}, ensure_ascii=False)}, "finish_reason": finish}]}


class IntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        import httpx
        from live.sophon_live import gateway
        self.gateway = gateway
        self.cfg = json.loads(os.environ["MARIO_TEST_BINDINGS"])
        self.bindings = DevBindings.from_config(self.cfg)
        self.tmp = tempfile.TemporaryDirectory(dir=self.bindings.fixtures_root)
        self.path = Path(self.tmp.name)
        self.responses = []
        self.calls = []
        self.gate = None
        self.entered = asyncio.Event()
        async def http(request):
            self.calls.append(json.loads(request.content))
            self.entered.set()
            if self.gate:
                try:
                    await self.gate.wait()
                except asyncio.CancelledError:
                    await self.gate.wait()
            value = self.responses.pop(0)
            if isinstance(value, Exception):
                raise value
            return httpx.Response(200, json=value)
        self.factory = await MarioFactory.open(self.bindings, transport=httpx.MockTransport(http), resource_root=self.path)
        self.sessions = []

    async def asyncTearDown(self):
        if self.gate:
            self.gate.set()
        for session in self.sessions:
            await asyncio.wait_for(session.close("test_done"), 5)
            await session.close("repeat")
            self.assertFalse(session._owned)
        await self.factory.close()
        await self.factory.close()
        self.assertFalse(self.factory.library.active_tasks)
        self.assertFalse([t for t in asyncio.all_tasks() if t is not asyncio.current_task() and t.get_name().startswith(("mario-", "live-session-"))])
        self.assertEqual(self.factory.library.manager.count(), 0)
        self.assertTrue(self.factory.library.client.client.is_closed)
        self.tmp.cleanup()

    async def session(self, enabled=True):
        args = SimpleNamespace(engine="unused", bridge="unused", mario_enabled=enabled, mario_factory=self.factory if enabled else None, mario_bindings=self.bindings if enabled else None)
        session = self.gateway.LiveSession(MemoryWS(), args, None, asyncio.Lock())
        session.engine = MemoryEngine()
        session.started = True
        if enabled:
            await session._open_mario()
        self.sessions.append(session)
        return session

    async def delegate(self, session, task="synthetic input", call="call_synthetic"):
        await session._delegate({"name": "delegate", "arguments": {"task": task}, "call_id": call})
        return next(reversed(session.deleg))

    async def settle(self, session, did):
        await session.mario.drain()
        await session._flush_deleg(did)
        if self.gateway.DELEG_MODE != "model":
            await session._short_done(did)

    async def test_off_preserves_client_delegation_and_no_mario(self):
        session = await self.session(False)
        did = await self.delegate(session)
        self.assertIsNone(session.mario)
        self.assertFalse(self.calls)
        await session.on_event({"type": "session.commentary.append", "delegation_id": did, "content": "client result"})
        await session._flush_deleg(did)
        if self.gateway.DELEG_MODE != "model":
            await session._short_done(did)
        self.assertIn("client result", session.engine.results[0][1])

    async def test_actual_jump_followup_and_correlated_commentary(self):
        session = await self.session()
        self.responses.extend([completion("opening", "Script_4"), completion("followup")])
        did = await self.delegate(session, "我想看车，还没有选具体车型")
        await self.settle(session, did)
        state = self.factory.library.manager.get_session(session.mario.uid)
        self.assertEqual(state.current_script, "Script_4")
        self.assertEqual(state.global_history[0].mario_text, "opening\n\nfollowup")
        self.assertEqual(session.engine.results[0][0], "call_synthetic")
        self.assertIn("opening\n\nfollowup", session.engine.results[0][1])
        self.assertEqual(len(session.engine.results), 1)
        await session._flush_deleg(did)
        self.assertEqual(len(session.engine.results), 1)

    async def test_noaction_and_noop(self):
        session = await self.session()
        self.responses.extend([completion(), completion(target="Script_1")])
        for i in range(2):
            did = await self.delegate(session, call="call_" + str(i))
            await self.settle(session, did)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(len(session.engine.results), 2)

    async def test_client_cannot_compete_for_internal_delegation(self):
        session = await self.session()
        self.responses.append(completion())
        did = await self.delegate(session)
        await session.on_event({"type": "session.commentary.append", "delegation_id": did, "content": "competing"})
        await self.settle(session, did)
        self.assertNotIn("competing", session.engine.results[0][1])
        self.assertTrue(any(e["type"] == "error" for e in session.ws.events))

    async def test_two_sessions_have_unique_uids_one_manager(self):
        a, b = await self.session(), await self.session()
        self.assertNotEqual(a.mario.uid, b.mario.uid)
        self.responses.extend([completion("a result"), completion("b result")])
        da, db = await self.delegate(a), await self.delegate(b)
        await asyncio.gather(self.settle(a, da), self.settle(b, db))
        self.assertEqual(len(a.engine.results), 1)
        self.assertEqual(len(b.engine.results), 1)
        self.assertEqual(self.factory.library.manager.count(), 2)

    async def test_invalid_completion_has_no_history_or_commentary(self):
        session = await self.session()
        self.responses.append(completion(finish="length"))
        did = await self.delegate(session)
        await self.settle(session, did)
        self.assertFalse(session.engine.results)
        state = self.factory.library.manager.get_session(session.mario.uid)
        self.assertEqual(state.revision, 0)
        self.assertFalse(state.global_history)
        self.assertTrue(any(e["type"] == "error" for e in session.ws.events))

    async def test_replacement_fences_suppressing_provider(self):
        session = await self.session()
        self.gate = asyncio.Event()
        self.responses.extend([completion("stale"), completion("fresh")])
        old = await self.delegate(session, call="old")
        await asyncio.wait_for(self.entered.wait(), 2)
        new = await self.delegate(session, call="new")
        self.gate.set()
        await self.settle(session, new)
        await session._flush_deleg(old)
        state = self.factory.library.manager.get_session(session.mario.uid)
        self.assertEqual(state.revision, 1)
        self.assertEqual(len(session.engine.results), 1)
        self.assertEqual(session.engine.results[0][0], "new")
        self.assertNotIn("stale", state.global_history[0].mario_text)

    async def test_bargein_fences_queued_settled_commentary(self):
        session = await self.session()
        self.responses.append(completion())
        did = await self.delegate(session)
        await session.mario.drain()
        session._drop_playback("synthetic barge-in")
        await session._flush_deleg(did)
        self.assertFalse(session.engine.results)
        self.assertFalse(session.deleg[did]["chunks"])

    async def test_engine_cancel_fences_late_error(self):
        session = await self.session()
        self.gate = asyncio.Event();self.responses.append(ValueError("synthetic failure"))
        did = await self.delegate(session)
        await asyncio.wait_for(self.entered.wait(), 2)
        pump = asyncio.create_task(session._engine_events())
        await session.engine.q.put({"t": "cancel"})
        await asyncio.sleep(0)
        self.gate.set()
        await session.mario.drain()
        pump.cancel();await asyncio.gather(pump, return_exceptions=True)
        self.assertFalse(session.engine.results)
        self.assertFalse(any(e["type"] == "error" for e in session.ws.events))

    async def test_disconnect_waits_for_owned_provider_and_no_stale_commit(self):
        session = await self.session()
        uid = session.mario.uid
        self.gate = asyncio.Event();self.responses.append(completion())
        await self.delegate(session)
        await asyncio.wait_for(self.entered.wait(), 2)
        closing = asyncio.create_task(session.close("disconnect"))
        await asyncio.sleep(0)
        self.gate.set()
        await asyncio.wait_for(closing, 5)
        self.assertFalse(session.engine.results)
        self.assertIsNone(self.factory.library.manager.get_session(uid))
        self.assertTrue(session.engine.closed)

    async def test_off_import_and_session_create_no_business_modules(self):
        import subprocess
        code = "from types import SimpleNamespace;import asyncio,sys;from live.sophon_live.gateway import LiveSession;s=LiveSession(None,SimpleNamespace(),None,asyncio.Lock());assert s.mario is None;assert not any(n=='mario_business' or n.startswith('mario_business.') for n in sys.modules);print('off-import-ok')"
        proc = await asyncio.create_subprocess_exec(__import__('sys').executable, "-B", "-c", code, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = await asyncio.wait_for(proc.communicate(), 10)
        self.assertEqual((proc.returncode, out, err), (0, b"off-import-ok\n", b""))

    async def test_unsafe_binding_and_modified_budget_fail_closed(self):
        import copy
        for field, value in [("activation_authorized", True), ("normal_observe_enabled", True), ("mario_library_root", str(self.path)), ("source_manifest_sha256", "0" * 64)]:
            config = copy.deepcopy(self.cfg)
            config["development_integration"][field] = value
            with self.assertRaises(ValueError):
                DevBindings.from_config(config)
        config = copy.deepcopy(self.cfg)
        config["development_integration"]["model_budget"]["max_total_requests"] = 7
        with self.assertRaises(ValueError):
            DevBindings.from_config(config)
        config = copy.deepcopy(self.cfg)
        config["development_integration"]["tls"]["verify"] = False
        with self.assertRaises(ValueError):
            DevBindings.from_config(config)
        self.assertFalse(self.calls)

    async def test_real_transport_cannot_get_resettable_fixture_budget(self):
        with self.assertRaises(ValueError):
            await MarioFactory.open(self.bindings, resource_root=self.path)
        self.assertFalse(self.calls)

    async def test_on_start_uses_real_factory_before_mocked_engine(self):
        session = self.gateway.LiveSession(MemoryWS(), SimpleNamespace(engine="unused", bridge="unused", mario_enabled=True, mario_factory=self.factory, mario_bindings=self.bindings), None, asyncio.Lock())
        engine = MemoryEngine()
        async def start(**kwargs):
            return None
        engine.start = start
        self.sessions.append(session)
        with patch.object(self.gateway, "VllmOmniAdapter", return_value=engine):
            self.assertTrue(await session.on_start({"session": {"delegation": {"type": "client"}}}))
        self.assertIsNotNone(session.mario)
        self.assertTrue(session.started)
        self.assertTrue(any(event["type"] == "session.started" for event in session.ws.events))
        await session.close("started_test")
        self.assertTrue(all(t.done() for t in session.tasks))

    async def test_unsafe_on_start_never_constructs_native_engine(self):
        session = self.gateway.LiveSession(MemoryWS(), SimpleNamespace(mario_enabled=True), None, asyncio.Lock())
        self.sessions.append(session)
        with patch.object(self.gateway, "VllmOmniAdapter") as engine:
            self.assertFalse(await session.on_start({}))
            engine.assert_not_called()
        self.assertFalse(self.calls)

    async def test_actual_engine_delegate_driver_does_not_block_event_pump(self):
        session = await self.session()
        self.gate = asyncio.Event();self.responses.append(completion())
        pump = session._spawn(session._engine_events())
        await session.engine.q.put({"t": "tool_call", "name": "delegate", "call_id": "engine_call", "arguments": {"task": "synthetic"}})
        await asyncio.wait_for(self.entered.wait(), 2)
        await session.engine.q.put({"t": "cancel"})
        for _ in range(5):
            await asyncio.sleep(0)
        self.assertFalse(pump.done())
        self.gate.set()
        await session.mario.drain()
        self.assertFalse(session.engine.results)
        self.assertEqual(self.factory.library.manager.get_session(session.mario.uid).revision, 0)

    async def test_revision_change_discards_already_queued_commentary(self):
        session = await self.session()
        self.responses.append(completion())
        did = await self.delegate(session)
        await session.mario.drain()
        state = self.factory.library.manager.get_session(session.mario.uid)
        state.revision += 1  # synthetic competing owner, not mocked business code
        await session._flush_deleg(did)
        self.assertFalse(session.engine.results)

    async def test_duplicate_tool_result_does_not_duplicate_business_commit(self):
        session = await self.session()
        self.responses.append(completion())
        did = await self.delegate(session)
        await self.settle(session, did)
        await session._flush_deleg(did)
        await session.on_event({"type": "session.thinking.append", "delegation_id": did, "content": "duplicate"})
        self.assertEqual(self.factory.library.manager.get_session(session.mario.uid).revision, 1)
        self.assertEqual(len(session.engine.results), 1)

    async def test_nonowned_client_result_still_works_when_mario_on(self):
        session = await self.session()
        session.deleg["nonowned"] = {"call_id": "client_call", "chunks": [], "timer": None, "t0": __import__('time').monotonic()}
        await session.on_event({"type": "session.commentary.append", "delegation_id": "nonowned", "content": "ordinary client result"})
        await session._flush_deleg("nonowned")
        if self.gateway.DELEG_MODE != "model":
            await session._short_done("nonowned")
        self.assertEqual(session.engine.results[0][0], "client_call")
        self.assertFalse(self.calls)

    async def test_later_round_failure_reports_actual_state_without_success(self):
        session = await self.session()
        self.responses.extend([completion("opening", "Script_4"), completion(finish="length")])
        did = await self.delegate(session)
        await self.settle(session, did)
        state = self.factory.library.manager.get_session(session.mario.uid)
        outcome = self.factory.library.last_outcomes[session.mario.uid]
        self.assertEqual((state.current_script, state.revision, outcome.status), ("Script_4", 1, "failed"))
        self.assertFalse(session.engine.results)
        self.assertTrue(any(e["type"] == "error" for e in session.ws.events))

    async def test_replayed_engine_call_never_recommits(self):
        session = await self.session()
        self.responses.append(completion())
        did = await self.delegate(session, call="same_engine_call")
        await self.settle(session, did)
        await session._delegate({"name": "delegate", "call_id": "same_engine_call", "arguments": {"task": "duplicate"}})
        await session.mario.drain()
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(len(session.deleg), 1)
        self.assertEqual(self.factory.library.manager.get_session(session.mario.uid).revision, 1)

    async def test_cancelled_factory_close_still_drains_clients_and_drivers(self):
        session = await self.session()
        self.gate = asyncio.Event();self.responses.append(completion())
        await self.delegate(session)
        await asyncio.wait_for(self.entered.wait(), 2)
        closing = asyncio.create_task(self.factory.close())
        await asyncio.sleep(0)
        closing.cancel();self.gate.set()
        with self.assertRaises(asyncio.CancelledError):
            await closing
        self.assertFalse(session.mario.drivers)
        self.assertTrue(self.factory.library.client.client.is_closed)
        self.assertFalse(self.factory.library.active_tasks)

    async def test_missing_factory_fails_closed(self):
        args = SimpleNamespace(mario_enabled=True, mario_factory=None, mario_bindings=self.bindings)
        s = self.gateway.LiveSession(MemoryWS(), args, None, asyncio.Lock())
        with self.assertRaises(ValueError):
            await s._open_mario()
        self.assertFalse(self.calls)


if __name__ == "__main__":
    unittest.main()
