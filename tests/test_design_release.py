import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import MagicMock
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'skills/talking-head-finish';sys.path.insert(0,str(S/'scripts'))
import design,generate,studio
class ReleaseDesignTests(unittest.TestCase):
 def test_exact_confirmation_and_no_rejected_route(self):
  receipt=design.read(S/'references/selection-receipt.json');catalog=design.effects()
  self.assertEqual(receipt['revision'],159);self.assertEqual(len(catalog),39)
  self.assertEqual(set(catalog),{x['id'] for x in receipt['keep']})
  self.assertFalse(set(catalog)&set(receipt['exclude_ids']))
  for x in receipt['keep']:self.assertEqual(catalog[x['id']]['frequency'],x['frequency'])
 def test_no_unreviewed_copy_or_wrong_timing_or_outside_paths(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);spec=design.example('V3-P2-Capacity');scene=dict(variant=spec['effect'],kind='mg',frames=round(spec['duration']*60))
   with self.assertRaises(ValueError):design.validate_spec(p,scene,spec)
   spec.update(semantic_alignment='本期示例动作',reviewed_for_current_script=True);self.assertTrue(design.validate_spec(p,scene,spec))
   spec['timing'][-1][1]+=1
   with self.assertRaises(ValueError):design.validate_spec(p,scene,spec)
   with self.assertRaises(ValueError):design.inside(p,'../private.json')
 def test_empty_successful_comfy_response_is_not_json_error(self):
  client=generate.Client('http://127.0.0.1:8190');response=MagicMock();response.__enter__.return_value.read.return_value=b'';client.op.open=MagicMock(return_value=response)
  self.assertEqual(client.request('/free',{'unload_models':True}),{})
  self.assertEqual(client.request('/view',raw=True),b'')
 def test_public_sources_and_keyframes_travel_with_skill(self):
  for e in design.effects().values():self.assertTrue((S/e['code_entry']).is_file());self.assertTrue((S/e['example']).is_file())
  recipes=design.read(S/'references/h3-shot-recipes.json');self.assertEqual(len(recipes),12)
  for recipe in recipes:
   if str(recipe.get('keyframe','')).startswith('assets/'):self.assertTrue((S/recipe['keyframe']).is_file())
 def test_caption_emphasis_keeps_words_and_rejects_invented_copy(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);rows=[dict(start=0,end=2,text='突出重点，保持原文')]
   studio.save(p/'plan.json',dict(caption_emphasis=[dict(start=0,words=['重点'])]));studio.ass(p,rows)
   text=(p/'captions.ass').read_text('utf-8');self.assertIn(r'{\fs58\c&H007EC7F0&}重点{\r}',text)
   studio.save(p/'plan.json',dict(caption_emphasis=[dict(start=0,words=['虚构词'])]))
   with self.assertRaises(ValueError):studio.ass(p,rows)
if __name__=='__main__':unittest.main()
