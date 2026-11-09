import hashlib,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/talking-head-finish';sys.path.insert(0,str(S/'scripts'))
import studio,matting,showreel
spec=importlib.util.spec_from_file_location('curated_installer',ROOT/'install_skill.py');installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
class CuratedWorkflow(unittest.TestCase):
 def test_rejected_mg_cannot_render_but_all_confirmed_mg_can(self):
  allowed=[x['id'] for x in studio.read(S/'references/approved-effects.json')['effects'] if x['mode']=='mg']
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);plan=dict(status='ready',fps=60,width=1920,height=1080,frames=120,presenter=None,scenes=[dict(id='scene',start=0,frames=120,kind='mg')])
   for effect in allowed:
    plan['scenes'][0]['variant']=effect;self.assertTrue(studio.validate(p,plan))
   for effect in ['Definition','RequirementsUI','G1-Capacity','G1-Packet']:
    plan['scenes'][0]['variant']=effect
    with self.assertRaises(ValueError):studio.validate(p,plan)
 def test_mask_counts_when_lossless_container_has_no_nb_frames(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'public').mkdir();(p/'public/mask.mkv').touch()
   plan=dict(status='ready',fps=60,width=1920,height=1080,frames=120,presenter=None,mask='mask.mkv',scenes=[dict(id='s',start=0,frames=120,kind='side')])
   with patch.object(studio,'probe',return_value=dict(streams=[dict(codec_type='video')])),patch.object(studio.subprocess,'check_output',return_value=b'{"streams":[{"nb_read_frames":"120"}]}'):
    self.assertTrue(studio.validate(p,plan))
   with patch.object(studio,'probe',return_value=dict(streams=[dict(codec_type='video',nb_frames='1')])):
    with self.assertRaises(ValueError):studio.validate(p,plan)
 def test_background_review_is_required_before_final_export(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);plan=dict(status='ready',fps=60,width=1920,height=1080,frames=120,presenter=None,background='didala-purple',scenes=[dict(id='s',start=0,frames=120,kind='side')])
   with self.assertRaises(ValueError):studio.validate(p,plan)
   (p/'matting').mkdir();studio.save(p/'matting/matting-record.json',dict(status='reviewed'))
   self.assertTrue(studio.validate(p,plan))
 def test_speech_boundary_reel_keeps_complete_short_mechanism(self):
  scenes=[dict(id='m',start=0,frames=540,kind='mg',variant='P2-Packet'),dict(id='s',start=540,frames=600,kind='side')]
  rows=[dict(start=0,end=9,text='完整动作'),dict(start=9.2,end=11.5,text='一句'),dict(start=11.6,end=15.5,text='第二句'),dict(start=15.6,end=17,text='不截断此句')]
  cuts=showreel.pick(dict(scenes=scenes),rows)
  self.assertEqual(cuts[0]['frames'],540);self.assertAlmostEqual((cuts[1]['start']+cuts[1]['frames'])/60,15.5)
 def test_managed_upgrade_backups_original_and_preserves_local_edits(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'skills/talking-head-finish';installer.install(target)
   old=target/'SKILL.md';old.write_bytes(old.read_bytes()+b'\nprior managed content\n');before=old.read_bytes()
   receipt=studio.read(target/installer.RECEIPT);receipt['version']='0.1.2-preview';receipt['files']['SKILL.md']=hashlib.sha256(before).hexdigest();studio.save(target/installer.RECEIPT,receipt)
   out=installer.install(target,upgrade=True);self.assertEqual(out['status'],'upgraded');self.assertEqual((Path(out['backup'])/'SKILL.md').read_bytes(),before)
   old=target/'SKILL.md';old.write_bytes(old.read_bytes()+b'\nuser edit\n');before=old.read_bytes()
   with self.assertRaises(ValueError):installer.install(target,upgrade=True)
   self.assertEqual(old.read_bytes(),before)
 def test_placement_preserves_visible_subject_and_bottom_anchor(self):
  s,x,y=matting.placement([400,100,1300,1080],'right')
  self.assertGreaterEqual(x+s*400,0);self.assertLessEqual(x+s*1300,1920);self.assertAlmostEqual(y+s*1080,1080,delta=1)
if __name__=='__main__':unittest.main()
