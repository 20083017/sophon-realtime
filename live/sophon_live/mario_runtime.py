"""Transport-neutral business-text mapping, explicitly constructed per session.

No gateway/Mario imports, transport, history, actions or inference are provided.
The injected callables must be async and cancellation-cooperative. Use on one
asyncio event loop; the caller must await handle() and close() on disconnect.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable


@dataclass(frozen=True)
class MarioRequest:
    """Validated local identity and text; generation is never a wire field."""

    session_id: str
    turn_id: str
    delegation_id: str
    generation: int
    task: str


BusinessCallable = Callable[[MarioRequest], Awaitable[str]]
EventCallback = Callable[[dict[str, object]], Awaitable[None]]


def _identifier(value: object) -> bool:
    return (isinstance(value, str) and bool(value)
            and not any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in value))


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _error(code: str, message: str) -> dict[str, object]:
    return {"type": "error", "error": {"code": code, "message": message}}


class _InvalidInput(Exception):
    def __init__(self, message: str, code: str = "invalid_value"):
        super().__init__(message)
        self.code = code


def _parse(event: object, turn_id: str) -> tuple[str, str]:
    # All rejection messages are fixed, not interpolated from input.
    if not _identifier(turn_id):
        raise _InvalidInput("turn_id must be a non-empty identifier.")
    if not isinstance(event, dict):
        raise _InvalidInput("Event must be a dictionary.")
    if not _text(event.get("type")):
        raise _InvalidInput("event.type must be non-empty text.")
    if event["type"] != "session.delegation.created":
        raise _InvalidInput("Unsupported event type.", "invalid_request_error")
    delegation = event.get("delegation")
    if not isinstance(delegation, dict):
        raise _InvalidInput("event.delegation must be a dictionary.")
    if not _identifier(delegation.get("id")):
        raise _InvalidInput("delegation.id must be a non-empty identifier.")
    if delegation.get("type") != "delegation":
        raise _InvalidInput("delegation.type must be delegation.")
    if delegation.get("target") != "client":
        raise _InvalidInput("delegation.target must be client.")
    if not _text(delegation.get("task")):
        raise _InvalidInput("delegation.task must be non-empty text.")
    return delegation["id"], delegation["task"]


class MarioRuntime:
    """Own at most one business/callback task for one explicitly injected session.

    A valid handle replaces prior work, even within the same turn. Invalid input
    only hands an error to the callback in the caller's coroutine, leaving valid
    work alone. Neither returning None nor callback completion is a send/playback
    receipt. Lifecycle calls from owned business/callback work are unsupported.
    """

    def __init__(self, session_id: str, business: BusinessCallable, emit: EventCallback):
        if not _identifier(session_id):
            raise ValueError("session_id must be a non-empty identifier.")
        if not callable(business) or not callable(emit):
            raise TypeError("business and emit must be callable.")
        self._session_id = session_id
        self._business: BusinessCallable | None = business
        self._emit: EventCallback | None = emit
        self._lock = asyncio.Lock()
        self._generation = 0
        self._closed = False
        self._current: MarioRequest | None = None
        self._task: asyncio.Task[None] | None = None

    def _check_lifecycle_caller(self) -> None:
        if asyncio.current_task() is self._task:
            raise RuntimeError("Lifecycle calls from owned work are not supported.")

    def _invalidate(self) -> None:
        # Called under the lifecycle lock, BEFORE cancellation can run user code.
        self._generation += 1
        self._current = None

    def is_active(self, request: MarioRequest) -> bool:
        """Same-loop pre-commit identity guard for explicitly injected business."""
        return (not self._closed and self._current is request
                and request.generation == self._generation
                and request.session_id == self._session_id)

    def invalidate(self) -> None:
        """Fence synchronously before an owning adapter schedules cancellation.

        Does not replace awaited cleanup: the owner still drains handle/close.
        Use only on the runtime's event loop, never from an owned callback.
        """
        self._check_lifecycle_caller()
        self._invalidate()

    async def handle(self, event: object, *, turn_id: str) -> None:
        """Await local work, or an error handoff. Concurrent valid calls replace.

        CancelledError propagates after owned cooperative cleanup. Superseded
        calls may raise CancelledError, or return None if the business callable
        suppressed cancellation; in neither case is stale output handed off.
        """
        self._check_lifecycle_caller()
        if self._closed:
            raise RuntimeError("Runtime is closed.")
        try:
            delegation_id, text = _parse(event, turn_id)
        except _InvalidInput as exc:
            # No suspension between the closed check and this error handoff.
            # This callback is awaited by the caller, not a background task.
            emit = self._emit
            assert emit is not None
            await emit(_error(exc.code, str(exc)))
            return

        async with self._lock:
            if self._closed:
                raise RuntimeError("Runtime is closed.")
            self._invalidate()
            await self._stop_owned()
            request = MarioRequest(self._session_id, turn_id, delegation_id, self._generation, text)
            self._current = request
            task = asyncio.create_task(self._run(request), name="mario-runtime")
            self._task = task
        try:
            # Shield prevents caller cancellation from reaching business code
            # before we invalidate its identity under the lifecycle lock.
            await asyncio.shield(task)
        except asyncio.CancelledError:
            await self._cancel_if_owned(task)
            raise
        finally:
            async with self._lock:
                if self._task is task and task.done():
                    self._task = None
                    self._current = None

    async def _run(self, request: MarioRequest) -> None:
        business, emit = self._business, self._emit
        assert business is not None and emit is not None
        try:
            result = await business(request)
        except asyncio.CancelledError:
            raise
        except Exception:
            # Never format/log a provider exception or include task/history/audio.
            event = _error("server_error", "Business callable failed.")
        else:
            if not _text(result):
                event = _error("invalid_value", "Business result must be non-empty text.")
            else:
                event = {"type": "session.commentary.append",
                         "delegation_id": request.delegation_id, "content": result}

        # Identity of the frozen request fences session, turn and delegation;
        # generation also fences cancellation-suppressing and delayed providers.
        # No await between this fence and callback handoff. After handoff we
        # cannot retract a send/effect. Callback failures propagate, never retry.
        if (not self._closed and self._current is request
                and request.session_id == self._session_id
                and request.generation == self._generation):
            await emit(event)

    async def _stop_owned(self) -> None:
        """Under lock: cancel once, drain despite caller cancellation, release."""
        task = self._task
        if task is None:
            return
        task.cancel()
        interrupted = False
        while not task.done():
            try:
                # wait() does not propagate the owned task's CancelledError and
                # does not forward cancellation to it during cooperative cleanup.
                await asyncio.wait({task})
            except asyncio.CancelledError:
                interrupted = True
        if not task.cancelled():
            task.exception()  # retrieve, but do not re-emit a prior callback failure
        self._task = None
        self._current = None
        if interrupted:
            raise asyncio.CancelledError

    async def _cancel_if_owned(self, task: asyncio.Task[None]) -> None:
        # The caller is already propagating CancelledError. Repeated cancellation
        # must not abandon the lock wait or interrupt the owned cleanup.
        while True:
            try:
                async with self._lock:
                    if self._task is task:
                        self._invalidate()
                        await self._stop_owned()
                return
            except asyncio.CancelledError:
                continue

    async def close(self) -> None:
        """Idempotently invalidate/cancel/drain; propagate cancellation afterward.

        No forced timeout: an uncooperative callable cannot be safely terminated.
        A cancelled attempt to acquire the lifecycle lock has not closed anything.
        """
        self._check_lifecycle_caller()
        async with self._lock:
            if self._closed:
                return
            self._closed = True
            self._invalidate()
            try:
                await self._stop_owned()
            finally:
                self._business = None
                self._emit = None
