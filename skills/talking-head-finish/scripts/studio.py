"""Portable, standard-library CLI for authored talking-head video projects."""
from pathlib import Path
import argparse,array,hashlib,json,math,os,random,re,shutil,subprocess,sys,wave
from capabilities import validate_choice
from design import compile_project,validate_spec,inside as design_inside
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
SKILL=Path(__file__).resolve().parents[1]

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,obj):Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(argv,cwd=None):
    result=subprocess.run([str(x) for x in argv],cwd=cwd)
    if result.returncode:raise RuntimeError('Command failed; see the preceding diagnostic. Exit '+str(result.returncode))
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def srt_rows(path):
    text=Path(path).read_text(encoding='utf-8-sig').replace('\r\n','\n').strip()
    rows=[]
    def stamp(s):
        h,m,z=re.split(':',s);return int(h)*3600+int(m)*60+float(z.replace(',','.'))
    for block in re.split(r'\n\s*\n',text):
        lines=block.splitlines();i=next((i for i,s in enumerate(lines) if '-->' in s),-1)
        if i<0:raise ValueError('Invalid SRT block: missing timestamps')
        a,b=lines[i].split('-->');a,b=stamp(a.strip()),stamp(b.strip())
        if b<=a or a<0 or (rows and a<rows[-1]['start']):raise ValueError('Invalid or unsorted SRT times')
        rows.append(dict(start=a,end=b,text='\n'.join(lines[i+1:])))
    if not rows:raise ValueError('SRT is empty')
    return rows

def inside(project,asset):
    p=(project/'public'/asset).resolve()
    if not p.is_relative_to((project/'public').resolve()):raise ValueError('Assets must remain in project/public')
    return p

def validate(project,plan,require_ready=True):
    if require_ready and plan.get('status')!='ready':raise ValueError('This is a scaffold. Author the semantic scene plan and set status=ready after review.')
    if require_ready:validate_choice(project)
    if plan['fps']!=60 or [plan['width'],plan['height']]!=[1920,1080]:raise ValueError('This release currently supports 1920x1080 / 60fps')
    if type(plan['frames']) is not int or plan['frames']<=0:raise ValueError('Total frames must be a positive integer')
    for key in ['presenter','mediaPreview','foreground','audio_source']:
        if plan.get(key) and not inside(project,plan[key]).is_file():raise ValueError('Missing project asset: '+key)
    for event in plan.get('sound_events',[]):
        if not 0<=event['at']<plan['frames']/60:raise ValueError('Sound event is outside the movie')
        if event.get('kind','tick') not in ['whoosh','tick','paper']:raise ValueError('Unknown sound event kind')
    cursor=0;ids=set()
    for s in plan['scenes']:
        if s['id'] in ids:raise ValueError('Duplicate scene ID')
        ids.add(s['id'])
        if type(s['start']) is not int or type(s['frames']) is not int or s['start']!=cursor or s['frames']<=0:raise ValueError('Scene plan must cover the movie with integer frames, without gaps or overlaps')
        cursor+=s['frames']
        if s['kind'] not in ['side','punch','mg','h3','video','screen','promo']:raise ValueError('Unknown scene kind')
        if s.get('design'):
            spec=read(design_inside(project,s['design']))
            validate_spec(project,s,spec,plan.get('technical_demo',False))
            recipe=spec.get('recipe',{})
            if plan.get('presenter') and any(b.get('kind') in ['punch','hero'] for b in [recipe]+recipe.get('beats',[])) and not s.get('through_body'):raise ValueError('This confirmed choreography needs the current dynamic foreground/mask and through_body=true')
        if s['kind'] in ['mg','h3','screen'] or (s['kind'] in ['side','punch'] and (s.get('lines') or s.get('variant'))):
            if not s.get('design'):raise ValueError('Choose a confirmed effect and author its design spec; old default styles are retired')
        if s['kind']=='mg':
            allowed={x['id'] for x in read(SKILL/'references/approved-effects.json')['effects'] if x['mode']=='mg'}
            if s.get('variant',s['id']) not in allowed:raise ValueError('MG is not in the confirmed effect collection')
        if s.get('through_body') and plan.get('presenter') and not plan.get('mask'):raise ValueError('Through-body text requires a real dynamic person mask. No static-mask fallback.')
        if plan.get('presenter') and (s['kind']=='punch' or s.get('variant',s['id']) in ['V31-CapacityHuman','V31-ManageHuman','V31-ClosingHuman'] or any(b.get('kind') in ['punch','hero'] for b in s.get('beats',[]))) and not s.get('through_body'):raise ValueError('Presenter punch choreography must set through_body=true and use the current dynamic foreground/mask')
        last_beat=-1
        for beat in s.get('beats',[]):
            if beat['at']<0 or beat['at']<=last_beat or beat['at']>=s['frames']/60 or not beat.get('lines') or beat.get('kind','side') not in ['side','punch','cta','hero']:raise ValueError('Human beats require ordered in-scene timestamps and authored lines')
            last_beat=beat['at']
        for tag in s.get('tags',[]):
            if tag.get('at') is not None and not 0<=tag['at']<s['frames']/60:raise ValueError('Human tag is outside the scene')
            if tag.get('asset') and not inside(project,tag['asset']).is_file():raise ValueError('Missing this-episode tag image')
        if s['kind'] in ['h3','video']:
            p=inside(project,s.get('asset',''));v=next(x for x in probe(p)['streams'] if x['codec_type']=='video')
            if float(v.get('duration',0))+1/float(plan['fps'])<(s['frames']+s.get('trimBefore',0))/plan['fps']:raise ValueError('Generated clip is too short; freezing its tail is not allowed')
        if s['kind']=='screen' and not s.get('design'):
            cfg=s.get('screen',{})
            if not inside(project,cfg['asset']).is_file():raise ValueError('Missing original screenshot')
            if min(cfg['width'],cfg['height'])<=0:raise ValueError('Screenshot dimensions must be positive')
            x,y,w,h=cfg['focus']
            if x<0 or y<0 or min(w,h)<=0 or x+w>cfg['width'] or y+h>cfg['height']:raise ValueError('Focus rectangle is outside original screenshot')
    if cursor!=plan['frames']:raise ValueError('Plan length does not equal total frames')
    if plan.get('mask'):
        v=next(x for x in probe(inside(project,plan['mask']))['streams'] if x['codec_type']=='video')
        count=v.get('nb_frames')
        if not count or count=='N/A':
            counted=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=nb_read_frames','-of','json',str(inside(project,plan['mask']))]))
            count=counted['streams'][0].get('nb_read_frames',0)
        if int(count)<plan['frames']:raise ValueError('Mask must be a full-length moving video, not an image')
    if plan.get('background') and require_ready:
        record=project/'matting/matting-record.json'
        if not record.is_file() or read(record).get('status')!='reviewed':raise ValueError('Review moving hair, hands and person edges; then record matting status=reviewed before final export')
    return True

