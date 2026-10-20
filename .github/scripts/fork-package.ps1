$ErrorActionPreference = 'Stop'
$exe = 'Plain Craft Launcher 2/bin/Plain Craft Launcher 2.exe'
if (!(Test-Path $exe)) { throw 'Build output is missing.' }
$version = [System.Diagnostics.FileVersionInfo]::GetVersionInfo((Resolve-Path $exe))
Write-Host "Built executable version: $($version.FileVersion)"

$safeTag = $env:UPSTREAM_TAG -replace '[^A-Za-z0-9._-]', '_'
$asset = "PCL-chensunlai-$safeTag"
New-Item -ItemType Directory -Force dist, package | Out-Null
Copy-Item $exe "dist/$asset.exe"
# Include any runtime files produced by MSBuild, as well as the standalone executable.
Copy-Item 'Plain Craft Launcher 2/bin/*' package -Recurse
Copy-Item LICENCE, FORK.md package
$metadata = [ordered]@{
    upstream = 'Meloong-Git/PCL'
    upstream_tag = $env:UPSTREAM_TAG
    upstream_commit = $env:UPSTREAM_SHA
    fork_commit = $env:SOURCE_SHA
    restrict_mc_download = $false
    credential_source = 'matching official release executable'
    runtime_credential_environment_variables = $false
    workflow_run = "$env:GITHUB_SERVER_URL/$env:GITHUB_REPOSITORY/actions/runs/$env:GITHUB_RUN_ID"
}
$metadata | ConvertTo-Json | Set-Content 'package/build-info.json' -Encoding utf8
Compress-Archive -Path 'package/*' -DestinationPath "dist/$asset.zip"
Get-ChildItem dist -File | Sort-Object Name | ForEach-Object {
    "$((Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower())  $($_.Name)"
} | Set-Content 'dist/SHA256SUMS.txt' -Encoding ascii

@"
这是第三方独立修改的 **Plain Craft Launcher (PCL) chensunlai 修改版**，不是 PCL 官方发行版。

- 上游 Release：$env:UPSTREAM_URL
- 上游提交：$env:UPSTREAM_SHA
- 本次编译源码：$env:GITHUB_SERVER_URL/$env:GITHUB_REPOSITORY/tree/$env:SOURCE_SHA
- 功能修改：仅将 ``RestrictMcDownload`` 设为 ``False``。
- GitHub Actions 云端编译，附可执行文件、完整打包文件和 SHA-256 校验值。
- 原作者：龙腾猫跃；赞助：https://afdian.com/a/LTCat
- 微软 Client ID 与 CurseForge 配置已从同版本官方程序读取并内置，无需设置环境变量。
- 发布前已静态核验成品中的两项配置与官方一致，并确认下载限制关闭；未代替用户进行账号登录测试。

<!-- pcl-upstream-release:$env:UPSTREAM_RELEASE_ID -->
"@ | Set-Content release-notes.md -Encoding utf8
