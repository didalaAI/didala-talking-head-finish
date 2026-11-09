"""Optional serial Real-ESRGAN + RIFE finish. Requires a reviewed native clip."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys
from fractions import Fraction

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--accepted-native-sha256',required=True);p.add_argument('--sr-model',type=Path,required=True);p.add_argument('--rife-exe',type=Path,required=True);p.add_argument('--rife-model',type=Path,required=True);p.add_argument('--frames',type=int,required=True);a=p.parse_args()
    if sha(a.input)!=a.accepted_native_sha256:raise ValueError('Native hash differs from the action-reviewed clip. Review the current video first.')
    if a.out.exists() and any(a.out.iterdir()):raise ValueError('Use a new empty output folder; intermediate frames are never silently reused.')
    if a.frames<=1:raise ValueError('Invalid output frame count')
    for path in [a.sr_model,a.rife_exe,a.rife_model]:
        if not path.exists():raise FileNotFoundError(path.name)
    try:
        import numpy as np
        from PIL import Image
        import torch
    except ImportError:raise RuntimeError('Run this optional helper with a configured GPU Python containing Torch, NumPy and Pillow; base rendering does not need them.')
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(a.input)]))['streams'][0]
    w,h,count=int(info['width']),int(info['height']),int(info['nb_frames'])
    if abs(a.frames/60-count/float(Fraction(info['r_frame_rate'])))>.1:raise ValueError('Output frames would change playback speed; choose a matching duration.')
    a.out.mkdir(parents=True,exist_ok=True);sr=a.out/'sr';sr.mkdir();interpolated=a.out/'rife';interpolated.mkdir()
    os.environ['REALESRGAN_MODEL']=str(a.sr_model.resolve());module_path=Path(__file__).resolve().parents[1]/'integrations/comfy-h3/superres_local.py'
    spec=importlib.util.spec_from_file_location('didala_superres',module_path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);up=module.Upscale('cuda',256)
    dec=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-i',str(a.input),'-an','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
    for i in range(count):
        raw=dec.stdout.read(w*h*3)
        if len(raw)!=w*h*3:raise RuntimeError('Native decoder ended unexpectedly')
        frame=np.frombuffer(raw,np.uint8).reshape(h,w,3);scaled=up(frame[:,:,::-1],(1920,round(1920*h/w)));start=(scaled.shape[0]-1080)//2
        if start<0:raise ValueError('Native aspect ratio is too wide for this centered 16:9 finish; author an appropriate crop first.')
        Image.fromarray(scaled[start:start+1080,:,::-1]).save(sr/f'{i:04}.png')
        if i%12==0:print('SUPERRES',i,count,flush=True)
    dec.stdout.close()
    if dec.wait():raise RuntimeError('Native decode failed')
    del up;torch.cuda.empty_cache()
    subprocess.run([str(a.rife_exe.resolve()),'-i',str(sr.resolve()),'-o',str(interpolated.resolve()),'-n',str(a.frames),'-m',str(a.rife_model.resolve()),'-g','0','-j','1:2:1','-f','%08d.png'],check=True)
    if len(list(interpolated.glob('*.png')))!=a.frames:raise RuntimeError('Incomplete RIFE output')
    target=a.out/'finished60.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-framerate','60','-i',str(interpolated/'%08d.png'),'-frames:v',str(a.frames),'-an','-c:v','libx264','-crf','16','-preset','fast','-pix_fmt','yuv420p',str(target)],check=True)
    (a.out/'finish-record.json').write_text(json.dumps(dict(native_sha256=sha(a.input),native_size=[w,h],native_frames=count,native_fps=info['r_frame_rate'],finished_size=[1920,1080],finished_fps=60,finished_frames=a.frames,output_sha256=sha(target),superres='Real-ESRGAN general-x4v3',interpolation='RIFE; model path supplied by operator',hold_frames=0,voice_speed=1.0,visual_motion_review='pending'),indent=2),encoding='utf-8')
    print('FINISHED; review current motion before use:',target)
if __name__=='__main__':
    try:main()
    except (ValueError,RuntimeError,FileNotFoundError) as e:print('ERROR:',e,file=sys.stderr);raise SystemExit(1)
