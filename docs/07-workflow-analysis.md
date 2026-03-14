# 07 — AI 短视频自动生成：工具链选型与工作流分析

> 最后更新：2026-03-14 | 基于对 30+ 工具、6 大商业平台、主流开源项目的系统调研

---

## 1. 推荐方案：现在用什么生成视频

### 1.1 一句话结论

> **主力方案：Kling 3.0**（4K/60fps + 原生音频 + 多镜头叙事 + 角色一致性），通过第三方 API 调用，~$0.12-0.15/秒。备选 Seedance 2.0（成本更低但全球 API 受限）。零成本原型用 Pexels + CLIP 语义匹配。

### 1.2 三档工具链

| 档位 | 生成方案 | 管道模式 | 单条成本 | 首次可用率 | 适用场景 |
|------|---------|---------|---------|-----------|---------|
| **入门档** | Pexels 素材 + CLIP 语义排序 + edge-tts + FFmpeg | 传统 6 步 | **$0** | 40-50% | 零成本验证、量产测试 |
| **主力档** | Kling 3.0 API（原生音频+多镜头） | 坍缩 4 步 | **$0.60-1.00** | 60-65% | 日常生产 |
| **精品档** | Kling 3.0 Pro（4K/60fps）或 Veo 3.1 | 坍缩 4 步 | **$3-9** | 60-73% | 旗舰内容 |

### 1.3 管道结构变化（2026.02 之后）

2026 年 2 月之后，顶级模型（Kling 3.0 / Seedance 2.0 / Veo 3.1）原生集成音频生成，管道发生结构性坍缩：

```
传统 6 步（2025）：    脚本 → TTS → 视频素材 → 字幕 → 配乐 → 合成
坍缩 4 步（2026.02+）：脚本 → AI 视频+音频一体生成 → 字幕 → 合成
```

TTS 和 BGM 被模型本身吸收。**这改变了质量评估的粒度** — 从"画面质量"变成"音画整体质量"。

### 1.4 为什么推荐 Kling 3.0 而非其他

| 对比维度 | Kling 3.0 | Seedance 2.0 | Veo 3.1 | Runway Gen-4.5 |
|---------|-----------|-------------|---------|----------------|
| 分辨率 | **4K/60fps** | 2K | 4K | 4K |
| 原生音频 | ✅ | ✅ | ✅ | ❌ |
| 多镜头叙事 | ✅ 15s 多镜头 | ✅ 单 prompt | 有限 | 关键帧 |
| 角色一致性 | ✅ 元素绑定 | ✅ 12 参考文件 | ❌ | ✅ |
| API 可用性 | ✅ 多渠道可用 | ⚠️ 全球 API 推迟 | ✅ 但配额严格 | ✅ |
| API 价格 | $0.12-0.15/s | $0.10-0.14/s（火山引擎） | $0.15/s (Fast) | $0.05/s (Turbo) |
| 免费层 | ✅ 66 daily credits | ✅ 225 daily tokens | ❌ 无免费视频配额 | ✅ 125 credits |
| 风险 | 低 | **高**（版权争议） | 中（配额限制） | 低 |

**Seedance 2.0 全球 API 因版权争议无限期推迟。** 2026.02 生成的含好莱坞演员/受版权保护角色的病毒视频引发迪士尼停止函、派拉蒙指控、MPA 谴责。目前主要通过中国国内应用（即梦/豆包）和少数第三方平台访问。

**Veo 3.1 无免费视频生成配额，** preview 模型限 10 RPM，配额耗尽返回 429。实际首次可用率仅 15-20%，需 4-6 次尝试，真实成本 = 标价 × 3-5。

### 1.5 各档位详细管道

**入门档：Pexels + CLIP 语义匹配**

```
LLM 脚本 → edge-tts → Pexels 搜索(CLIP 余弦排序) → Whisper 字幕 → BGM → FFmpeg
                              ↑
               关键词搜索 → CLIP 语义匹配（解决 #1 质量问题）
```

