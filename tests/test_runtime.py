import importlib.util,json,os,tempfile,threading,unittest
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'skills/talking-head-finish/scripts'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
studio=load('studio');generate=load('generate')

class PlanTests(unittest.TestCase):
    def test_srt_clock_and_multiline(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.srt';p.write_text('1\n00:01:02,125 --> 00:01:04,000\n第一行\n第二行',encoding='utf-8')
            self.assertEqual(studio.srt_rows(p),[dict(start=62.125,end=64,text='第一行\n第二行')])
    def test_reject_empty_and_reversed_srt(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.srt'
            for value in ['', '1\n00:00:04,000 --> 00:00:01,000\n错误']:
                p.write_text(value,encoding='utf-8')
                with self.assertRaises(ValueError):studio.srt_rows(p)
    def test_plan_gap_and_missing_dynamic_mask(self):
        plan=dict(status='ready',fps=60,width=1920,height=1080,frames=60,presenter=None,scenes=[dict(id='a',start=1,frames=60,kind='side')])
        with self.assertRaises(ValueError):studio.validate(Path('.'),plan)
        with tempfile.TemporaryDirectory() as d:
            project=Path(d);(project/'public').mkdir();(project/'public/source.mp4').touch()
            plan['presenter']='source.mp4';plan['scenes'][0].update(start=0,through_body=True)
            with self.assertRaisesRegex(ValueError,'dynamic person mask'):studio.validate(project,plan)
    def test_reject_fractional_frames_and_negative_sound(self):
        plan=dict(status='ready',fps=60,width=1920,height=1080,frames=60,scenes=[dict(id='a',start=0,frames=60.0,kind='side')])
        with self.assertRaises(ValueError):studio.validate(Path('.'),plan)
        plan['scenes'][0]['frames']=60;plan['sound_events']=[dict(at=-1,kind='tick')]
        with self.assertRaises(ValueError):studio.validate(Path('.'),plan)
    def test_media_preview_cannot_escape(self):
        plan=dict(status='ready',fps=60,width=1920,height=1080,frames=60,mediaPreview='../../private.mp4',scenes=[])
        with self.assertRaises(ValueError):studio.validate(Path('.'),plan)
    def test_assets_cannot_escape_project(self):
        with self.assertRaises(ValueError):studio.inside(Path('.').resolve(),'../../private.png')
    def test_init_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'user.txt').write_text('keep')
            with self.assertRaises(ValueError):studio.init(p,demo=True)
            self.assertEqual((p/'user.txt').read_text(),'keep')

class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.calls=[];self.submits=0;self.redirect_headers=[];outer=self
        class Redirect(BaseHTTPRequestHandler):
            def do_GET(self):
                outer.redirect_headers.append(dict(self.headers));self.send_response(200);self.end_headers();self.wfile.write(b'media')
            def log_message(self,*a):pass
        self.target=ThreadingHTTPServer(('127.0.0.1',0),Redirect);threading.Thread(target=self.target.serve_forever,daemon=True).start()
        class Handler(BaseHTTPRequestHandler):
            def answer(self,obj,status=200):
                self.send_response(status);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(obj).encode())
            def do_POST(self):
                body=self.rfile.read(int(self.headers.get('Content-Length',0)));outer.calls.append((self.path,dict(self.headers),body))
                if self.path.endswith('/upload/image'):self.answer({'name':'hash-input.png','subfolder':'ignored-for-cloud'})
                elif self.path.endswith('/prompt'):outer.submits+=1;self.answer({'prompt_id':'job-1'})
                else:self.answer({'private':'do not disclose secret body'},402)
            def do_GET(self):
                outer.calls.append((self.path,dict(self.headers),b''))
                if '/history' in self.path:self.answer({'job-1':{'status':{'completed':True},'outputs':{'15':{'images':[{'filename':'clip.mp4','type':'output'}]}}}})
                elif '/view' in self.path:
                    self.send_response(302);self.send_header('Location',f'http://127.0.0.1:{outer.target.server_port}/signed');self.end_headers()
                else:self.answer({'error':'do not disclose secret body'},402)
            def log_message(self,*a):pass
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=self.server.serve_forever,daemon=True).start();os.environ['DIDALA_TEST_KEY']='test-only-not-a-real-key'
        self.client=generate.Client(f'http://127.0.0.1:{self.server.server_port}/api','cloud','DIDALA_TEST_KEY')
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.target.shutdown();self.target.server_close();os.environ.pop('DIDALA_TEST_KEY',None)
    def test_cloud_history_auth_upload_and_resume(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'keyframe.png').write_bytes(b'png-protocol-fixture')
            self.assertEqual(self.client.upload(p/'keyframe.png'),'hash-input.png')
            workflow={'1':{'class_type':'test','inputs':{}}};receipt=p/'receipt.json'
            self.client.job(workflow,receipt);self.client.job(workflow,receipt)
            self.assertEqual(self.submits,1)
            self.assertTrue(any(c[0]=='/api/history_v2/job-1' for c in self.calls))
            self.assertTrue(all(c[1].get('X-Api-Key')=='test-only-not-a-real-key' for c in self.calls))
            with self.assertRaises(ValueError):self.client.job({'different':{}},receipt)
    def test_redirect_does_not_leak_api_key(self):
        self.assertEqual(self.client.request('/view?filename=clip.mp4',raw=True),b'media')
        self.assertNotIn('X-Api-Key',self.redirect_headers[0])
    def test_generate_utf8_provenance_resumes_without_upload_or_submit(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'image.png').write_bytes(b'protocol-fixture')
            (p/'workflow.json').write_text(json.dumps({str(i):{'inputs':{}} for i in [1,5,6]}),encoding='utf-8')
            (p/'config.json').write_text(json.dumps(dict(base_url=self.client.base,provider='cloud',key_env='DIDALA_TEST_KEY',workflow='workflow.json')),encoding='utf-8')
            for _ in range(2):generate.generate(p/'config.json',p/'image.png','中文镜头：纸张交接',p/'shot')
            self.assertEqual(self.submits,1)
            self.assertEqual(sum(c[0].endswith('/upload/image') for c in self.calls),1)
            self.assertEqual(json.loads((p/'shot/generation.json').read_text(encoding='utf-8'))['action_review'],'pending')
    def test_http_failure_does_not_print_private_body(self):
        with self.assertRaises(RuntimeError) as error:self.client.request('/fail')
        self.assertNotIn('secret',str(error.exception));self.assertIn('402',str(error.exception))

if __name__=='__main__':unittest.main()
