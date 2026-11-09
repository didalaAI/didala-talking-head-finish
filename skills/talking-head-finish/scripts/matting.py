"""Local recurrent ONNX human matting. No footage is uploaded; weights are external."""
from pathlib import Path
import argparse,hashlib,json,math,os,shutil,subprocess,sys,urllib.request,venv
SKILL=Path(__file__).resolve().parents[1]
MODEL_URL='https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_{variant}_fp32.onnx'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args):subprocess.run([str(x) for x in args],check=True)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def placement(bbox,mode):
 x0,y0,x1,y1=bbox
 if mode=='keep':return 1.,0,0
 scale=min(1.05,(900 if mode=='right' else 1120)/max(1,x1-x0),1020/max(1,y1-y0))
 x=round((1430 if mode=='right' else 960)-scale*(x0+x1)/2);y=round(1080-scale*y1)
 return scale,x,y
def fetch_model(directory,variant):
 directory.mkdir(parents=True,exist_ok=True);dest=directory/f'rvm_{variant}_fp32.onnx'
 if not dest.exists():
  temp=dest.with_suffix('.partial');urllib.request.urlretrieve(MODEL_URL.format(variant=variant),temp)
  if temp.stat().st_size<1000000:raise ValueError('Model download is incomplete')
  os.replace(temp,dest)
 save(directory/(dest.stem+'-source.json'),dict(url=MODEL_URL.format(variant=variant),sha256=sha(dest),license='GPL-3.0; see upstream terms',weights_not_bundled=True))
 print(dest)
def prepare(directory):
 if not directory.exists():venv.EnvBuilder(with_pip=True).create(directory)
 python=directory/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
 run([python,'-m','pip','install','--index-url','https://pypi.org/simple','numpy==2.2.6','onnxruntime==1.24.4','Pillow==11.3.0'])
 print('Use this isolated interpreter for matting:',python)