核心升级点：将 MoneyPrinterTurbo 的关键词搜索替换为 CLIP 语义匹配。成本 $0，解决最常见的"素材-脚本语义失配"问题。

**主力档：Kling 3.0 原生音频**

```
LLM 脚本(含镜头描述) → Kling 3.0(多镜头视频+音频) → Whisper 字幕 → FFmpeg 合成
```

- 第三方 API（ModelsLab/PiAPI）~$0.12-0.15/s，5s 片段 ≈ $0.60-0.75
- 原生音频 + 唇形同步，省去 TTS + BGM
- 多镜头模式：单 prompt 生成最长 15s 连贯多镜头

**精品档：Kling 3.0 Pro 4K/60fps**

```
LLM 结构化脚本 → Kling 3.0 Pro(4K/60fps 多镜头+音频) → Whisper 字幕 → FFmpeg
```

- 原生 4K/60fps，.mov 导出
- Canvas Agent 对话式迭代编辑
- 成本高但质量顶级

---

## 2. 整体局势（2026 年 3 月）

### 2.1 2026.02 大爆发：行业转折点

2026 年 2 月第一周，三大模型同时发布，行业格局剧变：

```
2026.01.05  LTX-2 开源发布（4K/50fps+音频，Apache 2.0）
2026.01.07  Sora 限制免费使用
2026.01.10  Sora 免费层完全停止
2026.02.05  ★ Kling 3.0 发布 — 首个原生 4K/60fps AI 视频模型
2026.02.07  ★ Seedance 2.0 发布 — 原生音频 + 12 文件多模态输入
2026.02.10  ★ Runway Gen-4.5 API 上线
2026.02.12  Seedance 2.0 版权争议爆发
2026.03.04  Seedance 2.0 API 通过火山引擎上线（仅中国）
2026.03.xx  NVIDIA GDC 发布 ComfyUI App View + LTX-2.3 优化
```

### 2.2 行业趋势

```
2025 年常态                        2026.02 之后新常态
─────────────                     ─────────────
单片段生成                         → 多镜头叙事生成
视频/音频分离管道                    → 原生音视频一体生成
1080p 为主流                       → 4K/60fps 成为标杆
文本/图像输入                       → 多模态输入（12+ 参考文件）
手动改 prompt 重试                  → 故事板 + 对话式迭代编辑
生成模型竞争                        → 全创作管道竞争（编辑+导出+发布）
```

### 2.3 市场格局

**商业平台第一梯队（2026.03）：**
- **Kling 3.0**（快手）— 4K/60fps，多镜头，免费层
- **Seedance 2.0**（字节跳动）— 多模态输入最强，但全球受限
- **Veo 3.1**（Google）— 写实感最强，但配额严格且贵
- **Runway Gen-4.5** — 视觉保真最高，专业创作者首选
- **Sora 2**（OpenAI）— 最长视频（25s），但已无免费层

**中国市场双寡头：** 即梦（字节）vs 可灵（快手），海螺（MiniMax）为第三极。

**开源突破：** LTX-2（4K+音频，12GB 可跑）和 Wan 2.2（VBench #1，10GB 可跑）让消费级 GPU 跑 AI 视频成为现实。

### 2.4 核心结论

1. **原生音频是新标配** — 所有顶级模型都原生生成音频，后期配音正在变成可选项
2. **没有任何工具有自动质量门控** — 所有平台、所有开源工具，质量控制完全靠人工
3. **"生成 10 个挑 1 个"是行业通用做法** — 批量生成 + 人工筛选是唯一的"质量策略"
4. **87% 的失败可通过更好的 Prompt 解决** — 但 Prompt 优化目前完全手动
5. **即使最好的模型（Runway 73%），6 片段全合格率也只有 15%** — 开环不可能一次成功
6. **API 价格正在快速商品化** — 第三方定价比官方便宜 85-95%

---

## 3. 首次可用率与真实成本

### 3.1 各平台首次可用率

一次生成即可使用（无需重试）的概率：

