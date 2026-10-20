# Plain Craft Launcher (PCL) chensunlai 修改版

这是第三方基于 [PCL](https://github.com/Meloong-Git/PCL) 独立修改的版本，不是官方发行版。
原作者：**龙腾猫跃**；[赞助原作者](https://afdian.com/a/LTCat)。保留上游署名、关于页面和 LICENCE。

下载功能修改：`Plain Craft Launcher 2/Modules/ModSecret.vb` 中
`Public Const RestrictMcDownload As Boolean = False`。
构建时另将同版本官方成品中的微软 Client ID 和 CurseForge 配置内置到程序，无需运行时环境变量。

## 自动跟随 Release

- GitHub Actions 每小时第 23 分钟检查一次，实际开始时间可能受 GitHub 调度影响。
- 从 `2.99.0.0` 开始跟踪之后发布的所有 Release，包含预发布；不会补编更早的历史版本。
- 按发布时间依次合并上游 Release **标签指向的源码**，保留这一个常量修改及本仓库的自动化文件。
- 仅在 GitHub Windows runner 上编译 Release，不在本地编译。
- 成功后发布 `fork-上游标签-embedded`，附 `.exe`、完整 `.zip` 和 `SHA256SUMS.txt`；预发布标记与上游一致。旧的无内置配置版本保留历史记录。
- 已成功发布的版本会跳过；失败的版本下次检查自动重试。上传完成后才公开 Release。
- 修改位置变化、合并冲突或出现额外源码差异时会失败并停止发布，避免静默发布错误版本。
- 上游长期不发布时，每 30 天生成一个无源码变化的空提交，防止计划工作流因仓库不活跃而停用。
- 可在 Actions → Follow upstream releases → Run workflow 手动检查并重试。
- 只使用 GitHub 自动提供的 `GITHUB_TOKEN`，不需要保存个人 PAT。
- 上游自带的 Build 工作流在此 fork 中停用，由本工作流负责编译和发布。
- 应用源码及资源跟随上游；`.github/workflows/` 保留本 fork 的定义，避免普通自动化令牌无法更新工作流文件而中断同步。

这里的“自动更新”指仓库同步和 GitHub Release 发布；未修改启动器自身的在线更新服务。
下载修改版请使用本仓库的 Releases。

## 内置官方成品配置

Actions 从上游 Release 标签自带的 `最新正式版.zip` 读取官方 EXE，先验证程序版本与标签一致，
再静态读取微软 Client ID 和 CurseForge 请求头配置，写入未提交的构建副本。
编译完成后验证 EXE 中的配置与官方一致、`RestrictMcDownload = False`，
且不再包含 `PCL_MS_CLIENT_ID` 或 `PCL_CURSEFORGE_API_KEY` 的运行时查找。

配置值不提交到公开源码，不明文打印到日志；发布包中的程序已内置配置。
每次构建都重新读取对应的官方成品，因此会跟随官方配置变化。
如果上游改变存放方式、缺少匹配版本的官方成品或验证失败，工作流停止发布，不会退回空配置版本。
静态校验不等于实际账号登录验证，服务是否接受请求仍取决于上游服务状态和应用权限。
