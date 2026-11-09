"""Compact official Real-ESRGAN x4v3 inference without BasicSR dependency.

Architecture: xinntao/Real-ESRGAN, BSD-3-Clause, SRVGGNetCompact.
Adapted architecture: https://github.com/xinntao/Real-ESRGAN/blob/master/realesrgan/archs/srvgg_arch.py
Copyright (c) 2021, Xintao Wang. BSD-3-Clause; see ../../references/licenses/Real-ESRGAN-BSD-3-Clause.txt.
Weights are not distributed. Supply and verify your own REALESRGAN_MODEL file.
"""
from pathlib import Path
import torch,torch.nn as nn,torch.nn.functional as F
import numpy as np,sys,time,json,os
from PIL import Image
HERE=Path(__file__).resolve().parent
class SRVGGNetCompact(nn.Module):
 def __init__(self):
  super().__init__();layers=[nn.Conv2d(3,64,3,1,1),nn.PReLU(num_parameters=64)]
  for _ in range(32):layers.extend([nn.Conv2d(64,64,3,1,1),nn.PReLU(num_parameters=64)])
  layers.append(nn.Conv2d(64,48,3,1,1));self.body=nn.ModuleList(layers);self.upsampler=nn.PixelShuffle(4)
 def forward(self,x):
  out=x
  for layer in self.body:out=layer(out)
  return self.upsampler(out)+F.interpolate(x,scale_factor=4,mode='nearest')

class Upscale:
 def __init__(self,device='cuda',tile=256):
  torch.set_num_threads(2);self.device=torch.device(device);self.tile=tile
  self.model=SRVGGNetCompact();p=torch.load(Path(os.environ.get('REALESRGAN_MODEL', str(HERE/'superres/realesr-general-x4v3.pth'))),map_location='cpu',weights_only=True)
  self.model.load_state_dict(p['params'],strict=True);self.model.eval().to(self.device)
  self.half=device.startswith('cuda')
  if self.half:self.model.half()
 @torch.inference_mode()
 def __call__(self,bgr,size=(1920,1080)):
  h,w=bgr.shape[:2];out=np.empty((h*4,w*4,3),np.uint8);pad=34
  for y in range(0,h,self.tile):
   for x in range(0,w,self.tile):
    y0=max(0,y-pad);y1=min(h,y+self.tile+pad);x0=max(0,x-pad);x1=min(w,x+self.tile+pad)
    patch=np.ascontiguousarray(bgr[y0:y1,x0:x1,::-1].transpose(2,0,1));t=torch.from_numpy(patch).to(self.device).unsqueeze(0)/255
    if self.half:t=t.half()
    result=self.model(t).float().squeeze(0).clamp_(0,1).cpu().numpy().transpose(1,2,0)
    sy=(y-y0)*4;sx=(x-x0)*4;dh=min(self.tile,h-y)*4;dw=min(self.tile,w-x)*4
    out[y*4:y*4+dh,x*4:x*4+dw]=np.rint(result[sy:sy+dh,sx:sx+dw,::-1]*255).astype(np.uint8)
  return np.asarray(Image.fromarray(out).resize(size,Image.Resampling.LANCZOS)) if size else out

if __name__=='__main__':
 src=Path(sys.argv[1]);dest=Path(sys.argv[2]);device=sys.argv[3] if len(sys.argv)>3 else 'cpu'
 im=np.array(Image.open(src).convert('RGB'))[:,:,::-1];crop=im[155:600,300:950] if '--crop' in sys.argv else im
 tick=time.time();up=Upscale(device,256);out=up(crop,(round(crop.shape[1]*1080/im.shape[0]),round(crop.shape[0]*1080/im.shape[0])))
 Image.fromarray(out[:,:,::-1]).save(dest);print('UPSCALE',out.shape,round(time.time()-tick,2),flush=True)
