# 发布与粉丝试用

本版 v0.2.0-preview。完整源码通过 main 与同名 Release 提供；粉丝只需把仓库链接交给可执行的 Agent，请它安装完整 skills/talking-head-finish。

已有受管旧版本可用 install_skill.py --upgrade，在校验收据后整体备份升级；私用或用户改过的副本需要宿主展示差异并单独备份，不能覆盖。确认当前宿主加载的是 0.2.0-preview，再发 MP4+SRT 测试。

Release 附件包括完整源码 ZIP、36 秒实际宣传式安装演示、原示例 SRT、核验记录及两个轻量宿主引导包。轻量包不是完整渲染资源，不替代完整安装。

首次测试建议用用户自己的 20–40 秒已剪口播与 SRT；选择背景，检查动态人物边缘与语义，再跑完整片。H3 由用户选择；本地抠像不依赖 H3，但需要自己的 RVM 模型及可运行 ONNX 环境。

完整成片与宣传样片分开。用户视频、声音、截图或生成素材不因安装 Skill 自动公开上传，发布另按明确授权执行。

验证见 [VALIDATION.md](VALIDATION.md)，安装约定见 [INSTALL-FOR-AGENTS.md](INSTALL-FOR-AGENTS.md)。
