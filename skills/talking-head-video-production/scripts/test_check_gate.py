from pathlib import Path
import copy
import json
import tempfile
import unittest
from check_gate import check, sha256, template_hash

class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.path=self.root/'project.json'
        (self.root/'audio.wav').write_bytes(b'test-only-audio-not-real')
        (self.root/'board.html').write_text('test-only-board',encoding='utf-8')
        base=dict(status='approved',project_id='test-fixture',timeline_revision='v1',evidence=dict(role='user',quote='TEST FIXTURE approval',message_id='fixture-only'))
        self.project=dict(project_id='test-fixture',timeline_revision='v1',audio=dict(path='audio.wav',sha256=sha256(self.root/'audio.wav')),style_board=dict(path='board.html',sha256=sha256(self.root/'board.html')))
        self.project['approvals']=dict(G1_audio=dict(**copy.deepcopy(base),audio_sha256=self.project['audio']['sha256']),G2_style_palette=dict(**copy.deepcopy(base),style_id='tactile',palette_id='sky',choice='A2',template_sha256=template_hash(),board_sha256=self.project['style_board']['sha256']))
    def run_check(self,stage='render',scene=None):
        self.path.write_text(json.dumps(self.project),encoding='utf-8'); return check(self.path,stage,scene)
    def test_valid(self): self.run_check(scene=dict(style_id='tactile',palette_id='sky'))
    def test_no_g2(self):
        del self.project['approvals']['G2_style_palette']
        self.run_check('style')
        with self.assertRaises(ValueError): self.run_check()
    def test_partial_selection(self):
        del self.project['approvals']['G2_style_palette']['palette_id']
        with self.assertRaises(ValueError): self.run_check()
    def test_assistant_is_not_user(self):
        self.project['approvals']['G2_style_palette']['evidence']['role']='assistant'
        with self.assertRaises(ValueError): self.run_check()
    def test_audio_changed(self):
        (self.root/'audio.wav').write_bytes(b'changed')
        with self.assertRaises(ValueError): self.run_check()
    def test_timeline_changed(self):
        self.project['timeline_revision']='v2'
        with self.assertRaises(ValueError): self.run_check()
    def test_board_changed(self):
        (self.root/'board.html').write_text('changed',encoding='utf-8')
        with self.assertRaises(ValueError): self.run_check()
    def test_template_changed(self):
        self.project['approvals']['G2_style_palette']['template_sha256']='old'
        with self.assertRaises(ValueError): self.run_check()
    def test_mismatched_render(self):
        with self.assertRaises(ValueError): self.run_check(scene=dict(style_id='editorial',palette_id='sky'))
    def test_mismatched_choice(self):
        self.project['approvals']['G2_style_palette']['choice']='A1'
        with self.assertRaises(ValueError): self.run_check()
    def test_skip_requires_explicit_scope(self):
        g2=self.project['approvals']['G2_style_palette']; g2['status']='user_authorized_skip'
        with self.assertRaises(ValueError): self.run_check()
        g2['scope']='TEST FIXTURE delegate style and palette choice'; self.run_check()

if __name__=='__main__': unittest.main()
