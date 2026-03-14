# 13 — YouTube AI 视频创作者图谱：谁在做、用什么、怎么做 (2026.03)

> 基于 YouTube 频道分析，覆盖 20 个活跃 AI 视频创作者/频道，按影响力分层。

---

## 核心统计

**跨 20 个创作者的工具使用频率：**

| 工具 | 使用率 | 定位 |
|------|--------|------|
| **Midjourney** | 80%+ | 首帧/关键帧生成（几乎人手一个） |
| **ElevenLabs** | 75%+ | 配音（绝对主导） |
| **ChatGPT/Claude/Gemini** | 70%+ | 脚本/提示词 |
| **Runway** | 65% | 视频生成+风格迁移 |
| **Kling** | 55% | 视频生成（运动/物理） |
| **Veo 3/3.1** | 50% | 视频生成（对话/写实） |
| **Topaz Video AI** | 45% | 放大+补帧 |
| **After Effects** | 40% | 合成+特效 |
| **DaVinci Resolve** | 40% | 调色+剪辑 |
| **Premiere Pro** | 35% | 剪辑 |
| **CapCut** | 30% | 快速剪辑+字幕 |
| **Sora 2** | 30% | 视频生成 |
| **Higgsfield** | 25% | 多模型聚合 |

**关键发现：平均每位创作者使用 5.8 个工具。零人只用单一工具。**

---

## TIER 1：大频道（10万+ 订阅）

### 1. [Corridor Digital / Corridor Crew](https://youtube.com/@CorridorCrew) — 707 万订阅

**类型：** VFX 实验 + AI 短片 + 幕后解析

**工具：** Stable Diffusion + Unreal Engine + After Effects + 自训练 AI 抠像模型 + 绿幕实拍

**工作流：** 真人绿幕拍摄 → 用角色参考图训练 AI 模型 → Stable Diffusion 做风格迁移（如动漫化）→ Unreal Engine 虚拟场景合成 → 传统 VFX 后期

**独特方法：** **混合实拍+AI** — 他们不做纯文生视频，而是用真人实拍作为基础，AI 作为渲染/风格层。2026 年 3 月最新创新是自训练 AI 抠像模型。

**代表作：** "Did We Just Change Animation?"（AI 动漫短片）

---

### 2. [Hashem Al-Ghaili](https://youtube.com/@HashemalGhaili) — 118 万订阅（全平台 210 亿播放）

**类型：** AI 科幻短片 + 科学传播

**工具（10+）：**
- 出图：Whisk, Runway, Midjourney, Dreamina, Sora
- 生视频：Veo 3 (via Google Flow), Dreamina, Higgsfield, Kling
- 配音：ElevenLabs
- 唇形同步：Veo 3, Dreamina, HeyGen
- 配乐：Suno AI
- 音效：MMAudio, ElevenLabs
- 脚本：ChatGPT
- 后期：Photoshop, DaVinci Resolve, CapCut

**工作流：** 每个镜头选不同模型。prompt 结构：**镜头运动在前，角色/场景在中，对话在最后**（防止角色说话太快）。大量后期：Photoshop 修瑕疵、AI 放大、胶片颗粒叠加、混响增加沉浸感。

**独特方法：** "对话后置" prompt 结构 + 重度后期去"AI 味"（颗粒+混响+调色）

**代表作：** "Simulation"（获 Global Shorts 卓越奖+最佳视效），"Kira"（12 天、600 prompt、$500 预算）

---

### 3. [Matt Wolfe / Future Tools](https://youtube.com/@MattWolfe) — 91 万订阅

**类型：** AI 工具评测 + 周报 + 工作流教程

**工具：** ChatGPT, Midjourney, Stable Diffusion, ElevenLabs（用自己声音训练）, OpusClip, Make.com, AIVA/Soundraw

**工作流：** LLM 写脚本 → Midjourney+SD 做封面 → ElevenLabs 配音（克隆自己声音）→ 剪辑 → OpusClip 自动拆短视频分发

