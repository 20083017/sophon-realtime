"""Synthetic, stdlib-only tests: no gateway, Mario, model or tool imports."""
import asyncio
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import FrozenInstanceError
import io
import unittest
from unittest.mock import patch

from live.sophon_live.mario_runtime import MarioRequest, MarioRuntime


TASK = "SYNTHETIC_TEST_ONLY_TASK"
RESULT = "SYNTHETIC_TEST_ONLY_RESULT"
PRIVATE = "SYNTHETIC_TEST_ONLY_NOT_FOR_ERRORS" * 100
TIMEOUT = 5


def delegation(did="item_test", task=TASK):
    return {"type": "session.delegation.created", "offset_ms": 0,
            "delegation": {"id": did, "type": "delegation", "target": "client", "task": task}}


def commentary(did="item_test", content=RESULT):
    return {"type": "session.commentary.append", "delegation_id": did, "content": content}


def error(code, message):
    return {"type": "error", "error": {"code": code, "message": message}}


async def bounded(awaitable):
    return await asyncio.wait_for(awaitable, TIMEOUT)


class MarioRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.runtimes = []
        self.callers = []
        self.gates = []
        self.owned = []
        self.requests = []
        self.events = []

    async def asyncTearDown(self):
        # Release only synthetic barriers owned by this test, including failure paths.
        for gate in self.gates:
            gate.set()
        for task in self.callers:
            if not task.done():
                task.cancel()
        for runtime in self.runtimes:
            await bounded(runtime.close())
        if self.callers:
            await bounded(asyncio.gather(*self.callers, return_exceptions=True))
        self.assertTrue(all(task.done() for task in self.owned), "owned work leaked")

    def gate(self):
        gate = asyncio.Event()
        self.gates.append(gate)
        return gate

    def spawn(self, awaitable):
        task = asyncio.create_task(awaitable)
        self.callers.append(task)
        return task

    def runtime(self, business=None, emit=None, session_id="session_test"):
        async def fake(request):
            return RESULT

        async def observed(request):
            self.requests.append(request)
            self.owned.append(asyncio.current_task())
            return await (business or fake)(request)

        async def record(event):
            self.events.append(event)

        runtime = MarioRuntime(session_id, observed, emit or record)
        self.runtimes.append(runtime)
        return runtime

    async def test_exact_commentary_and_immutable_typed_request(self):
        runtime = self.runtime()
        self.assertIsNone(await bounded(runtime.handle(delegation(), turn_id="turn_test")))
        self.assertEqual(self.events, [commentary()])
        self.assertEqual(self.requests, [MarioRequest("session_test", "turn_test", "item_test", 1, TASK)])
        with self.assertRaises(FrozenInstanceError):
            self.requests[0].generation = 99
        self.assertEqual(set(self.events[0]), {"type", "delegation_id", "content"})

    async def test_text_is_preserved_without_normalization(self):
        text = "  SYNTHETIC_TEST_ONLY\n全角；：= and script_jump are inert text.  "

        async def fake(request):
            self.assertEqual(request.task, text)
            return text

        await bounded(self.runtime(fake).handle(delegation(task=text), turn_id="turn_test"))
        self.assertEqual(self.events, [commentary(content=text)])
        self.assertEqual(self.events[0]["content"].encode("utf-8"), text.encode("utf-8"))

    async def test_completed_shape_fixture_extracts_response_only_in_test_provider(self):
        fixture = {"response": "SYNTHETIC_TEST_ONLY_RESPONSE",
                   "actions": [{"skill": "script_jump", "params": {"target_script": "Script_4"}}]}

        async def fake(request):
            return fixture["response"]

        await bounded(self.runtime(fake).handle(delegation(), turn_id="turn_test"))
        self.assertEqual(self.events, [commentary(content=fixture["response"])])
        self.assertEqual(fixture, {"response": "SYNTHETIC_TEST_ONLY_RESPONSE",
                                  "actions": [{"skill": "script_jump", "params": {"target_script": "Script_4"}}]})

    async def test_invalid_session_ids_rejected_before_provider(self):
        async def unused(value):
            self.fail("invalid constructor must not call injected functions")

        for value in (None, "", " ", 4, [], {}, "has space", " leading", "tab\t", "nul\x00", "del\x7f"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, r"^session_id must be a non-empty identifier\.$"):
                    MarioRuntime(value, unused, unused)
        with self.assertRaises(TypeError):
            MarioRuntime(business=unused, emit=unused)
        self.assertEqual(self.requests, [])

    async def test_invalid_callables_rejected(self):
        async def unused(value):
            pass

        for business, emit in ((None, unused), (unused, None), (42, [])):
            with self.subTest(business=business, emit=emit):
                with self.assertRaises(TypeError):
                    MarioRuntime("session_test", business, emit)

    async def test_invalid_turn_ids_never_call_provider(self):
        runtime = self.runtime()
        for value in (None, "", " ", 4, [], {}, "has space", "\n", "nul\x00"):
            with self.subTest(value=value):
                self.events.clear()
                await bounded(runtime.handle(delegation(), turn_id=value))
                self.assertEqual(self.events, [error("invalid_value", "turn_id must be a non-empty identifier.")])
        with self.assertRaises(TypeError):
            await runtime.handle(delegation())
        self.assertEqual(self.requests, [])

    async def test_malformed_events_never_call_provider(self):
        cases = [(value, "Event must be a dictionary.") for value in (None, [], 1, TASK)]
        cases += [(value, "event.type must be non-empty text.")
                  for value in ({}, {"type": None}, {"type": 4}, {"type": " \t"})]
        for nested in (None, [], TASK, 1):
            event = delegation()
            event["delegation"] = nested
            cases.append((event, "event.delegation must be a dictionary."))
        event = delegation()
        del event["delegation"]
        cases.append((event, "event.delegation must be a dictionary."))
        fields = {
            "id": ("delegation.id must be a non-empty identifier.", (None, "", " ", [], 1, "a b", "nul\x00")),
            "type": ("delegation.type must be delegation.", (None, "", [], 1, "other")),
            "target": ("delegation.target must be client.", (None, "", [], 1, "server")),
            "task": ("delegation.task must be non-empty text.", (None, "", " \n\t", [], {}, 1, False)),
        }
        for field, (message, values) in fields.items():
            event = delegation()
            del event["delegation"][field]
            cases.append((event, message))
            for value in values:
                event = delegation()
                event["delegation"][field] = value
                cases.append((event, message))
        runtime = self.runtime()
        for event, message in cases:
            with self.subTest(event=event):
                self.events.clear()
                await bounded(runtime.handle(event, turn_id="turn_test"))
                self.assertEqual(self.events, [error("invalid_value", message)])
        self.assertEqual(self.requests, [])

    async def test_unsupported_event_has_exact_sanitized_error(self):
        runtime = self.runtime()
        for event_type in ("session.close", PRIVATE):
            self.events.clear()
            await bounded(runtime.handle({"type": event_type}, turn_id="turn_test"))
            self.assertEqual(self.events, [error("invalid_request_error", "Unsupported event type.")])
        self.assertEqual(self.requests, [])

    async def test_invalid_request_does_not_cancel_active_work(self):
        started, release = asyncio.Event(), self.gate()

        async def fake(request):
            started.set()
            await release.wait()
            return RESULT

        runtime = self.runtime(fake)
        caller = self.spawn(runtime.handle(delegation(), turn_id="turn_test"))
        await bounded(started.wait())
        await bounded(runtime.handle({}, turn_id="turn_bad"))
        self.assertFalse(caller.done())
        release.set()
        await bounded(caller)
        self.assertEqual(self.events, [error("invalid_value", "event.type must be non-empty text."), commentary()])
        self.assertEqual(len(self.requests), 1)

    async def test_provider_failure_is_fixed_bounded_and_silent(self):
        class SensitiveFailure(Exception):
            def __str__(self):
                raise AssertionError("provider exception must not be formatted")

        async def fake(request):
            raise SensitiveFailure(PRIVATE)

        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output), patch("logging.Logger._log") as log:
            await bounded(self.runtime(fake).handle(delegation(task=PRIVATE), turn_id="turn_test"))
        self.assertEqual(self.events, [error("server_error", "Business callable failed.")])
        self.assertLess(len(self.events[0]["error"]["message"]), 100)
        self.assertEqual(output.getvalue(), "")
        log.assert_not_called()

    async def test_invalid_results_have_exact_error_not_commentary(self):
        for value in (None, "", " \t\n", 0, False, [], {"response": RESULT, "actions": []}):
            with self.subTest(value=value):
                async def fake(request):
                    return value

                self.events.clear()
                await bounded(self.runtime(fake).handle(delegation(), turn_id="turn_test"))
                self.assertEqual(self.events, [error("invalid_value", "Business result must be non-empty text.")])

    async def exercise_replacement(self, outcome, same_turn=False):
        started, cancelled, cleaned, new_started = (asyncio.Event() for _ in range(4))
        release = self.gate()
        order = []

        async def fake(request):
            if request.delegation_id == "item_old":
                started.set()
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    order.append("cancel")
                    cancelled.set()
                    await release.wait()
                    order.append("cleaned")
                    cleaned.set()
                    if outcome == "cancel":
                        raise
                    if outcome == "error":
                        raise RuntimeError(PRIVATE)
                    return "SYNTHETIC_TEST_ONLY_STALE"
            self.assertTrue(cleaned.is_set(), "replacement started before old cleanup")
            order.append("new")
            new_started.set()
            return RESULT

        runtime = self.runtime(fake)
        old = self.spawn(runtime.handle(delegation("item_old"), turn_id="turn_old"))
        await bounded(started.wait())
        new = self.spawn(runtime.handle(delegation("item_new"), turn_id="turn_old" if same_turn else "turn_new"))
        await bounded(cancelled.wait())
        self.assertFalse(new_started.is_set())
        self.assertFalse(old.done())
        self.assertEqual(self.events, [])
        release.set()
        await bounded(new)
        old_result = (await bounded(asyncio.gather(old, return_exceptions=True)))[0]
        if outcome == "cancel":
            self.assertIsInstance(old_result, asyncio.CancelledError)
        else:
            self.assertIsNone(old_result)
        self.assertEqual(order, ["cancel", "cleaned", "new"])
        self.assertEqual(self.events, [commentary("item_new")])
        self.assertGreater(self.requests[1].generation, self.requests[0].generation)
        self.assertEqual(self.requests[1].session_id, self.requests[0].session_id)
        self.assertEqual(self.requests[1].turn_id, "turn_old" if same_turn else "turn_new")
        self.assertTrue(self.owned[0].done())

    async def test_new_turn_cancels_and_awaits_cleanup(self):
        await self.exercise_replacement("cancel")

    async def test_same_turn_replacement_also_serialized(self):
        await self.exercise_replacement("cancel", same_turn=True)

    async def test_suppressed_cancellation_stale_success_is_fenced(self):
        await self.exercise_replacement("success")

    async def test_suppressed_cancellation_stale_error_is_fenced(self):
        await self.exercise_replacement("error")

    async def exercise_cancelled_cleanup(self, operation, repeat_cancel=False):
        started, cancelled, cleaned = (asyncio.Event() for _ in range(3))
        release = self.gate()

        async def fake(request):
            started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                cancelled.set()
                await release.wait()
                cleaned.set()
                return "SYNTHETIC_TEST_ONLY_STALE"

        runtime = self.runtime(fake)
        original = self.spawn(runtime.handle(delegation(), turn_id="turn_test"))
        await bounded(started.wait())
        if operation == "caller":
            target = original
            target.cancel()
        elif operation == "replacement":
            target = self.spawn(runtime.handle(delegation("item_new"), turn_id="turn_new"))
        else:
            target = self.spawn(runtime.close())
        await bounded(cancelled.wait())
        self.assertFalse(target.done())
        if operation != "caller" or repeat_cancel:
            target.cancel()
        release.set()
        with self.assertRaises(asyncio.CancelledError):
            await bounded(target)
        self.assertTrue(cleaned.is_set())
        self.assertTrue(self.owned[0].done())
        self.assertEqual(self.events, [])
        if original is not target:
            await bounded(original)
        await bounded(runtime.close())
        self.assertEqual(len(self.requests), 1, "cancelled replacement must not start a provider")

    async def test_caller_cancellation_propagates_after_cleanup(self):
        await self.exercise_cancelled_cleanup("caller")

    async def test_repeated_caller_cancellation_does_not_interrupt_cleanup(self):
        await self.exercise_cancelled_cleanup("caller", repeat_cancel=True)

    async def test_caller_cancellation_during_replacement_drains_old_work(self):
        await self.exercise_cancelled_cleanup("replacement")

    async def test_caller_cancellation_during_close_drains_old_work(self):
        await self.exercise_cancelled_cleanup("close")

    async def test_disconnect_pending_and_repeated_close(self):
        started, cancelled, cleaned = (asyncio.Event() for _ in range(3))
        release = self.gate()

        async def fake(request):
            started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                cancelled.set()
                await release.wait()
                cleaned.set()
                return RESULT

        runtime = self.runtime(fake)
        caller = self.spawn(runtime.handle(delegation(), turn_id="turn_test"))
        await bounded(started.wait())
        closing = self.spawn(runtime.close())
        await bounded(cancelled.wait())
        again = self.spawn(runtime.close())
        self.assertFalse(closing.done())
        release.set()
        await bounded(asyncio.gather(closing, again, caller))
        await bounded(runtime.close())
        self.assertTrue(cleaned.is_set())
        self.assertEqual(self.events, [])
        with self.assertRaisesRegex(RuntimeError, r"^Runtime is closed\.$"):
            await bounded(runtime.handle(delegation(), turn_id="turn_new"))
        self.assertEqual(len(self.requests), 1)

    async def test_close_before_use_is_idempotent(self):
        runtime = self.runtime()
        await bounded(runtime.close())
        await bounded(runtime.close())
        with self.assertRaisesRegex(RuntimeError, r"^Runtime is closed\.$"):
            await bounded(runtime.handle({}, turn_id="turn_test"))
        self.assertEqual(self.requests, [])
        self.assertEqual(self.events, [])

    async def test_two_sessions_are_independent_even_with_same_turn_and_delegation_ids(self):
        started_a, started_b, cleaned_a = (asyncio.Event() for _ in range(3))
        release_b = self.gate()
        events_a, events_b = [], []

        async def fake(request):
            if request.session_id == "session_a":
                started_a.set()
                try:
                    await asyncio.Event().wait()
                finally:
                    cleaned_a.set()
            started_b.set()
            await release_b.wait()
            return RESULT

        async def emit_a(event):
            events_a.append(event)

        async def emit_b(event):
            events_b.append(event)

        a = self.runtime(fake, emit_a, "session_a")
        b = self.runtime(fake, emit_b, "session_b")
        caller_a = self.spawn(a.handle(delegation(), turn_id="turn_same"))
        caller_b = self.spawn(b.handle(delegation(), turn_id="turn_same"))
        await bounded(asyncio.gather(started_a.wait(), started_b.wait()))
        await bounded(a.close())
        self.assertTrue(cleaned_a.is_set())
        self.assertFalse(caller_b.done())
        release_b.set()
        await bounded(caller_b)
        self.assertIsInstance((await bounded(asyncio.gather(caller_a, return_exceptions=True)))[0], asyncio.CancelledError)
        self.assertEqual(events_a, [])
        self.assertEqual(events_b, [commentary()])
        self.assertEqual([request.generation for request in self.requests], [1, 1])
        await bounded(b.handle(delegation("item_b2"), turn_id="turn_b2"))
        self.assertEqual(events_b, [commentary(), commentary("item_b2")])
        self.assertEqual(self.requests[-1].generation, 2)

    async def test_callback_failure_propagates_without_retry_or_error_fallback(self):
        async def emit(event):
            self.events.append(event)
            if len(self.events) == 1:
                raise RuntimeError("SYNTHETIC_CALLBACK_FAILURE")

        runtime = self.runtime(emit=emit)
        with self.assertRaisesRegex(RuntimeError, r"^SYNTHETIC_CALLBACK_FAILURE$"):
            await bounded(runtime.handle(delegation(), turn_id="turn_test"))
        self.assertEqual(self.events, [commentary()])
        await bounded(runtime.handle(delegation("item_next"), turn_id="turn_next"))
        self.assertEqual(self.events, [commentary(), commentary("item_next")])

    async def test_callback_cancellation_propagates_without_error(self):
        async def emit(event):
            self.events.append(event)
            raise asyncio.CancelledError

        with self.assertRaises(asyncio.CancelledError):
            await bounded(self.runtime(emit=emit).handle(delegation(), turn_id="turn_test"))
        self.assertEqual(self.events, [commentary()])

    async def test_close_after_callback_handoff_cannot_retract_event(self):
        handed_off, cancelled = asyncio.Event(), asyncio.Event()
        release = self.gate()

        async def emit(event):
            self.events.append(event)
            handed_off.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                cancelled.set()
                await release.wait()

        runtime = self.runtime(emit=emit)
        caller = self.spawn(runtime.handle(delegation(), turn_id="turn_test"))
        await bounded(handed_off.wait())
        closing = self.spawn(runtime.close())
        await bounded(cancelled.wait())
        self.assertEqual(self.events, [commentary()])
        self.assertFalse(closing.done())
        release.set()
        await bounded(asyncio.gather(closing, caller))
        self.assertEqual(self.events, [commentary()])  # no reversal or sent/played receipt

    async def test_provider_cancellation_is_not_converted_to_server_error(self):
        async def fake(request):
            raise asyncio.CancelledError

        with self.assertRaises(asyncio.CancelledError):
            await bounded(self.runtime(fake).handle(delegation(), turn_id="turn_test"))
        self.assertEqual(self.events, [])

    async def test_reentrant_lifecycle_from_callback_fails_without_deadlock(self):
        async def emit(event):
            self.events.append(event)
            await runtime.close()

        runtime = self.runtime(emit=emit)
        with self.assertRaisesRegex(RuntimeError, r"^Lifecycle calls from owned work are not supported\.$"):
            await bounded(runtime.handle(delegation(), turn_id="turn_test"))
        self.assertEqual(self.events, [commentary()])

    async def test_reentrant_lifecycle_from_provider_is_sanitized(self):
        async def fake(request):
            await runtime.handle(delegation(), turn_id="turn_nested")
            return RESULT

        runtime = self.runtime(fake)
        await bounded(runtime.handle(delegation(), turn_id="turn_test"))
        self.assertEqual(self.events, [error("server_error", "Business callable failed.")])
        self.assertEqual(len(self.requests), 1)


    async def test_reused_turn_and_delegation_ids_still_fence_by_generation(self):
        started, cancelled = asyncio.Event(), asyncio.Event()
        release = self.gate()

        async def fake(request):
            if request.generation == 1:
                started.set()
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    cancelled.set()
                    await release.wait()
                    return "SYNTHETIC_TEST_ONLY_STALE"
            return RESULT

        runtime = self.runtime(fake)
        old = self.spawn(runtime.handle(delegation(), turn_id="turn_same"))
        await bounded(started.wait())
        new = self.spawn(runtime.handle(delegation(), turn_id="turn_same"))
        await bounded(cancelled.wait())
        release.set()
        await bounded(asyncio.gather(old, new))
        self.assertEqual(self.events, [commentary()])
        self.assertEqual([request.generation for request in self.requests], [1, 2])

    async def test_cancelled_lock_waiter_does_not_cancel_or_start_work(self):
        started, cancelled, queued = (asyncio.Event() for _ in range(3))
        release = self.gate()

        async def fake(request):
            if request.delegation_id == "item_old":
                started.set()
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    cancelled.set()
                    await release.wait()
                    return RESULT
            return RESULT

        runtime = self.runtime(fake)
        old = self.spawn(runtime.handle(delegation("item_old"), turn_id="turn_old"))
        await bounded(started.wait())
        new = self.spawn(runtime.handle(delegation("item_new"), turn_id="turn_new"))
        await bounded(cancelled.wait())

        async def waiting():
            queued.set()
            await runtime.handle(delegation("item_never"), turn_id="turn_never")

        waiter = self.spawn(waiting())
        await bounded(queued.wait())
        waiter.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await bounded(waiter)
        self.assertFalse(new.done())
        release.set()
        await bounded(asyncio.gather(old, new))
        self.assertEqual([request.delegation_id for request in self.requests], ["item_old", "item_new"])
        self.assertEqual(self.events, [commentary("item_new")])

    async def test_replacement_after_handoff_does_not_pretend_to_retract(self):
        handed_off = asyncio.Event()

        async def emit(event):
            self.events.append(event)
            if event["delegation_id"] == "item_old":
                handed_off.set()
                await asyncio.Event().wait()

        runtime = self.runtime(emit=emit)
        old = self.spawn(runtime.handle(delegation("item_old"), turn_id="turn_old"))
        await bounded(handed_off.wait())
        await bounded(runtime.handle(delegation("item_new"), turn_id="turn_new"))
        result = (await bounded(asyncio.gather(old, return_exceptions=True)))[0]
        self.assertIsInstance(result, asyncio.CancelledError)
        self.assertEqual(self.events, [commentary("item_old"), commentary("item_new")])

    async def test_validation_callback_failure_propagates_without_provider(self):
        async def emit(event):
            self.events.append(event)
            raise RuntimeError("SYNTHETIC_CALLBACK_FAILURE")

        with self.assertRaisesRegex(RuntimeError, r"^SYNTHETIC_CALLBACK_FAILURE$"):
            await bounded(self.runtime(emit=emit).handle({}, turn_id="turn_test"))
        self.assertEqual(self.events, [error("invalid_value", "event.type must be non-empty text.")])
        self.assertEqual(self.requests, [])

    async def test_validation_callback_handoff_is_caller_owned_not_background_work(self):
        handed_off = asyncio.Event()
        release = self.gate()

        async def emit(event):
            self.events.append(event)
            handed_off.set()
            await release.wait()

        runtime = self.runtime(emit=emit)
        caller = self.spawn(runtime.handle({}, turn_id="turn_test"))
        await bounded(handed_off.wait())
        await bounded(runtime.close())
        self.assertFalse(caller.done())
        self.assertEqual(self.owned, [])
        release.set()
        await bounded(caller)
        self.assertEqual(self.events, [error("invalid_value", "event.type must be non-empty text.")])
        self.assertEqual(self.requests, [])

    async def test_raw_unfinished_json_text_is_not_parsed_or_certified(self):
        raw = '{"response":"SYNTHETIC_TEST_ONLY", "actions":['

        async def fake(request):
            return raw

        await bounded(self.runtime(fake).handle(delegation(), turn_id="turn_test"))
        self.assertEqual(self.events, [commentary(content=raw)])


    async def test_wire_metadata_cannot_override_injected_identity(self):
        event = delegation()
        event.update(session_id="SYNTHETIC_WRONG_SESSION", turn_id="SYNTHETIC_WRONG_TURN", generation=999)
        event["delegation"]["generation"] = 999
        await bounded(self.runtime().handle(event, turn_id="turn_python"))
        self.assertEqual(self.requests, [MarioRequest("session_test", "turn_python", "item_test", 1, TASK)])
        self.assertEqual(self.events, [commentary()])


if __name__ == "__main__":
    unittest.main()
