# 0.1.0-preview 发行说明

本版把“只有规则文字”的Skill变成自包含的机制代码、运行脚本与镜头配方。主入口保留V4的人物旁字、进入后收稳的大字、实体MG、动态人物遮挡接口、原截图推近和可选H3；并未把整片统一换成Vox。

包含40段机制索引、23段MG实现、8组H3配方及实际API工作流。人像、原录音、聊天截图、旧生成片、模型、GPU环境和密钥不在公开包内。新文案仍需Agent做逐句语义设计，不能保证靠同一个随机提示词复制出逐像素相同的H3片段。

## 给粉丝的第一步

1. 从本仓库的Code ZIP或Release下载源码，解压到自己的目录。
2. 按README安装Python、Node/npm、FFmpeg和Chrome/Edge；执行doctor。
3. 先运行24秒demo，再安装Skill。已有同名私用Skill时安装器会拒绝覆盖。
4. 提供自己的已剪MP4与SRT，调用`$talking-head-finish`。先让Agent完成语义分镜和工程，再渲染。
5. 想用H3时再选择本地GPU或云服务。基础MG无需H3；本版不把复杂GPU依赖塞进基础安装。

## GitHub发布步骤

1. 在自己的账号或组织新建公开仓库`didala-talking-head-finish`；不要用个人私用Skill目录直接创建仓库。
2. 上传本公开源码包中的文件；README、LICENSE与第三方说明一起保留。
3. 执行仓库自带`python scripts/release.py audit`与单元测试；GitHub Actions会重复测试，并在Windows检查Node类型和完整demo渲染。
4. 创建`v0.1.0-preview`预发行版，把源码ZIP、24秒基础demo、验证记录和SHA256SUMS作为Release附件。大视频和模型不放进Git历史。
5. 抖音简介放仓库链接；置顶说明“Windows预览版，基础MG可跑，H3需自备后端，可能产生服务费用”。先邀请少量粉丝在不同机器试用，收集日志时删去本机路径和账号数据。
6. 本地H3、真实云生成、GPU后期和至少一台其他机器的完整验证完成后，再发布稳定版；新增环境实测写入VALIDATION，不用旧片成功记录代替。

本版先提供GitHub源码和本地Skill安装。后续若希望粉丝通过插件目录安装，可按[官方插件封装文档](https://developers.openai.com/plugins/build/plugins)包装同一技能及安装指引；这不免除本地FFmpeg/Node等执行依赖，不把“插件装上了”当作GPU环境已经就绪。

公开仓库：[wangkaixiang-ai/didala-talking-head-finish](https://github.com/wangkaixiang-ai/didala-talking-head-finish)。预览包、基础demo和校验文件通过Releases分发。使用者连接自己的GitHub或生成后端账号，作者凭据不随源码分发。
