# 随Skill分发的第三方声明

本Skill原创代码见同目录LICENSE。作者的MIT不替代以下条款。

- 思源黑体700/900字重随包提供，许可与版权所有人全文见[OFL文件](assets/template/public/SourceHanSansCN-LICENSE.txt)。未修改字形，不用字体保留名宣传新字体。
- 可选`integrations/comfy-h3/superres_local.py`改编Real-ESRGAN的SRVGGNetCompact架构，Copyright (c) 2021, Xintao Wang，许可全文见[BSD-3-Clause](references/licenses/Real-ESRGAN-BSD-3-Clause.txt)。不包含模型权重。
- Remotion由使用者另行安装，适用[Remotion许可与条件](https://www.remotion.dev/docs/license/pricing)；本仓MIT不赋予额外Remotion商业许可。
- React、TypeScript及其他npm依赖按安装包各自LICENSE使用。FFmpeg、浏览器、ComfyUI/GGUF、Torch、RIFE和模型均另行获取，遵守各自发行条款。
- MiniMax H3及其量化、编码器、VAE组件不分发。请读取[所选模型的完整许可](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)及权重来源，核对地区、用途和商业条件。云端账号受其服务条款及费用约束。

本包没有作者真人、原录音、聊天截图、模型权重、完整软件环境或凭据。用户应只输入自己有权处理、上传和发布的素材。


## 0.2 backgrounds and matting

The no-person purple studio background is included at the author's explicit request. The other three backgrounds are original procedural artwork. These four images may be reused with this project under its MIT distribution license. No private portrait or narration is bundled.

The independently written local ONNX adapter accepts separately acquired [Robust Video Matting](https://github.com/PeterL1n/RobustVideoMatting) weights. Upstream RVM code/weights use GPL-3.0; neither their model source nor their weights are bundled or relicensed here. Obtain them from the official source and follow their terms. NumPy, Pillow and ONNX Runtime retain their own licenses; optional dependencies are installed in a separate user-selected environment.

## Noto Serif SC

The unmodified Noto Serif SC variable font is bundled as EditorialSerif.ttf under SIL OFL 1.1. Full license travels with the font as NotoSerifSC-OFL.txt. Font binaries and their terms are not covered by the code MIT license. Source: https://github.com/google/fonts/tree/main/ofl/notoserifsc

## Original generated reference keyframes

The four assets/generation-keyframes images are original generated miniature/illustration references supplied with this project under the project MIT license. They contain no author portrait, voice or account screenshots. CelCounter uses a frame from the approved blue-checklist correction. Model/service terms still apply to newly generated outputs.
