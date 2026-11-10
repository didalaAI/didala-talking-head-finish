"""Install the complete skill; preserve private/unmanaged installations."""
from pathlib import Path
import argparse, hashlib, json, os, tempfile, shutil
from datetime import datetime

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'skills/talking-head-finish'
VERSION = '0.3.0'
REPOSITORY = 'https://github.com/didalaAI/didala-talking-head-finish'
RECEIPT = '.installation.json'
EXCLUDED = {'__pycache__', 'node_modules', '.git', '.env', '.venv'}


def files(folder):
    return sorted(p for p in folder.rglob('*') if p.is_file()
                  and not any(x in EXCLUDED for x in p.relative_to(folder).parts)
                  and p.suffix != '.pyc' and not p.name.startswith('config.local')
                  and p.name != RECEIPT)


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def payload(host):
    result = {}
    for p in files(SOURCE):
        if p.is_symlink():
            raise ValueError('The source must contain real files, not symlinks')
        result[p.relative_to(SOURCE).as_posix()] = p.read_bytes()
    if host == 'workbuddy':
        text = result['SKILL.md'].decode('utf-8')
        _, head, body = text.split('---', 2)
        head += ('display_name: 迪达拉口播成片\n'
                 'display_name_en: Didala Talking Head Finish\n'
                 'description_zh: 用自己的口播和SRT制作语义动效成片，按可用后端选择制作方式。\n'
                 'description_en: Produce semantic talking-head motion graphics from your video and SRT.\n'
                 'version: "0.3.0"\nauthor: "didalaAI"\n')
        result['SKILL.md'] = ('---' + head + '---' + body).encode('utf-8')
    required = ['scripts/studio.py', 'scripts/capabilities.py', 'references/first-run.md',
                'assets/template/public/SourceHanSansCN-700.otf',
                'assets/template/public/SourceHanSansCN-900.otf']
    if not all(x in result for x in required):
        raise ValueError('Incomplete source: install the complete skill folder')
    return result


def verify(target, expected=None):
    target = Path(target).resolve()
    receipt = target / RECEIPT
    if not receipt.is_file():
        raise ValueError('Existing skill is unmanaged/private; nothing overwritten. Choose a separate target or use the host installer to review an update.')
    record = json.loads(receipt.read_text(encoding='utf-8'))
    if record.get('repository') != REPOSITORY or record.get('schema') != 1 or not record.get('files'):
        raise ValueError('Unknown installation receipt; nothing overwritten')
    actual = {}
    for p in files(target):
        if p.is_symlink():
            raise ValueError('Installed symlink cannot be verified')
        actual[p.relative_to(target).as_posix()] = digest(p)
    if actual != record['files']:
        raise ValueError('Installed files differ from their receipt; preserve local edits and review the update. Nothing overwritten.')
    if expected is not None and actual != expected:
        raise ValueError('A different managed version exists. Install to a separate target or review an update with your host installer; nothing overwritten.')
    return dict(status='verified', version=record['version'], host=record['host'],
                files=len(actual), target=str(target), runtime_checked=False)


def install(target, host='codex', upgrade=False):
    if Path(target).is_symlink():raise ValueError('Use the real host installation folder; symlink targets are not replaced')
    target = Path(target).expanduser().resolve()
    if target == SOURCE or target.is_relative_to(SOURCE) or SOURCE.is_relative_to(target):
        raise ValueError('Installation target must be separate from the source skill')
    data = payload(host)
    hashes = {name: hashlib.sha256(value).hexdigest() for name, value in data.items()}
    backup=None
    if target.exists():
        current=verify(target)
        if json.loads((target/RECEIPT).read_text(encoding='utf-8'))['files']==hashes:
            current['status']='already_installed';return current
        if not upgrade:raise ValueError('A different managed version exists; use --upgrade for a verified update with backup. Nothing overwritten.')
        backup_root=(target.parent.parent/'skill-backups').resolve()
        backup=backup_root/(target.name+'-'+current['version']+'-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        if not backup.resolve().is_relative_to(backup_root) or backup.exists():raise ValueError('Unsafe or occupied backup path')
    target.parent.mkdir(parents=True, exist_ok=True)
    # Only this newly created staging directory is cleaned; never an existing skill.
    with tempfile.TemporaryDirectory(prefix='.talking-head-install-', dir=target.parent) as temporary:
        stage = Path(temporary).resolve() / 'skill'
        for name, value in data.items():
            p = stage / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(value)
        (stage / RECEIPT).write_text(json.dumps(dict(schema=1, repository=REPOSITORY,
            version=VERSION, host=host, files=hashes), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        verify(stage, hashes)
        if backup:
            for local_config in target.glob('config.local*'):
                if local_config.is_file() and not local_config.is_symlink():shutil.copy2(local_config,stage/local_config.name)
            backup.parent.mkdir(parents=True,exist_ok=True)
            # Both resolved paths are fixed to the selected install folder and the dedicated backup root.
            target.rename(backup)
        try:stage.rename(target)
        except OSError:
            if backup and not target.exists():backup.rename(target)
            raise
    result = verify(target, hashes)
    result['status'] = 'upgraded' if backup else 'installed'
    if backup:result['backup']=str(backup)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', type=Path, help='Exact skill folder in the actual host skill location')
    p.add_argument('--host', choices=['codex', 'workbuddy', 'doubao-work', 'generic'], default='codex')
    p.add_argument('--legacy-codex-home', action='store_true')
    p.add_argument('--verify', action='store_true', help='Verify the receipt without changing files')
    p.add_argument('--upgrade', action='store_true', help='Update an unchanged managed installation, retaining a verified backup')
    a = p.parse_args()
    try:
        if a.legacy_codex_home and a.host != 'codex':
            raise ValueError('--legacy-codex-home only applies to Codex')
        codex_root = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
        if a.target is None:
            if a.host != 'codex':
                raise ValueError('Use the actual host installer/location and pass --target; no cross-host path is guessed')
            if not a.legacy_codex_home and (codex_root / 'skills/talking-head-finish').exists():
                raise ValueError('Legacy same-name skill exists; preserve it and choose --target explicitly')
            a.target = (codex_root / 'skills' if a.legacy_codex_home else Path.home() / '.agents/skills') / 'talking-head-finish'
        result = verify(a.target) if a.verify else install(a.target, a.host,a.upgrade)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError) as error:
        p.exit(1, 'ERROR: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
