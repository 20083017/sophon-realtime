"""Strict completed Mario reply validation, without inference or action execution.

This detached boundary supports nonblank speech and at most one script_jump.
It does not unwrap API/SSE envelopes, salvage model prose, or mutate Mario state.
"""
from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
import json


class MarioReplyError(ValueError):
    """A fixed, payload-free validation error, not a business execution result."""


@dataclass(frozen=True)
class ScriptJump:
    """Validated intent only; even a non-noop transition has not been applied."""

    source_script: str
    target_script: str
    is_noop: bool


@dataclass(frozen=True)
class MarioReply:
    response: str
    actions: tuple[ScriptJump, ...]


def _identifier(value: object) -> bool:
    if (not isinstance(value, str) or not value
            or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in value)):
        return False
    try:
        value.encode("utf-8")
    except UnicodeError:
        return False
    return True


def _object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    obj: dict[str, object] = {}
    for key, value in pairs:
        if key in obj:
            raise MarioReplyError("Reply JSON contains duplicate keys.")
        obj[key] = value
    return obj


def _constant(value: str) -> None:
    raise MarioReplyError("Reply JSON contains a nonfinite constant.")


def parse_mario_reply(
    content: str, *, finish_reason: str, allowed_scripts: Collection[str], current_script: str,
) -> MarioReply:
    """Validate complete content using explicit caller-owned script context.

    Only finish_reason='stop' is supported. Script context is required even for
    empty actions. A response is kept verbatim; actions are immutable metadata,
    not executed commands or receipts. All rejected inputs have fixed messages.
    """
    if (not isinstance(allowed_scripts, Collection)
            or isinstance(allowed_scripts, (str, bytes, bytearray, Mapping))):
        raise MarioReplyError("Allowed scripts must be a non-empty collection of identifiers.")
    names = tuple(allowed_scripts)
    if not names or not all(_identifier(name) for name in names):
        raise MarioReplyError("Allowed scripts must be a non-empty collection of identifiers.")
    allowed = frozenset(names)
    if not _identifier(current_script) or current_script not in allowed:
        raise MarioReplyError("Current script must be an allowed identifier.")
    if not isinstance(finish_reason, str) or finish_reason != "stop":
        raise MarioReplyError("Completion must finish with stop.")
    if not isinstance(content, str) or not content.strip():
        raise MarioReplyError("Reply content must be non-empty JSON text.")

    invalid_json = False
    try:
        obj = json.loads(content, object_pairs_hook=_object, parse_constant=_constant)
    except MarioReplyError:
        raise
    except (ValueError, RecursionError):
        # Includes JSON syntax errors and interpreter-specific integer limits.
        invalid_json = True
    # Raise outside the decoder exception handler: do not retain/chain its raw
    # content-bearing JSONDecodeError into a validation error or traceback.
    if invalid_json:
        raise MarioReplyError("Reply JSON is invalid.")
    if not isinstance(obj, dict) or set(obj) != {"response", "actions"}:
        raise MarioReplyError("Reply must contain exactly response and actions.")
    response = obj["response"]
    if not isinstance(response, str) or not response.strip():
        raise MarioReplyError("Reply response must be nonblank text.")
    invalid_unicode = False
    try:
        response.encode("utf-8")
    except UnicodeError:
        invalid_unicode = True
    if invalid_unicode:
        raise MarioReplyError("Reply response must be valid Unicode text.")
    actions = obj["actions"]
    if not isinstance(actions, list) or len(actions) > 1:
        raise MarioReplyError("Reply actions must be an array with at most one action.")
    if not actions:
        return MarioReply(response, ())

    action = actions[0]
    if not isinstance(action, dict) or set(action) != {"skill", "params"}:
        raise MarioReplyError("Action must contain exactly skill and params.")
    if action["skill"] != "script_jump":
        raise MarioReplyError("Unsupported action; only script_jump metadata is allowed.")
    params = action["params"]
    if not isinstance(params, dict) or set(params) != {"target_script"}:
        raise MarioReplyError("Script jump params must contain exactly target_script.")
    target = params["target_script"]
    if not _identifier(target) or target not in allowed:
        raise MarioReplyError("Script jump target must be an allowed identifier.")
    return MarioReply(response, (ScriptJump(current_script, target, target == current_script),))
