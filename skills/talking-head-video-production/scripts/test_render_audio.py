import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from array import array
import wave
from render_audio import plan_timeline, render_samples, render


def edl(segments):
    return {'schema_version': 1, 'timebase': 'source_seconds_from_zero',
            'source_id': 'test', 'timeline_revision': 'v1', 'segments': segments}


class AudioTests(unittest.TestCase):
    def test_overlap_mapping_and_samples(self):
        plan = plan_timeline(edl([{'start': 0, 'end': 1}, {'start': 2, 'end': 3}]), 1000, 3000, 4)
        self.assertEqual(plan['output_samples'], 1996)
        result = render_samples(array('h', [1000] * 1000 + [0] * 1000 + [-1000] * 1000), 1, plan)
        self.assertEqual(len(result), 1996)
        self.assertEqual(list(result[996:1000]), [600, 200, -200, -600])
        self.assertEqual(plan['video_segments'][0]['output_end_seconds'], .998)
        self.assertEqual(plan['video_segments'][1]['output_start_seconds'], .998)
        self.assertAlmostEqual(sum(x['source_end_seconds'] - x['source_start_seconds'] for x in plan['video_segments']), 1.996)

    def test_no_fade_is_exact(self):
        plan = plan_timeline(edl([{'start': 0, 'end': .2}, {'start': .5, 'end': .8}]), 1000, 1000, 0)
        samples = array('h', range(1000))
        self.assertEqual(render_samples(samples, 1, plan), samples[:200] + samples[500:800])

    def test_stereo(self):
        plan = plan_timeline(edl([{'start': 0, 'end': .1}, {'start': .2, 'end': .3}]), 1000, 300, 4)
        samples = array('h', [100, -100] * 300)
        self.assertEqual(list(render_samples(samples, 2, plan)), [100, -100] * 196)

    def test_adjacent_ranges_stay_unchanged(self):
        plan = plan_timeline(edl([{'start': 0, 'end': .5}, {'start': .5, 'end': 1}]), 1000, 1000, 4)
        samples = array('h', range(1000))
        self.assertEqual(plan['output_samples'], 1000)
        self.assertEqual(render_samples(samples, 1, plan), samples)

    def test_rejected_intervals(self):
        for spans in [[], [{'start': -1, 'end': 1}], [{'start': 1, 'end': 1}],
                      [{'start': 0, 'end': 4}], [{'start': float('nan'), 'end': 1}],
                      [{'start': True, 'end': 2}], [{'start': 0, 'end': .005}],
                      [{'start': 0, 'end': 2}, {'start': 1, 'end': 3}],
                      [{'start': 2, 'end': 3}, {'start': 0, 'end': 1}]]:
            with self.subTest(spans=spans), self.assertRaises(ValueError):
                plan_timeline(edl(spans), 1000, 3000)

    def test_reorder_requires_flag(self):
        plan = plan_timeline(edl([{'start': 2, 'end': 3}, {'start': 0, 'end': 1}]), 1000, 3000, allow_reorder=True)
        self.assertEqual(plan['segments'][0]['source_start_sample'], 2000)

    def test_invalid_schema_and_fade(self):
        good = edl([{'start': 0, 'end': 1}])
        for change in [{'timebase': 'unverified'}, {'source_id': ''}, {'schema_version': 2}]:
            with self.assertRaises(ValueError):
                plan_timeline(dict(good, **change), 1000, 2000)
        for fade in [-1, 21, float('inf'), True]:
            with self.assertRaises(ValueError):
                plan_timeline(good, 1000, 2000, fade)

    def test_file_render_preserves_source_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'source ; with spaces.wav'
            with wave.open(str(source), 'wb') as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(1000)
                w.writeframes(array('h', range(3000)).tobytes())
            original = hashlib.sha256(source.read_bytes()).hexdigest()
            config = root / 'edl.json'
            config.write_text(json.dumps(edl([{'start': 0, 'end': 1}, {'start': 2, 'end': 3}])))
            result = render(source, config, root / 'v1')
            self.assertEqual(result['approval_status'], 'awaiting_user')
            with wave.open(str(root / 'v1/audio.wav'), 'rb') as w:
                self.assertEqual(w.getnframes(), 1996)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), original)
            with self.assertRaises(FileExistsError):
                render(source, config, root / 'v1')


if __name__ == '__main__':
    unittest.main()
