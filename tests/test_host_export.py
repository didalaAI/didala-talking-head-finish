import hashlib,importlib.util,json,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('host_export',ROOT/'scripts/export_host_skill.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class HostExportTests(unittest.TestCase):
    def test_both_bootstrap_archives_keep_resource_limits_and_truthful_scope(self):
        with tempfile.TemporaryDirectory() as d:
            for host in m.HOSTS:
                p=Path(d)/(host+'.zip');report=m.export(host,p)
                with zipfile.ZipFile(p) as z:
                    self.assertIsNone(z.testzip());self.assertLess(sum(x.file_size for x in z.infolist()),16*1024*1024)
                    self.assertTrue(all(x.file_size<2*1024*1024 for x in z.infolist()))
                    self.assertFalse(any(x.filename.endswith(('.otf','.mp4','.gguf','.pth')) for x in z.infolist()))
                    r=json.loads(z.read('talking-head-finish-'+host+'/runtime-location.json'))
                    self.assertTrue(r['bootstrap_only']);self.assertFalse(r['runtime_included']);self.assertFalse(r['host_end_to_end_tested'])
                    self.assertIn('/didalaAI/',r['repository'])
    def test_workbuddy_frontmatter_has_official_market_display_fields(self):
        _,files=m.content('workbuddy');head=files['SKILL.md'].split('---',2)[1]
        for field in ['name','display_name','display_name_en','description','description_zh','description_en','version','author']:
            self.assertRegex(head,r'(?m)^'+field+r':')
    def test_refuse_existing_or_source_tree_output(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'user.zip';p.write_bytes(b'keep')
            with self.assertRaises(ValueError):m.export('workbuddy',p)
            self.assertEqual(p.read_bytes(),b'keep')
        with self.assertRaises(ValueError):m.export('workbuddy',ROOT/'unexpected.zip')
    def test_export_preserves_complete_core_font_files(self):
        fonts=list((ROOT/'skills/talking-head-finish/assets/template/public').glob('*.otf'))
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in fonts};self.assertEqual(len(before),2)
        with tempfile.TemporaryDirectory() as d:m.export('doubao-work',Path(d)/'host.zip')
        self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in fonts})
if __name__=='__main__':unittest.main()
