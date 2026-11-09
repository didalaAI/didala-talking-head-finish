# V4公开版效果覆盖

该索引保留原案例的镜头作用，用于找到实际机制。新文案需重新编排时间、台词和动作；这里不是固定40镜头的通用时间轴。

人物字效9段、全屏MG23段、H3配方8段。私用原片和生成视频不在公开包中。

| 原机制ID | 形式 | 原案例语义 | 可复用入口 |
| --- | --- | --- | --- |
| IntroHuman | 人物旁字 | 开场禁止同一窗口聊到底；视觉回应突然变笨的经历 | [文件](../skills/talking-head-finish/assets/template/src/Human.tsx) |
| RequirementsUI | 全屏MG | 明确三条要求，随后状态开始丢失 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| FixLoss | H3配方 | 提醒一项恢复，另一项却掉线 | [文件](../skills/talking-head-finish/references/h3-shot-recipes.json) |
| WaitingUI | 全屏MG | 小修改迟迟没有完成，连续显示卡住与重试 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| ClarifyHuman | 人物旁字 | 降智疑问转向上下文窗口，整词排版 | [文件](../skills/talking-head-finish/assets/template/src/Human.tsx) |
| Definition | 全屏MG | 一次输入的文字通过有限读取范围，直接解释窗口 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| Aperture | H3配方 | 实体读取孔径拓宽，同时读入更多信息 | [文件](../skills/talking-head-finish/references/h3-shot-recipes.json) |
| MisconceptionHuman | 人物旁字 | 提出模型是否真的记住的误区 | [文件](../skills/talking-head-finish/assets/template/src/Human.tsx) |
| StatelessIntro | H3配方 | A current question is handled; transaction ends and the active desk is cleared. No old request is retained in the active call. | [文件](../skills/talking-head-finish/references/h3-shot-recipes.json) |
| StatelessCore | H3配方 | A current question is handled; transaction ends and the active desk is cleared. No old request is retained in the active call. | [文件](../skills/talking-head-finish/references/h3-shot-recipes.json) |
| MemoryQuestionHuman | 人物旁字 | 三个应用与看似记住的反问，动态历史辅助 | [文件](../skills/talking-head-finish/assets/template/src/Human.tsx) |
| NewWindow | 全屏MG | 原窗口含历史，新窗口未携带旧对话，直接展示原因 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| RoundPacket | 全屏MG | 第三轮输入逐项接入当前问题、第一轮提问和回复、第二轮提问和回复 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| HistoryResend | 全屏MG | 历史整段重发，在回答前重新读取 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| ReReadFilm | H3配方 | 外部记录带连续流经读取头，解释重读而非模型记忆 | [文件](../skills/talking-head-finish/references/h3-shot-recipes.json) |
| HistoryStack | 全屏MG | 新问题与回复不断落入真实变厚的记录堆 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| FiniteIntro | 全屏MG | 明确可处理范围有限，超出后转入流水线例子 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| OverflowA | 全屏MG | Replace earlier repeated robot conveyor shot; old material outside the reading boundary is not processed. | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| OverflowB | H3配方 | 同一个动作故事续镜，只在本段使用机器人流水线 | [文件](../skills/talking-head-finish/references/h3-shot-recipes.json) |
| CapacityHuman | 人物旁字 | 不是变笨，是达到可读取范围的限制 | [文件](../skills/talking-head-finish/assets/template/src/Human.tsx) |
| Screenshots | 全屏MG | 真实原截图连续定位并放大占用提示，无画框式标题 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| GaugeIntro | 全屏MG | 个人经验的70%提示，建立观察负载 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| LoadEngine | 全屏MG | 信息负载增加，精密机械运转吃力、变慢 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| TokenCost | 全屏MG | 读取的信息和消耗的Token随输入增加 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| ManageHuman | 人物旁字 | 硬聊被删去，转为管理上下文 | [文件](../skills/talking-head-finish/assets/template/src/Human.tsx) |
| ModelCapacity | 全屏MG | 模型标识依原声切换，范围扩大，部分型号支持100万Token | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| WatchHuman | 人物旁字 | 窗口再大也不硬聊；关注使用情况；70%按原话出现 | [文件](../skills/talking-head-finish/assets/template/src/Human.tsx) |
| HandoffRequest | 全屏MG | 从占用提示接到总结进度与重点的请求，标题继续进入下一镜 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| HandoffPack | 全屏MG | 从杂乱工作记录中整理要点，放入便携交接文件夹 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| HandoffCarry | H3配方 | 同一文件夹从旧桌移到干净新桌，打开读取 | [文件](../skills/talking-head-finish/references/h3-shot-recipes.json) |
| ResumeWork | 全屏MG | 新窗口已读入交接，接着同一项工作 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| CompressFold | 全屏MG | Long conversation folds into a compact useful summary | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| CompressLoad | H3配方 | A physical miniature reading machine works slowly under a huge input burden | [文件](../skills/talking-head-finish/references/h3-shot-recipes.json) |
| CompressionResult | 全屏MG | A missing concrete constraint can affect the following video-editing result | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| SummaryHuman | 人物旁字 | 完整真人开场总结，提出模型本身不主动记忆 | [文件](../skills/talking-head-finish/assets/template/src/Human.tsx) |
| RecapRead | 全屏MG | 看似记得来自每次重发和重读，记录继续增长 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| RecapCapacity | 全屏MG | 有限范围容不下旧内容，新的内容确实把旧内容推到范围外 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| RecapHandoff | 全屏MG | 从旧对话提取进度、重要要求与下一步，生成同一份交接.md | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| FreshPaperDesk | 全屏MG | 纸艺人物带交接文件到干净桌面，打开并继续写作 | [文件](../skills/talking-head-finish/assets/template/src/Remade.tsx) |
| ClosingHuman | 人物旁字 | 先讲完更靠谱的结论，再结束、点赞关注评论、下期见 | [文件](../skills/talking-head-finish/assets/template/src/Human.tsx) |

H3配方包含风格/道具/动作/运镜及生成提示；不包含原片生成结果。GPU后期助手仍待本轮实际环境验证。文字代码和MG机制可以直接查看、改编、运行；人物动态遮挡要使用自己的视频mask。