def write_data(project,plan,rows):
    compile_project(project,plan)
    (project/'src/data.ts').write_text("import {Plan} from './RuntimeContext';\nexport const plan:Plan="+json.dumps(plan,ensure_ascii=False)+";\nexport const captions:{start:number;end:number;text:string}[]="+json.dumps(rows,ensure_ascii=False)+";\n",encoding='utf-8')

def init(project,video=None,srt=None,demo=False):
    project=project.resolve()
    if project.exists() and any(project.iterdir()):raise ValueError('Use an empty/new project folder. Existing work is never overwritten.')
    shutil.copytree(SKILL/'assets/template',project,dirs_exist_ok=True)
    shutil.copytree(SKILL/'assets/backgrounds',project/'public/backgrounds',dirs_exist_ok=True)
    if demo:
        shutil.copytree(SKILL/'assets/demo-designs',project/'designs',dirs_exist_ok=True)
        plan=read(SKILL/'assets/demo-plan.json');shutil.copy2(SKILL/'assets/demo.srt',project/'original.srt')
    else:
        if not video or not srt:raise ValueError('init requires --video and --srt')
        video=video.resolve();srt=srt.resolve();info=probe(video);duration=float(info['format']['duration']);frames=math.ceil(duration*60-1e-7)
        video_duration=float(next(s for s in info['streams'] if s['codec_type']=='video').get('duration',duration))
        if duration-video_duration>.2:raise ValueError('Source audio/video tail difference exceeds 0.2 seconds; review the input edit first.')
        source=project/'public/source.mp4'
        run(['ffmpeg','-v','error','-y','-i',video,'-vf','scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=60,tpad=stop_mode=clone:stop_duration=0.2','-t',str(duration),'-c:v','libx264','-crf','16','-preset','fast','-c:a','aac','-b:a','192k',source])
        shutil.copy2(srt,project/'original.srt')
        save(project/'source-record.json',dict(original_srt_sha256=sha(srt),original_video_sha256=sha(video),source_duration=duration,speed=1.0))
        plan=dict(version=1,status='needs_authoring',fps=60,width=1920,height=1080,frames=frames,presenter='source.mp4',mask=None,scenes=[dict(id='author-this-scene',start=0,frames=frames,kind='side',eyebrow='请按本期文案重新设计',lines=['本期重点'])])
    rows=srt_rows(project/'original.srt');save(project/'plan.json',plan);save(project/'captions.json',rows);write_data(project,plan,rows)
    if not demo:save(project/'production-choice.json',dict(schema=1,mode=None,user_choice_required=True,history=[]))
    print('INITIALIZED',project,'status='+plan['status'])