def render(project,model,background,position,ratio=.25):
 import numpy as np
 import onnxruntime as ort
 project=project.resolve();plan=read(project/'plan.json');src=project/'public/source.mp4';source=probe(src)
 if not model.is_file():raise ValueError('Provide an existing FP32 RVM ONNX model; fetch-model downloads official weights separately.')
 backgrounds=read(SKILL/'assets/backgrounds/catalog.json')['items'];bg=next((b for b in backgrounds if b['id']==background),None)
 if not bg:raise ValueError('Unknown background. Use list-backgrounds to see choices.')
 work=project/'matting';work.mkdir(exist_ok=True)
 if (work/'matting-record.json').exists():raise ValueError('Matting already exists. Preserve it before retrying in a new project/work directory.')
 opts=ort.SessionOptions();opts.intra_op_num_threads=min(8,os.cpu_count() or 2)
 sess=ort.InferenceSession(str(model.resolve()),sess_options=opts,providers=['CPUExecutionProvider'])
 names={x.name for x in sess.get_inputs()}
 if not {'src','r1i','r2i','r3i','r4i','downsample_ratio'}<=names:raise ValueError('This adapter expects the official RVM recurrent ONNX interface')
 count=plan['frames'];w,h=1920,1080
 dec=subprocess.Popen(['ffmpeg','-v','error','-i',str(src),'-vf','scale=1920:1080,fps=60','-frames:v',str(count),'-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 fg=work/'foreground-native.mp4';mask=work/'alpha-native.mkv';logs=[];enc=[]
 for target,fmt,codec in [(fg,'rgb24',['-c:v','libx264','-crf','14','-preset','fast','-pix_fmt','yuv420p']),(mask,'gray',['-c:v','ffv1','-level','3','-pix_fmt','gray'])]:
  log=(work/(target.stem+'.log')).open('wb');logs.append(log)
  enc.append(subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt',fmt,'-s',f'{w}x{h}','-r','60','-i','-','-an',*codec,str(target)],stdin=subprocess.PIPE,stderr=log))
 rec=[np.zeros((1,1,1,1),np.float32) for _ in range(4)];bbox=[w,h,0,0];occupancy=[];previous=None;changes=[]
 try:
  for frame in range(count):
   raw=dec.stdout.read(w*h*3)
   if len(raw)!=w*h*3:raise RuntimeError('Input ended before planned frame count; no frozen-tail replacement was made')
   rgb=np.frombuffer(raw,np.uint8).reshape(h,w,3);inp=np.ascontiguousarray(rgb.transpose(2,0,1)[None]/255,dtype=np.float32)
   fgr,alpha,*rec=sess.run(None,dict(src=inp,r1i=rec[0],r2i=rec[1],r3i=rec[2],r4i=rec[3],downsample_ratio=np.array([ratio],np.float32)))
   a=np.uint8(np.clip(alpha[0,0],0,1)*255);f=np.uint8(np.clip(fgr[0].transpose(1,2,0),0,1)*255)
   enc[0].stdin.write(f.tobytes());enc[1].stdin.write(a.tobytes())
   if frame%12==0:
    yy,xx=np.where(a>110);occupancy.append(float((a>110).mean()))
    if len(xx):bbox=[min(bbox[0],int(xx.min())),min(bbox[1],int(yy.min())),max(bbox[2],int(xx.max())+1),max(bbox[3],int(yy.max())+1)]
    small=a[::12,::12].astype(np.float32)/255
    if previous is not None:changes.append(float(np.abs(small-previous).mean()))
    previous=small
   if frame%120==0:print('MATTING',frame,count,flush=True)
 finally:
  dec.stdout.close()
  if dec.poll() is None:dec.terminate()
  for e in enc:
   if e.stdin:e.stdin.close()
  codes=[e.wait() for e in enc]
  for log in logs:log.close()
 if any(codes):raise RuntimeError('Matting encoder failed; inspect project/matting logs')
 if not occupancy or min(occupancy)<.005 or bbox[2]<=bbox[0]:raise ValueError('Person detection is empty or unstable. Review mask before applying a background.')
 s,x,y=placement(bbox,position);sw=round(w*s/2)*2;sh=round(h*s/2)*2;duration=count/60
 public=project/'public';bgfile=public/'selected-background.png';shutil.copy2(SKILL/'assets/backgrounds'/bg['file'],bgfile)
 # Identical transforms for RGB and alpha, including masks later used to restore through-body text occlusion.
 placed_fg=public/'presenter-foreground.mp4';placed_alpha=public/'presenter-mask.mkv';composite=public/'presenter-composite.mp4'
 for inp,out,pix,codec in [(fg,placed_fg,'yuv420p',['-c:v','libx264','-crf','14','-preset','fast']),(mask,placed_alpha,'gray',['-c:v','ffv1','-level','3'])]:
  filt=f'color=black:s=1920x1080:r=60:d={(count+1)/60},settb=1/60000,setpts=N*1000[canvas];[0:v]settb=1/60000,setpts=N*1000,scale={sw}:{sh}:flags=lanczos[placed];[canvas][placed]overlay={x}:{y}:shortest=0:eof_action=pass:repeatlast=0,format={pix}[v]'
  run(['ffmpeg','-v','error','-y','-i',inp,'-filter_complex',filt,'-map','[v]','-frames:v',count,'-an',*codec,'-pix_fmt',pix,out])
 filt='[0:v]settb=1/60000,setpts=N*1000,format=rgb24[f];[1:v]settb=1/60000,setpts=N*1000,format=gray[a];[f][a]alphamerge,format=rgba[person];[2:v]scale=1920:1080,format=rgba[bg];[bg][person]overlay=shortest=1:format=auto,format=yuv420p[v]'
 run(['ffmpeg','-v','error','-y','-i',placed_fg,'-i',placed_alpha,'-framerate','60','-loop','1','-i',bgfile,'-filter_complex',filt,'-map','[v]','-an','-frames:v',count,'-r','60','-c:v','libx264','-crf','16','-preset','fast',composite])
 check=next(v for v in probe(composite)['streams'] if v['codec_type']=='video')
 if int(check.get('nb_frames',0))!=count or check['r_frame_rate']!='60/1':raise RuntimeError('Composite frame count/rate does not match the input timeline')
 counted=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=nb_read_frames','-of','json',str(placed_alpha)]))
 if int(counted['streams'][0]['nb_read_frames'])!=count:raise RuntimeError('Positioned alpha lost frames; final export must not proceed')
 plan.update(presenter=composite.name,foreground=placed_fg.name,mask=placed_alpha.name,audio_source='source.mp4',background=background)
 save(project/'plan.json',plan)
 record=dict(status='needs_visual_review',backend='RVM ONNX CPU; recurrent states recycled across sequential frames',model_sha256=sha(model),model_license='GPL-3.0 external weights',source_sha256=sha(src),frames=count,fps=60,width=w,height=h,background=background,position=position,transform=dict(scale=s,x=x,y=y),source_person_bbox=bbox,min_mask_occupancy=min(occupancy),max_sampled_alpha_change=max(changes,default=0),uploaded=False,voice_source='source.mp4; speed 1.0',manual_hair_hand_edge_review=False)
 save(work/'matting-record.json',record)
 # Three native comparison images for the Agent's edge/gesture review; never substitute them for moving footage.
 for i,at in enumerate([0,max(0,duration/2),max(0,duration-2/60)]):
  image=work/f'check-{i}.png';run(['ffmpeg','-v','error','-y','-ss',str(at),'-i',composite,'-frames:v','1',image])
  if not image.is_file():raise RuntimeError('Matting check image was not produced')
 print('MATTED; inspect moving hair/hands and the 3 check images before setting matting review to passed.',flush=True)
def main():
 p=argparse.ArgumentParser(description=__doc__);q=p.add_subparsers(dest='command',required=True)
 q.add_parser('list-backgrounds');s=q.add_parser('prepare');s.add_argument('--env-dir',type=Path,required=True)
 s=q.add_parser('fetch-model');s.add_argument('--directory',type=Path,required=True);s.add_argument('--variant',choices=['mobilenetv3','resnet50'],default='resnet50')
 s=q.add_parser('render');s.add_argument('--project',type=Path,required=True);s.add_argument('--model',type=Path);s.add_argument('--background',default='didala-purple');s.add_argument('--position',choices=['right','center','keep'],default='right');s.add_argument('--downsample',type=float,default=.25)
 a=p.parse_args()
 try:
  if a.command=='list-backgrounds':print(json.dumps(read(SKILL/'assets/backgrounds/catalog.json'),ensure_ascii=False,indent=2))
  elif a.command=='prepare':prepare(a.env_dir.resolve())
  elif a.command=='fetch-model':fetch_model(a.directory.resolve(),a.variant)
  else:
   if not 0<a.downsample<=1:raise ValueError('downsample must be in (0,1]')
   configured=read(SKILL/'config.local.json').get('matting_model') if (SKILL/'config.local.json').is_file() else None
   model=a.model or (Path(os.environ.get('RVM_ONNX_MODEL') or configured) if (os.environ.get('RVM_ONNX_MODEL') or configured) else None)
   if model is None:raise ValueError('Choose an existing model with --model, RVM_ONNX_MODEL, or config.local.json matting_model; use fetch-model for official weights.')
   render(a.project,model,a.background,a.position,a.downsample)
 except (ValueError,RuntimeError,FileNotFoundError,ImportError,subprocess.CalledProcessError) as e:print('ERROR:',e,file=sys.stderr);raise SystemExit(1)
if __name__=='__main__':main()
