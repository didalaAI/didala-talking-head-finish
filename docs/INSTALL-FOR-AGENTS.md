# 给 Agent 的安装约定

用户只需发送仓库链接并说“帮我安装这个 Skill”。由Agent完成安装与检查，不要求用户先执行整页命令。制作视频时读取安装副本内的SKILL.md。

完整Skill是 `skills/talking-head-finish`，不是仓库根目录或轻量bootstrap包。仓库：<https://github.com/didalaAI/didala-talking-head-finish>。

## 安装完整资源

- 优先使用当前Agent原生Skill安装能力，安装整个 `skills/talking-head-finish`。保留scripts、references、integrations、模板、两份完整字体及许可。只有SKILL.md不算完整安装。
- 没有原生安装工具时，下载/克隆完整仓库到持久的授权工作区，读取代码后运行根目录 `install_skill.py`。临时缓存不能充当永久运行资源。
- Codex运行 `python install_skill.py`，默认位置 `~/.agents/skills/talking-head-finish`。旧`.codex/skills`已有同名版本时会保留并停止，先定位用户想用的版本，不覆盖私用版。
- WorkBuddy、豆包工作及其他Agent：用原生安装器或客户端实际识别的技能目录，不猜通用路径。确认后运行 `python install_skill.py --host workbuddy --target <实际目录/talking-head-finish>`；豆包工作用`--host doubao-work`，其他宿主用`--host generic`。WorkBuddy安装器补齐展示元数据，不改变完整运行资源。
- 本安装器核对全部源文件SHA256并写`.installation.json`。相同版本重复安装返回`already_installed`；用户编辑、私用版或不同版本均保留原目录。更新用宿主安装器展示差异/备份，或独立目标安装后切换；不能把拒绝覆盖报告为成功。

原生安装器不写本仓收据时，不用`--verify`判它失败；改为比对源Skill和安装副本的完整清单，再验证宿主能发现它。需要刷新时执行支持的刷新或提示重开客户端。

## 准备基础环境

从**安装副本**运行 `python <Skill目录>/scripts/studio.py doctor`。Python不存在时先按宿主能力准备Python。需要Python≥3.11（测试3.12）、Node/npm或pnpm（测试Node24）、FFmpeg/ffprobe/libass、Chrome或Edge。首次安装需联网；`REMOTION_BROWSER_EXECUTABLE`可指定实际浏览器。

安装任务包含检查并在权限允许时补齐基础依赖；使用官方渠道及用户目录/隔离环境，遵守宿主权限，不默认全局管理员安装。准备后重测。doctor返回0表示基础检测通过，2表示缺项；GPU、Torch、ComfyUI、H3不属基础必装项。

在授权工作区**新目录**运行：

```text
python <Skill目录>/scripts/studio.py demo --project <新演示目录>
python <Skill目录>/scripts/studio.py setup --project <新演示目录>
python <Skill目录>/scripts/studio.py render --project <新演示目录>
```

检查MP4和report.json。报告分别写清：Skill安装、宿主识别、基础检测、实际渲染、可选生成后端。没有文件执行/浏览器/长任务能力时说明具体缺项及已完成部分，不承诺所有Agent只读链接就能渲染。

同一安装及环境已有有效演示记录可复用；代码/依赖变化后重验，不要求每期重复安装。

## 下一次只需视频和SRT

用户发MP4、SRT并说“按照这个Skill剪辑好口播视频”，进入安装副本的[首次制作与后端选择](../skills/talking-head-finish/references/first-run.md)。Agent自动读取输入、检测能力、设计分镜和制作，不要求用户懂Comfy或Remotion。

有可用本地H3就沿用并先验证短镜头。没有则由用户选择：动态MG与现有素材完成整片、接入自己的云服务、Agent已有其他视频模型、先做其余部分稍后补动画。不自动切换、不自动下载大模型或提交收费任务。

公开源码无需GitHub登录。粉丝使用自己的素材和后端账号，不需要作者密码、令牌或模型。WorkBuddy、豆包工作仍待真实客户端试用，见[运行边界](../skills/talking-head-finish/references/host-compatibility.md)。
