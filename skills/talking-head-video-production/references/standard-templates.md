# 标准模板 V2.1：预览与渲染共用源文件

## 包内有什么

- assets/catalog.html：离线可开九格，含对象动画与四种版式；只含通用绘图人物，不能当用户项目已批准。
- assets/studio.css：720×1280 母版构图、材质、角色配色与字幕；不是只有颜色列表。
- assets/studio.mjs：三种画风 × 三色 × 四种版式的语义对象、独立动作和文案校验；sceneHTML(config,time,options) 可复用。
- assets/studio-remotion.tsx：同源 StandardScene 组件及示例入口；渲染依赖由宿主提供，不附带 node_modules。
- assets/style-presets.json：稳定风格/配色 ID 与基础角色色。完整材质渐变、阴影、对比色以共享 CSS 为准，不根据基础 HEX 临时重画。
- scripts/build_style_board.py + build_studio.mjs：用本次真人帧生成完整离线板，Python 3 + Node.js，默认不联网。
- scripts/check_gate.py：检查批准、输入身份与模板版本是否一致；不是用户身份认证服务。
- scripts/render_studio.mjs：使用已有 Remotion + Chrome 导出一个场景资产或公开演示，不是自动剪完整原片的引擎。

## 最短执行方法

下面相对路径均以已安装 Skill 目录为工作目录。跨 Agent 要复制完整目录，不能只读 SKILL.md。

1. 公共底库直接打开 assets/catalog.html；重建：

```bash
python3 -B scripts/build_style_board.py --demo --output /new/path/catalog.html
```

2. G1 批准后，记录真实 project.json，再生成本次九格：

```bash
python3 -B scripts/build_style_board.py --project /project/project.json --presenter /project/frame.png --title '把知识|变成工具' --caption '打包成一个 AI Skill' --labels '方法论,知识点,解决思路' --concept 'AI Skill' --output /project/style-board-v1.html
```

标题与字幕均可用 | 按语义换行；字幕来自实际批准原声。默认工具包文案只是示例：用 --config /project/scene.json 替换 kicker、description、benefit、compare、steps、result 等所有内容，并沿用共享构图重新生成九格，禁止残留无关示例文案。build_studio.mjs 接受标准输入 JSON：{config:{...},portrait:'data:image/png;base64,...',demo:false}；直接调用也必须先执行 G1 检查。

3. G2 批准后，批量资产和任何后端的最终编码之前运行：

```bash
python3 -B scripts/check_gate.py --project /project/project.json --stage render --scene /project/scene.json
```

不通过则停止渲染并修正记录/回到用户确认；不可让 Agent 把失败改成警告。--scene 应对每个场景检查，正式工程也要核对一致。用户另有定制品牌/画幅时须做等价确认与验证，不能拿标准检查失败当作擅自换回预设的理由。

4. 已有依赖时导出六秒公共对象动画（示例，不是成片）：

```bash
node scripts/render_studio.mjs --runtime /existing/remotion-project --browser /path/to/existing/chrome-executable --demo --style tactile --palette apricot --layout collect --output /new/path/demo.mp4
```

加 --still 可导出 PNG，--frame 指定帧。真实单场景导出用 --project 与 --scene 代替 --demo，scene.json 顶层含配置和 portrait_data_url（本次授权原片的本地 PNG/JPEG）；缺确认直接报错。--demo 不接受任何私有配置/素材，仅能使用包内样例。

必须预检 Node、可用 Python、React、remotion、@remotion/media、@remotion/bundler、@remotion/renderer 和现有 Chrome。用户已授权补齐运行依赖时先按 [环境初始化](setup.md) 自动安装缺项并验证；未授权才询问，不在渲染中隐式下载。--runtime-report 可传入已验证的本机安装报告，复用实际运行目录和浏览器路径。临时构建目录保留在系统临时区，包含本次素材时同样不得公开上传。

## 接到整条视频，不要把六秒样例重复铺满

- 同一 G1 音频/源时间映射生成 host timeline；在需要解释内容的时段用 Sequence 放入 StandardScene。其余以真人或真实证据画面承接。
- 使用 source 属性传入宿主已授权可读的真实视频，trimBefore 为当前来源起点帧；Video 已静音，原声只放一条批准母带。视频小窗必须随同源时间走，不可拿静帧冒充全程真人视频。
- scene.config 的 duration_seconds、对象入场与揭示应匹配该句语义；内置六秒时机是可改起点，不代表所有台词都适合。阶段动画用明确 frame/time 驱动，不靠 CSS 动画时钟。
- caption_lines 是当前字幕 cue，不是整段逐字稿；宿主按剪后时间码每帧选 cue，传给组件。示例字幕不附真实 ASR 时间戳。两个 cue 间没有字幕时传 showCaption=false，不留上一句。
- 共享母版以 720×1280 为基准，可等比到 1080×1920。其他画幅须重新设计确认，禁止拉伸。
- 不同后端可移植实际布局/对象/动作；先对照已选样张和字幕验证等价，不强制所有学员安装 Remotion。不支持共享 CSS/字体时明确说明，不以低清纯色卡片替代。

## 字幕与精细度下限（本母版规范，非全平台法规）

- 普通口播字幕 38px，最低36px；1080输出等比57px。最多两行，每行最多14个显示单位（汉字约1、ASCII约0.55），仍需检查实际字体宽度；超出就按语义分 cue，不缩成小字长条。
- 字幕左右48px、底部118px是本母版起点，目标平台遮挡另行验证。关键词最多少量强调，不改写否定/条件/单位；标题结论与原话字幕分层。
- A 使用深主题色圆角字幕，B 使用纸色与编辑分隔线，C 使用功能型浅面板；不跨风格统一替换为默认 ASS 黑条。ASS 可用，但应实现并验证等价的尺度、行距和颜色。
- 字体优先当前已验证中文字体，记录字体名和替代情况，不把未经授权系统字体打包。换字体重验最长文案、普通真人和信息最密集帧。
- 每段 B-roll 要有语义主体和至少一种可辨关系/变化：汇集、对比、推进、证据放大等。标题+竖线+姓名标签不算一个内容 B-roll。元素不是越多越好，也不规定每秒都必须动。
- 至少查看入场、落定、退出以及连续动作；多个独立对象形成关系，不能把一张海报全局缩放当多对象动画。人物框无「真人原片」标签，留脸和字幕安全区。

## 记录格式与边界

project.json 必须保留原有来源和范围字段，再补：project_id、timeline_revision、audio:{path,sha256}、style_board:{path,sha256}。相对路径以 project.json 所在目录解析。哈希由实际文件计算，不手填占位值。

approvals.G1_audio：status、project_id、timeline_revision、audio_sha256、evidence:{role:'user',message_id,quote}。

approvals.G2_style_palette：同样的身份/证据字段，加 style_id、palette_id、choice、board_sha256、template_sha256。模板哈希用 python3 scripts/check_gate.py --template-hash 获得。用户免确认时 status=user_authorized_skip，并记录 scope；不能称用户已经试听/选择。

音频/时间线变更使上下游批准失效；候选板/母版变化需检查视觉变化并更新对应批准，不能只刷新哈希绕开用户。历史批准可用真实消息补录，测试夹具绝不可复制成真实项目批准。

检查器只能发现记录不完整、版本陈旧、选择错配；无法防止 Agent 伪造 JSON 或绕开脚本另写渲染器。宿主必须遵守 SKILL 的暂停规则；本包不承诺所有 Agent 都强制服从。
