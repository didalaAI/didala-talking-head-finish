"""Release conditioning models before H3 sampling on this 12 GB workstation."""
import comfy.model_management


class H3ReleaseConditioningModels:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'conditioning': ('CONDITIONING',), 'latent': ('LATENT',)}}

    RETURN_TYPES = ('CONDITIONING', 'LATENT')
    FUNCTION = 'release'
    CATEGORY = 'local/H3'

    def release(self, conditioning, latent):
        comfy.model_management.unload_all_models()
        comfy.model_management.soft_empty_cache()
        return conditioning, latent


NODE_CLASS_MAPPINGS = {'H3ReleaseConditioningModels': H3ReleaseConditioningModels}
