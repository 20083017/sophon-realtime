"""Synthetic completed-reply fixtures only: no model, gateway or audio service."""
import asyncio
import base64
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import FrozenInstanceError
import io
import json
import traceback
import unittest
import wave

from live.sophon_live.mario_reply import (
    MarioReply, MarioReplyError, ScriptJump, parse_mario_reply,
)
from live.sophon_live.mario_runtime import MarioRuntime


TEXT = "SYNTHETIC_OK"
PRIVATE = "SYNTHETIC_PRIVATE_PAYLOAD_NOT_FOR_ERRORS" * 50


def jump(target="Script_4"):
    return {"skill": "script_jump", "params": {"target_script": target}}


def document(response=TEXT, actions=None):
    return json.dumps({"response": response, "actions": [] if actions is None else actions},
                      ensure_ascii=False)


class MarioReplyTests(unittest.TestCase):
    def parse(self, content, **overrides):
        options = {"finish_reason": "stop", "allowed_scripts": {"Script_1", "Script_4"},
                   "current_script": "Script_1"}
        options.update(overrides)
        return parse_mario_reply(content, **options)

    def reject(self, content, **overrides):
        with self.assertRaises(MarioReplyError) as caught:
            self.parse(content, **overrides)
        self.assertLessEqual(len(str(caught.exception)), 120)
        return caught.exception

    def test_schema_baseline_accepts_exact_response_and_empty_actions(self):
        self.assertEqual(self.parse(document()), MarioReply(TEXT, ()))

    def test_schema_jump_is_metadata_not_applied_state(self):
        allowed = {"Script_1", "Script_4"}
        parsed = self.parse(document("SYNTHETIC_JUMP_REPLY", [jump()]), allowed_scripts=allowed)
        self.assertEqual(parsed, MarioReply("SYNTHETIC_JUMP_REPLY",
                                          (ScriptJump("Script_1", "Script_4", False),)))
        self.assertEqual(allowed, {"Script_1", "Script_4"})
        self.assertFalse(hasattr(parsed.actions[0], "applied"))
        self.assertFalse(hasattr(parsed.actions[0], "executed"))

    def test_schema_mention_without_action_never_infers_a_jump(self):
        response = "SYNTHETIC: script_jump is a term; remain in Script_1."
        self.assertEqual(self.parse(document(response)), MarioReply(response, ()))

    def test_three_plain_prompt_contamination_shapes_reject(self):
        fixtures = [
            "Thinking Process:\nSYNTHETIC reasoning\n" + document(),
            "SYNTHETIC example: " + document(actions=[jump()]) + "\nSYNTHETIC final: " + document(),
            "```json\n" + document("SYNTHETIC explanation of script_jump") + "\n```",
        ]
        for content in fixtures:
            with self.subTest(content=content[:30]):
                self.reject(content)

    def test_finish_reason_must_explicitly_be_stop(self):
        for reason in (None, "", "length", "tool_calls", "content_filter", "STOP", " stop", 0, True, []):
            with self.subTest(reason=reason):
                self.reject(document(), finish_reason=reason)
        with self.assertRaises(TypeError):
            parse_mario_reply(document(), allowed_scripts={"Script_1"}, current_script="Script_1")

    def test_complete_json_is_still_rejected_when_truncated_completion_reported(self):
        self.reject(document(actions=[jump()]), finish_reason="length")

    def test_content_must_be_text_not_envelope_or_bytes(self):
        for content in (None, b'{"response":"x","actions":[]}', {}, [], 0, True):
            with self.subTest(content_type=type(content).__name__):
                self.reject(content)

    def test_malformed_trailing_bom_and_fullwidth_structure_reject(self):
        fixtures = ["", " ", "null", "[]", "true", '"text"',
                    '{"response":"SYNTHETIC", "actions":[',
                    document() + document(), document() + " trailing",
                    "﻿" + document(),
                    '{"response"："SYNTHETIC","actions":[]}',
                    '{"response":"SYNTHETIC"，"actions":[]}']
        for content in fixtures:
            with self.subTest(content=content[:35]):
                self.reject(content)

    def test_json_whitespace_allowed_without_changing_response(self):
        self.assertEqual(self.parse(" \r\n\t" + document("  SYNTHETIC  ") + "\n ").response,
                         "  SYNTHETIC  ")

    def test_duplicate_keys_at_every_level_reject_even_identical_values(self):
        fixtures = [
            '{"response":"x","response":"x","actions":[]}',
            r'{"response":"x","response":"x","actions":[]}',
            '{"response":"x","actions":[],"actions":[]}',
            '{"response":"x","actions":[{"skill":"script_jump","skill":"script_jump",'
            '"params":{"target_script":"Script_4"}}]}',
            '{"response":"x","actions":[{"skill":"script_jump",'
            '"params":{"target_script":"Script_4","target_script":"Script_4"}}]}',
        ]
        for content in fixtures:
            with self.subTest(content=content[:50]):
                self.reject(content)

    def test_nonfinite_constants_and_numeric_overflow_reject(self):
        for number in ("NaN", "Infinity", "-Infinity", "1e9999"):
            with self.subTest(number=number):
                self.reject('{"response":' + number + ',"actions":[]}')
                self.reject('{"response":"x","actions":[' + number + ']}')

    def test_oversized_integer_decoder_failure_is_a_sanitized_validation_error(self):
        # Newer Python decoders impose an integer digit limit; older ones still
        # reject the decoded integer at our schema boundary.
        self.reject('{"response":"x","actions":[{"skill":"script_jump",'
                    '"params":{"target_script":' + "9" * 5000 + '}}]}')

    def test_excessive_nesting_has_sanitized_validation_error(self):
        self.reject('{"response":"x","actions":' + "[" * 2048 + "0" + "]" * 2048 + "}")

    def test_root_requires_exact_response_and_actions_fields(self):
        for obj in ({}, {"response": TEXT}, {"actions": []},
                    {"response": TEXT, "actions": [], "reasoning": PRIVATE},
                    {"response": TEXT, "actions": [], "session_id": "SYNTHETIC_SESSION"}):
            with self.subTest(keys=list(obj)):
                self.reject(json.dumps(obj))

    def test_nonblank_string_response_required_in_this_bounded_version(self):
        for response in (None, "", " \n\t", 1, False, [], {}):
            with self.subTest(response_type=type(response).__name__):
                self.reject(document(response))
        self.reject(document("", [jump()]))

    def test_actions_must_be_zero_or_one_object(self):
        for actions in (None, {}, "script_jump", True, 0, [None], ["script_jump"],
                        [jump(), jump()], [jump(), jump("Script_1")]):
            with self.subTest(actions_type=type(actions).__name__):
                self.reject(json.dumps({"response": TEXT, "actions": actions}))

    def test_action_and_params_require_exact_fields(self):
        fixtures = [
            {}, {"skill": "script_jump"}, {"params": {"target_script": "Script_4"}},
            {"skill": "script_jump", "params": None},
            {"skill": "script_jump", "params": {}},
            {"skill": "script_jump", "params": {"target_script": "Script_4", "extra": PRIVATE}},
            {"skill": "script_jump", "params": {"target_script": "Script_4"}, "applied": True},
        ]
        for action in fixtures:
            with self.subTest(keys=list(action)):
                self.reject(document(actions=[action]))

    def test_external_and_unknown_skills_are_explicitly_unsupported(self):
        for skill in ("skill_navigate", "navigate", "screen_cast", "voice_play", "SCRIPT_JUMP", None, 0):
            with self.subTest(skill=skill):
                self.reject(document(actions=[{"skill": skill, "params": {"target_script": "Script_4"}}]))

    def test_unknown_or_invalid_targets_reject_without_normalization(self):
        for target in ("Script_999", "script_4", " Script_4", "Script_4 ", "", None,
                       True, 4, [], "Script_4\x00"):
            with self.subTest(target_type=type(target).__name__):
                self.reject(document(actions=[jump(target)]))

    def test_caller_context_is_required_even_without_actions(self):
        for current in (None, "", " Script_1", "Script_1\n", True, [], "Script_999"):
            with self.subTest(current_type=type(current).__name__):
                self.reject(document(), current_script=current)
        for allowed in (None, "Script_1", b"Script_1", {}, [], set(), {1}, {""},
                        {"Script_1", "bad id"}, (name for name in ("Script_1",))):
            with self.subTest(allowed_type=type(allowed).__name__):
                self.reject(document(), allowed_scripts=allowed)

    def test_context_accepts_collections_without_hardcoded_script_names(self):
        for allowed in (["Scene_A", "Scene_B"], ("Scene_A", "Scene_B"),
                        frozenset({"Scene_A", "Scene_B"})):
            with self.subTest(allowed_type=type(allowed).__name__):
                parsed = self.parse(document(actions=[jump("Scene_B")]),
                                    allowed_scripts=allowed, current_script="Scene_A")
                self.assertEqual(parsed.actions, (ScriptJump("Scene_A", "Scene_B", False),))

    def test_same_target_is_explicit_noop_metadata(self):
        parsed = self.parse(document(actions=[jump("Script_1")]))
        self.assertEqual(parsed.actions, (ScriptJump("Script_1", "Script_1", True),))

    def test_reply_and_action_metadata_are_immutable(self):
        parsed = self.parse(document(actions=[jump()]))
        self.assertIsInstance(parsed.actions, tuple)
        with self.assertRaises(FrozenInstanceError):
            parsed.response = "changed"
        with self.assertRaises(FrozenInstanceError):
            parsed.actions[0].target_script = "changed"

    def test_sound_tags_unicode_and_utf8_bytes_are_preserved(self):
        text = "  SYNTHETIC [laughter]\n全角；：= café 😀\t  "
        parsed = self.parse(document(text))
        self.assertEqual(parsed.response, text)
        self.assertEqual(parsed.response.encode("utf-8"), text.encode("utf-8"))
        self.assertIn("[laughter]", parsed.response)

    def test_unpaired_surrogates_reject_but_valid_unicode_escapes_accept(self):
        self.reject(r'{"response":"\ud800","actions":[]}')
        self.assertEqual(self.parse(r'{"response":"😀","actions":[]}').response, "😀")
        self.reject(document(), allowed_scripts={"Script_1", "\ud800"})

    def test_tag_and_flash_text_fixtures_keep_their_documented_distinction(self):
        # Synthetic examples of README HTTP text handling, not real backend output.
        tag = self.parse(document("SYNTHETIC hello"))
        flash = self.parse(document("SYNTHETIC [laughter] hello"))
        self.assertEqual(tag.response, "SYNTHETIC hello")
        self.assertEqual(flash.response, "SYNTHETIC [laughter] hello")
        self.assertNotEqual(tag.response, flash.response)

    def test_protocol_envelopes_cannot_be_misread_as_business_replies(self):
        native_update = {"type": "session.update", "session": {
            "input_audio_format": "pcm_f32le",
            "extra_body": {"auto_response": True, "language": "en"}}}
        native_append = {"type": "input_audio_buffer.append", "audio": "AAAAAA==",
                         "format": "pcm_f32le", "sample_rate_hz": 16000}
        live_append = {"type": "session.input_audio.append", "audio": "AAA="}
        live_start = {"type": "session.start", "session": {
            "audio": {"format": {"type": "audio/pcm", "rate": 16000}}}}
        live_commentary = {"type": "session.commentary.append", "delegation_id": "item_synthetic",
                           "content": document()}
        for event in (native_update, native_append, live_append, live_start, live_commentary):
            with self.subTest(type=event["type"]):
                self.reject(json.dumps(event))

    def test_http_audio_sse_fixtures_are_not_completed_mario_json(self):
        # Construct a tiny explicitly synthetic WAV; no existing recordings used.
        out = io.BytesIO()
        with wave.open(out, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(24000)
            wav.writeframes(b"\x00\x00" * 24)
        audio = base64.b64encode(out.getvalue()).decode("ascii")
        request = {"modalities": ["text", "audio"], "messages": [{"role": "user", "content": [
            {"type": "text", "text": "<|audio|>"},
            {"type": "input_audio", "input_audio": {"data": audio, "format": "wav"}},
        ]}]}
        chunk = {"modality": "audio", "choices": [{"delta": {"content": audio}}]}
        for content in (json.dumps(request), json.dumps(chunk), "data: " + json.dumps(chunk),
                        "data: " + document(), "data: [DONE]"):
            with self.subTest(content=content[:35]):
                self.reject(content)

    def test_transport_completion_envelope_is_not_implicitly_unwrapped(self):
        envelope = {"choices": [{"message": {"content": document()}, "finish_reason": "stop"}]}
        self.reject(json.dumps(envelope))

    def test_decoder_and_unicode_errors_do_not_chain_payload_bearing_exceptions(self):
        for content in (PRIVATE + document(), document(chr(0xD800))):
            with self.subTest(content_length=len(content)):
                error = self.reject(content)
                self.assertIsNone(error.__context__)
                self.assertIsNone(error.__cause__)

    def test_validation_is_silent_and_errors_never_echo_payload(self):
        fixtures = [PRIVATE + document(), document(PRIVATE, [jump(PRIVATE)]),
                    document(PRIVATE, [{"skill": PRIVATE, "params": {}}]),
                    '{"response":"' + PRIVATE + '","response":"x","actions":[]}']
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            for content in fixtures:
                error = self.reject(content)
                rendered = "".join(traceback.format_exception(type(error), error, error.__traceback__))
                self.assertNotIn(PRIVATE, str(error) + repr(error) + rendered)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")


class ReplyRuntimeBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def test_explicit_provider_returns_only_validated_response(self):
        fixture = document("SYNTHETIC_VALIDATED_TEXT", [jump()])
        events = []
        metadata = []

        async def business(request):
            parsed = parse_mario_reply(fixture, finish_reason="stop",
                                       allowed_scripts={"Script_1", "Script_4"}, current_script="Script_1")
            metadata.extend(parsed.actions)
            return parsed.response

        async def emit(event):
            events.append(event)

        runtime = MarioRuntime("session_synthetic", business, emit)
        try:
            await asyncio.wait_for(runtime.handle({"type": "session.delegation.created", "delegation": {
                "id": "item_synthetic", "type": "delegation", "target": "client", "task": "SYNTHETIC_TASK"}},
                turn_id="turn_synthetic"), 5)
        finally:
            await asyncio.wait_for(runtime.close(), 5)
        self.assertEqual(events, [{"type": "session.commentary.append",
                                  "delegation_id": "item_synthetic", "content": "SYNTHETIC_VALIDATED_TEXT"}])
        self.assertEqual(metadata, [ScriptJump("Script_1", "Script_4", False)])

    async def test_rejected_content_cannot_produce_commentary_success(self):
        events = []

        async def business(request):
            return parse_mario_reply(PRIVATE + document(), finish_reason="stop",
                                     allowed_scripts={"Script_1"}, current_script="Script_1").response

        async def emit(event):
            events.append(event)

        runtime = MarioRuntime("session_synthetic", business, emit)
        try:
            await asyncio.wait_for(runtime.handle({"type": "session.delegation.created", "delegation": {
                "id": "item_synthetic", "type": "delegation", "target": "client", "task": "SYNTHETIC_TASK"}},
                turn_id="turn_synthetic"), 5)
        finally:
            await asyncio.wait_for(runtime.close(), 5)
        self.assertEqual(events, [{"type": "error", "error": {
            "code": "server_error", "message": "Business callable failed."}}])
        self.assertNotIn(PRIVATE, json.dumps(events))


if __name__ == "__main__":
    unittest.main()
