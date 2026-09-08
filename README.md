# AI 口播精剪工作流

把一条真人口播原片，按「内容剪辑 → 风格确认 → 视觉包装 → 成片验收」的流程制作成完整视频。

这是一套供 AI 助手执行的 Skill，不是独立剪辑软件。安装 Skill 不会自动安装转写模型、图片生成服务、剪映或视频渲染器。

当前 Skill 版本：`1.0.0`。

## 你能得到什么

- 先整理带时间码的原话和内容逻辑，再剪口误、重复与无意义停顿。
- 根据每条视频的内容推荐三套视觉方向，先看真人合成关键帧，再确认动态样片。
- 统一人物处理、B-roll、字幕、贴纸与动效；每个阶段都有产物和验收标准。
- 每次执行先检查工具与多模态能力；不同环境如需替代方案，明确说明差异和限制。

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
```

将下面整段话发给 Codex：

```text
请使用 $skill-installer 安装这个 GitHub 仓库中的 Skill：
https://github.com/realpzyyy/ai-video-skills/tree/main/skills/talking-head-video-production
如果已有同名 Skill，请先说明差异，不要直接覆盖。
```

该地址安装 `main` 分支中的当前版本。如果需要固定课程版本，可在安装时要求使用明确的提交编号。

安装成功后，在下一轮对话中使用：

```text
使用 $talking-head-video-production 处理这条口播原片。
先检查工具和多模态能力，整理逐字稿与内容逻辑，给我看粗剪。
之后推荐三套风格，先做关键帧和动态样片供我确认。
保留原声，不新增配音或数字人，不自动上传素材或使用付费服务。
```

如果客户端内置安装器的路径或行为不同，让它先发现本机的安装能力，不要照抄他人电脑的绝对路径。官方说明见 [Build skills](https://learn.chatgpt.com/docs/build-skills)；具体 GitHub 安装选项以客户端的 `skill-installer` 为准。

## 无法访问 GitHub，或使用其他客户端

可以由授课者提前分发完整 Skill 文件夹或 ZIP，再让客户端按照自己的 Skill 导入机制安装。必须保留 `SKILL.md`、`references`、`scripts` 与 `agents` 的相对路径。

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

## 本地验证

在仓库根目录执行（Windows 可将 `python3` 换成可用的 Python 3 命令）：

```bash
python3 -B skills/talking-head-video-production/scripts/test_probe_local.py
python3 -B skills/talking-head-video-production/scripts/probe_local.py
```

如需检测自己的本地原片：

```bash
python3 -B skills/talking-head-video-production/scripts/probe_local.py --media "/path/to/your-video.mp4"
```

检测结果可能包含本机路径，请勿原样提交到公开仓库。单元测试验证检测脚本行为，不证明视频剪辑质量；跨模型、跨客户端完整试剪仍需单独验证。

## 发布与维护

- 只提交本目录内经审核的文档、脚本和 Skill 文件，不提交课程原片、成片、逐字稿、检测报告、令牌或机器配置。
- 收到修改建议后先维护仓库中的 Skill，再验证并更新已安装副本；不要把不同位置当作自动同步。
- 推荐发布固定版本标签供课程使用；标签创建并验证后，才把安装地址中的 `main` 换成该标签。
- 目前未附加开源许可证；如需明确的再分发或商用授权，请联系仓库作者。公开可访问不等于自动获得任意使用授权。
