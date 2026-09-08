# AI 口播精剪工作流

把一条真人口播原片，按「逐字稿与精简 → 音频试听确认 → 3×3 风格配色确认 → 最终成片」的流程制作成完整视频。

这是一套供 AI 助手执行的 Skill，不是独立剪辑软件。安装 Skill 不会自动安装转写模型、图片生成服务、剪映或视频渲染器。

当前 Skill 版本：`2.1.0`。完整的首次安装、更新与跨 Agent 使用说明见 [安装与使用指南](INSTALL.md)。

## V2.1：直接带上三套实际视觉母版

| 画风 | 奶油杏橙 | 晴空钴蓝 | 香芋青柠 |
| --- | --- | --- | --- |
| 磨砂工具箱 | A1 | A2 | A3 |
| 纸白知识杂志 | B1 | B2 | B3 |
| 精密流程科技 | C1 | C2 | C3 |

保留原方案的构图、人物框、材质、字幕和对象动作，扩展到统一三色；不再只写「高级、杂志风」让 Agent 自由猜测。内置汇集、对照、步骤、真人承接四种版式。下载后直接打开 [离线模板画廊](skills/talking-head-video-production/assets/catalog.html)；GitHub 文件页本身不执行 HTML。

预览与 Remotion 场景使用同源模板。未取得本次完整风格/配色选择必须暂停；批准检查器拒绝缺失/陈旧/错配的记录。它不是不可绕过的安全沙箱，仍要求执行 Agent 遵守流程。用法与字幕下限见 [标准模板说明](skills/talking-head-video-production/references/standard-templates.md)。公共包不含讲师真人音视频或私人逐字稿。

## 你能得到什么

- 先整理带时间码的原话和内容逻辑，清理口误、重复、口水词与无意义停顿，保留原意和自然听感。
- 先输出精简音频试听；确认后建立同源视频时间线，不单独导出粗剪 MP4。
- 根据内容提供三套视觉风格，每套三种配色，一次选定完整组合后直接制作成片。
- 统一人物处理、B-roll、字幕、贴纸与动效；每个阶段都有产物和验收标准。
- 每次执行先检查工具与多模态能力；不同环境如需替代方案，明确说明差异和限制。
- 默认仅音频、风格配色两次用户确认；动态检查保留为内部 QA，不默认制作封面。

## 安装到 Codex

仓库目录如下；安装时选择 `skills/talking-head-video-production`，不要只下载一个 `SKILL.md`，也不要把整个仓库当作单个 Skill。

```text
README.md
.gitignore
skills/
  talking-head-video-production/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
    assets/
```

将下面整段话发给 Codex：

```text
请使用 $skill-installer 安装或更新这个 GitHub 仓库中的 Skill：
https://github.com/realpzyyy/ai-video-skills/tree/main/skills/talking-head-video-production
先核对远端版本和本机安装位置。如果有旧版，先完整备份到不会被扫描为 Skill 的目录。
没有本地自定义改动时再更新；有自定义改动或发现比目标更新的版本时，先说明差异。
保留整个 Skill 文件夹，完成后报告版本、来源提交和安装位置。
```

该地址安装 `main` 分支中的当前版本。如果需要固定课程版本，可在安装时要求使用明确的提交编号。

安装成功后，在下一轮对话中使用：

```text
使用 $talking-head-video-production 处理这条口播原片。
先检查工具和多模态能力，整理逐字稿与逻辑，输出精简音频让我试听确认。
音频确认后建立同源视频时间线，不单独导出粗剪 MP4。
展示 3 种视觉风格 × 每种 3 种配色的真实合成样张，让我选择完整组合。
风格配色确认后，加入字幕、B-roll 和动效，完成必要检查并输出最终视频。
不额外增加默认样片审批，不做封面。
保留原声，不新增配音或数字人，不自动上传素材或使用付费服务。
```

