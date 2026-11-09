"""Read-only backend preflight and explicit per-project production choice. Stdlib only."""
from pathlib import Path
import argparse, json, os, urllib.error, urllib.parse, urllib.request

SKILL = Path(__file__).resolve().parents[1]
MODES = ['motion', 'local-h3', 'cloud', 'other', 'defer']
CHOICES = [
    dict(mode='motion', label='动态 MG＋现有素材完成整片',
         detail='无需H3；按文意重新设计动作、运镜与图形，不用静图/PPT填充。'),
    dict(mode='cloud', label='接入自己的云端生成服务',
         detail='先确认服务、费用与素材上传；自备账号和可用工作流。'),
    dict(mode='other', label='使用当前 Agent 可调用的其他视频模型',
         detail='先确认具体工具、费用和上传范围；重新适配并审核动作，不保证和H3完全相同。'),
    dict(mode='defer', label='先完成其余部分，稍后补生成动画',
         detail='先做分镜、字幕、真人字效、MG与声音；缺失镜头单列，不把工作预览当最终成片。'),
]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('Metadata probe does not follow redirects')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def inspect_backend(config=None, timeout=3):
    path = Path(config).resolve() if config else SKILL / 'integrations/comfy-h3/local.example.json'
    report = dict(status='not_detected', provider='local', generation_tested=False,
                  task_submitted=False, metadata_only=True)
    try:
        cfg = read(path)
        provider = cfg.get('provider', 'local')
        report['provider'] = provider
        if provider not in ['local', 'cloud']:
            raise ValueError('Unsupported provider')
        parsed = urllib.parse.urlsplit(cfg['base_url'])
        if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.scheme not in ['http', 'https'] or not parsed.hostname:
            raise ValueError('Use a plain endpoint; credentials belong in environment variables')
        if provider == 'local' and parsed.hostname not in ['localhost', '127.0.0.1', '::1']:
            raise ValueError('Local auto-probe is loopback only; use the selected backend adapter for remote services')
        if provider == 'cloud':
            if parsed.scheme != 'https':
                raise ValueError('Cloud endpoint must use HTTPS')
            report['credential_present'] = bool(os.environ.get(cfg.get('key_env', 'COMFY_CLOUD_API_KEY')))
            report['status'] = 'needs_cloud_verification'
            report['reason'] = 'Cloud credentials/workflow must be checked after the user selects this service; no cloud request made'
            report['workflow_present'] = (path.parent / cfg['workflow']).is_file()
            return report
        workflow = read(path.parent / cfg['workflow'])
        if not isinstance(workflow, dict) or not workflow or 'nodes' in workflow:
            raise ValueError('Expected a nonempty API workflow')
        required = {node['class_type'] for node in workflow.values()}
        if not any('MiniMaxH3' in name for name in required):
            raise ValueError('The workflow does not identify an H3 generation node')
        if cfg.get('split_conditioning'):
            required.update(['H3SaveConditioning', 'H3LoadConditioning', 'EmptyMiniMaxH3LatentAV'])
        opener = urllib.request.build_opener(NoRedirect(), urllib.request.ProxyHandler({}))
        request = urllib.request.Request(cfg['base_url'].rstrip('/') + '/object_info', method='GET')
        with opener.open(request, timeout=timeout) as response:
            info = json.load(response)
        missing_nodes = sorted(required - info.keys())
        missing_options = []
        unverified_models = []
        for node in workflow.values():
            spec = info.get(node['class_type'], {}).get('input', {})
            inputs = {**spec.get('required', {}), **spec.get('optional', {})}
            for field, value in node.get('inputs', {}).items():
                descriptor = inputs.get(field, [])
                if field == 'image' or isinstance(value, (list, dict)):
                    continue
                if descriptor and isinstance(descriptor[0], list) and value not in descriptor[0]:
                    missing_options.append(node['class_type'] + '.' + field + ': ' + str(value))
                if field in ['clip_name', 'vae_name', 'unet_name', 'ckpt_name'] and not (descriptor and isinstance(descriptor[0], list)):
                    unverified_models.append(node['class_type'] + '.' + field)
        report.update(status='compatible_metadata' if not missing_nodes and not missing_options and not unverified_models else 'needs_configuration',
                      missing_nodes=missing_nodes, missing_options=missing_options, unverified_models=unverified_models,
                      reason='Metadata checks do not prove model loading, VRAM sufficiency or successful generation')
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        report.update(status='not_detected', reason='No compatible running endpoint detected, or configuration is invalid; this does not prove H3 is uninstalled')
    return report


def inspect(config=None):
    backend = inspect_backend(config)
    choices = list(CHOICES)
    if backend['status'] == 'compatible_metadata':
        choices.insert(0, dict(mode='local-h3', label='使用已检测到的本地 H3 工作流',
            detail='先做短镜头验证模型可加载和动作合格；失败后保留其他制作进度，并重新选择。'))
    return dict(schema=1, backend=backend, choices=choices, selection_required=True,
                instruction='Use the user’s existing explicit choice if present; otherwise ask once. No timed or automatic fallback.')


def choose(project, mode, note=''):
    if mode not in MODES:
        raise ValueError('Unknown production mode')
    project = Path(project).resolve()
    if not (project / 'plan.json').is_file():
        raise ValueError('Initialize the video project before saving its choice')
    file = project / 'production-choice.json'
    previous = read(file) if file.exists() else {}
    if previous.get('mode') and previous['mode'] != mode:
        raise ValueError('A mode is already selected. Use change with an explicit new user choice to preserve the history')
    if previous.get('mode') == mode:
        return previous
    record = dict(schema=1, mode=mode, note=note, user_choice_required=False,
                  history=previous.get('history', []), backend_verified=False)
    file.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return record


def change(project, mode, note):
    if mode not in MODES or not note.strip():
        raise ValueError('Changing the mode needs the user’s explicit new choice in --note')
    project = Path(project).resolve()
    file = project / 'production-choice.json'
    previous = read(file)
    history = previous.get('history', [])
    if previous.get('mode'):
        history.append({k: previous.get(k) for k in ['mode', 'note']})
    record = dict(schema=1, mode=mode, note=note, user_choice_required=False,
                  history=history, backend_verified=False)
    file.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return record


def validate_choice(project):
    file = Path(project) / 'production-choice.json'
    if not file.exists():
        return  # Legacy and code-only demo projects do not retroactively require a choice.
    mode = read(file).get('mode')
    if mode not in MODES:
        raise ValueError('Ask the user to select a production mode, then save it with capabilities.py choose')
    if mode == 'defer':
        raise ValueError('Generation is deferred: deliver work-in-progress and missing-shots list, not a final movie. Ask for the next choice when resuming.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    q = subs.add_parser('inspect')
    q.add_argument('--config', type=Path)
    for name in ['choose', 'change']:
        q = subs.add_parser(name)
        q.add_argument('--project', type=Path, required=True)
        q.add_argument('--mode', choices=MODES, required=True)
        q.add_argument('--note', default='', required=name == 'change')
    a = parser.parse_args()
    try:
        result = inspect(a.config) if a.command == 'inspect' else (
            choose(a.project, a.mode, a.note) if a.command == 'choose' else change(a.project, a.mode, a.note))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, 'ERROR: ' + str(error) + '\n')


if __name__ == '__main__':
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
