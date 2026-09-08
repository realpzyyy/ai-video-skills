from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from build_style_board import build, load_presets


class Inspector(HTMLParser):
    def __init__(self):
        super().__init__(); self.options = []; self.images = []; self.scripts = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article': self.options.append(attrs)
        if tag == 'img': self.images.append(attrs)
        if tag == 'script': self.scripts.append(attrs)


class BoardTests(unittest.TestCase):
    def test_matrix_and_local_embedded_frame(self):
        with tempfile.TemporaryDirectory() as d:
            frame = Path(d) / 'frame.png'
            frame.write_bytes(b'\x89PNG\r\n\x1a\n' + b'test-fixture')
            parser = Inspector()
            parser.feed(build(frame, '<标题>|演示', '一句台词', ['甲', '乙', '丙'], '工具'))
            self.assertEqual([x['data-choice'] for x in parser.options], ['A1','A2','A3','B1','B2','B3','C1','C2','C3'])
            self.assertEqual(len({x['data-style'] for x in parser.options}), 3)
            self.assertEqual(len(parser.images), 9)
            self.assertTrue(all(x['src'].startswith('data:image/png;base64,') for x in parser.images))
            self.assertEqual(len({x['src'] for x in parser.images}), 1)
            self.assertEqual(len(parser.scripts), 1)
            self.assertNotIn('<标题>', build(frame, '<标题>|演示', '一句台词', ['甲','乙','丙'], '工具'))

    def test_presets_have_all_roles(self):
        for style in load_presets():
            self.assertEqual(len(style['palettes']), 3)
            self.assertEqual([p['id'] for p in style['palettes']], ['apricot','sky','lilac'])
            for palette in style['palettes']:
                self.assertNotEqual(palette['text'], palette['background'])

    def test_reject_non_image_and_long_copy(self):
        with tempfile.TemporaryDirectory() as d:
            frame = Path(d) / 'x.png'; frame.write_bytes(b'not-image')
            with self.assertRaises(ValueError): build(frame, '标题', '字幕', ['甲','乙','丙'], '工具')
            frame.write_bytes(b'\x89PNG\r\n\x1a\n')
            with self.assertRaises(ValueError): build(frame, '很长' * 30, '字幕', ['甲','乙','丙'], '工具')
            with self.assertRaises(ValueError): build(frame, '标题', '字幕', ['甲'], '工具')

    def test_demo_excludes_private_frame(self):
        with self.assertRaises(ValueError): build(__file__, demo=True)
        document = build(demo=True)
        self.assertIn('通用人物示意', document)
        self.assertNotIn('data:image/png;base64,', document)


if __name__ == '__main__': unittest.main()
