# 已确认效果覆盖 · 0.2

本页保留原链接，内容已按本轮确认替换。V4 的 40 段不是默认效果库。

| id | 形式 | 频率 | 含义 |
| --- | --- | --- | --- |
| IntroHuman | side | regular | 开场禁止同一窗口聊到底；视觉回应突然变笨的经历 |
| FixLoss | h3 | regular | 提醒一项恢复，另一项却掉线 |
| ClarifyHuman | side | regular | 降智疑问转向上下文窗口，整词排版 |
| Aperture | h3 | regular | 实体读取孔径拓宽，同时读入更多信息 |
| MisconceptionHuman | side | regular | 提出模型是否真的记住的误区 |
| StatelessIntro | h3 | regular | A current question is handled; transaction ends and the active desk is cleared. No old request is retained in the active call. |
| StatelessCore | h3 | regular | A current question is handled; transaction ends and the active desk is cleared. No old request is retained in the active call. |
| MemoryQuestionHuman | side | regular | 三个应用与看似记住的反问，动态历史辅助 |
| ReReadFilm | h3 | regular | 外部记录带连续流经读取头，解释重读而非模型记忆 |
| OverflowB | h3 | regular | 同一个动作故事续镜，只在本段使用机器人流水线 |
| CapacityHuman | side | regular | 不是变笨，是达到可读取范围的限制 |
| ManageHuman | side | regular | 硬聊被删去，转为管理上下文 |
| WatchHuman | side | regular | 窗口再大也不硬聊；关注使用情况；70%按原话出现 |
| HandoffCarry | h3 | regular | 同一文件夹从旧桌移到干净新桌，打开读取 |
| CompressLoad | h3 | regular | A physical miniature reading machine works slowly under a huge input burden |
| SummaryHuman | side | regular | 完整真人开场总结，提出模型本身不主动记忆 |
| ClosingHuman | side | regular | 先讲完更靠谱的结论，再结束、点赞关注评论、下期见 |
| P2-Capacity | mg | regular | 上下文窗口：一次能读取、处理多少内容 |
| P2-Packet | mg | regular | 第三轮提问时，应用把前两轮问答也随请求带入 |
| W1-Capacity | mg | occasional | 上下文窗口：一次能读取、处理多少内容 |
| W1-Packet | mg | occasional | 第三轮提问时，应用把前两轮问答也随请求带入 |
| V1-Capacity | mg | occasional | 上下文窗口：一次能读取、处理多少内容 |
| V1-Packet | mg | occasional | 第三轮提问时，应用把前两轮问答也随请求带入 |

完整机器可读清单见 [approved-effects.json](../skills/talking-head-finish/references/approved-effects.json)。
