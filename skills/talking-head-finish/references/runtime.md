# 运行与项目格式

基础CLI仅依赖Python标准库；Node依赖、FFmpeg和浏览器需单独安装。当前参考组合为Python3.12、Node24、Remotion4.0.539、React19.2.0和TypeScript5.9.3。基础渲染无需Torch或H3。首先执行doctor，必要时用`REMOTION_BROWSER_EXECUTABLE`指向实际Chrome/Edge。

`demo`创建24秒完整示例；`init`为用户自己的视频创建未设计分镜的工程；两者都拒绝覆盖非空目录。`setup`优先npm ci，无npm时可使用pnpm导入同一package-lock并冻结安装。它不复制作者旧node_modules。`check`校验计划，`render`从计划生成Remotion数据、准确字幕、SFX和最终MP4。

项目文件：

```text
plan.json         Agent为本期编写的整数帧分镜
original.srt      原字幕，不改写
source-record.json 输入哈希（真实输入项目）
public/           本项目视频、动态mask、截图、字体和生成片段
src/              可编辑Remotion组件
out/final.mp4
out/final.srt
out/report.json
```

## 计划示例

```json
{
  "version": 1, "status": "ready", "fps": 60,
  "width": 1920, "height": 1080, "frames": 360,
  "presenter": "source.mp4", "mask": null,
  "scenes": [
    {"id":"a","start":0,"frames":180,"kind":"side","eyebrow":"本期重点","lines":["完整词组","分层呈现"],"foot":"辅助解释"},
    {"id":"b","start":180,"frames":180,"kind":"mg","variant":"Definition"}
  ]
}
```

`start/frames`均为整数帧，覆盖总帧数，不留空隙或重叠，ID不重复。`status`为needs_authoring时拒绝成片。内置MG例子的文案仅适合原上下文主题；新片必须改编。新增组件在Remade中明确注册。

- `side/punch`：`eyebrow`、`lines`、`foot`决定本期文字。punch为大字进入并收稳。
- `mg`：`variant`选择V4机制；索引见v4-effect-catalog.json。需要用户动态预览时设`mediaPreview`为public中的视频，该视频应覆盖所用局部时长和代码的trimBefore偏移。
- `h3`：`asset`指向public中的实际生成视频；不足时长会拒绝，不能冻结尾部填充。`lines`可放准确画外标题。
- `screen`：`screen`包含`asset/name/width/height/focus`；focus为原图像素中的[x,y,w,h]。使用完整原图，不用作者私有截图。
- `through_body:true`且有presenter时，必须提供全长动态灰度视频mask（白为人物），`mask`相对于public。合成恢复原人物后再烧录字幕，不让人物覆盖字幕。蒙版必须和本期机位/动作匹配；仅帧数检查不能证明抠像边缘合格。

本版将原片规范到1080p60，不变速；音视频尾差超过0.2秒时需先检查输入，不自动长冻结。短尾差仅补足原片声音所需的画面。源字幕哈希被保留；要改稿应另建明确的新版本，而不是直接改original.srt。

修改plan后执行check，再渲染。检查out/report.json中的技术状态，并实际观看当前MP4。文字阅读不够应改镜头分工、提前进入或保留标签，不擅自加速口播。
