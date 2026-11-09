"""Persist H3 conditioning so encoding and sampling can use separate sessions."""
from pathlib import Path
import json
import re
import torch
import folder_paths
import comfy.utils


def cache_path(name):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', name):
        raise ValueError('Use a simple H3 cache name.')
    directory = Path(folder_paths.get_output_directory()) / 'h3-conditioning'
    directory.mkdir(parents=True, exist_ok=True)
    return directory / (name + '.safetensors')


class H3SaveConditioning:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'conditioning': ('CONDITIONING',), 'name': ('STRING', {'default': 'h3-shot'})}}

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = 'save'
    CATEGORY = 'local/H3'

    def save(self, conditioning, name):
        tensors = {}
        def pack(value):
            if isinstance(value, torch.Tensor):
                key = 'tensor_' + str(len(tensors))
                tensors[key] = value.detach().cpu().contiguous().clone()
                return {'tensor': key}
            if isinstance(value, dict):
                return {'dict': {k: pack(v) for k, v in value.items()}}
            if isinstance(value, (list, tuple)):
                return {'list': [pack(v) for v in value]}
            if value is None or isinstance(value, (str, int, float, bool)):
                return {'value': value}
            raise TypeError('Unsupported H3 conditioning field: ' + type(value).__name__)
        layout = pack(conditioning)
        path = cache_path(name)
        comfy.utils.save_torch_file(tensors, str(path), metadata={'h3_layout': json.dumps(layout)})
        return {'ui': {'text': [str(path)]}}


class H3LoadConditioning:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'name': ('STRING', {'default': 'h3-shot'})}}

    RETURN_TYPES = ('CONDITIONING',)
    FUNCTION = 'load'
    CATEGORY = 'local/H3'

    def load(self, name):
        tensors, meta = comfy.utils.load_torch_file(str(cache_path(name)), return_metadata=True)
        def unpack(value):
            if 'tensor' in value:
                return tensors[value['tensor']]
            if 'dict' in value:
                return {k: unpack(v) for k, v in value['dict'].items()}
            if 'list' in value:
                return [unpack(v) for v in value['list']]
            return value['value']
        return (unpack(json.loads(meta['h3_layout'])),)


NODE_CLASS_MAPPINGS = {'H3SaveConditioning': H3SaveConditioning, 'H3LoadConditioning': H3LoadConditioning}
