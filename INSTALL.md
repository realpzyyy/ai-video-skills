# 在其他 Agent 中安装、更新和使用

适用版本：`talking-head-video-production 2.2.0`。

本版新增安装阶段的依赖初始化；保留三套实际视觉母版：磨砂工具箱、纸白知识杂志、精密流程科技 × 奶油杏橙、晴空钴蓝、香芋青柠。更新后务必保留 assets、scripts 等完整目录，包括 runtime-package.json 与 runtime-package-lock.json，不是只替换 SKILL.md。详情见 [标准模板](skills/talking-head-video-production/references/standard-templates.md) 和 [环境初始化](skills/talking-head-video-production/references/setup.md)。

这是流程 Skill，不是独立剪辑软件、自动配好的插件包或一键云服务。换一个 Agent 后，仍需重新确认文件访问、执行工具、转写、看图、听音和视频渲染能力。

## 1. Codex：发给安装器

将下面整段发给目标 Codex：

```text
请使用 $skill-installer 安装或更新以下 Skill：
https://github.com/realpzyyy/ai-video-skills/tree/main/skills/talking-head-video-production

请先读取远端 SKILL.md 核对版本，并确认本客户端实际采用的安装目录。
如没有旧版，安装完整的 talking-head-video-production 文件夹。
如已有旧版，先识别本地自定义改动，完整备份到 Skill 扫描目录之外。
没有自定义改动且目标版本不比本地旧时，更新；已完全一致时不用重复安装。
有自定义改动、同名多份安装或可能降级时，先说明差异，不要直接覆盖。
保留 references、scripts、assets、agents 的相对路径，不要只下载 SKILL.md。
安装后读取实际文件，报告版本、来源提交、安装位置与缺失能力。
我同意安装此 Skill 必需的 FFmpeg/FFprobe 与固定版本 React/Remotion 运行依赖。
请读取 references/setup.md，先发现宿主已提供的 Python、Node、npm、Chrome 及现有依赖的真实路径，再执行 scripts/setup_runtime.py --install。
已有依赖复用，缺失才安装；完成合成音视频与模板静帧测试，输出 runtime-report.json 的位置和就绪状态，不要只列缺失项。
不授权管理员提权、付费、大模型下载或上传我的素材。缺基础环境、网络或权限时说明准确原因，不绕过限制。
```

`main` 是持续更新的分支，不是永久固定的 V2。课程要固定同一版时，把 URL 中的 `main` 替换为仓库中已验证的完整提交 SHA，或明确要求安装该提交的同一路径；不要虚构版本标签。

安装器可能在同名目录已存在时退出，所以更新不是反复运行首次安装命令。先下载到临时目录、校验并备份旧版，再按当前客户端机制切换；切换失败保留或恢复旧版。备份不要放在会被扫描的技能目录中，避免新旧同名 Skill 同时触发。

