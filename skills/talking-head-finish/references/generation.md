# 生成后端与后期

基础渲染不要求H3。完整场景可由用户自己选择本地或云端，生成前确认相应素材去向、账号费用和许可。API密钥不写入工作流、仓库或日志。

## 本地ComfyUI

按[Comfy官方指南](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)安装对应软件和模型；安装[ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF)。`integrations/comfy-h3/nodes`为本制作流程的CPU编码器、conditioning缓存与释放节点，按Comfy自定义节点方式放入自己的安装目录。不要覆盖别人的节点文件。

`local-workflow.json`是API格式，采用1344×768、124帧、24fps、20步的本机参考配置。具体模型文件名来自该组合，权重不包含在发行包中，使用者从原仓获得并核对条款：

- `minimax_h3_fl2va_pruned_fp8_Q4_0.gguf`：[第三方量化仓库](https://huggingface.co/molbal/MiniMax-H3-GGUF)
- `qwen3vl-32B-MiniMax-H3-Q2_K.gguf`及其匹配编码器组件：使用与你的GGUF节点匹配的来源与命名。
- 视频/音频VAE：[Comfy-Org打包](https://huggingface.co/Comfy-Org/MiniMax-H3)

复制local.example.json到自己的配置文件，填写Comfy地址。命令：

```text
python scripts/generate.py --config <配置.json> --image <首帧.png> --prompt-file <镜头.txt> --out <空镜头目录>
```

低显存参考模式先编码保存conditioning，再采样，队列空闲才请求释放模型；不取消其他用户任务。超时保留receipt，使用相同参数重跑会续等同一任务，输入改变则要求换目录。成功返回native.mp4也仍是“动作待审”，不是自动合格。

当前开发机新一轮启动被Windows应用程序控制拦截了Torch的fbgemm.dll。此预览包不声称已重新完成本地H3端到端实测；不建议关闭保护或改名/挪动DLL规避策略。应由设备管理者允许可信软件或另选合规运行环境，再进行实际生成验证。

## Comfy Cloud

复制cloud.example.json，设置自己的COMFY_CLOUD_API_KEY。先从云端导出其支持的**API格式**工作流，填入workflow文件和image/prompt/seed的节点字段绑定；不能把本地CPU缓存节点直接当成云端已支持节点。

适配器根据[Comfy官方OpenAPI](https://github.com/Comfy-Org/docs/blob/main/openapi-cloud.yaml)使用`/api/upload/image`、`/api/prompt`、`/api/history_v2/{id}`与`/api/view`，鉴权为X-API-Key。跨站下载重定向会移除鉴权头，避免将Key传给媒体存储。HTTP失败不打印私有响应体，保存收据供账户端排查，不自动重新计费提交。

本轮验证覆盖本地模拟服务器上的协议行为；没有真实云账号的生成实测，发布前应完成一条真实流程并保存模型/工作流版本。云端可省本地显卡，不等于免费，也不等于随机画面与本地完全一致。

## 原生动作到1080p60

先用实际原速和关键帧审核手、物件、动作闭环及前后连续性。审核当前native.mp4后，传其SHA256给可选postprocess.py：

```text
<GPU环境Python> scripts/postprocess.py --input <native.mp4> --out <新的后期目录> --accepted-native-sha256 <审核过的哈希> --sr-model <RealESRGAN权重> --rife-exe <RIFE程序> --rife-model <RIFE模型目录> --frames <匹配时长的60fps帧数>
```

此助手要求GPU Python中的Torch、NumPy、Pillow，以及另装的Real-ESRGAN权重和RIFE。序列先超分，再插帧，最后统一编码；不把后期称为原生规格，不以静图或hold填缺帧。当前预览版该GPU后期路径尚待本轮重新实测，CLI与参考代码不是完整GPU安装器。

H3输出可带声音，本口播流程使用它的静音画面，配音仍取用户原录音；不把生成旁白覆盖原声。字幕与画外准确字层在后期处理。
