# 项目记录与阶段状态

标准模板的可执行 G1/G2 字段与哈希规则见 [标准模板](standard-templates.md#记录格式与边界)。保留本文件的原有来源/范围字段；缺乏真实用户消息时不可虚构批准来满足校验。

## 输出位置与最小文件集

尊重用户指定位置。没有指定时，在当前工作区建立不覆盖既有目录的版本化项目目录，例如 `outputs/<date>-talking-head-v1/`。仅创建当前阶段需要的文件，不填充空文件或虚构路径。

- `project.json`：任务范围、原片身份、当前时间线、阶段状态、批准记录和实际产物。
- `capability-report.json`：全局与各执行 agent 的能力证据。
- 内容阶段：转写稿、精简脚本/选段表、试听音频、源到输出映射、字幕源；不默认导出粗剪视频。
- 视觉阶段：3×3风格配色候选板、`style-spec.json`、未渲染视频时间线、画面设计表、内部QA与实际资产。
- 交付阶段：完整视频、字幕、实际工程、QA 记录与素材来源。

文件名可适配已有工程；语义与记录字段不能丢失。对已有制作项目，不强制搬目录或转换数据格式。

## project.json 必要字段

以下为字段约定，不是可直接宣称完成的示例：

| 字段 | 内容 |
| --- | --- |
| skill_version | `2.1.0`；历史版本保留原值 |
| request_scope | 本次制作/局部修改/分析范围及不做的事项 |
| sources | 素材 ID、实际路径或平台资产 ID、时长/规格；本地可用哈希记录身份 |
| target | 平台、画幅、时长意图、原声策略、交付格式；未知项明确写出 |
| constraints | 预算、云上传、安装、生成/声音使用等已知限制与授权来源 |
| timeline_revision | 当前定稿语音时间线版本 |
| style_revision | 当前视觉规范版本或尚未选定 |
| approvals | G1_audio/G2_style_palette 的状态、用户表述依据、时间与覆盖范围；未确认用 null/待确认 |
| stages | 阶段 ID、状态、输入版本、实际产物、验收证据、失败/跳过理由、下一步 |
| deliverables | 已真实生成的结果路径与类型；不要提前填完成路径 |

阶段状态可用：`planned`、`in_progress`、`produced`、`rendered`、`verified`、`needs_user`、`blocked`、`not_applicable`、`stale`。

`verified` 必须有与该阶段标准对应的证据；`not_applicable` 必须说明与当前范围的关系。九组风格配色“已输出”不等于“用户已选择”。无停顿执行只记录授权跳过等待，不伪造批准。

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

## V2新增记录与旧项目迁移

- G1_audio：批准文件路径/身份、timeline_revision、源时间基准、用户依据、内容/听感检查者、状态。
- G2_style_palette：style_id、palette_id、组合编号、样张路径、字体/资产/模板版本及用户依据。
- performance：target_active_seconds、阶段start/end、active_elapsed_seconds、user_wait_seconds、cold_start_seconds、total_elapsed_seconds、retry_count、返工原因；并行区间合并，不能把CPU用时当总体验耗时。无测量值用null，不编造零。
- 未渲染视频用timeline_ready或produced阶段表示，artifacts引用实际选段/工程；没有MP4时不能写rendered。
- 旧G1若明确已包含原声听感批准，可继承为G1_audio，不逼用户重听；旧G2有完整风格及配色可继承。旧G3只保留历史，不作为V2必经审批。
- 记录可合并为project.json、transcript/edl、style-spec、qa几个文件，不为每个小动作重复生成说明书。

### render_audio.py 的输入约定

输入是从单一源媒体以已校准零点提取的16-bit PCM WAV（保持原采样率/声道，不在提取时改速）。其他采样格式先由已验证媒体工具转换一次。未校准非零流起点、多源和漂移要另建时间基准，不能直接套此脚本。

EDL字段：schema_version=1，timebase=source_seconds_from_zero，source_id，timeline_revision，segments数组；每段含start、end（秒，源WAV基准）、可选id/text/reason。默认顺序且不重叠；显式允许重排仍需内容与听感复核。

脚本输出audio.wav、timeline.json；后者含源身份、采样率、音频区间/重叠、画面有效剪口video_segments、输出长度与运行时间。它不自动判定应该删哪些词，不做ASR，不生成视频或字幕，不代表用户已批准。
