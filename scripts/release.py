"""Audit and package only public source; never bundle installed environments."""
from pathlib import Path
import argparse,hashlib,json,re,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
EXTENSIONS={'.md','.py','.tsx','.ts','.cjs','.json','.yaml','.yml','.txt','.otf','.png'}
NAMES={'LICENSE','.gitignore','.gitattributes','.env.example'}
TEXT_ASSETS={'examples/demo.srt','skills/talking-head-finish/assets/demo.srt'}
EXCLUDED={'.git','node_modules','__pycache__','.venv','projects','outputs','out'}

def source_files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(part in EXCLUDED for part in p.relative_to(ROOT).parts))

def audit():
    errors=[];files=source_files()
    required=['LICENSE','THIRD_PARTY_NOTICES.md','README.md','docs/VALIDATION.md','skills/talking-head-finish/SKILL.md','skills/talking-head-finish/LICENSE','skills/talking-head-finish/THIRD_PARTY_NOTICES.md']
    for value in required:
        if not (ROOT/value).is_file():errors.append('Missing required file: '+value)
    patterns=[re.compile(r'[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s\'"<>]+'),re.compile(r'\b(?:sk-[A-Za-z0-9]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b')]
    for p in files:
        rel=p.relative_to(ROOT).as_posix()
        if p.suffix.lower() not in EXTENSIONS and p.name not in NAMES and rel not in TEXT_ASSETS:errors.append('Unexpected source file: '+rel)
        if p.is_symlink():errors.append('Symlinks are not release source: '+rel)
        if p.stat().st_size>=100*1024*1024:errors.append('File exceeds repository limit: '+rel)
        if p.suffix.lower() in {'.otf','.png'}:continue
        content=p.read_text(encoding='utf-8-sig')
        if any(pattern.search(content) for pattern in patterns):errors.append('Potential private path or credential in '+rel)
        if p.suffix=='.md':
            for value in re.findall(r'\[[^\]]+\]\(([^)]+)\)',content):
                if re.match(r'^[a-z]+:',value) or value.startswith('#'):continue
                target=(p.parent/value.split('#')[0]).resolve()
                if not target.is_relative_to(ROOT) or not target.is_file():errors.append('Broken local link in '+rel+': '+value)
    if errors:raise ValueError('\n'.join(errors))
    result=dict(status='passed',files=len(files),source_bytes=sum(p.stat().st_size for p in files),media_bundled=False,background_images_bundled=sum(p.suffix.lower()=='.png' for p in files),model_weights_bundled=False,installed_environments_bundled=False)
    print(json.dumps(result,indent=2));return files,result

def package(destination):
    destination=destination.resolve()
    if destination.is_relative_to(ROOT):raise ValueError('Write release ZIP outside the source repository')
    if destination.exists():raise ValueError('Release file exists; choose a new filename')
    files,result=audit();destination.parent.mkdir(parents=True,exist_ok=True)
    manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:z.write(p,'didala-talking-head-finish/'+p.relative_to(ROOT).as_posix())
        z.writestr('didala-talking-head-finish/SOURCE_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    print('PACKAGED',destination.name,hashlib.sha256(destination.read_bytes()).hexdigest())

def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True);s.add_parser('audit');q=s.add_parser('package');q.add_argument('--out',type=Path,required=True);a=p.parse_args()
    try:
        if a.command=='audit':audit()
        else:package(a.out)
    except (ValueError,UnicodeError) as e:print('ERROR:',e,file=sys.stderr);raise SystemExit(1)
if __name__=='__main__':main()
