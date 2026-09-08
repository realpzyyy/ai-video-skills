# 项目记录与阶段状态

## 输出位置与最小文件集

尊重用户指定位置。没有指定时，在当前工作区建立不覆盖既有目录的版本化项目目录，例如 `outputs/<date>-talking-head-v1/`。仅创建当前阶段需要的文件，不填充空文件或虚构路径。

- `project.json`：任务范围、原片身份、当前时间线、阶段状态、批准记录和实际产物。
- `capability-report.json`：全局与各执行 agent 的能力证据。
- 内容阶段：转写稿、编辑脚本/选段表、原声粗剪、字幕源。
- 视觉阶段：三套候选样张、`style-spec.json`、画面设计表、动态样片、实际资产。
- 交付阶段：完整视频、字幕、实际工程、QA 记录与素材来源。

文件名可适配已有工程；语义与记录字段不能丢失。对已有制作项目，不强制搬目录或转换数据格式。

## project.json 必要字段

以下为字段约定，不是可直接宣称完成的示例：

| 字段 | 内容 |
| --- | --- |
| skill_version | `1.0.0` |
| request_scope | 本次制作/局部修改/分析范围及不做的事项 |
| sources | 素材 ID、实际路径或平台资产 ID、时长/规格；本地可用哈希记录身份 |
| target | 平台、画幅、时长意图、原声策略、交付格式；未知项明确写出 |
| constraints | 预算、云上传、安装、生成/声音使用等已知限制与授权来源 |
| timeline_revision | 当前定稿语音时间线版本 |
| style_revision | 当前视觉规范版本或尚未选定 |
| approvals | G1/G2/G3 的状态、用户表述依据、时间与覆盖范围；未确认用 null/待确认 |
| stages | 阶段 ID、状态、输入版本、实际产物、验收证据、失败/跳过理由、下一步 |
| deliverables | 已真实生成的结果路径与类型；不要提前填完成路径 |

阶段状态可用：`planned`、`in_progress`、`produced`、`rendered`、`verified`、`needs_user`、`blocked`、`not_applicable`、`stale`。

`verified` 必须有与该阶段标准对应的证据；`not_applicable` 必须说明与当前范围的关系。三套风格“已输出”不等于“用户已选择”。无停顿执行只记录授权跳过等待，不伪造批准。

## capability-report.json 必要字段

- `checked_at`、`environment`（宿主/系统/执行环境，不含凭证）、`agent_id`。
- 每个 `capability`：ID、作用阶段、是否必需、实际提供者/工具、`status`、`evidence`、`limitation`、`fallback`。
- `status`：`available_verified`、`unavailable`、`untested`、`human_review_required`、`not_required`。
- 证据写“哪个检查返回了什么”，而不是只写“支持”。云服务目录可见与真正生成成功分开记录。离线探测结果不能替代云工具和模型能力验证。
- 记录各执行 agent 自己复核过的能力与有效范围。不能将用户待人工审核的路径写成已自动通过。

## 时间线与素材溯源

选段记录至少含：`source_id`、`source_in_seconds`、`source_out_seconds`、`output_start_seconds`、处理理由、对应原话。

字幕、图形、B-roll 记录其依据的 `timeline_revision`；视觉资产另关联 `style_revision`。实际编辑器已有等价字段时使用原生记录，不重造一套不一致的时间线。

记录实际来源与用途：`source_footage`、`user_provided`、`screen_recording`、`licensed_stock`、`generated_bitmap`、`code_graphic`。对外部素材保存出处和已知使用条件；没有证据时标待核验，不声称已获得商业授权。隐私脱敏版与原始证据分开保留。

## 返修与恢复

1. 恢复时先读记录并确认真实文件存在，不能仅凭上轮总结继续。
2. 语音选段或顺序改变：更新时序版本，相关字幕、视觉锚点、音效与成片 QA 标 `stale`。
3. 仅字体/颜色改变：保留原声与选段，重验受影响的图层、阅读性与输出，不重新转写。
4. 人物分割改变：重验快速运动、边缘及合成；不擅自改变台词。
5. 风格变化：先回到 G2，复核相关资产和动态样片；与主题无关的来源信息不重做。
6. 原素材、工程、视频分别标清版本，不覆盖唯一源文件。暂停时写出已完成、未完成、所需决定和准确恢复点。
