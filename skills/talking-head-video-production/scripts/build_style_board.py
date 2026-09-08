#!/usr/bin/env python3
"""Build one offline 3×3 style/palette HTML from one real local PNG/JPEG frame.

Usage: build_style_board.py --presenter frame.png --output board.html
 --title '把知识|变成工具' --caption '把方法打包成一个 AI Skill'
 --labels '方法论,知识点,解决思路' --concept 'AI Skill'
This is an editable static style board, not animated B-roll or a cover.
Only three bundled 9:16 code-native styles are implemented; adapt topic/graphics
before use. The script makes no network calls and does not render PNG/video.
"""
import argparse
import base64
import html
import json
from pathlib import Path
import re
import sys
import time


def load_presets():
    path = Path(__file__).resolve().parent.parent / 'assets/style-presets.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    styles = data['styles']
    if len(styles) != 3 or len({s['id'] for s in styles}) != 3:
        raise ValueError('Need three distinct styles')
    if {s['id'] for s in styles} != {'tactile', 'editorial', 'precision'}:
        raise ValueError('Unknown layout; provide an actual implementation')
    for style in styles:
        if len(style['palettes']) != 3 or len({p['id'] for p in style['palettes']}) != 3:
            raise ValueError('Each style needs three distinct palettes')
        for p in style['palettes']:
            for token in ('background', 'text', 'accent', 'surface', 'muted', 'shadow'):
                if not re.fullmatch(r'#[0-9a-fA-F]{6}', p[token]):
                    raise ValueError('Invalid palette role: ' + token)
    return styles


CSS = '''
*{box-sizing:border-box}body{margin:0;padding:24px;background:#eeeae4;color:#292827;font-family:"Heiti SC","STHeiti",sans-serif}header{max-width:1220px;margin:auto auto 20px}h1{font-size:26px;margin:0 0 8px}p{margin:6px 0;line-height:1.5}.board{max-width:1220px;margin:auto;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.option{min-width:0}.name{padding:9px 0;font-size:16px;font-weight:bold}.shot{aspect-ratio:9/16;position:relative;overflow:hidden;background:var(--background);color:var(--text)}.shot h2{position:absolute;left:7%;top:8%;margin:0;width:58%;font-size:clamp(18px,2.7vw,36px);line-height:1.2;overflow-wrap:anywhere}.portrait{position:absolute;right:7%;top:7%;width:27%;height:27%;object-fit:cover;object-position:center 10%;border:2px solid var(--surface);border-radius:42% 42% 18% 18%}.art{position:absolute;left:8%;right:8%;top:39%;height:37%}.labels{display:flex;justify-content:space-between;gap:5%}.label{display:block;font-size:clamp(10px,1.5vw,19px);line-height:1.3;overflow-wrap:anywhere}.concept{font-size:clamp(18px,3vw,39px);font-weight:bold;line-height:1.1;overflow-wrap:anywhere}.caption{position:absolute;left:7%;right:7%;bottom:12%;font-size:clamp(12px,1.8vw,23px);line-height:1.35;padding:9px 10px;border-radius:9px;background:var(--text);color:var(--background);text-align:center}.note{position:absolute;bottom:6%;left:7%;font-size:clamp(9px,1vw,13px);color:var(--muted)}.motion{font-size:13px;color:#5d5954}.tactile .shot{background:radial-gradient(ellipse at 30% 50%,var(--surface),var(--background) 76%)}.tactile .label{white-space:nowrap;font-size:clamp(10px,1.25vw,16px);padding:18% 3%;width:30%;border-radius:8px;background:var(--surface);box-shadow:3px 5px 0 var(--shadow);transform:rotate(-7deg)}.tactile .label:nth-child(2){transform:translateY(-12px) rotate(2deg)}.tactile .label:nth-child(3){transform:rotate(8deg)}.tactile .concept{position:absolute;top:59%;left:4%;right:2%;padding:10% 7%;background:var(--surface);border-radius:12px;box-shadow:0 7px 0 var(--shadow),8px 18px 22px #0002;transform:rotate(-3deg);color:var(--accent)}.editorial .shot{border-top:9px solid var(--accent)}.editorial .shot h2{top:8%;width:84%;font-size:clamp(21px,3.3vw,43px);border-bottom:4px solid var(--accent);padding-bottom:12px}.editorial .portrait{left:8%;top:31%;width:38%;height:37%;border-radius:0}.editorial .art{left:53%;right:7%;top:33%;height:33%}.editorial .labels{display:block}.editorial .label{padding:8px 0;margin-bottom:12px;border-top:1px solid var(--muted)}.editorial .concept{margin-top:24px;font-size:clamp(17px,2.5vw,32px);color:var(--accent)}.precision .shot{background-image:linear-gradient(#8881 1px,transparent 1px),linear-gradient(90deg,#8881 1px,transparent 1px);background-size:22px 22px}.precision .portrait{border-radius:10px;border-color:var(--accent)}.precision .labels{display:block;border-left:2px solid var(--accent);padding-left:10%}.precision .label{display:flex;align-items:center;gap:12px;padding:10px;border:1px solid var(--muted);background:var(--surface);margin-bottom:13px}.precision .label:before{content:attr(data-number);color:var(--accent);font-family:monospace}.precision .concept{padding-top:12px;color:var(--accent);font-size:clamp(18px,2.5vw,32px)}
@media(max-width:650px){.board{grid-template-columns:1fr}.shot{max-width:420px}.shot h2{font-size:35px}.label{font-size:19px}.concept{font-size:34px}.caption{font-size:22px}.note{font-size:12px}.editorial .shot h2{font-size:39px}.editorial .concept,.precision .concept{font-size:30px}}
'''


