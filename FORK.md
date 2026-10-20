# Plain Craft Launcher (PCL) chensunlai 修改版

这是第三方基于 [PCL](https://github.com/Meloong-Git/PCL) 独立修改的版本，不是官方发行版。
原作者：**龙腾猫跃**；[赞助原作者](https://afdian.com/a/LTCat)。保留上游署名、关于页面和 LICENCE。

唯一功能修改：`Plain Craft Launcher 2/Modules/ModSecret.vb` 中
`Public Const RestrictMcDownload As Boolean = False`。

## 自动跟随 Release

- GitHub Actions 每小时第 23 分钟检查一次，实际开始时间可能受 GitHub 调度影响。
- 从 `2.99.0.0` 开始跟踪之后发布的所有 Release，包含预发布；不会补编更早的历史版本。
- 按发布时间依次合并上游 Release **标签指向的源码**，保留这一个常量修改及本仓库的自动化文件。
- 仅在 GitHub Windows runner 上编译 Release，不在本地编译。
- 成功后发布 `fork-上游标签`，附 `.exe`、完整 `.zip` 和 `SHA256SUMS.txt`；预发布标记与上游一致。
- 已成功发布的版本会跳过；失败的版本下次检查自动重试。上传完成后才公开 Release。
- 修改位置变化、合并冲突或出现额外源码差异时会失败并停止发布，避免静默发布错误版本。
- 上游长期不发布时，每 30 天生成一个无源码变化的空提交，防止计划工作流因仓库不活跃而停用。
- 可在 Actions → Follow upstream releases → Run workflow 手动检查并重试。
- 只使用 GitHub 自动提供的 `GITHUB_TOKEN`，不需要保存个人 PAT。
- 上游自带的 Build 工作流在此 fork 中停用，由本工作流负责编译和发布。
- 应用源码及资源跟随上游；`.github/workflows/` 保留本 fork 的定义，避免普通自动化令牌无法更新工作流文件而中断同步。

这里的“自动更新”指仓库同步和 GitHub Release 发布；未修改启动器自身的在线更新服务。
下载修改版请使用本仓库的 Releases。

## 上游保留的配置

上游公开源码没有附带微软应用 Client ID 和 CurseForge API Key，本 fork 不捏造或借用其他项目的密钥。
如需这些服务，可在运行启动器的 Windows 环境中设置上游已支持的变量：

- `PCL_MS_CLIENT_ID`：你自己的微软应用 Client ID。
- `PCL_CURSEFORGE_API_KEY`：你自己的 CurseForge API Key。

不配置这些值会影响对应服务，但与本次解除下载限制的常量修改相互独立。
