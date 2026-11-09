# 迪达拉口播成片 Skill

**0.1.2-preview · Windows 公开预览版。**

公开仓库：[didalaAI/didala-talking-head-finish](https://github.com/didalaAI/didala-talking-head-finish)。打包源码、24秒基础demo与验证材料通过仓库的Releases提供。

从你自己的已剪视频与SRT出发，由Agent按文意编排旁字、实体MG、准确字幕和可选场景动画。包含真实V4机制代码，而非只有提示词。原声原速1.0，无BGM；新题材仍需重新设计语义分镜和审核动作。

## 粉丝只需这样使用

把下面这句话发给自己的Codex、WorkBuddy、豆包工作或支持本地技能的Agent：

> 帮我安装这个 Skill：https://github.com/didalaAI/didala-talking-head-finish

**给Agent：请先读[安装约定](docs/INSTALL-FOR-AGENTS.md)。** 完整Skill在`skills/talking-head-finish`。按当前宿主支持的方式安装完整文件夹，检查并在权限允许时准备基础环境，从安装副本实际运行演示。无需让粉丝先手动克隆、敲命令或配置H3；只有宿主实际不具备执行/安装能力时才说明缺项。

装好后，发送自己的**已剪口播MP4＋对应SRT**，再说：

> 调用 talking-head-finish，按照这个 Skill 的要求，剪辑好我的口播视频，保留原声原速。

Agent会检测可用生成服务。有可用本地H3就沿用并验证短镜头；没有时，**由粉丝自行选择**：动态MG与现有素材完成整片、接入自己的云服务、使用Agent已有其他视频模型，或先完成其余部分稍后补动画。选择按本期保存，不自动切换或默认下载大模型，详见[首次制作与选择](skills/talking-head-finish/references/first-run.md)。

这套流程面向能联网读仓库、安装技能、访问素材并执行命令的Agent；仅能聊天的入口不能保证完成本地安装或渲染。当前基础工程已验证，WorkBuddy和豆包工作仍待真实客户端端到端试用。

[40段效果覆盖](docs/V4-COVERAGE.md) · [发行与粉丝安装步骤](docs/RELEASE.md) · [实际验证记录](docs/VALIDATION.md)

跨客户端边界见[使用说明](skills/talking-head-finish/references/host-compatibility.md)。以下是供Agent和开发者执行的技术说明；普通粉丝按上面两句话使用即可。技能市场限制体积时另有轻量工程引导包，完整字体与渲染代码仍从仓库安装。

## 目前可以运行

- 24秒、1920×1080/60fps的无GPU基础演示：文字进入/收稳、有限阅读区、历史累积、摘要、字幕和独立短音效。
- 用户视频初始化、原SRT保存、计划校验、渲染、原声/SFX混音、最终解码/帧数校验。
- 参数化旁字/大字；用户提供动态人物蒙版时支持穿身遮挡，字幕在遮挡之后烧录。
- 23段V4全屏MG的具体实现与9段人物效果的机制索引；截图支持完整原图到真实坐标的连续推近。
- 本地ComfyUI与Comfy Cloud适配器，支持上传、收据续跑、错误处理和结果下载；8组H3场景配方；可选Real-ESRGAN/RIFE后期辅助。

基础演示没有旁白或真人素材，不声称已替你制作任意主题的最终口播。H3、云端账号、抠像模型与工具不打包进来；缺少生成后端时不会用静图或长停帧冒充动画。

## 验证状态

基础依赖在全新项目目录从npm官方源安装，完成类型检查、1440帧实际渲染、原字幕一致性及完整解码。Python基础CLI仅用标准库，也在无第三方包的隔离venv运行了测试。

云端协议使用本地模拟服务器测试，**没有使用真实云端账号生成**。本机新一轮H3实测被Windows应用程序控制拦截Torch DLL，不能将本预览版标为H3端到端重新实测通过。完整状态和限制见[验证记录](docs/VALIDATION.md)。没有关闭系统保护，也没有据此降低动画质量。

## 基础环境（Agent执行）

首先安装Python 3.12、Node.js（本轮测试24）、FFmpeg/ffprobe以及Chrome或Edge。FFmpeg需要`subtitles`/libass滤镜。Node包依赖固定为Remotion 4.0.539、React 19.2.0、TypeScript 5.9.3。

官方来源：[Python](https://www.python.org/downloads/)、[Node.js](https://nodejs.org/en/download)、[FFmpeg](https://ffmpeg.org/download.html)。本版支持npm，缺少npm时也可使用pnpm；不会静默下载浏览器。

在解压后的仓库根目录，PowerShell执行：

```powershell
python skills/talking-head-finish/scripts/studio.py doctor
python skills/talking-head-finish/scripts/studio.py demo --project ./projects/demo
python skills/talking-head-finish/scripts/studio.py setup --project ./projects/demo
python skills/talking-head-finish/scripts/studio.py render --project ./projects/demo
```

输出：`projects/demo/out/final.mp4`、同名原SRT及`report.json`。依赖只安装到项目内，不修改系统Python包。第一次`setup`需要联网。运行后还应检查画面和声音，技术通过不等于主观效果已确认。

## 装入Codex

```powershell
python install_skill.py
```

默认安装到当前用户的`.agents/skills/talking-head-finish`，对应[OpenAI官方技能文档](https://learn.chatgpt.com/docs/build-skills)中的用户级位置。完整文件按SHA256校验并记录收据；重复安装同版本返回已安装，私用版、本地编辑和其他版本不会被覆盖。旧`.codex/skills`已有同名版本时默认停止；旧位置用`--legacy-codex-home`，自定义实际位置用`--target`。其他宿主加`--host workbuddy|doubao-work|generic`并指定它实际识别的目标。无需作者私用目录，安装后验证宿主识别；必要时重启，同名Skill不自动合并。

然后给Agent自己的视频与SRT，调用：

> `$talking-head-finish 读取我的视频和SRT，参考V4实际机制重新设计本期语义分镜，保留原声原速，制作可编辑工程和成片。`

只有视频文件和SRT不能自动决定所有镜头设计；Agent需要阅读`references/production.md`、选择或编写合适的机制，而非整片套用同一模板。

## 使用自己的视频

```powershell
python skills/talking-head-finish/scripts/studio.py init --video ./my-video.mp4 --srt ./my-video.srt --project ./projects/my-episode
```

初始化生成`needs_authoring`项目，拒绝把空白占位计划当成成片。Agent完成`plan.json`及必要的组件改编后设为`ready`，再执行check/render。具体字段、素材路径和动态蒙版规则见[项目格式](skills/talking-head-finish/references/runtime.md)。

新项目的`production-choice.json`最初未选。按first-run.md检测后端、沿用用户明确选择，或问一次；用`capabilities.py choose`记录后再出最终成片。选择“稍后补动画”时交付工作工程与缺镜头清单，不能伪装成完整成片。

本版直接保留用户原片背景；如需替景，先准备合适的动态底片和人物蒙版。公开版没有复制作者的人像、声音、截图、AI账号或完整私用项目。

## 可选H3

本地、云端及超分/插帧分别配置，见[生成接入](skills/talking-head-finish/references/generation.md)。你自行获取对应模型或账号，按各自条款使用，密钥只从本机环境变量读取。

云端例子要求你导出该云环境支持的API格式工作流并填写绑定；不假定作者本地自定义节点已安装在云端。原生片先审核，再后期。使用原生24fps素材不等于取得原生1080p60。

## 开发与授权

```powershell
python -m unittest discover -s tests -v
```

原创代码采用[MIT](LICENSE)，第三方依赖与模型见[独立声明](THIRD_PARTY_NOTICES.md)。MIT不替代Remotion、H3、字体或其他依赖的许可。预览版发布前请阅读验证记录及发行说明；本仓库未包含模型权重、私人素材、凭据和已安装的软件环境。
