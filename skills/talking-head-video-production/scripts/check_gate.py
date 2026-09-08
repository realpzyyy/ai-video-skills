#!/usr/bin/env python3
"""Check project approval consistency; this is not authentication or a sandbox."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ASSETS = Path(__file__).resolve().parent.parent / 'assets'
STYLES = ['tactile', 'editorial', 'precision']
PALETTES = ['apricot', 'sky', 'lilac']

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def template_hash():
    h = hashlib.sha256()
    for name in ['style-presets.json', 'studio.css', 'studio.mjs', 'studio-remotion.tsx']:
        h.update(name.encode()); h.update((ASSETS / name).read_bytes())
    return h.hexdigest()

def require(condition, message):
    if not condition: raise ValueError(message)

def check(project_path, stage='render', scene=None):
    path = Path(project_path).resolve()
    p = json.loads(path.read_text(encoding='utf-8'))
    require(p.get('project_id') and p.get('timeline_revision'), 'Missing project identity / timeline revision')
    def asset(record):
        target = path.parent / record['path']
        require(sha256(target) == record.get('sha256'), 'Asset changed: ' + record['path'])
    def approval(key):
        a = p.get('approvals', {}).get(key) or {}
        require(a.get('status') in ['approved', 'user_authorized_skip'], key + ': pause for user confirmation')
        e = a.get('evidence') or {}
        require(e.get('role') == 'user' and e.get('quote') and e.get('message_id'), key + ': explicit user evidence required')
        require(a.get('project_id') == p['project_id'] and a.get('timeline_revision') == p['timeline_revision'], key + ': stale project / timeline')
        if a['status'] == 'user_authorized_skip': require(a.get('scope'), key + ': skip scope required')
        return a
    audio = p.get('audio') or {}
    require(audio.get('path'), 'Missing confirmed audio')
    asset(audio)
    g1 = approval('G1_audio')
    require(g1.get('audio_sha256') == audio['sha256'], 'G1: audio approval is stale')
    if stage == 'style': return p
    g2 = approval('G2_style_palette')
    s, c = g2.get('style_id'), g2.get('palette_id')
    require(s in STYLES and c in PALETTES, 'G2: both standard style and palette required')
    require(g2.get('choice') == chr(65 + STYLES.index(s)) + str(PALETTES.index(c) + 1), 'G2: choice mismatch')
    require(g2.get('template_sha256') == template_hash(), 'G2: template changed; compare and renew visual approval')
    if g2['status'] == 'approved':
        board = p.get('style_board') or {}
        require(board.get('path'), 'G2: no shown style board')
        asset(board)
        require(g2.get('board_sha256') == board['sha256'], 'G2: board approval is stale')
    if scene is not None:
        require(scene.get('style_id') == s and scene.get('palette_id') == c, 'Rendered scene differs from G2 choice')
    return p

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project')
    parser.add_argument('--stage', choices=['style', 'render'], default='render')
    parser.add_argument('--scene')
    parser.add_argument('--template-hash', action='store_true')
    a = parser.parse_args()
    try:
        if a.template_hash: print(template_hash()); return 0
        if not a.project: raise ValueError('--project required')
        scene = json.loads(Path(a.scene).read_text(encoding='utf-8')) if a.scene else None
        check(a.project, a.stage, scene)
        print(json.dumps({'status': 'consistent', 'stage': a.stage, 'not_authentication': True}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr); return 2

if __name__ == '__main__': raise SystemExit(main())
