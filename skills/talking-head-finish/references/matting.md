# 动态人物分离与背景选择

本模块独立于 H3。本仓含本地 ONNX 适配器，FP32 RVM 模型与运行依赖需在用户环境准备；用户已有可用动态抠像工具也可以使用，但仍交付实际动态前景与 alpha。

## 背景

`python scripts/matting.py list-backgrounds` 列出：

| id | 背景 |
| --- | --- |
| didala-purple | 作者指定的紫蓝 AI 演播室，无人物底图 |
| pearl-gallery | 珍珠白展厅 |
| midnight-navy | 午夜蓝演播室 |
| warm-editorial | 暖灰人文书房 |

图片位于 assets/backgrounds，安装时保持完整。用原视频短段预览所选背景；保留已有选择，不每期反复询问。用户提供自有背景时先检查分辨率、授权和人物文字可读区，再配置独立项目资源。

## 本地准备与执行

基础 CLI 不依赖 NumPy/ONNX Runtime。需要本地抠像时先检查实际环境能否 import 并加载模型；仅安装包存在不算通过。推荐隔离环境：

```text
python scripts/matting.py prepare --env-dir <用户工作区/抠像环境>
<该环境的python> scripts/matting.py fetch-model --directory <用户模型缓存> --variant resnet50
<该环境的python> scripts/matting.py render --project <本期项目> --model <FP32 ONNX> --background didala-purple --position right
```

ResNet50 权重约 107 MB，MobileNetV3 是更轻的备选；准备前说明下载与本地计算，已有用户模型优先。模型来自 [RVM 官方项目](https://github.com/PeterL1n/RobustVideoMatting)，其权重/上游代码适用独立 GPL-3.0 条款，不随本仓 MIT 代码分发。本适配器按公开张量接口独立实现；不复制上游模型代码。

模型可由 `--model`、`RVM_ONNX_MODEL` 或安装目录私有 `config.local.json` 的 `matting_model` 指定；私有配置不进入安装分发包。

`position` 可选 right、center、keep。位置由本片实际 alpha 范围计算，不沿用作者固定坐标。默认全分辨率输入/输出，模型内部 downsample 不是把最终视频降成低清。逐帧顺序执行并回收循环状态；不能每帧清零导致闪烁。

输出 public/presenter-composite.mp4、presenter-foreground.mp4、presenter-mask.mkv，以及 matting/matting-record.json 和三张检查图。自动更新 plan 的 presenter、foreground、mask、audio_source；原声始终从 source.mp4 读取。RGB 与 alpha 使用完全相同的位移/缩放，穿身合成使用处理后的前景，不能拿原房间恢复到文字前面。

## 逐期验收

查看真实动态片而不只看静帧：发丝/耳边/肩膀/衣领/手指、动作与遮挡、人物消失或分裂、漏抠/旧背景残留、白边与时间闪烁。核对 1080p60、总帧数、全长 mask 与声画同步。源片没拍到的下半身或被物体遮住的部位，不能声称“恢复完整”。

审查通过后由执行 Agent 将 matting-record.json 的 status 改为 reviewed，并记录已检查的时间点及剩余问题；否则最终 render 会阻止交付。质量不合格时用本期局部处理、更高质量工具或说明具体素材局限，不静默拿静止抠图替代。
