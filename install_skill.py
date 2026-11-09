"""Install this public skill without overwriting an existing private skill."""
from pathlib import Path
import argparse,os,shutil
codex_root=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path);p.add_argument('--legacy-codex-home',action='store_true',help='Use the older CODEX_HOME/skills location instead of ~/.agents/skills');a=p.parse_args()
if a.target is None and not a.legacy_codex_home and (codex_root/'skills/talking-head-finish').exists():raise SystemExit('A legacy skill with the same name exists. Keep your private version; choose --target explicitly for a separate test install.')
a.target=a.target or ((codex_root/'skills') if a.legacy_codex_home else (Path.home()/'.agents/skills'))/'talking-head-finish'
source=Path(__file__).resolve().parent/'skills/talking-head-finish';target=a.target.resolve()
if target.exists():raise SystemExit('Target already exists. Keep it or use --target with another skill folder; nothing overwritten.')
shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc','node_modules','.env','config.local*.json'))
print('INSTALLED',target)
