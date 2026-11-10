# 从确认源码制作本期效果

安装必须包含完整 Skill 文件夹。approved-effects.json 给出 39 个精确版本、频率、默认版本、源文件与可编辑 JSON 示例；selection-receipt.json 保存 revision 159。assets/designs 的 TSX 是已确认动画的实际实现，tokens.json 标记可替换文案，四个系列分别独立保留，不能只复制 SKILL.md。

1. 按原 SRT 做全长分镜，选择清单中的 effect ID。
2. 运行 `python scripts/design.py example --effect V31-IntroHuman --out <项目>/designs/opening.json`。脚本拒绝覆盖已有文件。该文件是示例，不是本期完成稿。
3. 按文意编辑 `text`（T 编号对应同系列 tokens.json 中的原句；包括未执行分支，勿删键）、`recipe` 中的文案、`assets` 中的本期素材、`text_region` 中测量的文字区。text 值可含换行，不接受代码。真人各变体保留各自编排；应用列表必须配对应图标，不能把文字列表当图标。
4. `timing` 每项为 `[参考秒, 本期段内秒]`。根据本期 SRT 的动作落点填写，保持递增；始于 `[0,0]`，末项覆盖完整动作与本段。它不是改原声速度；只重映射动画时钟。长段需增加新动作或分镜，不能用拉长最后一帧填充。真人 recipe.beats 的时码使用参考时钟，由同一映射转换。
5. 界面类填写 `screens`：原图路径、真实尺寸、`focus=[x,y,w,h]`、软件名、图标和真实数值。旧双界面变体可填两个截图；最新与 V2 使用一个。素材相对项目 public；不是作者界面的固定截图坐标。
6. 生成类先按 h3-shot-recipes.json 完成用户选择的真实生成，在 scene.asset 指向本期视频；不要用静态图或测试占位视频代替。参考首帧只适用相同含义。电影 overlay 与生成底片分开保存。
7. 写 `semantic_alignment` 说明本期对象/动作/结果，检查所有在用词句与时码后设置 `reviewed_for_current_script=true`。plan.scenes 对应段设置 `variant` 为 effect ID、`design` 为该 JSON 的项目相对路径；`kind` 按 human→side/punch、mg→mg、screen→screen、h3→h3。
8. `studio.py check` 验证选择、素材、时序和蒙版；`design.py compile --project <项目>` 生成 src/selected 下的独立组件。studio.py render 也自动编译。生成代码保留批准版排版/动作，模板代码不在运行时执行任意表达式。

真人：项目 presenter 提供完整当前底片，穿身段 through_body=true，并提供同时间线动态 mask/foreground。V31 Capacity/Manage/Closing 的大字过程需要遮挡；其余含 punch/hero 的本期编排也要检查。抠像默认将人物放右侧，但必须检查实际边界。未使用效果的纯真人段可以用没有 lines/variant/design 的 side 段。

默认安装演示是独立 36 秒工程，明确 technical_demo=true。其示例文案允许保留，仅用于验收。真实输入不得标成 technical_demo 来绕过本期编排检查。

字幕强调：plan.caption_emphasis 可填写 `[{"start": 原SRT句子的开始秒, "words": ["一个重点词"]}]`。每句最多两个，必须来自原句。最终 ASS 用 52px 正文、58px 暖金强调，原 SRT 内容不改；预览播放器显示普通字幕，检查编码成片确认强调。

复杂新题材可在可编辑工程里修改生成的组件，但先复制到独立 authored/ 目录并变更明确的项目路由，避免下一次 compile 覆盖。不要改共享已确认源库去适应某一期，除非用户明确要求更新 Skill。