安装后在下一轮对话中调用；如果仍未出现，检查客户端 Skill 列表和目录，必要时重启。Codex 的目录发现及安装机制以当前客户端和 [官方说明](https://learn.chatgpt.com/docs/build-skills) 为准，不照抄另一台电脑的绝对路径。本文不要求改动全局配置。

## 2. 其他支持 Skill 的 Agent：通用安装请求

以下是给 Agent 的任务说明，不是宣称每个客户端都有统一的安装命令：

```text
请先确认你是否支持本地 Agent Skill、读取文件和执行脚本。
我要使用 realpzyyy/ai-video-skills 仓库的 skills/talking-head-video-production：
https://github.com/realpzyyy/ai-video-skills/tree/main/skills/talking-head-video-production

若支持，请通过你已核实的 Skill 导入机制安装完整目录；已有旧版先检查改动并备份，再更新。
请报告实际加载的版本与来源提交，并重新检查这台机器的工具和多模态能力。
我同意安装必需的 FFmpeg/FFprobe 与固定版本 React/Remotion 依赖。请读取 references/setup.md，复用本机/宿主管理的现有工具，执行 scripts/setup_runtime.py --install，缺失才安装并完成合成验证。
输出实际运行路径、安装报告和测试状态，不要仅列缺失项。不授权管理员提权、付费、大模型下载或素材上传；缺基础环境或受限时说明准确原因。
若不支持原生 Skill，但能读取和执行本地项目文件，请读取完整 SKILL.md，按阶段读取其引用文件，并把它作为本次任务的流程执行；明确这不等于原生安装成功。
若只能聊天、无法读本地文件或执行剪辑，就直接说明哪些步骤需要我手动完成。
不要编造工具可用性、安装路径、已听审/已看图或渲染结果。
```

尚未对 WorkBuddy 等其他客户端做完整安装与端到端试剪验证。`$skill-installer` 是 Codex 的调用写法，不要求其他 Agent 识别；它们也不一定读取 `agents/openai.yaml`。不支持某元数据不代表可以忽略 `SKILL.md` 中的确认和权限边界。

## 3. 开始剪辑：附上原片再发这段

先让目标 Agent 能真正访问视频：本地客户端使用它能读到的路径；远程客户端按其获准的文件传入方式提供素材。另一台电脑不能读取讲师电脑的路径。此文档不构成上传私人音视频的授权。

```text
请使用 talking-head-video-production Skill 剪辑我提供的真人口播原片。
先报告实际加载版本，并检查本次需要的工具和多模态能力。

1. 提取带时间码的逐字稿，梳理逻辑，精简重复、口误和无意义口水词，保留原意与自然起音。
2. 先输出完整精简音频和简短删改摘要，暂停让我试听确认。
3. 我确认后，建立与音频同源的视频时间线，不单独导出粗剪 MP4。
4. 使用包内三套实际母版与三配色，按本次内容/真人生成九格，编号 A1–C3，暂停让我选择完整组合。不要自行改成简单文字卡片，不要先出成片再问风格；渲染前检查 G1/G2。
5. 我选定后，制作字幕、B-roll 与贴纸动效，内部检查后直接烧制最终视频；不做封面，不额外增加默认样片审批。

保留原声和原片，不自动改声线、加配音、数字人或音乐。
需要额外安装、付费或上传私人素材时先说明并征求同意。
尽量复用现有工具和模板；按 Skill 记录耗时，不为凑十分钟跳过验收。
```

在 Codex 中可将第一句的名称写成 `$talking-head-video-production` 或从 Skill 选择器选中。其他客户端使用其自己的调用方式。

## 4. 没有 GitHub 网络：提前分发离线文件

授课者可在能访问 GitHub 的电脑上下载经过核验的仓库 ZIP，再分发其中完整的 `skills/talking-head-video-production/`；不要将仓库外层目录当成单个 Skill。原始目录结构如下：

```text
talking-head-video-production/
  SKILL.md
  agents/openai.yaml
  references/
  scripts/
  assets/
    style-presets.json
    catalog.html
    studio.css
    studio.mjs
    studio-remotion.tsx
```

也可以使用授课者提供的仅含公开 Skill 与说明文件的离线包。无需学员能访问 GitHub即可读取本地包，但转写/图片/渲染后端是否能离线运行，要另外确认。不要临时绕过网络限制或改用未核实的第三方镜像。

## 5. 安装验收与能力清单

- 读取实际安装的 `SKILL.md`：本版 `metadata.version` 为 `2.2.0`，默认确认点为 G1 音频、G2 风格配色。
- 四个配套目录齐全；不是只把 README 或 SKILL.md 放进聊天上下文。
- 在 Skill 目录运行 `python3 -B -m unittest discover -s scripts -p 'test_*.py'` 与 `node --test scripts/test_studio.mjs`。Windows 使用本机可用的 Python 3 命令。
- 复制 Skill 不是依赖已验证：安装 Agent 必须按上面授权执行 setup_runtime.py --install。只有安装报告为 dependencies_ready 才能说基础剪辑依赖已就绪；这不代表 ASR、听审或看图能力已具备。缺 Node/Python/npm/Chrome/包管理器或受权限限制时另行准备基础环境。
- 检测/音频/批准脚本使用 Python 3 标准库；重新生成九格另需 Node.js。`probe_local.py --media` 需要 `ffprobe`，提取音频通常需要 `ffmpeg`；场景渲染另需已安装的 Remotion/React 依赖与 Chrome，可移植到已验证的其他后端。
- ASR/强制对齐、图片生成或 HTML/SVG 渲染、听音/看图能力独立检查。能写代码不代表能看懂或听懂产物。
- 内置音频工具不会自动决定删哪些字；九格 HTML 可预览实际对象动画，但不是 MP4。场景渲染工具产出场景资产，完整视频仍需同源时间线、字幕与批准音频合成。
- 缺乏图片生成时可以选择已验证的代码绘图路径；缺乏视觉理解时仍需人工视觉确认，不能用 HTML 绕过验收。
- 单元测试通过只证明辅助脚本行为，不证明某客户端完整兼容、所有 Agent 不会绕过确认，或一分钟视频可在十分钟内完成。第一次联网安装可能耗时，应在工作坊前执行；下一次使用复用安装报告中的真实路径。

维护、版权和许可边界见 [README](README.md)。Skill 不会自动更新已经完成的视频，也不会让另一台机器同步获得本机的插件、字体、模型或账户权限。