def setup(project,pm='auto'):
    chosen=shutil.which('npm') if pm in ['auto','npm'] else None
    if chosen:run([chosen,'ci','--ignore-scripts'],project)
    else:
        chosen=shutil.which('pnpm') if pm in ['auto','pnpm'] else None
        if not chosen:raise ValueError('Install an official Node.js distribution with npm, or pnpm; neither package manager was found.')
        run([chosen,'import'],project);run([chosen,'install','--frozen-lockfile','--ignore-scripts'],project)
    node=shutil.which('node')
    if not node:raise ValueError('Node.js was not found')
    run([node,project/'node_modules/typescript/bin/tsc','--noEmit'],project)
    save(project/'setup-record.json',dict(manager=Path(chosen).name,package_lock_sha256=sha(project/'package-lock.json'),runtime_lock='4.0.539',isolated_project=True))

def ass(project,rows):
    def stamp(t):
        cs=round(t*100);h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100);return f'{h}:{m:02}:{s:02}.{cs:02}'
    head='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Source Han Sans CN,52,&H00FFFAFC,&H00302016,&H00302016,&H500C0914,-1,0,0,0,100,100,0,0,1,2,1.3,2,80,80,89,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    marks=read(project/'plan.json').get('caption_emphasis',[]) if (project/'plan.json').exists() else []
    for mark in marks:
        row=next((r for r in rows if abs(r['start']-mark['start'])<.001),None)
        if not row or not 1<=len(mark['words'])<=2 or any(not w or w not in row['text'] for w in mark['words']):raise ValueError('Caption emphasis must match one or two actual words at an original SRT cue start')
    for row in rows:
        text=row['text'].replace('\\','／').replace('{','（').replace('}','）').replace('\n',r'\N')
        words=next((m['words'] for m in marks if abs(m['start']-row['start'])<.001),[])
        if words:
            escaped=[w.replace('\\','／').replace('{','（').replace('}','）').replace('\n',r'\N') for w in words]
            text=re.sub('|'.join(re.escape(w) for w in sorted(escaped,key=len,reverse=True)),lambda m:r'{\fs58\c&H007EC7F0&}'+m[0]+r'{\r}',text)
        head+=f"Dialogue: 0,{stamp(row['start'])},{stamp(row['end'])},Default,,0,0,0,,{text}\n"
    (project/'captions.ass').write_text(head,encoding='utf-8')

def sound(project,plan):
    rate=48000;n=math.ceil(plan['frames']/60*rate);data=array.array('f',[0])*n;rng=random.Random(79011)
    events=plan.get('sound_events',[dict(at=s['start']/60+.12,kind='whoosh') for s in plan['scenes']])
    for event in events:
        start=round(event['at']*rate);kind=event.get('kind','tick');length=.34 if kind=='whoosh' else .12
        low=0.0
        for i in range(round(length*rate)):
            pos=start+i
            if pos>=n:break
            t=i/rate;env=math.sin(math.pi*i/(length*rate))**2
            low=.76*low+.24*rng.uniform(-1,1)
            value=low if kind=='whoosh' else math.sin(2*math.pi*(740 if kind=='tick' else 210)*t)*math.exp(-t*30)
            data[pos]+=value*env*.055
    pcm=array.array('h',(round(max(-1,min(1,x))*32767) for x in data))
    with wave.open(str(project/'sfx.wav'),'wb') as out:out.setparams((1,2,rate,0,'NONE','not compressed'));out.writeframes(pcm.tobytes())