**独特方法：** 运营 [FutureTools.io](https://futuretools.io)（最大 AI 工具目录）。用 ElevenLabs 训练自己声音的克隆，AI 旁白和真人一样。

---

### 4. [Curious Refuge](https://youtube.com/@CuriousRefuge)（Caleb Ward）— 25.7 万订阅

**类型：** AI 电影制作教育（全球首家 AI 电影学校）

**工具：** Higgsfield AI（调用 Kling 3.0/Sora 2/Seedance/Veo）, Gemini, Claude, Imagen 4, Runway 节点工具, Adobe Firefly, Crystal Video Upscaler, Freepik, Krea

**工作流（2026.02 教程）：**
- 预制作：Custom GPT 写脚本 → Imagen 4 定"视觉 DNA"（主风格 prompt 锁定光照/质感）
- 制作：Runway 节点工具做动画（内置 Veo 3.1 和 Nano Banana 做 B-roll）
- 后期：Premiere Pro 剪辑（把 AI 素材当纪录片素材剪）

**独特方法：** **教学内容就是多工具混合。** 明确教授"按镜头选模型"的方法论。2026.02.19 教程直接用 Higgsfield Cinema Studio 在一个平台内切换 Kling/Sora/Veo。

**代表作：** "Star Wars by Wes Anderson"、"Lord of the Rings by Wes Anderson"（病毒传播）

→ [教程 1: PRO SHORT FILM](https://youtube.com/curiousrefuge) | [教程 2: 2026 Content Workflow](https://youtube.com/curiousrefuge) | [官网](https://curiousrefuge.com)

---

### 5. [Theoretically Media](https://youtube.com/@theoretically) (Tim Simmons) — 18.4 万订阅

**类型：** AI 工具深度评测 + 创意实验

**工具：** Runway, Kaiber, Midjourney v8, Pika, ComfyUI, LTX, Nano Banana, Veo 3.1, Magnific Video, Seedance 2.0, Kling 3.0, Luma Ray 3.14, EbSynth, Skyglass

**独特方法：** **同一 prompt 跨平台对比测试** — 用相同提示词在多个平台生成，给观众客观比较。强调"AI 工具是原材料，需要大量人工雕琢"。

---

### 6. [Tao Prompts](https://youtube.com/@TaoPrompts) — 17.2 万订阅

**类型：** AI 视频/艺术教程 + 工具排名 + prompt 工程

**工具：** Kling 3.0, Sora 2, Veo 3.1 等主流模型

**代表作：** "The Best AI Video Generators in 2026 (Ranked)" — 最受欢迎的 AI 视频工具排名视频之一

---

## TIER 2：专业创作者（1万-10万 订阅）

### 7. [Dave Clark](https://youtube.com/@daveclark) — 活跃增长中

**类型：** 原创 AI 短片 + 平台合作

**工具：** Google Flow (Veo/Imagen/Gemini), Kling 2.5/3.0, Sora, Runway, Midjourney, ElevenLabs, ChatGPT, Nano Banana, Topaz

**工作流：** Midjourney 出首帧 → Runway 生成 4s 片段 → **Topaz 变帧率（24fps→60/120fps）延长时长** → ElevenLabs 自演所有角色再变声 → 精修

**独特方法：** 被公认为"故事驱动 AI 电影"先驱。与 Google 直接合作（为 Google I/O 2025 制作 "Freelancers"）。**最活跃的跨平台实验者** — 同时测试所有主流 AI 视频平台。

**代表作：** "Freelancers"（Google I/O）, "Father Time"（Sora 制作）, "Enter The Closet"（Kling 2.5 + Veo 3.1 + Nano Banana 混合）

---

### 8. [Rourke Heath / GenHQ](https://youtube.com/@rourkeheath) — 4.8 万订阅

**类型：** 专家访谈 + 技术教程 + 生成式 AI 工作流

**工具：** Midjourney, Kling, Premiere Pro, 各种 LLM

**独特方法：** 提出"操作顺序"哲学 — LLM → 图像模型 → 视频模型的固定顺序。运营 GenHQ 社区。与 Google 和 Meta 合作。

---

### 9. [Sebastian Jefferies](https://youtube.com/@sebastianjefferies) — 13.8 万订阅

**类型：** AI 工具教程 + 视频编辑

**540 个视频发布。** 理念："AI 应该提升而非替代手艺"。运营视频编辑机构，将 AI 工具整合到商业工作流中。

---

### 10. [Keanu Visuals](https://youtube.com/@keanuvisuals) — 4.8 万订阅

**类型：** VFX + AI 混合教程，概念车/产品可视化

**工具：** After Effects, Freepik Spaces, AI 图像/视频生成器, Artlist AI Toolkit

**独特方法：** **传统 VFX 合成 + AI 增强** — 不是纯 AI，是 AI 辅助的影视制作。

**代表作：** "I Created a Concept Car Brand with AI (Full Breakdown)"

---

## TIER 3：独立电影人 + 先锋实验者

### 11. [Shy Kids](https://youtube.com/@shykids)（Walter Woodman, Patrick Cederberg, Sidney Leeder）

**类型：** 超现实 AI 短片

**工具：** Sora（主力）, Topaz（放大）, After Effects（将 Sora 元素合成到实拍中）

**工作流：** 480p 低分辨率快速生成 → 大量迭代 → Topaz 放大。3 个人 1.5-2 周完成一部短片。

**独特方法：** **OpenAI 首批 Sora 邀请创作者之一。** 开创了"低分辨率生成+后期放大"工作流。自称"朋克版 Pixar"。

**代表作：** "Air Head" — 最早用 Sora 制作的短片之一

---

### 12. Nicolas Neubert / [iamneubert](https://youtube.com/@iamneubert)

**类型：** AI 预告片 + 品牌合作

**工具：** Runway（主力 — 他是 Runway 创意团队成员）, Midjourney

**独特方法：** 创意导演视角 — 把 AI 视频当导演媒介，不只是技术工具。

**代表作：** "Genesis"（让 AI 预告片品类走红），与 Red Bull、大众汽车、Jared Leto 合作

---

### 13. Emonee LaRussa — 两座艾美奖

**类型：** 音乐视觉 + 动态图形

**工具：** After Effects（主力）+ AI 增强工具

为 Kanye West、Lil Nas X、Megan Thee Stallion、格莱美颁奖典礼、SNL 制作视觉。目前从传统动态图形向 AI 增强过渡。

---

## 特殊类别

### 14. [Neural Frames](https://neuralframes.com) — AI 音乐视频平台

上传歌曲 → AI 分析歌词+分离音轨 → 逐场景生成随音频脉动的视觉 → 4K 导出。可训练自定义模型（锁定你的艺术风格或脸）。AI 音乐视频领域的**绝对主导平台**。

### 15. Animaj Studio — AI 儿童动画（争议案例）

用 Google Veo + Gemini + Imagen 生成儿童动画。2025 年跨频道 220 亿播放。**已引发儿童安全组织批评（"AI 垃圾内容"）**，YouTube 正在打击低质量 AI 儿童内容。获得 Google AI Futures Fund 100 万美元投资。

### 16. Screen Culture / KH Studio — 反面教材

制作"假 AI 电影预告"（给不存在的续集做预告），用 AI 声音克隆。**两个频道均因虚假宣传和版权问题被 YouTube 封禁/处罚。** 代表 AI 视频创作的"暗面"。

---

## 5 大工作流模式（跨创作者统计）

| 模式 | 代表创作者 | 核心做法 |
|------|----------|---------|
| **多模型混合（Frankenstein）** | Hashem, Dave Clark, Curious Refuge | 每镜头选最强模型，5-8 工具混合 |
| **实拍+AI 混合** | Corridor Digital, Keanu Visuals | 真人拍摄为基础，AI 做风格/渲染层 |
| **低分辨率迭代+放大** | Shy Kids, Dave Clark | 480p-720p 快速试错 → Topaz 4K |
| **平台聚合** | Curious Refuge (Higgsfield) | 一个平台内切换多模型 |
| **重度后期去 AI 味** | Hashem | 胶片颗粒+混响+调色+Photoshop 修瑕 |

---

## 附录：数据来源

| 来源 | 链接 |
|------|------|
| Curious Refuge | [curiousrefuge.com](https://curiousrefuge.com) |
| Corridor Digital | [corridordigital.com](https://corridordigital.com) |
| Matt Wolfe / FutureTools | [futuretools.io](https://futuretools.io) |
| Hashem Al-Ghaili YouTube | [youtube.com/@HashemalGhaili](https://youtube.com/@HashemalGhaili) |
| Dave Clark AI films | [youtube.com/@daveclark](https://youtube.com/@daveclark) |
| Theoretically Media | [youtube.com/@theoretically](https://youtube.com/@theoretically) |
| Shy Kids / Sora | [fxguide.com](https://fxguide.com) / [nofilmschool.com](https://nofilmschool.com) |
| Nicolas Neubert | [victrays.com](https://victrays.com) |
| Neural Frames | [neuralframes.com](https://neuralframes.com) |
| Rourke Heath / GenHQ | [youtube.com/@rourkeheath](https://youtube.com/@rourkeheath) |
| Reddit r/aivideo | [reddit.com/r/aivideo](https://reddit.com/r/aivideo) |
| Google Flow / Labs | [labs.google](https://labs.google) |
