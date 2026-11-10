"""Export small host-specific bootstrap skills without removing core fonts/assets."""
from pathlib import Path
import argparse,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
VERSION='0.3.0'
REPOSITORY='https://github.com/didalaAI/didala-talking-head-finish'
HOSTS={'workbuddy':'WorkBuddy','doubao-work':'豆包工作'}

def content(host):
    if host not in HOSTS:raise ValueError('Unsupported host')
    name='talking-head-finish-'+host
    if host=='workbuddy':
        front='''---
name: talking-head-finish-workbuddy
display_name: 迪达拉口播制作·工程引导
display_name_en: Didala Talking Head Production Bootstrap
description: 在用户授权的完整工程中制作语义动效口播；先检查本地Python、Node、FFmpeg和浏览器，再使用原声、准确字幕与实际MG代码。
description_zh: 使用完整开源工程制作口播视频；本包是轻量引导入口，不包含渲染素材和模型。
description_en: Bootstrap an authorized local talking-head project using the complete public runtime, original audio and semantic motion graphics.
version: "0.3.0"
author: "didalaAI"
examples_zh:
  - "使用迪达拉口播制作，先检查环境并运行36秒演示。"
---
'''
    else:
        front='''---
name: talking-head-finish-doubao-work
description: 在用户授权的完整工程中制作语义动效口播；先验证当前执行环境能运行Python、Node、FFmpeg与浏览器，再读取原SRT、复用实际MG代码制作成片。
metadata:
  version: "0.3.0"
  author: "didalaAI"
---
'''
    body=f'''\n# 迪达拉口播制作 · {HOSTS[host]}本地工程引导

本包只提供入口。完整代码、字体、字幕机制与素材规则来自 {REPOSITORY}，对应版本 {VERSION}。宿主客户端端到端制作尚未实测，不把结构校验称为客户端验收或市场上架。

用户只给仓库链接说“安装Skill”时，由Agent读取仓库的docs/INSTALL-FOR-AGENTS.md，按当前宿主能力安装完整Skill并验证，不要求用户自己跑整套终端命令。这个轻量包仅在导入/市场体积受限时提供入口，不替代完整安装。

1. 在用户授权的工作区定位完整仓库；需要下载时使用上述公开仓库和对应发行版。要求仓库中存在 `skills/talking-head-finish/scripts/studio.py` 与完整 `assets/template`。不要把这个轻量包自身当成完整渲染工程。
2. 确认当前命令执行环境与素材所在环境相同，读取完整仓库的 `README.md`、`skills/talking-head-finish/SKILL.md`、`references/production.md`、`references/runtime.md` 和 `references/host-compatibility.md`。references目录位于完整Skill中。
3. 在仓库根目录执行 `python skills/talking-head-finish/scripts/studio.py doctor`。缺少Python、Node/npm或pnpm、FFmpeg/ffprobe/libass或浏览器时，按宿主权限准备运行环境；不把预装假设当成检查结果。云端进程不能直接访问用户电脑盘符；先选择确实可访问素材的环境。
4. 新建空项目，先运行 `demo --project projects/host-demo`、`setup --project projects/host-demo`、`render --project projects/host-demo`（均调用同一个studio.py）。实际检查36秒MP4与报告后才报告基础渲染成功。缺少运行能力时说明缺什么，不输出虚构成片或静态PPT替代。
5. 用户自己的MP4/SRT用 `init`建立needs_authoring工程。Agent按本期语义编写分镜与plan，保留原声原速；读取已确认39个版本的真实源码及 design-authoring.md，按制作规范逐段验证。新主题不能照搬上下文窗口例子的文字、道具和时码。
6. 保留完整字体、动态字幕、原速动作和质量门槛。穿身效果使用用户本期动态mask。不要为了压缩Skill体积修改字体或替换MG；大文件应留在完整工程。
7. H3不是当前聊天模型。需要生成时读取完整Skill的generation.md，保持用户选择的后端与授权；宿主要求连接器时通过认可的连接器执行。更换内置视频模型属于新后端，需要适配与重新审片，不能直接声称与H3一致。
8. 字幕、音频、素材与本次MP4均完成校验后再交付。工具没有执行、生成后端不可用或没有实际观看/试听时，分别如实记录，不假称端到端通过。

制作前还必须读取完整Skill的references/first-run.md，运行capabilities.py inspect。没有可用H3时由用户选择动态MG＋现有素材、自己的云服务、Agent已有其他视频模型，或稍后补生成动画；记录production-choice.json，不自动切换或下载模型。已有验证记录的相同环境不必每期重跑安装演示。

完整工程中的基础渲染无需Codex专用API；本宿主的文件权限、命令工具、执行环境和外部生成后端仍需分别配置。
'''
    readme=f'''# {HOSTS[host]} 轻量引导包

版本 {VERSION}。适用对象是可以读取授权项目并执行命令的Agent工作环境。此包不会安装Python、Node、FFmpeg、浏览器、H3或完整工程。

在客户端支持的本地技能导入入口导入整个文件夹，或让客户端按自身实际安装位置读取SKILL.md；不要只上传正文并丢弃运行工程。完整工程：{REPOSITORY} 。

随后把完整仓库选为工作区，明确要求Agent先跑doctor与36秒demo。宿主若无法启动命令，先解决执行工具或连接器；不能把SKILL.md读入成功当作MP4渲染成功。

本包仅做结构、链接和体积检查，未在{HOSTS[host]}里完成端到端口播测试，也未提交任何技能市场审核。开放平台上架还需按各自规则补齐图标、资质、工具鉴权及测试材料。
'''
    record=dict(host=host,version=VERSION,repository=REPOSITORY,bootstrap_only=True,runtime_included=False,host_end_to_end_tested=False)
    return name,{'SKILL.md':front+body,'README.md':readme,'runtime-location.json':json.dumps(record,ensure_ascii=False,indent=2)+'\n','LICENSE':(ROOT/'LICENSE').read_text(encoding='utf-8')}

def export(host,destination):
    destination=Path(destination).resolve()
    if destination.is_relative_to(ROOT):raise ValueError('Write exported ZIP outside the source repository')
    if destination.exists():raise ValueError('Destination exists; nothing overwritten')
    name,files=content(host);destination.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as z:
        for filename,value in files.items():z.writestr(name+'/'+filename,value)
    return dict(host=host,files=len(files),zip_bytes=destination.stat().st_size,sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),bootstrap_only=True,host_end_to_end_tested=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--host',choices=HOSTS,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    try:print(json.dumps(export(a.host,a.out),indent=2))
    except ValueError as error:p.error(str(error))
