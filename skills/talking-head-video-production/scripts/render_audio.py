#!/usr/bin/env python3
"""Render reviewed keep-segments from a zero-based PCM16 WAV; no ASR or video.

Usage: render_audio.py --source-wav source.wav --edl edits.json --output-dir new-dir
EDL: {"schema_version":1,"timebase":"source_seconds_from_zero","source_id":"s1",
      "timeline_revision":"audio-v1","segments":[{"start":0,"end":2,"text":"..."}]}
Only use after source audio/video time origins have been verified. The default
4 ms crossfade is configurable (0–20 ms), not a guarantee of natural speech.
"""
import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import wave


def finite_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(name + ' must be a finite number')
    return value


def plan_timeline(edl, rate, total_frames, fade_ms=4, allow_reorder=False):
    if edl.get('schema_version') != 1 or edl.get('timebase') != 'source_seconds_from_zero':
        raise ValueError('Unsupported EDL schema or unverified timebase')
    for field in ('source_id', 'timeline_revision'):
        if not isinstance(edl.get(field), str) or not edl[field].strip():
            raise ValueError('Missing ' + field)
    fade_ms = finite_number(fade_ms, 'crossfade_ms')
    if not 0 <= fade_ms <= 20:
        raise ValueError('crossfade_ms must be between 0 and 20')
    if not isinstance(edl.get('segments'), list) or not edl['segments']:
        raise ValueError('Need at least one reviewed segment')
    fade = round(fade_ms * rate / 1000)
    rows, current, previous_end = [], 0, 0
    for i, segment in enumerate(edl['segments']):
        start = finite_number(segment.get('start'), 'start')
        end = finite_number(segment.get('end'), 'end')
        if start < 0 or end <= start or end > total_frames / rate:
            raise ValueError('Invalid or out-of-range source interval')
        lo, hi = round(start * rate), round(end * rate)
        length = hi - lo
        if length <= 0 or (fade and length <= 2 * fade):
            raise ValueError('Segment too short for crossfade; revise or set fade to zero')
        if not allow_reorder and lo < previous_end:
            raise ValueError('Overlapping/reordered source ranges need explicit review and --allow-reorder')
        # Adjacent source ranges already form continuous audio; do not shorten
        # or alter them just because the transcript had a segment boundary.
        overlap = fade if i and lo != previous_end else 0
        out_start = current - overlap
        current = out_start + length
        rows.append({'id': segment.get('id', str(i + 1)),
                     'source_start_sample': lo, 'source_end_sample': hi,
                     'output_start_sample': out_start, 'output_end_sample': current,
                     'crossfade_from_previous_samples': overlap,
                     'text': segment.get('text', ''), 'reason': segment.get('reason', '')})
        previous_end = hi
    # Audio overlaps; picture cuts use each overlap midpoint. These non-overlap
    # picture intervals cover exactly the same output duration as the audio.
    boundaries = [0] + [r['output_start_sample'] + r['crossfade_from_previous_samples'] / 2
                        for r in rows[1:]] + [current]
    video = []
    for i, row in enumerate(rows):
        a, b = boundaries[i:i + 2]
        video.append({'segment_id': row['id'], 'output_start_seconds': a / rate,
                      'output_end_seconds': b / rate,
                      'source_start_seconds': (row['source_start_sample'] + a - row['output_start_sample']) / rate,
                      'source_end_seconds': (row['source_start_sample'] + b - row['output_start_sample']) / rate})
    return {'schema_version': 1, 'timebase': edl['timebase'], 'source_id': edl['source_id'],
            'timeline_revision': edl['timeline_revision'], 'sample_rate': rate,
            'crossfade_ms': fade_ms, 'output_samples': current, 'output_duration_seconds': current / rate,
            'segments': rows, 'video_segments': video, 'approval_status': 'awaiting_user'}


def render_samples(samples, channels, timeline):
    output = array('h')
    for row in timeline['segments']:
        part = samples[row['source_start_sample'] * channels:row['source_end_sample'] * channels]
        overlap = row['crossfade_from_previous_samples']
        if overlap:
            base = len(output) - overlap * channels
            for frame in range(overlap):
                weight = (frame + 1) / (overlap + 1)
                for ch in range(channels):
                    j = frame * channels + ch
                    output[base + j] = round(output[base + j] * (1 - weight) + part[j] * weight)
        output.extend(part[overlap * channels:])
    if len(output) != timeline['output_samples'] * channels:
        raise ValueError('Internal sample length mismatch')
    return output


def render(source, edl_path, output_dir, fade_ms=4, allow_reorder=False):
    started = time.perf_counter()
    source, edl_path, output_dir = Path(source).resolve(), Path(edl_path).resolve(), Path(output_dir).resolve()
    if output_dir.exists():
        raise FileExistsError('Output directory exists; use a new revision')
    edl = json.loads(edl_path.read_text(encoding='utf-8'))
    with wave.open(str(source), 'rb') as reader:
        if reader.getsampwidth() != 2 or reader.getcomptype() != 'NONE' or reader.getnchannels() not in (1, 2):
            raise ValueError('Requires uncompressed PCM16 mono/stereo WAV')
        rate, channels, count = reader.getframerate(), reader.getnchannels(), reader.getnframes()
        raw = reader.readframes(count)
    if len(raw) != count * channels * 2:
        raise ValueError('Truncated source WAV')
    timeline = plan_timeline(edl, rate, count, fade_ms, allow_reorder)
    samples = array('h', raw)
    if sys.byteorder != 'little':
        samples.byteswap()
    output = render_samples(samples, channels, timeline)
    if sys.byteorder != 'little':
        output.byteswap()
    output_dir.mkdir(parents=True, exist_ok=False)
    with wave.open(str(output_dir / 'audio.wav'), 'wb') as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(2)
        writer.setframerate(rate)
        writer.writeframes(output.tobytes())
    timeline.update({'source_wav': str(source), 'source_pcm_sha256': hashlib.sha256(raw).hexdigest(),
                     'output_pcm_sha256': hashlib.sha256(output.tobytes()).hexdigest(),
                     'channels': channels, 'source_duration_seconds': count / rate,
                     'audio_render_elapsed_seconds': round(time.perf_counter() - started, 6),
                     'limits': ['No ASR, automatic word deletion, listening review or final video render.',
                                'Video consumer must use video_segments, not concatenate overlapping audio ranges.']})
    with (output_dir / 'timeline.json').open('x', encoding='utf-8') as writer:
        json.dump(timeline, writer, ensure_ascii=False, indent=2)
    return timeline


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-wav', required=True)
    parser.add_argument('--edl', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--crossfade-ms', type=float, default=4)
    parser.add_argument('--allow-reorder', action='store_true', help='Only after explicitly reviewing source reordering')
    args = parser.parse_args()
    try:
        result = render(args.source_wav, args.edl, args.output_dir, args.crossfade_ms, args.allow_reorder)
        print(json.dumps({'duration_seconds': result['output_duration_seconds'],
                          'elapsed_seconds': result['audio_render_elapsed_seconds'],
                          'approval_status': result['approval_status']}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, wave.Error, TypeError, AttributeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
