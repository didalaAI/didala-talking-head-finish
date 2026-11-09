"""Build a promotional review reel from real rendered episode excerpts, at original speed."""
from pathlib import Path
import argparse,math,os,shutil,sys
import studio
def pick(plan,rows,maximum=4):
 candidates=[s for s in plan['scenes'] if s['kind'] in ['side','punch','mg','h3','video','screen'] and s['frames']>=120]
 chosen=[];seen=set()
 for s in candidates:
  kind=s.get('variant') or s['kind']
  if kind not in seen:chosen.append(s);seen.add(kind)
  if len(chosen)==maximum:break
 if not chosen:raise ValueError('No complete authored episode scenes are available for a review reel')
 cuts=[]
 for s in chosen:
  a=s['start']/60;b=min((s['start']+s['frames'])/60,a+(10.5 if s['kind'] in ['mg','h3'] else 7))
  within=[r for r in rows if a-.01<=r['start'] and r['end']<=b+.01]
  if within:a=within[0]['start'];b=within[-1]['end']
  if b-a<.8:continue
  cuts.append(dict(start=round(a*60),frames=round((b-a)*60),kind=s['kind'],variant=s.get('variant'),source_scene=s['id']))
 if not cuts:raise ValueError('No speech-boundary excerpts fit the selected scenes')
 return cuts
def build(project,target,source=None):
 project=project.resolve();target=target.resolve();source=(source or project/'out/final.mp4').resolve()
 plan=studio.read(project/'plan.json');rows=studio.srt_rows(project/'original.srt');cuts=pick(plan,rows)
 if not source.is_file():raise ValueError('Render a real episode/work preview first; a reel must show actual footage rather than fabricated before/after claims')
 info=studio.probe(source);video=next(x for x in info['streams'] if x['codec_type']=='video')
 duration=float(info['format']['duration'])
 if any((c['start']+c['frames'])/60>duration+.03 for c in cuts):raise ValueError('Review source does not cover the selected episode ranges')
 studio.init(target,demo=True);public=target/'public';dest=public/'review-source.mp4'
 try:os.link(source,dest)
 except OSError:shutil.copy2(source,dest)
 reel=dict(version=2,status='ready',fps=60,width=1920,height=1080,frames=0,presenter=None,mask=None,captions_burned=True,audio_source='reel-voice.wav',scenes=[],sound_events=[])
 reel['scenes'].append(dict(id='reel-intro',kind='promo',variant='intro',start=0,frames=180,lines=['从文意出发，','让重点被看见。'],foot='本期真实片段 · 原声原速'))
 cursor=180
 for i,c in enumerate(cuts):
  reel['scenes'].append(dict(id='proof-'+str(i),kind='video',asset=dest.name,trimBefore=c['start'],start=cursor,frames=c['frames']))
  c['destination_start']=cursor;cursor+=c['frames']
 reel['scenes'].append(dict(id='reel-outro',kind='promo',variant='outro',start=cursor,frames=180,lines=['同一段口播，','更多种表达。'],foot='效果与完整时间线，均保存在可编辑工程中。'))
 reel['frames']=cursor+180;reel['sound_events']=[dict(at=.1,kind='whoosh'),dict(at=(cursor+.1*60)/60,kind='whoosh')]
 studio.save(target/'plan.json',reel);studio.save(target/'production-choice.json',dict(schema=1,mode='motion',user_choice_required=False,history=[dict(note='Derivative of actual rendered footage; no new generation service selected')]))
 # Keep subtitles as an accessible retimed sidecar; pixels already contain the episode captions.
 def stamp(t):
  ms=round(t*1000);secs,ms=divmod(ms,1000);mins,secs=divmod(secs,60);hrs,mins=divmod(mins,60);return f'{hrs:02}:{mins:02}:{secs:02},{ms:03}'
 cues=[]
 for c in cuts:
  for r in rows:
   a=max(r['start'],c['start']/60);b=min(r['end'],(c['start']+c['frames'])/60)
   if b>a:cues.append(dict(start=(a-c['start']/60)+c['destination_start']/60,end=(b-c['start']/60)+c['destination_start']/60,text=r['text']))
 if not cues:cues=[dict(start=0,end=2.5,text='本期真实成片预览')]
 (target/'original.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(r["start"])} --> {stamp(r["end"])}\n{r["text"]}' for i,r in enumerate(cues))+'\n',encoding='utf-8')
 filters=[];tracks=[]
 if any(x['codec_type']=='audio' for x in info['streams']):
  for i,c in enumerate(cuts):
   a=c['start']/60;b=(c['start']+c['frames'])/60;delay=round(c['destination_start']/60*1000)
   filters.append(f'[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,afade=t=in:d=0.025,afade=t=out:st={max(0,b-a-.025)}:d=0.025,adelay={delay}|{delay}[a{i}]');tracks.append(f'[a{i}]')
 filters.append(f'anullsrc=r=48000:cl=stereo:d={reel["frames"]/60}[silence]');tracks.append('[silence]')
 filters.append(''.join(tracks)+f'amix=inputs={len(tracks)}:duration=longest:normalize=0[out]')
 studio.run(['ffmpeg','-v','error','-y','-i',source,'-filter_complex',';'.join(filters),'-map','[out]','-t',reel['frames']/60,'-c:a','pcm_s16le',public/'reel-voice.wav'])
 studio.write_data(target,reel,studio.srt_rows(target/'original.srt'))
 studio.save(target/'showreel-record.json',dict(source_sha256=studio.sha(source),source_frames=plan['frames'],reel_frames=reel['frames'],cuts=cuts,speed=1.0,private_footage=True,purpose='promotional review; does not replace full episode'))
 print('SHOWREEL PROJECT',target,'frames',reel['frames'])
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,required=True);p.add_argument('--out-project',type=Path,required=True);p.add_argument('--source',type=Path);a=p.parse_args()
 try:build(a.project,a.out_project,a.source)
 except (ValueError,RuntimeError,FileNotFoundError,KeyError) as e:print('ERROR:',e,file=sys.stderr);raise SystemExit(1)
if __name__=='__main__':main()
