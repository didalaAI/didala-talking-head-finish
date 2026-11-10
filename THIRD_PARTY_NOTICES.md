# 第三方声明

本项目的MIT只覆盖作者原创部分。第三方代码、字体、软件、模型、服务以及用户输入继续遵守各自条款；不代表这些组件全部开源、免费或适合任意商用。

| 项目 | 本包如何使用 | 许可或条款来源 |
| --- | --- | --- |
| Source Han Sans CN / 思源黑体 | 随包提供700、900字重 | SIL OFL 1.1，全文在`skills/talking-head-finish/assets/template/public/SourceHanSansCN-LICENSE.txt` |
| Real-ESRGAN | 可选超分助手改编SRVGGNetCompact架构；不含权重 | [上游](https://github.com/xinntao/Real-ESRGAN)，BSD-3-Clause全文在`skills/talking-head-finish/references/licenses/Real-ESRGAN-BSD-3-Clause.txt` |
| Remotion | package-lock固定版本，使用者自行安装 | [许可与使用条件](https://www.remotion.dev/docs/license/pricing)，不能用本仓MIT替代 |
| React / TypeScript及npm依赖 | 使用者通过锁文件安装，不随包提供node_modules | 各依赖安装后的LICENSE与包元数据；使用者另行核对 |
| FFmpeg / Chrome或Edge | 用户自行安装，不分发二进制 | [FFmpeg](https://ffmpeg.org/legal.html)、对应浏览器发行条款 |
| ComfyUI / ComfyUI-GGUF | 可选本地后端，不分发安装目录 | [ComfyUI](https://github.com/Comfy-Org/ComfyUI)、[GGUF节点](https://github.com/city96/ComfyUI-GGUF)各自许可证 |
| MiniMax H3及其量化权重/编码器/VAE | 可选，自行获取，不分发权重 | [原模型许可](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)及各权重仓库；尤其应核对地区、用途和商业条件 |
| Torch / Pillow / NumPy / RIFE | 只供可选GPU后期使用，未打包 | 对应软件与所选模型仓库的许可 |
| Comfy Cloud及其他云账号 | 可选外部服务 | 对应服务条款、用量费用及素材政策 |

`integrations/comfy-h3/nodes`是本项目的辅助节点代码，不能代替Comfy及GGUF上游。云端工作流须由使用者从实际账号导出；本包不携带账号工作流中的密钥。H3镜头配方只包含创作方法和参数，不包含原片、真人或生成视频。

本仓库不承诺上游许可永久不变。发布模型或将其用于商业活动前，使用者应读取所选版本的完整许可。不存在“安装这个Skill即可绕过模型或Remotion授权”的安排。


## 0.2 backgrounds and matting

The no-person purple studio background is included at the author's explicit request. The other three backgrounds are original procedural artwork. These four images may be reused with this project under its MIT distribution license. No private portrait or narration is bundled.

The independently written local ONNX adapter accepts separately acquired [Robust Video Matting](https://github.com/PeterL1n/RobustVideoMatting) weights. Upstream RVM code/weights use GPL-3.0; neither their model source nor their weights are bundled or relicensed here. Obtain them from the official source and follow their terms. NumPy, Pillow and ONNX Runtime retain their own licenses; optional dependencies are installed in a separate user-selected environment.

## Noto Serif SC

The unmodified Noto Serif SC variable font is bundled as EditorialSerif.ttf under SIL OFL 1.1. Full license travels with the font as NotoSerifSC-OFL.txt. Font binaries and their terms are not covered by the code MIT license. Source: https://github.com/google/fonts/tree/main/ofl/notoserifsc

## Original generated reference keyframes

The four assets/generation-keyframes images are original generated miniature/illustration references supplied with this project under the project MIT license. They contain no author portrait, voice or account screenshots. CelCounter uses a frame from the approved blue-checklist correction. Model/service terms still apply to newly generated outputs.
