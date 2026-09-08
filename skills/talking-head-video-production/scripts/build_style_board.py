#!/usr/bin/env python3
"""Build an offline shared-template 3x3 board (Python 3 + Node.js; no network).
A personal board requires --project with valid G1 and a local PNG/JPEG.
--demo contains only the bundled generic illustration and sample copy.
"""
import argparse
import base64
import json
from pathlib import Path
import re
import subprocess
import sys
from check_gate import check

def load_presets():
    data = json.loads((Path(__file__).resolve().parent.parent / 'assets/style-presets.json').read_text(encoding='utf-8'))
    styles = data['styles']
    if [s['id'] for s in styles] != ['tactile','editorial','precision']: raise ValueError('Three canonical styles required')
    for s in styles:
        if [p['id'] for p in s['palettes']] != ['apricot','sky','lilac']: raise ValueError('Same three canonical palettes required')
        for p in s['palettes']:
            for token in ('background','text','accent','surface','muted','shadow'):
                if not re.fullmatch(r'#[0-9a-fA-F]{6}', p[token]): raise ValueError('Invalid palette role')
    return styles

def build(presenter=None, title='把知识|打包成 Skill', caption='打包成一个 AI Skill', labels=None, concept='AI Skill', demo=False, node='node', scene_config=None):
    load_presets()
    image_url = ''
    if presenter:
        raw = Path(presenter).read_bytes()
        mime = 'image/png' if raw.startswith(b'\x89PNG\r\n\x1a\n') else 'image/jpeg' if raw.startswith(b'\xff\xd8\xff') else None
        if not mime or len(raw) > 15*1024*1024: raise ValueError('Need lightweight local PNG/JPEG')
        image_url = 'data:' + mime + ';base64,' + base64.b64encode(raw).decode('ascii')
    elif not demo: raise ValueError('Need a real presenter frame')
    if demo and presenter: raise ValueError('Public demo cannot contain private media')
    if demo and scene_config: raise ValueError('Public demo cannot contain custom scene data')
    config = {} if demo else dict(title=title.split('|'), caption_lines=caption.split('|'), labels=labels or ['方法论','知识点','解决思路'], concept=concept, highlights=[concept] if concept in caption else [])
    if scene_config: config.update(scene_config)
    result = subprocess.run([node,str(Path(__file__).with_name('build_studio.mjs'))],input=json.dumps(dict(config=config,portrait=image_url,demo=demo)),text=True,capture_output=True,timeout=30)
    if result.returncode: raise ValueError(result.stderr.strip())
    return result.stdout

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--presenter'); p.add_argument('--output',required=True); p.add_argument('--project')
    p.add_argument('--demo',action='store_true'); p.add_argument('--node',default='node')
    p.add_argument('--config',help='JSON overrides for all actual topic fields; no user approval is inferred')
    p.add_argument('--title',default='把知识|打包成 Skill'); p.add_argument('--caption',default='打包成一个 AI Skill')
    p.add_argument('--labels',default='方法论,知识点,解决思路'); p.add_argument('--concept',default='AI Skill')
    a=p.parse_args()
    try:
        if not a.demo:
            if not a.project: raise ValueError('Pause: --project with G1 approval is required')
            check(a.project,'style')
        scene_config=json.loads(Path(a.config).read_text(encoding='utf-8')) if a.config else None
        document=build(a.presenter,a.title,a.caption,[s.strip() for s in a.labels.split(',')],a.concept,a.demo,a.node,scene_config)
        with Path(a.output).open('x',encoding='utf-8') as f: f.write(document)
        print(json.dumps({'choices':9,'template_version':'2.1.0','type':'offline_html_not_video','approved':False}))
        return 0
    except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as exc:
        print(str(exc),file=sys.stderr); return 2

if __name__=='__main__': raise SystemExit(main())