def build(presenter, title, caption, labels, concept):
    styles = load_presets()
    raw = Path(presenter).read_bytes()
    if raw.startswith(b'\x89PNG\r\n\x1a\n'):
        mime = 'image/png'
    elif raw.startswith(b'\xff\xd8\xff'):
        mime = 'image/jpeg'
    else:
        raise ValueError('Presenter must be a real local PNG or JPEG')
    if len(raw) > 15 * 1024 * 1024:
        raise ValueError('Use a lightweight representative frame, not a huge source asset')
    if len(labels) != 3 or not all(labels):
        raise ValueError('Provide three semantic labels')
    if not title or not caption or not concept:
        raise ValueError('Title, caption and concept must not be empty')
    if len(title) > 18 or len(caption) > 32 or len(concept) > 18 or any(len(s) > 10 for s in labels):
        raise ValueError('Text too long for template; revise layout or shorten without changing meaning')
    e = html.escape
    title_html = '<br>'.join(e(line) for line in title.split('|'))
    image_url = 'data:' + mime + ';base64,' + base64.b64encode(raw).decode('ascii')
    options = []
    for i, style in enumerate(styles):
        for j, palette in enumerate(style['palettes']):
            ident = chr(65 + i) + str(j + 1)
            tokens = ';'.join('--' + k + ':' + palette[k] for k in ('background', 'text', 'accent', 'surface', 'muted', 'shadow'))
            tags = ''.join('<span class="label" data-number="0' + str(k + 1) + '">' + e(label) + '</span>' for k, label in enumerate(labels))
            options.append(f'<article class="option {style["id"]}" data-choice="{ident}" data-style="{style["id"]}" data-palette="{palette["id"]}"><div class="name">{ident} · {e(style["name"])} / {e(palette["name"])}</div><div class="shot" style="{tokens}"><h2>{title_html}</h2><img class="portrait" src="{image_url}" alt="同一原片人物"><div class="art"><div class="labels">{tags}</div><div class="concept">{e(concept)}</div></div><div class="caption">{e(caption)}</div><div class="note">概念示意 · 静态风格样张</div></div><p class="motion">运动方向：{e(style["motion"])}</p></article>')
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>3×3口播风格配色</title><style>' + CSS + '</style><header><h1>选择视觉风格 × 配色</h1><p>每行同一画风，每列为该画风的一种配色。请回复完整编号，如 A2。</p><p>同一真人、同一句台词、同一信息量；此板不是动画，也不是封面。</p></header><main class="board">' + ''.join(options) + '</main></html>'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--presenter', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--title', default='把知识|变成工具', help='Use | for a semantic line break')
    p.add_argument('--caption', default='把方法打包成一个 AI Skill')
    p.add_argument('--labels', default='方法论,知识点,解决思路')
    p.add_argument('--concept', default='AI Skill')
    a = p.parse_args()
    start = time.perf_counter()
    try:
        document = build(a.presenter, a.title, a.caption, [x.strip() for x in a.labels.split(',')], a.concept)
        with Path(a.output).open('x', encoding='utf-8') as f:
            f.write(document)
        print(json.dumps({'choices': 9, 'type': 'static_html_not_video', 'build_seconds': round(time.perf_counter() - start, 6)}))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
