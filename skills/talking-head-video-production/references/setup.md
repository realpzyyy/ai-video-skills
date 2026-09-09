# V2.2 安装与环境初始化

## 完成标准

安装 Skill 不是只复制文件：在用户明确要求「安装 Skill 并补齐必要依赖」时，安装 Agent 必须继续完成 **检测 → 复用 → 缺项安装 → 实际测试 → 记录路径**。不要只回一张缺失表。普通 ZIP/Skill 导入没有本包可保证的自动执行钩子，因此安装提示词必须包含运行本脚本。

明确区分：Skill 已加载、依赖已检测、依赖已验证、ASR/多模态已确认、正式视频已完成。它们不是同一种成功。

## 先确认范围，授权过的不重复问

- 用户明确要求补齐这些依赖：可以安装完整 FFmpeg（通常含 FFprobe）及本包固定版本的 React/Remotion npm 依赖。先简述计划再执行，不逐包反复提问。
- 用户仅要求复制 Skill、仅检查、禁止下载，或尚未授权：只运行 --check；说明缺项并请求安装范围，不能由作者的要求代替使用者授权。
- 不包含 Node/Python/包管理器/Chrome 的首次安装、管理员提权、付费购买、大型模型、云插件登录、私有素材上传、声音克隆。缺这些才另行说明并请求对应处理，不绕过宿主权限或网络策略。
- 本脚本面向已有 Python 3.9+、Node.js 22+、npm 与 Chrome/Chromium 的桌面环境。先从宿主的 managed runtime 发现真实路径，不能只看 PATH 就认定没装。可用显式路径传入。没有基础执行能力的纯聊天 Agent 不能完成本地安装。

## 执行

以完整 Skill 文件夹为工作目录；下面命令中的 Python/Node 要替换为已发现的本机命令或完整路径。不要照抄讲师电脑路径。

```bash
python3 -B scripts/setup_runtime.py --check
python3 -B scripts/setup_runtime.py --install
```

已有明确安装授权时，可直接 --install：它先检测，已有项不会重装。缺 FFmpeg 或 FFprobe 时按下表安装一套，安装后同时验证两个命令；Remotion 在 Skill 专属缓存中安装，不修改已有项目的 package.json 或全局 npm。

| 平台 | 自动安装 FFmpeg 的路径 | 边界 |
| --- | --- | --- |
| macOS | 复用已有 Homebrew：brew install ffmpeg | 没有 Homebrew 不执行远程 shell 安装器；另请用户准备包管理器或提供完整 FFmpeg |
| Windows | 复用已有 winget 的 Gyan.FFmpeg，限定 user scope | 不提权；安装器不支持用户范围或策略限制时报告失败，不擅改成管理员安装 |
| Linux | 已为 root 且有 apt-get 时安装 ffmpeg | 不自动 sudo/更新系统；其他发行版或权限不足时提供人工处理入口 |

这是尽力自动化的支持范围，不承诺任意电脑零配置。FFmpeg 构建需有常用剪辑滤镜、H.264/AAC 编码器。Remotion 自带的精简二进制不能直接当成本 Skill 的完整 FFmpeg；版本输出成功仍需功能测试。

固定依赖定义在 assets/runtime-package.json，传递依赖和完整性摘要由 runtime-package-lock.json 锁定。安装使用官方 npm registry、npm ci、局部 --prefix，不强制第三方镜像、不做 npm 全局安装。下载并执行依赖包的安装脚本属于此次软件安装范围。已有不同版本项目不原地升级，另建隔离运行目录。

可选参数：

```bash
python3 -B scripts/setup_runtime.py --install --node /actual/node --npm-cli /actual/npm/bin/npm-cli.js --browser /actual/chrome --runtime /existing/compatible/project
```

