#!/usr/bin/env python3
"""Check, provision with explicit --install consent, and smoke-test local dependencies.

Python 3.9+, Node 22+, npm and an existing Chrome/Chromium are prerequisites.
No media uploads, model downloads, shell profile changes, sudo or global npm.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parent
MANIFEST = BASE.parent / 'assets' / 'runtime-package.json'
LOCK = BASE.parent / 'assets' / 'runtime-package-lock.json'
VERSION = '2.2.0'


def cache_root():
    if platform.system() == 'Windows':
        parent = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local'))
    elif platform.system() == 'Darwin':
        parent = Path.home() / 'Library/Caches'
    else:
        parent = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache'))
    return parent / 'talking-head-video-production'


def run(argv, timeout=30, cwd=None, env=None):
    result = subprocess.run([str(v) for v in argv], cwd=cwd, env=env,
                            capture_output=True, text=True, encoding='utf-8',
                            errors='replace', timeout=timeout, check=False)
    if result.returncode:
        # Do not echo package-manager logs: they may contain private registry URLs.
        raise RuntimeError(f'{Path(str(argv[0])).name} failed (exit {result.returncode}); inspect locally or retry the displayed plan')
    return result.stdout


def candidates(name, explicit=None):
    if explicit:
        return [Path(explicit).expanduser()]
    found = [shutil.which(name)]
    if platform.system() == 'Windows':
        local = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local'))
        found += [local / 'Microsoft/WinGet/Links' / (name + '.exe')]
        # Only the named package's install directory, not a whole disk scan.
        if name in ('ffmpeg', 'ffprobe'):
            found += sorted((local / 'Microsoft/WinGet/Packages').glob(f'Gyan.FFmpeg_*/ffmpeg-*/bin/{name}.exe'))
    else:
        found += [Path.home() / '.local/bin' / name,
                  Path('/opt/homebrew/bin') / name, Path('/usr/local/bin') / name,
                  Path('/usr/bin') / name]
    return [Path(p) for p in found if p]


def executable(name, explicit=None):
    for p in candidates(name, explicit):
        if not p.is_file():
            continue
        try:
            line = run([p, '--version' if name == 'node' else '-version']).splitlines()[0]
            return {'path': str(p.resolve()), 'version': line[:240]}
        except (OSError, RuntimeError, subprocess.TimeoutExpired, IndexError):
            pass
    return None


def browser_path(explicit=None):
    if explicit:
        return str(Path(explicit).expanduser().resolve()) if Path(explicit).expanduser().is_file() else None
    paths = [shutil.which(n) for n in ('google-chrome', 'chromium', 'chromium-browser')]
    paths += ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
              str(Path.home() / 'Applications/Google Chrome.app/Contents/MacOS/Google Chrome')]
    for key in ('PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA'):
        if os.environ.get(key):
            paths.append(str(Path(os.environ[key]) / 'Google/Chrome/Application/chrome.exe'))
    return next((str(Path(p).resolve()) for p in paths if p and Path(p).is_file()), None)


def npm_cli(node, explicit=None):
    if explicit:
        return str(Path(explicit).expanduser().resolve()) if Path(explicit).expanduser().is_file() else None
    paths = []
    npm = shutil.which('npm')
    if npm:
        target = Path(npm).resolve()
        if target.suffix == '.js':
            paths.append(target)
        paths.append(target.parent / 'node_modules/npm/bin/npm-cli.js')
    if node:
        parent = Path(node).parent
        paths += [parent / 'node_modules/npm/bin/npm-cli.js',
                  parent.parent / 'lib/node_modules/npm/bin/npm-cli.js']
    return next((str(p) for p in paths if p.is_file()), None)


def runtime_probe(node, runtime):
    if not node or not runtime or not (Path(runtime) / 'package.json').is_file():
        return None
    expected = json.loads(MANIFEST.read_text())['dependencies']
    script = """const path=require('node:path');