如果客户端内置安装器的路径或行为不同，让它先发现本机的安装能力，不要照抄他人电脑的绝对路径。官方说明见 [Build skills](https://learn.chatgpt.com/docs/build-skills)；具体 GitHub 安装选项以客户端的 `skill-installer` 为准。

## 无法访问 GitHub，或使用其他客户端

可以由授课者提前分发完整 Skill 文件夹或 ZIP，再让客户端按照自己的 Skill 导入机制安装。必须保留 `SKILL.md`、`references`、`scripts`、`assets` 与 `agents` 的相对路径。

目前没有验证 WorkBuddy 等其他客户端的安装入口和完整执行兼容性，不承诺一个 GitHub 安装指令适用于所有客户端。先确认目标客户端支持本地 Skill、文件访问与实际执行工具；不支持自动导入时，可将该流程用作人工执行参考，但这不等于已安装。

## 所需能力与费用边界

| 工作 | 要确认的能力 |
| --- | --- |
| 转写与粗剪 | 带时间码转写，以及可执行的剪辑/渲染工具 |
| 图片与人物包装 | 看图、合成；背景专用蒙层需可靠的人物分离能力 |
| 字幕、图表、贴纸 | 合适的图片生成或 HTML/SVG 等绘图与导出路径 |
| 最终验收 | 实际画面检查、声音听审、音画同步与文件检查 |

能生成图片不等于能看懂图片；能写 HTML 不等于完成视觉验收。缺少相关能力时会标记为待人工检查，不会虚报通过。

Skill 自带的本地检测脚本使用 Python 3 标准库。读取视频元数据需要可调用的 `ffprobe`。检测脚本不会安装依赖、下载模型或上传素材。模型、插件与云服务的收费和网络条件由所选工具决定；安装本 Skill 不代表后续制作全程免费。

`render_audio.py` 根据已审核选段表输出 PCM16 WAV 试听与时间映射，不自动转写或识别口水词。`build_style_board.py` 使用 Python 3 + Node.js 生成同源九格 HTML，支持预览对象动画；`render_studio.mjs` 使用已有 Remotion 与 Chrome 导出单个场景。运行时不会随 Skill 安装，不自动下载。完整视频仍需宿主编排批准音频、字幕时间与视频时间线，不能把六秒示例当最终作品。不同画幅/品牌另行适配。

## 速度目标

约一分钟常规口播、依赖模型已就绪、模板可复用、两次确认无需返工时，以累计主动处理 600 秒以内为优化目标。包含模型分析、工具等待、渲染和必要 QA；用户等待、冷启动与返工分别记录。完整端到端性能基准尚待验证，不承诺任意环境十分钟完成。详见 [速度预算](skills/talking-head-video-production/references/performance.md)。

## 本地验证

在仓库根目录执行（Windows 可将 `python3` 换成可用的 Python 3 命令）：

```bash
python3 -B -m unittest discover -s skills/talking-head-video-production/scripts -p 'test_*.py'
node --test skills/talking-head-video-production/scripts/test_studio.mjs
python3 -B skills/talking-head-video-production/scripts/probe_local.py
```

如需检测自己的本地原片：

```bash
python3 -B skills/talking-head-video-production/scripts/probe_local.py --media "/path/to/your-video.mp4"
```

检测结果可能包含本机路径，请勿原样提交到公开仓库。V2.1 包含 36 项 Python 与 7 项 Node 单元测试，验证预检、音频切段、风格板、共享场景和批准一致性。已在作者的 macOS / Remotion 环境检查九格并导出代表静帧和对象动画；不证明其他模型服从确认流程，跨客户端完整试剪与全流程十分钟基准仍待验证。

## 发布与维护

- 只提交本目录内经审核的文档、脚本和 Skill 文件，不提交课程原片、成片、逐字稿、检测报告、令牌或机器配置。
- 收到修改建议后先维护仓库中的 Skill，再验证并更新已安装副本；不要把不同位置当作自动同步。
- 推荐发布固定版本标签供课程使用；标签创建并验证后，才把安装地址中的 `main` 换成该标签。
- 目前未附加开源许可证；如需明确的再分发或商用授权，请联系仓库作者。公开可访问不等于自动获得任意使用授权。
