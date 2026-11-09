# WorkBuddy与豆包工作：能否得到同类成片

核对日期：2026-11-09。这里讨论豆包工作PC客户端，与普通豆包聊天、豆包应用插件的运行环境分别判断。基础公开工程已在本机和GitHub Windows机器渲染；当前没有在WorkBuddy、豆包工作客户端完成整片端到端测试。

## 哪些能复用，哪些不能保证

| 层次 | 换Agent后的情况 |
| --- | --- |
| 同一Remotion工程、时间轴、输入素材和字体 | 可复用同款字效与MG。相同代码驱动渲染，不依赖必须使用Codex；浏览器、编码器和系统差异仍可能影响编码字节与色彩，不能保证文件逐字节相同 |
| Agent为新文案设计分镜和改写代码 | 不同模型的理解、审美、执行与修订会有差异，Skill不能保证第一次就和原作者完全一样 |
| H3新生成的情景动画 | 需同一生成后端、模型/工作流、首尾帧和动作审核。聊天模型能写提示词不等于已经具备H3；相同提示词也不保证随机片段相同 |
| 私用V4原素材 | 作者的人像、原录音、聊天截图和旧生成片没有公开；公开版提供机制和配方，粉丝使用自己的素材 |

## WorkBuddy

普通粉丝只需发仓库链接说“帮我安装Skill”，Agent按[仓库安装约定](https://github.com/didalaAI/didala-talking-head-finish/blob/main/docs/INSTALL-FOR-AGENTS.md)安装完整资源并检测环境。制作时读[first-run.md](first-run.md)；没有可用H3由粉丝选择，不默认降为静态PPT。下面轻量包是受限导入的补充路线，不是唯一安装方式。

[WorkBuddy官方技能文档](https://open.workbuddy.cn/docs/skill)支持SKILL.md、参考资料和脚本；市场入口列出的元数据比本仓Codex入口更多。因此提供独立的WorkBuddy轻量引导包，补齐其展示字段，避免把Codex安装路径当成所有宿主的路径。

先导入轻量包，再把完整仓库作为授权工作区。由该环境实际运行Python、Node/npm或pnpm、FFmpeg/ffprobe/libass及Chrome/Edge。若缺工具，先配置；本包不假定WorkBuddy内置了这些软件，也不假定它与宿主电脑共享同一个盘符和进程环境。

本地直接使用完整仓库也可以：让WorkBuddy读 `skills/talking-head-finish/SKILL.md` 和相关references，再执行相同CLI。自定义目录安装可使用安装器的`--target`参数，路径以当前客户端识别的位置为准，不猜固定路径。

## 豆包工作PC客户端

[飞书官方介绍](https://www.feishu.cn/content/article/7677519271848610746)列出自建、导入技能及脚本、参考资料、模板等能力。是否能完成本工程，还要在当前执行环境实测命令、浏览器、字体、文件访问、时长与资源限制。

推荐本地完整工程加轻量引导，先做doctor和24秒demo。不把“支持技能”直接等同于已跑通Remotion。云端环境也可能运行，但本预览版未做对应云端适配；浏览器路径、依赖安装、素材上传、运行时限、文件保留与生成服务访问都需重新验证。

### 市场提审体积与本地使用是两条路线

[豆包开放平台Skill接入指南](https://open.doubao.com/document/doubao-developer-guide/skill-integration-guide)列出ZIP≤16MB、单文件解压后≤2MB、解压总量≤16MB及条目数限制，并有资质/审核要求。这些是开放平台提审要求，不能直接套用到所有本地目录导入方式。

当前完整工程的两份字体分别为8,569,308和8,808,068字节，单份已经超过2MB；所以不能把完整源码ZIP当成可直接提审包。轻量包只提供规则和仓库入口，完整字体与代码留在授权工程中；不通过删除字体或降低画面质量来塞入小包。

官方应用插件文档还说明该插件运行模式需通过MCP暴露执行能力。它与豆包工作客户端的自定义本地技能不是同一个接口；只有采用应用插件服务路线时，才需要另建受控的素材上传、项目/渲染任务、状态与下载工具，以及生成后端的授权。当前仓库没有冒充已经提供这一整套在线服务。

## 最少改动与验收

1. 使用对应宿主的引导入口/元数据，核心Remotion代码和字体保持完整。
2. 确认命令在素材可访问的环境执行；Windows为本版主要实测环境，其他系统显式配置浏览器路径。
3. 在完整仓库根目录运行README中的doctor→demo→setup→render，检查实际输出的MP4及SRT，不只看聊天回复。
4. 接入本期原视频、动态mask和H3后端。宿主不支持本地命令时，需要兼容连接器/渲染服务；不能只改提示词就宣称完成适配。
5. 在对应客户端用完整新文案制作至少一条，并按同一语义、动作、阅读与原速播放标准审片，再将该宿主标为“端到端已验证”。

## 导出引导包

在完整仓库根目录执行，输出目录放在仓库外：

```text
python scripts/export_host_skill.py --host workbuddy --out <仓库外目录>/workbuddy-bootstrap.zip
python scripts/export_host_skill.py --host doubao-work --out <仓库外目录>/doubao-work-bootstrap.zip
```

两者是轻量入口，不包含完整效果工程或模型，不等于已上架市场。完整仓库：https://github.com/didalaAI/didala-talking-head-finish 。