```
Runway Gen-4    ████████████████████████████████████░░░░░░░░░░  73%
Pika 2.5        ██████████████████████████████████░░░░░░░░░░░░  68%
Kling 3.0       ████████████████████████████░░░░░░░░░░░░░░░░░░  ~60-65%
Seedance 2.0    ████████████████████████░░░░░░░░░░░░░░░░░░░░░░  ~55-65%
Luma            ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░  40-70%
Pexels+CLIP     ██████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  40-50%
Google Veo 3.1  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  15-20%
```

### 3.2 每 10 秒视频的真实成本（含迭代）

| 方案 | 标价/10s | 迭代次数 | 真实成本/10s | API 来源 |
|------|---------|---------|-------------|---------|
| Pexels 素材 | $0 | 1 | **$0** | [pexels.com](https://www.pexels.com) |
| 开源 LTX-2 | $0（需 GPU） | 1 | **$0** | [github.com/Lightricks/LTX-2](https://github.com/Lightricks/LTX-2) |
| 开源 Wan 2.2 | $0（需 GPU） | 1 | **$0** | [github.com/Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2) |
| Hailuo | $0.19 | ~2 | $0.38 | [hailuoai.video](https://hailuoai.video) |
| Runway Turbo | $0.50 | ~2 | $1.00 | [runwayml.com](https://runwayml.com) |
| Kling 3.0 | $0.60-0.75 | ~2 | $1.20-1.50 | [klingai.com](https://klingai.com) / ModelsLab |
| Seedance 2.0 | $0.14/s 官方 | ~2 | $2.80 | 火山引擎 |
| Sora 2 | $1.00 | ~3 | $3.00 | [sora.com](https://sora.com) |
| Veo 3.1 Fast | $1.50 | **4-6** | **$6-9** | [aistudio.google.com](https://aistudio.google.com) |

### 3.3 开环质量基线（6 片段/条）

| 方案 | 首次可用率 | 6 片段全合格概率 | 说明 |
|------|-----------|----------------|------|
| Pexels+CLIP | 45% | 0.8% | 几乎不可能一次成功 |
| Seedance 2.0 | 60% | 4.7% | 20 条里约 1 条一次成功 |
| Kling 3.0 | 65% | 7.5% | 13 条里约 1 条一次成功 |
| Runway Gen-4 | 73% | **15.1%** | 7 条里约 1 条一次成功 |

**关键数字：即使首次可用率 73%（最高），6 片段全合格的概率也只有 15%。这就是为什么需要自动评分和筛选机制。**

---

## 4. 商业平台详细对比

### 4.1 Kling 3.0（快手）— 2026.02.05 发布

```
Text/Image Prompt → 多镜头生成(2-6 shots, 15s/shot) → 原生音频 → 角色绑定
```

| 能力 | 详情 |
|------|------|
| 分辨率 | 原生 2K/4K，30fps（Pro 60fps） |
| 多镜头 | 单 prompt 2-6 镜头，可延展至 ~3 分钟 |
| 原生音频 | 音乐/音效/旁白/对话，跨语言支持 |
| 角色一致性 | Subject Reference（元素绑定）+ 参考驱动 |
| 运动控制 | V3.0 Pro Motion Control，物理感知（重力/惯性/形变） |
| 编辑 | Canvas Agent（故事板+多轮对话编辑） |
| 定价 | Free 66 daily credits; Std $6.99/mo; Pro $25.99/mo; Premier $64.99/mo; Ultra $180/mo |
| API | ModelsLab ~$0.12-0.15/s; PiAPI $10/mo/seat; 企业方案 $4,200/30K units |

### 4.2 Seedance 2.0（字节跳动）— 2026.02.12 中国发布

```
12 参考文件(图片/视频/音频) + Text Prompt → 多镜头叙事 + 原生音频 → 角色/风格一致
```

| 能力 | 详情 |
|------|------|
| 分辨率 | 最高 2K |
| 多模态输入 | **最多 12 个参考文件**（图/视频/音频） |
| 原生音频 | 双声道，对话/环境音/音效/音乐同步 |
| 多语言唇形同步 | 英/中/西精确对齐 |
| 视频编辑 | 角色替换、内容增删、延展/拼接 |
| 定价 | 火山引擎 ~$0.14/s; Atlas Cloud $0.022/s (v1.5 Pro) |
| **风险** | **全球 API 因版权争议无限期推迟**（迪士尼/派拉蒙/MPA） |

### 4.3 Google Veo 3.1

```
Text Prompt → 8s 视频 + 原生音频 → 720p/1080p/4K
```

| 能力 | 详情 |
|------|------|
| 分辨率 | 720p / 1080p / 4K |
| 最长时长 | 8 秒/片段 |
| 原生音频 | 音效/对话/环境音 |
| 竖版视频 | 原生 9:16 |
| 定价 | Fast $0.15/s; Standard $0.40/s |
| 配额 | Preview 10 RPM; Production 50 RPM |
| **问题** | **无免费视频配额；首次可用率仅 15-20%** |

### 4.4 Runway Gen-4 / Gen-4.5 — 2026.02.10 API 上线

```
Text/Image/Video Prompt → 2-60s 视频 → 4K → 关键帧/运动画刷控制
```

| 能力 | 详情 |
|------|------|
| 首次可用率 | **73%（最高）** |
| 分辨率 | 最高 4K |
| 时长 | Gen-4 最长 60s; Gen-4.5 2-10s |
| 原生音频 | ❌（唯一不支持的顶级模型） |
| 特色 | Motion Brush 3.0, Director Mode, 角色/环境一致性 |
| 集成 | Adobe Firefly, Envato VideoGen |
| 定价 | Free 125 credits; Std $12/mo; Pro $28/mo; Unlimited $76/mo |
| API | Gen-4 Turbo $0.05/s（最便宜的商业 API） |

### 4.5 Sora 2（OpenAI）

```
Text/Image Prompt → 5-25s 视频 → 1080p → 故事板/延展
```

| 能力 | 详情 |
|------|------|
| 时长 | 标准 5-15s; Pro 最长 25s（业界最长） |
| 原生音频 | 对话/音效/音乐同步 |
| 特色 | 故事板工具, 视频延展, Character Cameos |
| **限制** | **2026.01.10 免费层完全停止** |
| 定价 | ChatGPT Plus $20/mo (1000 credits); Pro $200/mo |
| API | $0.10/s (base); $0.30/s (Pro 720p); $0.50/s (Pro 1080p) |

### 4.6 Pika 2.5

| 能力 | 详情 |
|------|------|
| 时长 | 5-10 秒 |
| 特色 | Pikaffects 物理效果（粉碎/融化/膨胀/爆破）, 时间线编辑器, 唇形同步 |
| 定价 | Free 80 credits; Std $8/mo; Pro $28/mo; Fancy $76/mo |
| API | fal.ai ~$0.20/5s 720p |

### 4.7 Hailuo / MiniMax

| 能力 | 详情 |
|------|------|
| 特色 | 性价比最高的商业方案，AI 转场，自定义风格 |
| 定价 | Std $9.99/mo; Pro $34.99/mo; Ultra $124.99/mo; Max $199.99/mo |
| API | $0.19-0.56/video |

---

## 5. 开源工具与本地模型

### 5.1 开源视频生成模型

| 模型 | 来源 | 分辨率 | 时长 | 消费级 GPU | 许可证 | 特点 |
|------|------|--------|------|-----------|--------|------|
| **Wan 2.2** (5B) | 阿里巴巴 | 720p@24fps | ~5s | ✅ RTX 3080 (10GB) | MIT | VBench #1, MoE 架构 |
| **Wan 2.2** (27B) | 阿里巴巴 | 720p@24fps | ~5s | ❌ 需 A100 (~60GB) | MIT | 最高质量 |
| **LTX-2** | Lightricks | **4K@50fps** | 10-20s | ✅ RTX 4090 (24GB) | Apache 2.0 | 音频同步, NVIDIA CES 合作 |
| **CogVideoX** (5B) | 智谱 | 720x480 | ~6s | ✅ RTX 4090 (24GB) | Apache 2.0 | 稳定，入门友好 |
| **HunyuanVideo** | 腾讯 | 720p@24fps | ~5s | ❌ 需 A100 (40-80GB) | Open | 13B 参数, 高质量 |
| **Mochi 1** | Genmo | 480p@30fps | ~5.4s | ❌ 需 A100 (40-80GB) | Apache 2.0 | 10B, prompt 遵循强 |

**消费级 GPU 推荐：**
- **RTX 3080/4070 (10-12GB)**：Wan 2.2 (5B) — 720p, ~9 分钟/片段
- **RTX 4090 (24GB)**：LTX-2 — 原生 4K, 音频同步
- **WanGP 工具**声称支持低至 6GB 的旧显卡（RTX 10XX/20XX, AMD）

### 5.2 开源全管道工具

| 工具 | GitHub Stars | 画面来源 | 质量检测 | 最新版本 |
|------|-------------|---------|---------|---------|
| **[MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)** | 55k+ | Pexels 关键词搜索 | ❌ | v1.2.6 (2025.05) |
| **[NarratoAI](https://github.com/linyqh/NarratoAI)** | ~5k | 用户上传视频 | ⚠️ VLM 场景分析 | — |
| **[ShortGPT](https://github.com/RayVentura/ShortGPT)** | ~5k | Pexels+YouTube | ❌ | — |
| **[Short Video Maker](https://github.com/gyoridavid/short-video-maker)** | ~1k | Pexels 搜索 | ❌ | — |
| **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)** | — | 本地 AI 模型 | ❌ | 持续更新 |

**关键发现：没有任何开源工具实现了自动质量检测或纠错闭环。** 所有工具都是"生成即交付"模式。

### 5.3 MoneyPrinterTurbo 为什么有 55k Stars

不是因为技术强，而是因为：
1. **零成本** — Pexels 免费素材
2. **一键出片** — Web UI，极低使用门槛
3. **批量生成** — 量大取胜
4. **不依赖 GPU** — 任何机器都能跑

**核心瓶颈：** Pexels 关键词搜索太粗糙 → 素材与脚本语义不匹配（质量问题 #1）。用 CLIP 语义匹配替代是最小投入最大回报的升级。

---

## 6. 内容创作者实际工作流

### 6.1 "短视频工厂"标准流程

```
选定垂直领域 → LLM 生成脚本 → TTS 配音 → 画面素材 → 字幕 → 人工快审 → 批量发布
                                           │
                            ┌──────────────┼──────────────┐
                            │              │              │
                       Pexels 搜索    AI 头像/口播    AI 生成视频
                       (最常见)       (次常见)        (高端用户)
```

### 6.2 产量与人工介入

| 创作者类型 | 产量 | 人工介入 |
|-----------|------|---------|
| 内容工厂 | 200-300 条/月（7-10 条/天） | 最小化 |
| 自动化频道 | 30-60 条/月（1-2 条/天） | 15-30 分钟/条 |
| 质量导向 | 1 条/天 | 1-2 小时/条 |
| 混合模式（头部） | 80% AI 量产 + 20% 人工精修 | 视内容类型 |

### 6.3 质量控制现状

| 方式 | 使用率 | 描述 |
|------|-------|------|
| **人工快审** | 最高 | 15-30 秒看一遍 |
| **批量生成+筛选** | 高 | "生成 10 个，挑 1 个" |
| **A/B 测试** | 中 | 发布多版本，让算法选赢家 |
| **自动质量门控** | **无** | 没有任何工具提供 |

### 6.4 中国市场工具链

| 工具 | URL | 定位 |
|------|-----|------|
| **即梦 Dreamina** | [jimeng.jianying.com](https://jimeng.jianying.com) / [dreamina.capcut.com](https://dreamina.capcut.com) | 字节跳动视频生成（Seedance） |
| **可灵 Kling** | [klingai.com](https://klingai.com) | 快手 4K/60fps 视频生成 |
| **海螺 Hailuo** | [hailuoai.video](https://hailuoai.video) | MiniMax 性价比视频生成 |
| **剪映 Jianying** | [jianying.com](https://jianying.com) | 字节跳动编辑器，集成即梦 |
| **豆包 Doubao** | [doubao.com](https://doubao.com) | 字节跳动 AI 助手，内置 Seedance |
| **WaveSpeedAI** | [wavespeed.ai](https://wavespeed.ai) | 多模型聚合平台（600+ 模型） |
| **即创 iClip** | — | RPA 机器人：采集/适配/发布/多账号 |

---

## 7. 十大质量问题

### 7.1 按频率排序

| # | 问题 | 影响工具类型 | 可自动检测？ | 可自动修复？ |
|---|------|------------|------------|------------|
| 1 | **素材-脚本语义失配** | 素材搜索型 | ✅ CLIP 余弦 | ⚠️ 重新搜索 |
| 2 | **音画不协调** | 全类型 | ✅ 节奏分析 | ❌ 需重编排 |
| 3 | **角色一致性差** | AI 生成型 | ⚠️ 人脸嵌入 | ❌ 需 consistent ID |
| 4 | **镜头运动混乱** | AI 生成型 | ✅ 光流分析 | ❌ 需重生成 |
| 5 | **唇形不同步** | 口播/头像型 | ✅ A/V sync | ⚠️ 可重对齐 |
| 6 | **环境不一致** | AI 生成型 | ⚠️ VLM 判断 | ❌ 需重生成 |
| 7 | **压缩伪影** | 合成型 | ✅ NIQE/VMAF | ⚠️ 可重编码 |
| 8 | **内容泛化/重复** | 全类型 | ⚠️ 语义分析 | ❌ 需人工介入 |
| 9 | **AI 痕迹明显** | AI 生成型 | ⚠️ 检测模型 | ❌ 模型能力限制 |
| 10 | **叙事断裂** | 全类型 | ⚠️ VLM 判断 | ❌ 需重编排 |

### 7.2 按工具类型分布

```
素材搜索型（MoneyPrinterTurbo 等）: #1 素材失配 > #2 音画不协调 > #7 压缩伪影
AI 生成型（Veo/Runway/Kling）:     #3 角色一致性 > #4 镜头混乱 > #6 环境不一致
口播/头像型（HeyGen/Synthesia）:   #5 唇形同步 > #8 内容泛化 > #9 AI 痕迹
```

---

## 8. 市场空白与机会

```
已解决（技术成熟）:                   未解决（机会空间）:
─────────────────                   ─────────────────
✅ 脚本生成（LLM）                    ❌ 自动质量评估（所有人靠肉眼）
✅ TTS（Edge-TTS 免费够用）            ❌ 批量生成自动排序/筛选
✅ 字幕（Whisper）                    ❌ 失败后自动 Prompt 纠正
✅ 合成（FFmpeg）                     ❌ 素材-脚本语义匹配（关键词→CLIP）
✅ AI 视频生成（多平台成熟）           ❌ 跨镜头角色/场景一致性
```

> **"AI 视频生成就是掷骰子。"** — Reddit 用户
>
> 87% 的失败内容通过更好的 Prompt 可以成功。但 Prompt 优化目前完全手动。没有任何工具将 Prompt 优化自动化。

---

## 9. 路线决策：先 B 后 A

### 9.1 两条路线

| | 路线 A：质量闭环 | 路线 B：批量筛选 |
|--|----------------|----------------|
| **问题** | "这个视频哪里不好？怎么改？" | "这 N 个里哪个最好？" |
| **方法** | 生成→评估→诊断→改prompt→重试 | 并行生成N个→评分→选最佳 |
| **类比** | 编译器优化 | MapReduce |
| **学术基础** | VISTA 闭环提升 60% | 行业"生成 10 挑 1" |
| **延迟** | 高（串行 ~9 分钟） | 低（并行 ~1 分钟） |
| **差异化** | 强（无竞品） | 中（容易模仿） |

### 9.2 成本模型（Kling 3.0, $0.12/s, 首次可用率 60%, 6 片段/条）

| 维度 | 路线 A | 路线 B (N=3) | **路线 C (B+A)** |
|------|-------|-------------|-----------------|
| 成本/条 | ~$4.60 | ~$8.10 | **~$6.00** |
| 耗时/条 | ~9 分钟 | ~1 分钟 | **~2 分钟** |
| 全通过率 | ~100% | 67.8% | **97%+** |

### 9.3 分阶段计划

```
阶段 1：评分验证（共同基础）
  → 跑 100 条真实视频，验证 L1+L2 评分与人工判断的相关性
  → 交付：经验证的评分模块

阶段 2：路线 B（批量+筛选）
  → 每片段 N=2 候选 → 评分选最佳
  → 副产物：积累 "prompt→视频→评分" 三元组数据

阶段 3：路线 A（数据驱动纠错）
  → 用阶段 2 数据训练 prompt 重写
  → 只对筛选后仍未通过的片段做闭环
```

### 9.4 决策记录

> **决策：采用路线 C（先 B 后 A），分三阶段迭代。**
>
> 理由：评分是共同基础，B 为 A 提供训练数据，风险逐阶段递减。
>
> 默认生成方案：Kling 3.0 第三方 API。
>
> 决策日期：2026-03-14

---

## 10. 完整工具链索引

### 10.1 AI 视频生成

| 工具 | URL | 核心能力 | 定价 | API |
|------|-----|---------|------|-----|
| **Kling 3.0** | [klingai.com](https://klingai.com) | 4K/60fps+多镜头+原生音频 | Free 66 daily; Std $6.99/mo | ✅ ~$0.12/s |
| **Seedance 2.0** | [dreamina.capcut.com](https://dreamina.capcut.com) | 2K+12文件多模态+原生音频 | Free 225 daily; Basic $18/mo | ⚠️ 中国+第三方 |
| **Veo 3.1** | [aistudio.google.com](https://aistudio.google.com) | 4K+原生音频+竖版 | AI Pro $19.99/mo | ✅ $0.15/s Fast |
| **Runway Gen-4.5** | [runwayml.com](https://runwayml.com) | 最高视觉保真+60s长视频 | Free 125 credits; Std $12/mo | ✅ $0.05/s Turbo |
| **Sora 2** | [sora.com](https://sora.com) | 最长视频(25s)+故事板+延展 | Plus $20/mo | ✅ $0.10-0.50/s |
| **Pika 2.5** | [pika.art](https://pika.art) | 物理效果+唇形同步 | Free 80 credits; Std $8/mo | ✅ fal.ai |
| **Hailuo** | [hailuoai.video](https://hailuoai.video) | 性价比最高 | Std $9.99/mo | ✅ $0.19/video |
| **Luma** | [lumalabs.ai](https://lumalabs.ai) | 3D/VFX 专长 | Free 30 gens; Lite $9.99/mo | ⚠️ 有限 |
| **Adobe Firefly** | [firefly.adobe.com](https://firefly.adobe.com) | 商业安全, Premiere 集成 | Creative Cloud | ✅ |
| **LTX Studio** | [ltx.studio](https://ltx.studio) | 全片+故事板+角色控制 | Free 800 credits; Lite $15/mo | ✅ |

### 10.2 视频编辑

| 工具 | URL | 定位 | 定价 |
|------|-----|------|------|
| **CapCut** | [capcut.com](https://capcut.com) | AI 编辑 | Free; Pro $19.99/mo |
| **Descript** | [descript.com](https://descript.com) | 转录即编辑 | Free; Pro $30/mo |
| **OpusClip** | [opus.pro](https://opus.pro) | 长→短提取 | Free; Starter $15/mo |

### 10.3 AI 头像 / 配音

| 工具 | URL | 定位 | 定价 |
|------|-----|------|------|
| **HeyGen** | [heygen.com](https://heygen.com) | AI 头像+175 语言 | Free; Creator $29/mo |
| **Synthesia** | [synthesia.io](https://synthesia.io) | 企业级数字人 | 企业定价 |
| **ElevenLabs** | [elevenlabs.io](https://elevenlabs.io) | 语音生成+克隆 | Free 10K; Pro $99/mo |
| **edge-tts** | [github.com/rany2/edge-tts](https://github.com/rany2/edge-tts) | 免费 TTS | 免费 |

### 10.4 开源项目

| 项目 | GitHub | 特点 |
|------|--------|------|
| **Wan 2.2** | [Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2) | VBench #1, 10GB 可跑, MIT |
| **LTX-2** | [Lightricks/LTX-2](https://github.com/Lightricks/LTX-2) | 4K+音频, 12GB+, Apache 2.0 |
| **ComfyUI** | [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) | 节点式工作流, GPL-3.0 |
| **CogVideoX** | [zai-org/CogVideo](https://github.com/zai-org/CogVideo) | 智谱, Apache 2.0 |
| **HunyuanVideo** | [Tencent/HunyuanVideo](https://github.com/Tencent/HunyuanVideo) | 腾讯 13B |
| **MoneyPrinterTurbo** | [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | 55k stars, 一键出片, MIT |
| **NarratoAI** | [linyqh/NarratoAI](https://github.com/linyqh/NarratoAI) | VLM 场景分析+解说 |

### 10.5 素材库

| 平台 | URL | 定价 |
|------|-----|------|
| **Pexels** | [pexels.com](https://www.pexels.com) | 完全免费, 200 req/hr |
| **Pixabay** | [pixabay.com](https://pixabay.com) | 完全免费 |

---

## 附录 A：数据来源

| 来源 | 用途 |
|------|------|
| [Kling AI](https://klingai.com) + [Kuaishou/Nasdaq](https://nasdaq.com) | Kling 3.0 发布确认 |
| [Seedance 2.0 / Dreamina](https://dreamina.capcut.com) | 字节跳动视频生成 |
| [火山引擎](https://volcengine.com) + [Atlas Cloud](https://atlascloud.ai) | Seedance API 定价 |
| [Google AI Studio](https://aistudio.google.com) | Veo 3.1 配额/定价 |
| [Runway ML](https://runwayml.com) + [releasebot.io](https://releasebot.io) | Gen-4.5 确认 |
| [Sora / OpenAI](https://sora.com) + [PCMag](https://pcmag.com) | Sora 2 定价/限制 |
| [Pika](https://pika.art) | Pika 2.5 功能 |
| [NVIDIA CES/GDC 2026](https://nvidia.com) | LTX-2 + ComfyUI 更新 |
| [ModelsLab](https://modelslab.com) + [PiAPI](https://piapi.ai) | 第三方 API 定价 |
| [MoneyPrinterTurbo GitHub](https://github.com/harry0703/MoneyPrinterTurbo) | 开源工具分析 |
| [LTX-2](https://github.com/Lightricks/LTX-2) + [TechPowerUp](https://techpowerup.com) | 本地模型确认 |
| [Wan 2.2](https://github.com/Wan-Video/Wan2.2) + [Stackademic](https://stackademic.com) | 开源模型数据 |
| [WaveSpeedAI](https://wavespeed.ai) | 中国市场多模型聚合 |
| Reddit r/aivideo, r/StableDiffusion | 用户真实反馈/首次可用率 |
| [36kr](https://36kr.com) | 中国 AI 视频市场 |

## 附录 B：术语表

| 术语 | 定义 |
|------|------|
| 首次可用率 | 一次生成即可使用（无需重试）的概率 |
| 管道坍缩 | 原生音频模型将 TTS+BGM 步骤吸收，6 步管道变为 4 步 |
| B-roll | 辅助画面素材，用于覆盖旁白 |
| 素材失配 | 画面内容与脚本/旁白语义不一致 |
| 闭环纠错 | 自动评估 → 诊断 → 改 prompt → 重生成的循环 |
| 开环生成 | 生成后不自动评估和纠正，依赖人工审核 |
| 路线 B | 批量生成 N 个候选 → 自动评分 → 选最佳 |
| 路线 A | 评估 → 诊断 → prompt 重写 → 重生成 → 再评估 |
| 路线 C | 先 B（批量筛选）后 A（纠错），混合策略 |
