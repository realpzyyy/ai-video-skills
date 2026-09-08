#!/usr/bin/env python3
"""Local behavioral tests; no plugins, cloud services, or user media are touched."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import probe_local as probe


def command_result(payload="", returncode=0, error=None):
    return {"returncode": returncode, "stdout": payload, "stderr": "", "error": error}


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="talking-head-skill-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.media = self.root / "视频 素材.mp4"
        self.media.write_bytes(b"test fixture, never decoded")

    def test_missing_commands_do_not_claim_capabilities(self):
        with patch.object(probe.shutil, "which", return_value=None):
            report = probe.build_report()
        self.assertIsNone(report["production_ready"])
        self.assertFalse(any(item["detected"] for item in report["commands"].values()))
        self.assertTrue(all(item["status"] == "untested" for item in report["agent_capabilities"].values()))

    def test_version_success_is_not_task_success(self):
        with patch.object(probe.shutil, "which", return_value="/tool/ffmpeg"), patch.object(
            probe, "run_command", return_value=command_result("ffmpeg test\nother")
        ):
            item = probe.inventory_command("ffmpeg", ["-version"])
        self.assertEqual(item["version_check"], "passed")
        self.assertEqual(item["task_capability"], "untested")

    def test_existing_broken_executable_is_reported_failed(self):
        with patch.object(probe.shutil, "which", return_value="/tool/node"), patch.object(
            probe, "run_command", return_value=command_result(returncode=None, error="OSError")
        ):
            item = probe.inventory_command("node", ["--version"])
        self.assertTrue(item["detected"])
        self.assertEqual(item["version_check"], "failed")

    def test_remote_media_never_runs_a_command(self):
        with patch.object(probe, "run_command") as run:
            result = probe.inspect_media("https://example.invalid/private.mp4", "/tool/ffprobe")
        self.assertEqual(result["status"], "invalid_input")
        run.assert_not_called()

    def test_missing_file_and_directory_are_not_media(self):
        for path in (self.root / "missing.mp4", self.root):
            with self.subTest(path=str(path)), patch.object(probe, "run_command") as run:
                result = probe.inspect_media(str(path), "/tool/ffprobe")
                self.assertEqual(result["status"], "invalid_input")
                run.assert_not_called()

    def test_existing_file_without_ffprobe_is_unavailable(self):
        self.assertEqual(probe.inspect_media(str(self.media), None)["status"], "unavailable")

    def test_special_filename_is_one_argument_without_shell(self):
        special = self.root / "素材 $(not-a-command) ;.mp4"
        special.write_bytes(b"fixture")
        fake = {"streams": [{"codec_type": "video", "width": 544, "height": 960,
                             "avg_frame_rate": "3850000/160417"}], "format": {"duration": "160.417"}}
        with patch.object(probe, "run_command", return_value=command_result(json.dumps(fake))) as run:
            result = probe.inspect_media(str(special), "/tool/ffprobe")
        argv = run.call_args.args[0]
        self.assertEqual(argv[-1], str(special.resolve()))
        self.assertEqual(argv[argv.index("-protocol_whitelist") + 1], "file,pipe")
        self.assertEqual(result["status"], "metadata_verified")
        self.assertEqual(result["metadata"]["streams"][0]["avg_frame_rate"], "3850000/160417")
        self.assertFalse(result["has_audio"])

    def test_audio_only_does_not_pass_as_video(self):
        with patch.object(probe, "run_command", return_value=command_result(
            json.dumps({"streams": [{"codec_type": "audio"}]}))):
            result = probe.inspect_media(str(self.media), "/tool/ffprobe")
        self.assertEqual(result["status"], "needs_video_source")

    def test_invalid_json_and_streams_fail(self):
        for payload in ("not-json", "[]", "{}", '{"streams":[null]}'):
            with self.subTest(payload=payload), patch.object(
                probe, "run_command", return_value=command_result(payload)
            ):
                self.assertEqual(probe.inspect_media(str(self.media), "/tool/ffprobe")["status"], "failed")

    def test_timeout_is_bounded_error(self):
        with patch.object(probe.subprocess, "run", side_effect=subprocess.TimeoutExpired(["x"], 1)):
            self.assertEqual(probe.run_command(["x"], timeout=1)["error"], "TimeoutExpired")

    def test_runner_does_not_enable_shell(self):
        completed = subprocess.CompletedProcess(["x"], 0, "ok", "")
        with patch.object(probe.subprocess, "run", return_value=completed) as run:
            result = probe.run_command(["x", "$(unused)"])
        self.assertEqual(result["stdout"], "ok")
        self.assertFalse(run.call_args.kwargs.get("shell", False))

    def test_output_is_unicode_json_and_never_overwrites(self):
        output = self.root / "检测.json"
        probe.emit_report({"status": "待人工看图"}, str(output))
        first = output.read_bytes()
        with self.assertRaises(FileExistsError):
            probe.emit_report({"status": "must not replace"}, str(output))
        self.assertEqual(output.read_bytes(), first)
        self.assertEqual(json.loads(first)["status"], "待人工看图")

    def test_cli_failure_still_emits_diagnostic_report(self):
        with patch.object(probe, "build_report", return_value={"media": {"status": "failed"}}), contextlib.redirect_stdout(io.StringIO()) as stdout:
            code = probe.main(["--media", str(self.media)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stdout.getvalue())["media"]["status"], "failed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