- --runtime：优先复用完整且版本匹配的已有项目；不匹配就保留它并创建独立缓存，不破坏用户工程。
- --ffmpeg / --ffprobe：明确指定已有完整二进制路径，不搬走文件，不改全局 PATH。
- --cache-dir：使用另一个专属缓存目录。默认 macOS ~/Library/Caches、Windows LOCALAPPDATA、Linux XDG_CACHE_HOME 或 ~/.cache 下的 talking-head-video-production。命令会输出实际绝对路径。
- --verify：不安装，只用已有环境执行下面的测试，保留报告和合成测试产物。
- --check：只读检测与安装计划；不下载、不建目录、不渲染；detected_not_verified 不等于安装验收通过。

没有 Python/Node/npm/Chrome 或包管理器时，先复用宿主提供的环境；确实没有，指出准确缺项并请求基础环境准备。不能为追求安装成功临时下载整套大模型、关闭安全机制或要求购买不必要的插件。

## 验证、记录与下次复用

--install 即使全部已存在，也执行最小测试；不重复下载依赖：

1. 运行 FFmpeg、FFprobe、Node，实际加载全部六个 npm 包并核对版本。
2. 检查常用音频滤镜；本地合成 1 秒 H.264/AAC MP4，读取音视频流与时长，并完整解码。
3. 使用现有 Chrome 将公共母版导出 PNG，检查文件格式；禁止自动下载浏览器。不使用用户真人或私人素材，不需要 G1/G2；公开示例通过不代替正式风格批准。
4. 全通过才记录 dependencies_ready。PNG 导出成功是渲染通路验证，不是美术验收，也不是完整视频已剪好。

报告保存在缓存的 runtime-report.json，同时保留带时间戳历史报告。报告含本机路径，仅本地使用，**不进 Git**。包含 Python、Node、FFmpeg、FFprobe、浏览器、npm 包版本及运行目录；后续调用使用这些路径，不能再仅凭 PATH 误报缺失。

```bash
python3 -B scripts/probe_local.py --runtime-report /actual/runtime-report.json --media /actual/video.mp4
node scripts/render_studio.mjs --runtime-report /actual/runtime-report.json --demo --still --output /new/path/test.png
```

probe_local.py 在默认缓存有报告时自动读取并重新验证命令。其他音视频命令使用报告中的绝对路径。render_studio.mjs 仍仅输出一个场景；整条视频由宿主按批准的时间线组合，不能拿测试片代替成片。

换机器/Agent 要验证路径与工具访问；报告不授予权限。相同环境下可复用近期测试，不每次剪辑都重装。ASR、强制对齐、看图、听音和生图仍独立预检，安装器不会给大模型新增多模态能力。

## 失败、速度与许可

- 网络/安装/渲染失败：报告对应阶段，保留已安装依赖，不宣称就绪。检查网络、磁盘、宿主权限及原始命令；不无限重试或切换未核实镜像。修复后重跑会复用已就绪项。
- 并发安装使用 setup.lock；锁存在时停止。先检查是否仍有安装进程；确认是残留锁后由维护者处理，不自动删别人的锁。
- 首次下载/安装是冷启动，单独记录实际耗时；应在工作坊前做，不能计作「每条一分钟视频十分钟内完成」的既有成绩。授课 ZIP 不含依赖，离线拿到 Skill 不代表离线能下载安装包。
- 本版 macOS 已做实机初始化与合成测试；Windows/Linux 的选择逻辑有单元测试，尚未做对应系统实机安装。不要报告跨平台已全面验收。
- 不会自动付款；不把依赖一概称为免费。Remotion 按用途和组织情况有许可条件，使用者应查看 [官方许可与价格](https://www.remotion.dev/license)。FFmpeg 的分发与使用条件见 [官方说明](https://ffmpeg.org/legal.html)。

官方实现依据：[Remotion 的平台二进制与浏览器选项](https://www.remotion.dev/docs/renderer/get-compositions)、[Homebrew FFmpeg](https://formulae.brew.sh/formula/ffmpeg)、[winget install](https://learn.microsoft.com/windows/package-manager/winget/install)。