def render(project):
    project=project.resolve();plan=read(project/'plan.json');validate(project,plan);rows=srt_rows(project/'original.srt')
    if rows[-1]['end']>plan['frames']/60+.05:raise ValueError('SRT extends beyond the planned movie')
    if (project/'source-record.json').exists() and sha(project/'original.srt')!=read(project/'source-record.json')['original_srt_sha256']:raise ValueError('Original SRT has changed')
    write_data(project,plan,rows);ass(project,rows);sound(project,plan)
    node=shutil.which('node');run([node,project/'render.cjs','video','out/visual.mp4'],project)
    args=['ffmpeg','-v','error','-y','-i','out/visual.mp4','-i','sfx.wav'];filters=[];video='0:v';audio='1:a';idx=2
    if plan.get('presenter') or plan.get('audio_source'):
        src=inside(project,plan.get('audio_source') or plan['presenter']);info=probe(src)
        args+=['-i',src];source_idx=idx;idx+=1
        if any(s['codec_type']=='audio' for s in info['streams']):filters.append(f'[{source_idx}:a]aresample=48000,apad[voice];[voice][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.97:level=false:latency=true[mix]');audio='mix'
        if plan.get('mask'):
            args+=['-i',inside(project,plan['mask'])];mask_idx=idx;idx+=1
            spans=[f'between(t,{s["start"]/60},{(s["start"]+s["frames"]-1)/60})' for s in plan['scenes'] if s.get('through_body')]
            if spans:
                rgb_idx=source_idx
                if plan.get('foreground'):
                    args+=['-i',inside(project,plan['foreground'])];rgb_idx=idx;idx+=1
                filters.append(f'[{mask_idx}:v]scale=1920:1080,fps=60,format=gray[mask];[{rgb_idx}:v][mask]alphamerge[person];[0:v][person]overlay=enable=\''+'+'.join(spans)+"'[restored]");video='restored'
    filters.append(f'[{video}]'+('null[v]' if plan.get('captions_burned') else 'subtitles=filename=captions.ass:fontsdir=public[v]'))
    args+=['-filter_complex',';'.join(filters),'-map','[v]','-map',f'[{audio}]' if audio=='mix' else audio,'-t',str(plan['frames']/60),'-c:v','libx264','-crf','16','-preset','fast','-c:a','aac','-b:a','192k','-pix_fmt','yuv420p','-movflags','+faststart','out/final.mp4']
    run(args,project);shutil.copy2(project/'original.srt',project/'out/final.srt')
    run(['ffmpeg','-v','error','-i','out/final.mp4','-f','null','-'],project)
    info=probe(project/'out/final.mp4');v=next(s for s in info['streams'] if s['codec_type']=='video')
    assert int(v['nb_frames'])==plan['frames'] and v['r_frame_rate']=='60/1'
    save(project/'out/report.json',dict(full_decode=True,frames=int(v['nb_frames']),fps=60,width=int(v['width']),height=int(v['height']),sha256=sha(project/'out/final.mp4'),srt_exact=sha(project/'original.srt')==sha(project/'out/final.srt'),voice_speed=1.0,bgm_added=False,narration='original input audio' if plan.get('presenter') or plan.get('audio_source') else 'none; code-only technical demo',agent_visual_review='pending',manual_listening=False))
    report=read(project/'out/report.json')
    report['production_mode']=read(project/'production-choice.json')['mode'] if (project/'production-choice.json').exists() else 'legacy_or_code_demo'
    save(project/'out/report.json',report)
    print('DELIVERED',project/'out/final.mp4')

def doctor(project=None):
    checks={k:shutil.which(k) for k in ['node','npm','pnpm','ffmpeg','ffprobe','nvidia-smi']}
    checks['python']=sys.version.split()[0];checks['python_supported']=sys.version_info>=(3,11)
    checks['font']=all((SKILL/'assets/template/public'/name).is_file() for name in ['SourceHanSansCN-700.otf','SourceHanSansCN-900.otf','EditorialSerif.ttf','NotoSerifSC-OFL.txt'])
    checks['browser']=next((str(p) for p in [Path(os.environ.get('REMOTION_BROWSER_EXECUTABLE','missing')),Path('C:/Program Files/Google/Chrome/Application/chrome.exe'),Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')] if p.is_file()),None)
    checks['libass']=bool(checks['ffmpeg'] and 'subtitles' in subprocess.check_output([checks['ffmpeg'],'-hide_banner','-filters'],stderr=subprocess.DEVNULL).decode('utf-8','replace'))
    checks['package_manager']=bool(checks['npm'] or checks['pnpm']);checks['base_ready']=all(checks[k] for k in ['node','ffmpeg','ffprobe','font','package_manager','browser','libass','python_supported'])
    if project:checks['project_plan_valid']=validate(project,read(project/'plan.json'))
    print(json.dumps(checks,ensure_ascii=False,indent=2))
    return checks

def main():
    p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='command',required=True)
    for cmd in ['demo','init','setup','render','check','doctor']:
        q=subs.add_parser(cmd);q.add_argument('--project',type=Path,required=cmd!='doctor')
        if cmd=='init':q.add_argument('--video',type=Path,required=True);q.add_argument('--srt',type=Path,required=True)
        if cmd=='setup':q.add_argument('--pm',choices=['auto','npm','pnpm'],default='auto')
    a=p.parse_args()
    try:
        if a.command=='doctor':
            if not doctor(a.project)['base_ready']:raise SystemExit(2)
        elif a.command=='demo':init(a.project,demo=True)
        elif a.command=='init':init(a.project,a.video,a.srt)
        elif a.command=='setup':setup(a.project.resolve(),a.pm)
        elif a.command=='render':render(a.project)
        else:validate(a.project.resolve(),read(a.project/'plan.json'));print('PLAN VALID')
    except (ValueError,RuntimeError,FileNotFoundError,KeyError) as e:print('ERROR:',e,file=sys.stderr);raise SystemExit(1)
if __name__=='__main__':main()