const r=require('node:module').createRequire(path.resolve(process.argv[1],'package.json'));
(async()=>{const out={};for(const p of JSON.parse(process.argv[2])){
 const meta=r(p+'/package.json');
 if(p==='@remotion/media')await import(require('node:url').pathToFileURL(path.resolve(path.dirname(r.resolve(p+'/package.json')),meta.module)).href);
 else r(p);
 out[p]=meta.version;
}console.log(JSON.stringify(out));})().catch(()=>process.exit(1));"""
    try:
        versions = json.loads(run([node, '-e', script, runtime, json.dumps(list(expected))]))
        if versions != expected:
            return None
        return {'path': str(Path(runtime).resolve()), 'packages': versions}
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired):
        return None


def ffmpeg_install_plan(system=None, which=shutil.which, root=False):
    system = system or platform.system()
    if system == 'Darwin':
        brew = which('brew')
        if not brew:
            brew = next((str(p) for p in (Path('/opt/homebrew/bin/brew'), Path('/usr/local/bin/brew')) if p.is_file()), None)
        if brew:
            return [brew, 'install', 'ffmpeg']
        raise RuntimeError('FFmpeg missing: Homebrew is not installed. Ask for foundation setup or provide existing --ffmpeg and --ffprobe; do not run a remote shell installer.')
    if system == 'Windows' and which('winget'):
        return [which('winget'), 'install', '--id', 'Gyan.FFmpeg', '--exact', '--source', 'winget',
                '--scope', 'user', '--silent', '--disable-interactivity',
                '--accept-source-agreements', '--accept-package-agreements']
    if system == 'Linux' and root and which('apt-get'):
        return [which('apt-get'), 'install', '-y', 'ffmpeg']
    raise RuntimeError('FFmpeg missing: no supported non-elevating package manager. Supply a verified FFmpeg distribution or request administrator/foundation setup; no sudo is run.')


def save_json(path, value):
    # Only our managed cache reports use replace; historical per-run reports remain.
    temp = path.with_suffix('.pending.json')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def smoke(report, work):
    commands = report['commands']
    ffmpeg, ffprobe, node = (commands[n]['path'] for n in ('ffmpeg', 'ffprobe', 'node'))
    filters = run([ffmpeg, '-hide_banner', '-filters'])
    for required in ('atrim', 'asetpts', 'afade', 'acrossfade', 'concat', 'loudnorm', 'silencedetect'):
        if required not in filters.split():
            raise RuntimeError('FFmpeg lacks required filter: ' + required)
    movie = work / 'synthetic.mp4'
    run([ffmpeg, '-nostdin', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=orange:s=64x64:r=25',
         '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000', '-t', '1',
         '-af', 'atrim=start=0:end=1,asetpts=PTS-STARTPTS,afade=t=in:d=0.01',
         '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(movie)], timeout=60)
    meta = json.loads(run([ffprobe, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', movie]))
    if {s['codec_type'] for s in meta.get('streams', [])} != {'audio', 'video'} or not .8 < float(meta['format']['duration']) < 1.3:
        raise RuntimeError('Synthetic MP4 metadata validation failed')
    run([ffmpeg, '-nostdin', '-v', 'error', '-i', movie, '-f', 'null', '-'], timeout=60)
    still = work / 'template.png'
    run([node, BASE / 'render_studio.mjs', '--demo', '--still', '--runtime', report['runtime']['path'],
         '--browser', report['browser'], '--output', still], timeout=240)
    if not still.is_file() or still.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
        raise RuntimeError('Template PNG validation failed')
    return {'ffmpeg_encode_decode': 'passed', 'ffprobe_metadata': 'passed',
            'remotion_template_png': 'passed', 'artifacts': str(work),
            'visual_review': 'not_performed', 'audio_review': 'not_performed'}


def setup(args):
    root = Path(args.cache_dir).expanduser().resolve() if args.cache_dir else cache_root()
    try:
        previous = json.loads((root / 'runtime-report.json').read_text(encoding='utf-8'))
        if not isinstance(previous, dict) or previous.get('schema_version') != 1:
            previous = {}
    except (OSError, ValueError):
        previous = {}
    recipe = hashlib.sha256(MANIFEST.read_bytes() + LOCK.read_bytes()).hexdigest()[:12]
    managed = root / ('runtime-' + recipe)
    report = {'schema_version': 1, 'skill_version': VERSION,
              'checked_at': datetime.now(timezone.utc).isoformat(), 'status': 'not_ready',
              'commands': {'python': {'path': sys.executable, 'version': platform.python_version()}},
              'runtime': None, 'browser': browser_path(args.browser or previous.get('browser')), 'actions': [], 'errors': [],
              'capabilities_not_tested': ['ASR', 'alignment', 'image_understanding', 'audio_review',
                                          'image_generation', 'full_video_production'],
              'report_path': str(root / 'runtime-report.json')}
    for name in ('node', 'ffmpeg', 'ffprobe'):
        saved = (previous.get('commands', {}).get(name) or {}).get('path')
        report['commands'][name] = executable(name, getattr(args, name))
        if not report['commands'][name] and not getattr(args, name) and saved:
            report['commands'][name] = executable(name, saved)
    node = report['commands']['node']
    if node and int(node['version'].lstrip('v').split('.')[0]) < 22:
        report['errors'].append('Need Node.js 22+ for the pinned runtime; no automatic Node upgrade.')
        node = None
    if not node:
        report['errors'].append('Node.js 22+ missing: reuse the host managed runtime with --node or request foundation setup.')
    node_path = node['path'] if node else None
    runtime_candidates = [args.runtime, managed, (previous.get('runtime') or {}).get('path')]
    if (Path.cwd() / 'package.json').is_file():
        runtime_candidates.append(Path.cwd())
    for candidate in runtime_candidates:
        report['runtime'] = runtime_probe(node_path, candidate)
        if report['runtime']:
            break
    if not report['browser']:
        report['errors'].append('Chrome/Chromium missing: provide --browser or request browser installation; no automatic browser download.')
    missing_ffmpeg = any(not report['commands'][name] for name in ('ffmpeg', 'ffprobe'))
    plans = []
    if missing_ffmpeg:
        try:
            argv = ffmpeg_install_plan(root=hasattr(os, 'geteuid') and os.geteuid() == 0)
            plans.append(('ffmpeg', argv))
        except RuntimeError as exc:
            report['errors'].append(str(exc))
    cli = npm_cli(node_path, args.npm_cli)
    if not report['runtime']:
        if node_path and cli:
            plans.append(('remotion', [node_path, cli, 'ci', '--global=false', '--prefix', str(managed), '--no-audit', '--no-fund', '--include=optional',
                                      '--registry=https://registry.npmjs.org', '--fetch-retries=1',
                                      '--fetch-timeout=60000']))
        else:
            report['errors'].append('npm CLI not found; provide --npm-cli pointing to npm-cli.js or ask the host for its managed npm.')
    report['plan'] = [{'dependency': name, 'argv': argv,
                       'target': str(managed) if name == 'remotion' else 'package-manager managed FFmpeg'} for name, argv in plans]
    if args.install:
        root.mkdir(parents=True, exist_ok=True)
        # One installation per cache; a crash leaves a lock to investigate, never force-remove.
        lock_path = root / 'setup.lock'
        with lock_path.open('x') as handle:
            handle.write(str(os.getpid()))
        try:
            for name, argv in plans:
                print('Installing ' + name + ': ' + json.dumps(argv), file=sys.stderr, flush=True)
                try:
                    cwd = None
                    if name == 'remotion':
                        managed.mkdir(exist_ok=True)
                        package = managed / 'package.json'
                        package_lock = managed / 'package-lock.json'
                        for target, source in ((package, MANIFEST), (package_lock, LOCK)):
                            if target.exists() and target.read_bytes() != source.read_bytes():
                                raise RuntimeError('Managed runtime contains different files; preserve it and use another --cache-dir.')
                            if not target.exists():
                                shutil.copyfile(source, target)
                        cwd = managed
                    env = os.environ.copy()
                    if node_path:
                        env['PATH'] = str(Path(node_path).parent) + os.pathsep + env.get('PATH', '')
                    env['HOMEBREW_NO_AUTO_UPDATE'] = '1'
                    env['HOMEBREW_NO_INSTALL_CLEANUP'] = '1'
                    run(argv, timeout=1200, cwd=cwd, env=env)
                    report['actions'].append({'dependency': name, 'status': 'install_command_completed'})
                except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
                    report['errors'].append(name + ': ' + str(exc))
            for name in ('ffmpeg', 'ffprobe'):
                existing = (report['commands'][name] or {}).get('path')
                report['commands'][name] = executable(name, getattr(args, name) or existing)
                if not report['commands'][name]:
                    report['errors'].append(name + ' still unavailable after setup; provide its actual executable path and rerun verification.')
            report['runtime'] = report['runtime'] or runtime_probe(node_path, managed)
            if not report['runtime']:
                report['errors'].append('Remotion modules did not load with the pinned versions; install-command completion is not readiness.')
        finally:
            lock_path.unlink()  # exact lock created by this invocation only
    ready = all(report['commands'].get(n) for n in ('node', 'ffmpeg', 'ffprobe')) and report['runtime'] and report['browser'] and not report['errors']
    if ready:
        report['status'] = 'detected_not_verified'
        if args.install or args.verify:
            root.mkdir(parents=True, exist_ok=True)
            work = Path(tempfile.mkdtemp(prefix='check-', dir=root))
            try:
                report['smoke_tests'] = smoke(report, work)
                report['status'] = 'dependencies_ready'
            except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
                report['status'] = 'verification_failed'
                report['errors'].append(str(exc))
    if args.install or args.verify:
        root.mkdir(parents=True, exist_ok=True)
        history = root / ('report-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f') + '.json')
        save_json(history, report)
        save_json(root / 'runtime-report.json', report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--install', action='store_true', help='Explicitly authorized install of only missing FFmpeg and pinned Remotion dependencies, then smoke tests')
    mode.add_argument('--verify', action='store_true', help='No installs; run synthetic smoke tests with existing dependencies')
    mode.add_argument('--check', action='store_true', help='Read-only inventory and proposed commands (default)')
    for option in ('cache-dir', 'node', 'npm-cli', 'runtime', 'browser', 'ffmpeg', 'ffprobe'):
        parser.add_argument('--' + option)
    args = parser.parse_args(argv)
    try:
        report = setup(args)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report['status'] in ('dependencies_ready', 'detected_not_verified') else 2
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status': 'setup_failed', 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
