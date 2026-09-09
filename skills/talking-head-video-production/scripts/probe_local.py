#!/usr/bin/env python3
"""Read-only local inventory, not a model/plugin/production-quality validator."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from setup_runtime import cache_root


COMMANDS = {
    "ffmpeg": ["-version"],
    "ffprobe": ["-version"],
    "node": ["--version"],
}
NONLOCAL_CAPABILITIES = (
    "transcribe", "image_inspect", "audio_review", "image_generate",
    "graphic_author", "render_composite", "person_segment", "asset_access",
)


def run_command(argv, timeout=12):
    """No shell, credentials, downloads, or automatic installation."""
    try:
        result = subprocess.run(
            argv, capture_output=True, text=True, timeout=timeout,
            check=False, encoding="utf-8", errors="replace",
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "error": None,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"returncode": None, "stdout": "", "stderr": "",
                "error": type(exc).__name__}


def inventory_command(name, version_args, explicit=None):
    executable = explicit or shutil.which(name)
    item = {"name": name, "path": executable, "detected": bool(executable),
            "version_check": "not_run", "version_line": None,
            "task_capability": "untested"}
    if executable:
        result = run_command([executable, *version_args])
        item["version_check"] = "passed" if result["returncode"] == 0 else "failed"
        lines = (result["stdout"] or result["stderr"]).splitlines()
        item["version_line"] = lines[0][:300] if lines else None
        if result["error"]:
            item["error"] = result["error"]
    return item


def inspect_media(media, ffprobe_path):
    if media is None:
        return {"status": "not_requested"}
    # Local files only; never fetch a URL as a side effect of preflight.
    if "://" in media:
        return {"status": "invalid_input", "reason": "local_file_required"}
    path = Path(media).expanduser().resolve()
    if not path.is_file():
        return {"status": "invalid_input", "path": str(path),
                "reason": "not_a_readable_regular_file"}
    if not ffprobe_path:
        return {"status": "unavailable", "path": str(path),
                "reason": "ffprobe_not_found", "exists": True}
    result = run_command([
        ffprobe_path, "-v", "error", "-protocol_whitelist", "file,pipe",
        "-show_entries",
        "format=duration,format_name:stream=index,codec_type,codec_name,width,height,avg_frame_rate,r_frame_rate,sample_rate,channels",
        "-of", "json", "-i", str(path),
    ], timeout=25)
    if result["returncode"] != 0:
        return {"status": "failed", "path": str(path),
                "reason": result["error"] or "ffprobe_failed",
                "detail": result["stderr"][:1200]}
    try:
        data = json.loads(result["stdout"])
        if not isinstance(data, dict) or not isinstance(data.get("streams"), list):
            raise ValueError("missing streams")
    except (json.JSONDecodeError, ValueError, TypeError):
        return {"status": "failed", "path": str(path),
                "reason": "invalid_ffprobe_response"}
    streams = data["streams"]
    if not all(isinstance(stream, dict) for stream in streams):
        return {"status": "failed", "path": str(path),
                "reason": "invalid_ffprobe_streams"}
    has_video = any(stream.get("codec_type") == "video" for stream in streams)
    has_audio = any(stream.get("codec_type") == "audio" for stream in streams)
    return {
        "status": "metadata_verified" if has_video else "needs_video_source",
        "path": str(path), "has_video": has_video, "has_audio": has_audio,
        "metadata": data,
        "notes": [
            "Metadata read does not prove full decode, playback, quality, or permissions for cloud upload.",
            "Frame-rate values are reported as received; this probe does not normalize VFR or infer edit timecodes.",
        ],
    }


def build_report(media=None, runtime_report=None):
    saved = {}
    if runtime_report:
        saved = json.loads(Path(runtime_report).read_text(encoding='utf-8'))
        if saved.get('schema_version') != 1 or not isinstance(saved.get('commands'), dict):
            raise ValueError('Invalid runtime report')
    commands = {name: inventory_command(name, args, (saved.get('commands', {}).get(name) or {}).get('path'))
                for name, args in COMMANDS.items()}
    return {
        "schema_version": "1.0.0", "kind": "local_environment_probe",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "environment": {"system": platform.system(), "release": platform.release(),
                        "machine": platform.machine(), "python": platform.python_version()},
        "commands": commands,
        "runtime_report": str(runtime_report) if runtime_report else None,
        "media": inspect_media(media, commands["ffprobe"]["path"]),
        "agent_capabilities": {name: {"status": "untested",
            "reason": "requires_current_agent_or_provider_evidence"}
            for name in NONLOCAL_CAPABILITIES},
        "production_ready": None,
        "limits": [
            "Does not discover host plugins, authentication, image understanding or audio-review ability.",
            "A detected executable is not an end-to-end production or visual-quality test.",
            "No network, package installation, model download, media rendering, or credential reads are performed.",
        ],
    }


def emit_report(report, output=None):
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if output:
        # Parent must exist; an old report is never silently overwritten.
        with Path(output).expanduser().open("x", encoding="utf-8") as handle:
            handle.write(payload)
    else:
        sys.stdout.write(payload)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--media", help="An explicitly provided local video file")
    parser.add_argument("--output", help="New JSON report path; existing files are refused")
    parser.add_argument("--runtime-report", help="Setup report with actual executable paths; defaults to the local managed report when present")
    args = parser.parse_args(argv)
    try:
        saved = args.runtime_report or (cache_root() / 'runtime-report.json')
        if args.runtime_report and not Path(saved).is_file():
            raise ValueError('Explicit runtime report does not exist')
        report = build_report(args.media, saved if Path(saved).is_file() else None)
        emit_report(report, args.output)
    except (OSError, ValueError) as exc:
        print(f"Cannot read input or create report: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    return 0 if report["media"]["status"] in ("not_requested", "metadata_verified") else 2


if __name__ == "__main__":
    raise SystemExit(main())
