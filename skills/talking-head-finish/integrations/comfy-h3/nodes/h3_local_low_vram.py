"""Keep H3's large quantized text encoder on CPU on a 12GB CUDA card."""
import logging
import torch
import nodes

class H3LocalCLIPCPU:
    @classmethod
    def INPUT_TYPES(cls):
        return nodes.NODE_CLASS_MAPPINGS['CLIPLoaderGGUF'].INPUT_TYPES()
    RETURN_TYPES=('CLIP',)
    FUNCTION='load_clip'
    CATEGORY='local/H3'
    TITLE='H3 quantized text encoder on CPU'

    def load_clip(self,clip_name,type='minimax',**kwargs):
        clip=nodes.NODE_CLASS_MAPPINGS['CLIPLoaderGGUF']().load_clip(clip_name,type=type,**kwargs)[0]
        cpu=torch.device('cpu')
        clip.patcher.load_device=cpu
        clip.patcher.offload_device=cpu
        clip.load_device=cpu
        logging.info('H3 local: quantized text/vision encoder stays on CPU; CUDA reserved for video sampling.')
        return (clip,)

NODE_CLASS_MAPPINGS={'H3LocalCLIPCPU':H3LocalCLIPCPU}
NODE_DISPLAY_NAME_MAPPINGS={'H3LocalCLIPCPU':H3LocalCLIPCPU.TITLE}
