"""Installation integrity and explicit optional-generation choices, without GPUs."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
import contextlib, importlib.util, io, json, os, sys, tempfile, threading, unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/talking-head-finish/scripts'))
import capabilities
import studio
spec = importlib.util.spec_from_file_location('installer', ROOT / 'install_skill.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallationTests(unittest.TestCase):
    def test_full_install_repeat_and_self_containment(self):
        with tempfile.TemporaryDirectory(prefix='安装 test ') as temporary:
            target = Path(temporary) / 'skills/talking-head-finish'
            result = installer.install(target)
            self.assertEqual(result['status'], 'installed')
            self.assertFalse(result['runtime_checked'])
            self.assertEqual(installer.install(target)['status'], 'already_installed')
            self.assertGreater((target / 'assets/template/public/SourceHanSansCN-900.otf').stat().st_size, 8_000_000)
            self.assertTrue((target / 'scripts/capabilities.py').is_file())
            self.assertTrue((target / 'references/first-run.md').is_file())
            with contextlib.redirect_stdout(io.StringIO()):
                studio.init(Path(temporary) / 'demo', demo=True)
            self.assertFalse((Path(temporary) / 'demo/production-choice.json').exists())

    def test_preserve_private_and_locally_edited_skills(self):
        with tempfile.TemporaryDirectory() as temporary:
            private = Path(temporary) / 'private'
            private.mkdir()
            (private / 'SKILL.md').write_text('private-custom-skill')
            with self.assertRaisesRegex(ValueError, 'unmanaged/private'):
                installer.install(private)
            self.assertEqual((private / 'SKILL.md').read_text(), 'private-custom-skill')
            target = Path(temporary) / 'public'
            installer.install(target)
            (target / 'SKILL.md').write_text('my customized instructions')
            with self.assertRaisesRegex(ValueError, 'local edits'):
                installer.install(target)
            self.assertEqual((target / 'SKILL.md').read_text(), 'my customized instructions')

    def test_missing_resource_is_not_verified_and_source_is_protected(self):
        with self.assertRaises(ValueError):
            installer.install(installer.SOURCE)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / 'public'
            installer.install(target)
            (target / 'assets/template/public/SourceHanSansCN-700.otf').unlink()
            with self.assertRaises(ValueError):
                installer.verify(target)

    def test_workbuddy_complete_install_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / 'full-skill'
            installer.install(target, 'workbuddy')
            text = (target / 'SKILL.md').read_text(encoding='utf-8')
            self.assertIn('display_name: 迪达拉口播成片', text)
            self.assertIn('references/first-run.md', text)
            self.assertNotIn('本包只提供入口', text)
            self.assertEqual(installer.install(target, 'workbuddy')['status'], 'already_installed')


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.metadata = {'MiniMaxH3ImageToVideo': {'input': {'required': {}}},
                         'UnetLoaderGGUF': {'input': {'required': {'unet_name': [['fixture.gguf']]}}}}
        outer = self
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                outer.calls.append(('GET', self.path))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(outer.metadata).encode())
            def do_POST(self):
                outer.calls.append(('POST', self.path))
                self.send_error(405)
            def log_message(self, *args):
                pass
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.workflow = {'1': {'class_type': 'MiniMaxH3ImageToVideo', 'inputs': {}},
                         '2': {'class_type': 'UnetLoaderGGUF', 'inputs': {'unet_name': 'fixture.gguf'}}}
        self.config = dict(provider='local', base_url=f'http://127.0.0.1:{self.server.server_port}', workflow='workflow.json')

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.temp.cleanup()

    def probe(self):
        for name, value in [('workflow.json', self.workflow), ('config.json', self.config)]:
            (self.folder / name).write_text(json.dumps(value), encoding='utf-8')
        return capabilities.inspect(self.folder / 'config.json')

    def test_probe_is_get_only_and_does_not_claim_generation_passed(self):
        result = self.probe()
        self.assertEqual(self.calls, [('GET', '/object_info')])
        self.assertEqual(result['backend']['status'], 'compatible_metadata')
        self.assertFalse(result['backend']['generation_tested'])
        self.assertFalse(result['backend']['task_submitted'])
        self.assertTrue(result['selection_required'])

    def test_missing_models_or_split_nodes_offer_choices_without_fallback(self):
        self.metadata['UnetLoaderGGUF']['input']['required']['unet_name'] = [['other-model.gguf']]
        self.config['split_conditioning'] = True
        result = self.probe()
        self.assertEqual(result['backend']['status'], 'needs_configuration')
        self.assertIn('H3SaveConditioning', result['backend']['missing_nodes'])
        self.assertTrue(result['backend']['missing_options'])
        self.assertEqual({c['mode'] for c in result['choices']}, {'motion', 'cloud', 'other', 'defer'})
        self.assertNotIn('selected_mode', result)

    def test_unknown_model_options_are_not_assumed_available(self):
        self.metadata['UnetLoaderGGUF'] = {}
        result = self.probe()
        self.assertEqual(result['backend']['status'], 'needs_configuration')
        self.assertTrue(result['backend']['unverified_models'])

    def test_cloud_key_does_not_imply_ready_or_trigger_request(self):
        self.config.update(provider='cloud', base_url='https://cloud.comfy.org/api', key_env='DIDALA_PROBE_TEST')
        with patch.dict(os.environ, {'DIDALA_PROBE_TEST': 'not-a-real-key-private-fixture'}):
            result = self.probe()
        self.assertEqual(result['backend']['status'], 'needs_cloud_verification')
        self.assertTrue(result['backend']['credential_present'])
        self.assertNotIn('private-fixture', json.dumps(result))
        self.assertFalse(self.calls)

    def test_arbitrary_remote_local_probe_is_refused(self):
        self.config['base_url'] = 'http://example.invalid'
        result = self.probe()
        self.assertEqual(result['backend']['status'], 'not_detected')
        self.assertTrue(result['selection_required'])
        self.assertFalse(self.calls)


class ChoiceTests(unittest.TestCase):
    def test_unselected_and_deferred_cannot_export_final_and_change_retains_choice(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / 'plan.json').write_text('{}')
            (project / 'production-choice.json').write_text('{"mode": null}')
            with self.assertRaisesRegex(ValueError, 'select a production mode'):
                capabilities.validate_choice(project)
            capabilities.choose(project, 'defer', '用户稍后补动画')
            with self.assertRaisesRegex(ValueError, 'deferred'):
                capabilities.validate_choice(project)
            with self.assertRaises(ValueError):
                capabilities.choose(project, 'motion')
            with self.assertRaises(ValueError):
                capabilities.change(project, 'motion', '')
            result = capabilities.change(project, 'motion', '用户改选动态MG完成整片')
            self.assertEqual(result['history'][0]['mode'], 'defer')
            capabilities.validate_choice(project)
            self.assertFalse(result['backend_verified'])

    def test_real_input_initialization_requires_explicit_mode(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            (folder / 'video.mp4').write_bytes(b'input fixture')
            (folder / 'video.srt').write_text('1\n00:00:00,000 --> 00:00:00,500\n原字幕', encoding='utf-8')
            metadata = {'format': {'duration': '1'}, 'streams': [{'codec_type': 'video', 'duration': '1'}]}
            with patch.object(studio, 'probe', return_value=metadata), patch.object(studio, 'run'), contextlib.redirect_stdout(io.StringIO()):
                studio.init(folder / 'project', folder / 'video.mp4', folder / 'video.srt')
            result = json.loads((folder / 'project/production-choice.json').read_text(encoding='utf-8'))
            self.assertIsNone(result['mode'])
            self.assertTrue(result['user_choice_required'])

    def test_doctor_missing_base_dependencies_returns_nonzero(self):
        with patch.object(sys, 'argv', ['studio.py', 'doctor']), patch.object(studio, 'doctor', return_value={'base_ready': False}):
            with self.assertRaises(SystemExit) as result:
                studio.main()
            self.assertEqual(result.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
