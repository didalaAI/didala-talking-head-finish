# 运行与项目格式 · 0.3.0

基础 CLI 使用 Python 标准库。需要 Python ≥3.11、Node/npm 或 pnpm、FFmpeg/ffprobe/libass、Chrome/Edge。锁定 Remotion 4.0.539、React 19.2.0、TypeScript 5.9.3。H3/Torch 不是基础渲染前提；生成与抠像另见各自说明。

`demo` 创建 36 秒独立安装演示；`init` 从用户完整视频/SRT 建立 needs_authoring 工程。两者拒绝覆盖非空目录。`setup` 安装锁定的依赖并类型检查；`check` 检查分镜；`render` 编译已确认设计、生成 ASS 与 SFX、恢复动态人物前景、最终编码与全长解码。保留原声原速，默认无 BGM。

工程包括 plan.json、original.srt、captions.json、source-record.json、production-choice.json、designs/、public/、src/selected/、out/final.mp4、out/final.srt、out/report.json。design-build.json 保存每段效果与本期设计的哈希。

```json
{
  "version": 3, "status": "needs_authoring", "fps": 60,
  "width": 1920, "height": 1080, "frames": 1044,
  "presenter": "source.mp4", "mask": null,
  "scenes": [
    {"id":"opening","start":0,"frames":389,"kind":"side","variant":"V31-IntroHuman","design":"designs/opening.json"},
    {"id":"explain","start":389,"frames":655,"kind":"mg","variant":"V3-P2-Capacity","design":"designs/explain.json"}
  ]
}
```

此示例不是可直接交付的成片：必须根据本期字幕建立两个 design 文件、素材和全长覆盖，再经检查设置 ready。详见 [源码改编](design-authoring.md)。start/frames 是整数帧，连续覆盖总时长；SRT 不改写、不均分、不得超过画面尾部。

- side/punch、mg、screen、h3：必须指定清单内的精确 variant 与已编排 design。纯真人无旁字可以用不带 variant/lines/design 的 side 段。
- h3：asset 指向本期实际生成的视频；时长不足拒绝，不冻结尾部。文本和动作时钟属于 design。
- screen：完整截图、软件身份、真实数值和 ROI 位于 design.screens，不能套作者截图位置。
- through_body：含 presenter 的穿身段必须提供同时间线动态 mask。白为人物；可另提供 foreground。字幕在人物合成后最后烧录，检查移动边缘，而不只看帧数。
- caption_emphasis：依据原 SRT cue.start 与重点词编排最终字幕层级；最多两个重点词，原 SRT 保留。
- video：用户实际素材视频，用 asset 与整数帧 trimBefore。promo 仅用于明确需要的宣传开场/背景展示/收尾，不给整片强加片头片尾。

当前仅支持 1920×1080、60fps。输入规范化不改速；音画尾差超过 0.2 秒先检查输入，不长冻结。抠像使用 matting.py，四种背景需选择和审片；缺 H3 时依 [首次制作](first-run.md)记录用户选择。技术检测、画帧检查、连续观看、人工听音分别记实。
