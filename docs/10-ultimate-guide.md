# 10 — AI 短视频制作终极指南 (2026.03)

> 本指南整合了 4 轮独立调研 + 10 份文档审查的成果。所有工具推荐基于独立盲测数据（Artificial Analysis / Video Arena），而非厂商营销。
>
> 适用对象：个人创作者 / 内容团队 / 商业广告制作 / 技术开发者

---

## 目录

1. [30 秒速查：现在该用什么](#1-30-秒速查现在该用什么)
2. [完整工作流（4 套，按场景选）](#2-完整工作流)
3. [第 1 步：脚本生成](#3-脚本生成)
4. [第 2 步：AI 视频生成 + Prompt 工程](#4-ai-视频生成--prompt-工程)
5. [第 3 步：配音（TTS）](#5-配音tts)
6. [第 4 步：字幕](#6-字幕)
7. [第 5 步：配乐与音效](#7-配乐与音效)
8. [第 6 步：剪辑合成](#8-剪辑合成)
9. [第 7 步：质量检查](#9-质量检查)
10. [第 8 步：发布与数据反馈](#10-发布与数据反馈)
11. [自动化工作流引擎](#11-自动化工作流引擎)
12. [成本与 ROI 计算](#12-成本与-roi-计算)
13. [常见坑与避雷指南](#13-常见坑与避雷指南)

---

## 1. 30 秒速查：现在该用什么

### 视频生成模型选型（基于独立盲测，非营销）

| 场景 | 首选 | 备选 | 不推荐 |
|------|------|------|--------|
| **氛围/质感/微距** | Runway Gen-4.5（盲测 Elo #1） | — | — |
| **角色一致/剧情连贯** | Seedance 2.0（@系统） | Kling 3.0（Subject Ref） | — |
| **极致写实/带对话** | Veo 3.1（原生音频+物理引擎） | — | — |
| **性价比量产** | 即梦 Jimeng（国内最便宜） | Hailuo（$0.19/video） | — |
| **零成本** | Pexels + CLIP 语义排序 | Wan 2.2 本地（10GB GPU） | — |
| **开源本地 4K** | LTX-2（Apache 2.0, 12GB+） | Wan 2.2 5B（MIT, 10GB+） | — |

### 按预算速查

| 月预算 | 脚本 | 视频 | 配音 | 字幕 | 配乐 | 剪辑 |
|--------|------|------|------|------|------|------|
| **$0** | DeepSeek | Pexels+CLIP | Edge-TTS | CapCut 自动 | Pixabay Music | CapCut |
| **~$30** | GPT-4o-mini | 即梦免费层 | Fish Audio | CapCut | Uppbeat | CapCut |
| **~$100** | Claude | Runway Std $28 | ElevenLabs $22 | CapCut Pro $20 | Artlist $17 | CapCut Pro |
| **~$300** | Claude | Runway $76 + Veo | ElevenLabs $99 | CapCut Pro | Artlist | Premiere |
| **自部署** | Ollama 本地 | Wan 2.2 / LTX-2 | CosyVoice / IndexTTS-2 | Whisper | 本地库 | FFmpeg |

---

## 2. 完整工作流

### 工作流 A：一人工作室（15 分钟/条，$0-1）

最成熟的个人创作者工作流。

```
① DeepSeek 写脚本 (Hook-Build-Body-CTA)
     ↓
② Edge-TTS 配音（zh-CN-XiaoxiaoNeural）
     ↓
③ Pexels 搜索素材 + CLIP 余弦排序（或即梦/Kling 免费层生成）
     ↓
④ CapCut 导入 → 自动卡拉 OK 字幕 → BGM（Pixabay）→ 音效
     ↓
⑤ 人工快审（3 秒钩子？字幕对？画面匹配？）
     ↓
⑥ 导出 9:16 → 发布
```

### 工作流 B：AI 原生视频（管道坍缩，~$1-3/条）

2026.02 之后的新范式 — AI 模型一次生成视频+音频+对话。

```
① LLM 写结构化脚本（含镜头、动作、对话、音效提示）
     ↓
② MidJourney 生成首帧参考图（锁定视觉风格）
     ↓
③ Runway/Seedance/Veo Image-to-Video（每场景 5-8 秒，2-3 候选选最佳）
     ↓
④ Whisper 转录 → CapCut 卡拉 OK 字幕
     ↓
⑤ Premiere/DaVinci 精修（调色+转场+Logo）
     ↓
⑥ 质量检查 → 多平台导出 → 发布
```

### 工作流 C：Agentic 自动化（Coze/Dify 智能体）

对话式生产 — 输入一句话，Agent 跑完全流程。

```
Coze/Dify 智能体配置：
  ├── 意图识别节点：分析输入主题
  ├── LLM 节点：DeepSeek 生成 5 个分镜 Prompt
  ├── 并行 API 节点：
  │   ├── SiliconFlow → Wan 2.2 视频生成
  │   ├── 或 Runway/Seedance API → 视频生成
  │   └── ElevenLabs/Fish Audio → TTS
  ├── 代码节点：FFmpeg 合成 + 字幕
  └── 输出节点：MP4 下载链接

用户输入："帮我做一个智能枕头广告"
Agent 自动输出：成片 MP4
```

**搭建步骤（Dify + SiliconFlow）：**
1. 注册 [SiliconCloud](https://siliconflow.cn)，获取 API Key
2. 在 Dify 插件市场安装 SiliconFlow 插件
3. 创建 Workflow，添加 SiliconFlow Video Generate 节点
4. 配置模型 `Wan-AI/Wan2.2-I2V-A14B`，设置 prompt 和 image 输入
5. 连接 End 节点输出视频 URL

### 工作流 D：ComfyUI 本地管道（极客/工作室）

全本地化，不依赖云 API，需 24GB+ GPU。

```
ComfyUI 节点流：
  Load Image → Upscale → LTX-2 Video Node → Audio Generation → Concat → Export MP4
```

- NVIDIA GDC 2026 发布 ComfyUI App View + LTX-2.3 NVFP4 优化
- Wan 2.2 和 LTX-2 均有 ComfyUI 自定义节点
- 适合需要完全控制、离线运行的团队

---

## 3. 脚本生成

### LLM 选择

| 场景 | 推荐 | 理由 |
|------|------|------|
| 中文短视频 | **豆包 / DeepSeek** | 中文语感最好 |
| 英文短视频 | **GPT-4o / Claude** | 创意写作强 |
| 零成本 | **DeepSeek** | 免费额度 |
| 批量 | **GPT-4o-mini** | 便宜快速 |

### 脚本公式：Hook-Build-Body-CTA

| 部分 | 60s | 30s | 作用 |
|------|-----|-----|------|
| **Hook** | 0-3s | 0-2s | 抓注意力（前 3 秒定生死） |
| **Build** | 3-15s | 2-8s | 建语境 |
| **Body** | 15-45s | 8-22s | 交付核心价值 |
| **CTA** | 45-60s | 22-30s | 引导行动 |

### 6 种 Hook 写法

| 类型 | 示例 | 适合 |
|------|------|------|
| 反常识 | "99% 的人不知道..." | 知识科普 |
| 提问 | "你有没有想过..." | 教育 |
| 痛点 | "还在为 X 发愁？" | 实用技巧 |
| 结果前置 | "最终效果是这样的——" | 教程/变身 |
| 强声明 | "这一个习惯彻底改变了我" | 个人成长 |
| 动态开场 | （直接动态画面，不要静态图） | 所有类型 |

### Prompt 模板

```
你是专业短视频编剧。请为以下主题写一个 {30/60} 秒脚本：
主题：{topic}
平台：{抖音/TikTok/YouTube Shorts}
风格：{知识科普/叙事/教程/评测}

要求：
1. Hook(0-3s) + Build + Body + CTA 四段式
2. Hook 使用{反常识/提问/痛点}手法
3. 每场景标注 [镜头描述]（英文，60-80 words）
4. 控制在 {150-200} 字

输出格式：
[00:00-00:03] Hook：旁白 | [镜头描述] | 音效提示
[00:03-00:10] Build：旁白 | [镜头描述] | 音效提示
...
```

---

## 4. AI 视频生成 + Prompt 工程

### 核心原则：Image-to-Video > Text-to-Video

**首帧图片引导法**是当前最佳实践：
1. 用 MidJourney/DALL-E 生成一张首帧参考图
2. 上传到 Runway/Seedance/Veo 做 Image-to-Video
3. 成功率从 ~60-73% 提升到 **~85-90%**

### 平台特定 Prompt 结构

#### Runway Gen-4.5

```
[镜头类型], [主体], [动作], [环境], [光照], [色调], [镜头运动]. [风格参考].

示例：
Close-up shot, a woman's hand placing a luxury bottle on marble, warm golden
hour lighting, shallow depth of field with bokeh, slow dolly-in. Cinematic
commercial, anamorphic lens flare.
```

**规则：**
- ❌ 不支持 negative prompt（只描述你想要的）
- ❌ 不要重复描述首帧图片已有的内容
- ✅ Image-to-Video 时只描述运动和镜头变化
- ✅ 一个 prompt 一个镜头，不要塞多个场景

#### Seedance 2.0（即梦）

```
主体 + 动作 + 场景 + 光线 + 镜头 + 风格 + 画质 + 约束

示例：
@图片1 作为首帧，一位女性缓缓转身面向镜头，五官清晰无变形，面部稳定，
柔和逆光，浅景深虚化背景，缓慢推进镜头，日系治愈风格，4K超高清细节丰富，
无模糊无残影画面稳定
```

**杀手锏 — @ 引用系统：**
- `@图片1 作为首帧` — 锁定首帧
- `@图片2 作为角色参考` — 角色一致性
- `@视频1 参考镜头语言` — 复制运动风格
- 最多 12 个参考文件

**关键参数：**
- 动态幅度拉低到 30-40%（微动更有电影感）
- 每段控制在 **5-8 秒**（10 秒后易崩坏 — "10 秒衰减定律"）
- 稳定性关键词：五官清晰、面部稳定、无变形、角色一致、服装一致

#### Veo 3.1

```
[镜头] [主体] in [场景], [动作], [光照], [运动]. 对话: "台词". 音频: [音效描述].
No subtitles, no text overlay.

示例：
Interior cafe, late afternoon. Medium two-shot at window table.
One line of dialogue from Person A: 'Are you ready?'
Camera: gentle dolly-in. Ambient: clinking cups, soft chatter.
No subtitles, no text overlay.
```

**Veo 独特能力：**
- 原生对话生成（prompt 末尾加对话文本）
- 三层音频：环境音 + 音效 + 音乐
- ✅ 必须加 "No subtitles, no text overlay"（否则自动加字幕）
- 镜头语言权重最高（prompt 开头放镜头描述）

### 跨平台速查

| 要素 | Runway | Seedance | Veo |
|------|--------|----------|-----|
| 语言 | 英文 | 中文优先 | 英文 |
| Negative prompt | ❌ | 约束词 | "No..." 有效 |
| 原生音频 | ❌ | ✅ | ✅ |
| 最长 | 60s (Gen-4) | 5-12s | ~8s |
| 首帧引导 | ✅（最佳实践） | ✅（@系统） | ✅ |
| Prompt 优先级 | 镜头类型在前 | 主体+动作在前 | 镜头在前+风格在前 |

---

## 5. 配音（TTS）

### 工具矩阵

| 工具 | 质量 | 中文 | 英文 | 成本 | 声音克隆 |
|------|------|------|------|------|---------|
| **Edge-TTS** | 7/10 | ✅ 晓晓/云希 | ✅ Jenny | $0 | ❌ |
| **Fish Audio** | 9/10 | ✅ 50+情感标记 | ✅ | $5.5/月 | ✅ |
| **ElevenLabs** | 9.5/10 | ⚠️ 可用 | ✅ 最佳 | $22-330/月 | ✅ 30s 音频 |
| **IndexTTS-2** | 9/10 | ✅ 最佳自然度 | — | 免费自部署 | ✅ |
| **CosyVoice** | 9/10 | ✅ 18 方言 | ✅ | 免费自部署 | ✅ 跨语言 |

### 配音参数

| 内容类型 | 语速 | 音调 | 停顿 |
|---------|------|------|------|
| 知识科普 | 1.0-1.1x | 默认 | 关键点后 0.3-0.5s |
| 娱乐/快节奏 | 1.15-1.25x | 略高 +5% | 最小化 |
| 商业广告 | 0.95-1.05x | 根据品牌调性 | 卖点后 0.5-1.0s |

### Edge-TTS 快速使用

```bash
pip install edge-tts
edge-tts --text "你好世界" --voice zh-CN-XiaoxiaoNeural --rate "+10%" -o output.mp3
```

⚠️ Edge-TTS 使用逆向工程微软 API，**无官方 SLA**，不适合商业关键业务。

---

## 6. 字幕

### 2026 标配：逐字卡拉 OK 高亮

| 参数 | 推荐值 |
|------|--------|
| 字体 | 无衬线粗体（思源黑体/Montserrat） |
| 每行 | 中文 8-12 字，英文 3-5 词 |
| 行数 | 最多 2 行 |
| 位置 | 屏幕中下 1/3（避开平台 UI） |
| 高亮色 | 黄色（与文字色强对比） |
| 时间 | 比语音**提前 0.1-0.2s** 出现 |
| 动画 | 逐字出现（卡拉 OK 式） |

### CapCut 字幕流程

```
导入视频+音频 → 文本 > 自动字幕 → 选卡拉 OK 样式 → 自定义字体/颜色 → 检查修正 → 导出
```

---

## 7. 配乐与音效

### 混音音量标准

| 音频层 | 音量 (dBFS) |
|--------|------------|
| 旁白/对话 | **-10 至 -12** |
| BGM（有旁白时） | **-24 至 -30**（比旁白低 15-20dB） |
| BGM（无旁白段） | **-12 至 -16** |
| 音效 | **-14 至 -20** |
| 整体响度 | **-14 LUFS** |

### 免费音乐来源

| 来源 | URL | 说明 |
|------|-----|------|
| YouTube Audio Library | YouTube Studio 内置 | YouTube Shorts 安全 |
| Pixabay Music | [pixabay.com/music](https://pixabay.com/music) | 完全免费 |
| 爱给网 | [aigei.com](https://aigei.com) | 中文最全免费音效+BGM |
| Fesliyan Studios | [fesliyanstudios.com](https://fesliyanstudios.com) | 有"对话背景音乐"分类 |
| Uppbeat | [uppbeat.io](https://uppbeat.io) | 创作者免费层 |

### 商用授权（广告必须正版）

| 平台 | 月费 | 说明 |
|------|------|------|
| **Artlist** | ~$17/月 | 全版权，无限下载，含音效 |
| **Epidemic Sound** | ~$15/月 | 社交媒体商用 |
| **Musicbed** | 按项目 | 高端广告 |

### 必备音效清单

| 类型 | 用途 | 获取 |
|------|------|------|
| Whoosh | 场景切换 | Pixabay / 爱给网 |
| Riser | 制造期待 | Pixabay / 爱给网 |
| Hit/Impact | 重点强调 | Pixabay / 爱给网 |
| Pop/Ding | 文字出现 | Pixabay / 爱给网 |

---

## 8. 剪辑合成

### 画幅规格

| 平台 | 画幅 | 分辨率 |
|------|------|--------|
| 抖音/TikTok/Shorts/Reels | 9:16 竖屏 | 1080×1920 |
| B 站 | 16:9 或 9:16 | 1920×1080 |
| YouTube 长视频 | 16:9 横屏 | 1920×1080 |

**核心原则：从一开始就按 9:16 竖版制作，不要从横版裁切。**

### 剪辑节奏

| 类型 | 每镜时长 |
|------|---------|
| 快节奏/娱乐 | 0.5-2s |
| 教程/展示 | 2-5s |
| 高端品牌广告 | 3-6s |

### 转场

| 类型 | 使用频率 |
|------|---------|
| 直接切 | 80%+ |
| 交叉溶解 | 10% |
| 滑动/推移 | 5% |
| 匹配剪辑 | 5% |

**2026 趋势：干净极简。花哨特效转场已过时。**

---

## 9. 质量检查

**这是全行业最大的空白 — 没有任何主流工具提供自动质量检查。以下是可用的方法：**

### 人工快审清单（60 秒内完成）

| # | 检查项 | 合格标准 |
|---|--------|---------|
| 1 | 前 3 秒钩子 | 有足够吸引力，不想划走 |
| 2 | 画面-脚本匹配 | 画面内容与旁白语义一致 |
| 3 | 字幕准确 | 无错字、时间同步 |
| 4 | 音量平衡 | 旁白清晰，BGM 不抢 |
| 5 | 画质 | 无明显模糊/伪影/闪烁 |
| 6 | 手机预览 | 在手机上字幕清晰、画面填满 |

### 自动化质量检测工具

| 工具 | 用途 | 安装 | 类型 |
|------|------|------|------|
| **VMAF** (Netflix) | 编码质量 vs 原始 | `ffmpeg`（内置 libvmaf） | 有参考 |
| **DNSMOS** (Microsoft) | 语音/音频质量 | `pip install torchmetrics[audio]` | 无参考 |
| **SyncNet** | 唇形同步检测 | `pip install syncnet-python` | 无参考 |
| **VBench** | AI 视频 16 维度评估 | `pip install vbench` | 无参考 |

### VMAF 快速使用

```bash
# 比较编码后 vs 原始（需要两个视频）
ffmpeg -i encoded.mp4 -i original.mp4 \
  -filter_complex libvmaf=model_path=vmaf_v0.6.1.json:log_path=log.json:log_fmt=json \
  -f null -
```

| 分数 | 质量 |
|------|------|
| 95+ | 过度（浪费带宽） |
| 84-92 | 好（UGC 目标） |
| 70-84 | 一般（可接受） |
| <70 | 差（不可接受） |

### DNSMOS 音频质量

```python
import torch
from torchmetrics.functional.audio import dnsmos
scores = dnsmos(preds=audio_tensor, fs=16000)
# 返回 [P808_MOS, MOS_SIG, MOS_BAK, MOS_OVR]
# 目标：MOS_OVR >= 3.5（可接受），>= 4.0（生产级）
```

### A/V 同步标准

| 偏移 | 感知 |
|------|------|
| ±20ms | 不可感知 |
| ±45ms | 训练有素的观众可察觉 |
| ±80ms+ | 明显干扰 |

---

## 10. 发布与数据反馈

### 最佳发布时间

| 平台 | 最佳时段 | 次优 |
|------|---------|------|
| 抖音 | 18:00-22:00 | 7:30-8:30, 12:00-13:00 |
| TikTok | 10-11 AM EST 周二-四 | 7-9 PM |
| YouTube Shorts | 2-4 PM EST | 8-10 PM |

### 多平台导出规格

| 平台 | 分辨率 | 帧率 | 码率 | 编码 |
|------|--------|------|------|------|
| 抖音 | 1080×1920 | 30fps | 12-15 Mbps | H.264 |
| 小红书 | 1080×1920 或 1080×1440 | 30fps | 10-15 Mbps | H.264 |
| TikTok | 1080×1920 | 30fps | 12 Mbps | H.264 |
| YouTube Shorts | 1080×1920 | 30fps | 12 Mbps | H.264 |

### 抖音 SEO（2025 算法更新后）

推荐引擎升级为"兴趣图谱 + 场景匹配"双引擎：
- **关键词布局**：标题 + 字幕 + 话题标签 + 评论区
- **关键词结构**：痛点 + 解决方案（如"零基础健身跟练"）
- **评论区 SEO**：评论关键词影响搜索排名 → 设计互动引导

### A/B 测试方法

**单变量法则：每次只改一个元素。**

| 优先级 | 测试项 | 衡量指标 |
|--------|--------|---------|
| 1 | Hook（前 3 秒） | 3 秒留存率 > 30% |
| 2 | 视频时长（15s/30s/60s） | 完播率 > 40% |
| 3 | 封面/缩略图 | 点击率 |
| 4 | CTA 措辞和位置 | 转化率 |

**测试协议：**
- 同一天上传两个版本
- 每个版本积累 1000+ 播放后再比较
- TikTok 看 48-72 小时数据，YouTube Shorts 看 1-2 周

### 发布后关键指标

| 指标 | 说明 | 目标 |
|------|------|------|
| 3 秒留存率 | Hook 有效性 | > 30% |
| 平均观看时长 | 内容吸引力 | > 50% 视频时长 |
| 完播率 | 整体质量信号 | > 40% (30s 以下) |
| 互动率 | 点赞+评论+分享/播放 | > 5% (TikTok) |
| 分享率 | 病毒性信号 | 越高越好 |

### 分析工具

| 工具 | 用途 | 成本 |
|------|------|------|
| 平台原生分析 | 自己账号数据 | 免费 |
| **Virlo** | AI 趋势发现 + 竞品分析 | 中等 |
| **Exolyt** | TikTok 实时趋势 | 中等 |
| **Brand24** | 情感分析 + 提及监控 | 入门 |

---

## 11. 自动化工作流引擎

### 三层架构

```
第 1 层：视觉控制（本地 GPU）
  └── ComfyUI — 节点式本地管道，接 Wan 2.2 / LTX-2

第 2 层：智能体编排（低代码）
  └── Coze / Dify — LLM 驱动的全自动流水线

第 3 层：企业集成（触发器+分发）
  └── n8n / Make — 监听 Notion → 触发生成 → 自动发布
```

### Coze（扣子）智能体搭建

```
1. 创建 Bot → 添加 Workflow 节点
2. Start 节点：用户输入主题
3. LLM 节点：DeepSeek 解析需求 → 输出分镜 JSON
4. Plugin 节点：调用 Runway/Seedance/SiliconFlow API → 视频
5. Plugin 节点：调用 TTS API → 配音
6. Code 节点：FFmpeg 合成
7. End 节点：返回 MP4 下载链接
```

### Dify + SiliconFlow 视频生成

```
1. 注册 SiliconCloud → 获取 API Key
2. Dify 插件市场安装 SiliconFlow 插件
3. 创建 Workflow → 添加 SiliconFlow Video Generate 节点
4. 配置模型：Wan-AI/Wan2.2-I2V-A14B
5. 设置 prompt + image 输入 + video_size (1280x720)
6. End 节点输出视频 URL
```

### n8n 多平台分发

```
Notion 数据库状态变更 → n8n Webhook 触发
  → 调用 Coze Agent API → 获取成片
  → 下载 MP4
  → 并行发布：
    ├── TikTok API
    ├── YouTube Shorts API
    └── Instagram Reels API
```

### Pixelle-Video：全开源一键出片（阿里 AIDC-AI）

**GitHub:** [AIDC-AI/Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video) | 许可证: Apache 2.0

输入主题 → 自动脚本 → AI 图片/视频 → TTS 旁白 → BGM → 合成出片。

```bash
git clone https://github.com/AIDC-AI/Pixelle-Video
# 配置 LLM 后端（GPT/DeepSeek/Ollama/通义千问）
# 配置图像生成模型
# 运行：输入主题字符串，系统自动跑通全流程
```

支持：自定义素材上传、动作迁移、数字人口播、多语言 TTS、image-to-video。

### MCP Server：让 Claude/Cursor 直接生成视频

| MCP Server | 能力 | 安装 |
|------------|------|------|
| **Kling AI MCP** | 13+ 工具：文生视频、图生视频、特效、唇形同步 | [GitHub](https://github.com/chuanky/kling-ai-mcp-server) |
| **Remotion MCP** | React 编程式视频创作，3D/字幕/动画 | [remotion.dev](https://remotion.dev) |
| **Remotion Video Gen** | Claude 直接创建和渲染视频 | [MCP Market](https://mcpmarket.com) |

```json
// Claude Desktop MCP 配置示例（Kling AI）
{
  "mcpServers": {
    "kling-ai": {
      "command": "node",
      "args": ["path/to/kling-mcp/index.js"],
      "env": { "KLING_ACCESS_KEY": "...", "KLING_SECRET_KEY": "..." }
    }
  }
}
```

### ComfyUI Wan 2.2 具体配置

**模型文件：**
```
models/diffusion_models/
  └── wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors  (Image-to-Video 14B)
models/clip/ 或 models/text_encoders/
  └── umt5_xxl_fp8_e4m3fn_scaled.safetensors
models/vae/
  └── wan2.2_vae.safetensors
models/loras/
  └── wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors  (加速 LoRA)
```

**必装自定义节点：** ComfyUI-GGUF, ComfyUI-KJNodes, ComfyUI-VideoHelperSuite, ComfyUI-mxToolkit, ComfyUI-Frame-Interpolation, ComfyUI-wanBlockswap, ComfyUI-MagCache

**参数：** Steps 15-30, Guidance Scale 6, 分辨率 720p

### 中国市场批量工具

| 工具 | 定位 | 优势 |
|------|------|------|
| **红鸦AI** | 小红书矩阵批量图文 | 20 条/天，全套风格一致 |
| **豆包** | 抖音优化脚本+视频 | 理解"黄金 3 秒"规则 |
| **即梦** | 低成本视频生成 | CapCut 深度集成 |
| **Pixelle-Video** | 全开源全自动出片 | Apache 2.0，可商用 |

---

## 12. 成本与 ROI 计算

### 单条视频成本对比（30s，6 片段）

| 方案 | 生成成本 | 配音 | 字幕 | 配乐 | 合计 |
|------|---------|------|------|------|------|
| **Pexels+Edge-TTS** | $0 | $0 | $0 | $0 | **$0** |
| **即梦免费层** | $0 | $0 | $0 | $0 | **$0** |
| **Runway Std** | ~$3.00 | $0.01 | $0 | $0 | **~$3** |
| **Runway+候选筛选(N=2)** | ~$6.00 | $0.01 | $0 | $0 | **~$6** |
| **传统拍摄** | $500-2000 | $50-200 | $20-50 | $30-100 | **$600-2350** |

### 月度 ROI（以自动化频道为例）

```
假设：每天 2 条，每条广告收入 $5-20
月产量：60 条
月工具成本：~$100（Runway Std + ElevenLabs + CapCut）
月收入：$300-1200
ROI：200-1100%
```

---

## 13. 常见坑与避雷指南

### ❌ 不要做的事

| 坑 | 说明 |
|----|------|
| 用横版裁切做竖版 | 画面信息丢失严重，永远不会好看 |
| 静态图开场 | 前 3 秒必须有动态 |
| 把 prompt 当作文写 | AI 视频模型需要具体物理描述，不是抽象概念 |
| 信 Kling "4K/60fps" 营销 | Reddit 用户反馈实际常用 1080p，渲染常失败 |
| 用免费 BGM 做商业广告 | 版权风险不值得 |
| Seedance 片段超过 10 秒 | "10 秒衰减定律"——10 秒后角色/场景易崩坏 |
| 依赖单一 AI 视频工具 | 混合使用 2-3 个工具，按场景选最合适的 |

### ✅ 关键法则

| 法则 | 说明 |
|------|------|
| **高频 > 极致** | 频繁发布合格内容 > 偶尔发布完美内容 |
| **3 秒定生死** | 前 3 秒决定一切，投入 50% 精力在 Hook |
| **手机测试** | 所有内容必须在手机上预览 |
| **音频 > 画面** | 73% 爆款靠音画协调（来源：行业实践共识） |
| **结构化 > 随意** | 固定结构 = 稳定质量 = 可自动化 |
| **Image-to-Video > Text-to-Video** | 首帧图片引导成功率从 60% 提升到 85%+ |
| **5-8 秒片段拼接** | 超过 10 秒的单镜头易崩坏，拆分为短片段 |

---

## 附录：数据来源与可信度

| 来源 | 类型 | 可信度 |
|------|------|--------|
| [Artificial Analysis](https://artificialanalysis.ai) | 独立盲测 Elo | ★★★★★ |
| [Video Arena](https://videoarena.tv) | 双盲人类投票 | ★★★★☆ |
| Reddit r/aivideo | 独立用户反馈 | ★★★★☆（负面评价几乎不可能被赞助） |
| 知乎/CSDN | 中文用户反馈 | ★★★☆☆（部分软文） |
| GitHub Stars/Issues | 开源项目真实数据 | ★★★★★ |
| 厂商官方文档 | 产品规格 | ★★★☆☆（可能夸大） |
| YouTube 对比视频 | 视觉对比 | ★★☆☆☆（多为付费/联盟） |
| 36kr/TechCrunch | 行业分析 | ★★★☆☆ |
