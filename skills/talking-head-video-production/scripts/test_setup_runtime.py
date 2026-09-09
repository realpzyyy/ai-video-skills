import argparse
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import setup_runtime as setup
import probe_local


def args(**changes):
    values = dict(install=False, verify=False, check=True, cache_dir=None,
                  node=None, npm_cli=None, runtime=None, browser=None, ffmpeg=None, ffprobe=None)
    values.update(changes)
    return argparse.Namespace(**values)


class SetupTests(unittest.TestCase):
    def test_manifest_has_exact_matching_remotion(self):
        manifest = json.loads(setup.MANIFEST.read_text())
        deps = manifest['dependencies']
        self.assertEqual({v for k, v in deps.items() if 'remotion' in k}, {'4.0.509'})
        self.assertTrue(manifest['private'])
        lock = json.loads(setup.LOCK.read_text())
        self.assertEqual(lock['packages']['']['dependencies'], deps)

    def test_macos_uses_existing_brew(self):
        self.assertEqual(setup.ffmpeg_install_plan('Darwin', lambda _: '/brew'), ['/brew', 'install', 'ffmpeg'])

    def test_windows_no_elevation(self):
        plan = setup.ffmpeg_install_plan('Windows', lambda _: 'winget.exe')
        self.assertIn('Gyan.FFmpeg', plan)
        self.assertIn('user', plan)
        self.assertIn('--disable-interactivity', plan)

    def test_linux_does_not_invent_sudo(self):
        with self.assertRaises(RuntimeError):
            setup.ffmpeg_install_plan('Linux', lambda _: '/apt-get', root=False)

    def test_linux_root_supported(self):
        self.assertEqual(setup.ffmpeg_install_plan('Linux', lambda _: '/apt-get', root=True), ['/apt-get', 'install', '-y', 'ffmpeg'])

    def test_unsupported_no_install(self):
        with self.assertRaises(RuntimeError):
            setup.ffmpeg_install_plan('Other', lambda _: None)

    def test_explicit_executable_not_silently_substituted(self):
        self.assertEqual(setup.candidates('ffmpeg', '/missing/ffmpeg'), [Path('/missing/ffmpeg')])

    def test_check_missing_only_plans_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(setup, 'executable', return_value=None), \
             patch.object(setup, 'browser_path', return_value=None), patch.object(setup, 'npm_cli', return_value=None), \
             patch.object(setup, 'ffmpeg_install_plan', return_value=['brew', 'install', 'ffmpeg']), \
             patch.object(setup, 'run') as run:
            root = Path(temp) / 'not-created'
            report = setup.setup(args(cache_dir=str(root)))
            self.assertEqual(report['status'], 'not_ready')
            self.assertFalse(root.exists())
            run.assert_not_called()
            self.assertEqual(len(report['plan']), 1)

    def test_ready_reuses_without_install(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(setup, 'executable', return_value={'path':'/tool','version':'v24.0.0'}), \
             patch.object(setup, 'runtime_probe', return_value={'path':'/runtime'}), \
             patch.object(setup, 'browser_path', return_value='/chrome'), \
             patch.object(setup, 'npm_cli', return_value='/npm.js'), patch.object(setup, 'run') as run, \
             patch.object(setup, 'smoke', return_value={'test':'passed'}) as smoke:
            report = setup.setup(args(cache_dir=temp, install=True, check=False))
            self.assertEqual(report['status'], 'dependencies_ready')
            self.assertEqual(report['actions'], [])
            self.assertTrue((Path(temp) / 'runtime-report.json').is_file())
            self.assertFalse((Path(temp) / 'setup.lock').exists())
            run.assert_not_called()
            smoke.assert_called_once()

    def test_smoke_failure_never_ready(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(setup, 'executable', return_value={'path':'/tool','version':'v24.0.0'}), \
             patch.object(setup, 'runtime_probe', return_value={'path':'/runtime'}), \
             patch.object(setup, 'browser_path', return_value='/chrome'), patch.object(setup, 'npm_cli', return_value='/npm.js'), \
             patch.object(setup, 'smoke', side_effect=RuntimeError('bad renderer')):
            report = setup.setup(args(cache_dir=temp, verify=True, check=False))
            self.assertEqual(report['status'], 'verification_failed')

    def test_concurrent_install_refused(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(setup, 'executable', return_value=None), \
             patch.object(setup, 'browser_path', return_value=None), patch.object(setup, 'npm_cli', return_value=None), \
             patch.object(setup, 'ffmpeg_install_plan', return_value=['brew']):
            marker = Path(temp) / 'setup.lock'
            marker.write_text('another-process')
            with self.assertRaises(FileExistsError):
                setup.setup(args(cache_dir=temp, install=True, check=False))
            self.assertEqual(marker.read_text(), 'another-process')

    def test_probe_uses_saved_absolute_paths(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(probe_local, 'run_command', return_value={'returncode':0,'stdout':'tool v1','stderr':'','error':None}):
            file = Path(temp) / 'report.json'
            file.write_text(json.dumps({'schema_version':1,'commands':{'ffmpeg':{'path':'/managed/ffmpeg'}, 'ffprobe':{'path':'/managed/ffprobe'}}}))
            report = probe_local.build_report(runtime_report=file)
            self.assertEqual(report['commands']['ffprobe']['path'], '/managed/ffprobe')

    def test_no_shell_execution(self):
        with patch.object(setup.subprocess, 'run') as run:
            run.return_value.returncode = 0
            run.return_value.stdout = 'ok'
            setup.run(['/a path/tool', 'x; echo unsafe'])
            self.assertNotIn('shell', run.call_args.kwargs)
            self.assertEqual(run.call_args.args[0][1], 'x; echo unsafe')


if __name__ == '__main__':
    unittest.main()
