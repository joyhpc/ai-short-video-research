# 12 — 广告级 AI 视频制作：立即执行手册

> **不计成本，只追求效果。** 以下三条路线按自动化程度排序，附每一步的具体操作。

---

## 路线 1：Luma Agents（一句话出片，5-10 分钟/条）

### 现在就做

**第 1 步：注册 Luma（2 分钟）**

1. 打开 [lumalabs.ai](https://lumalabs.ai)
2. 点 Sign Up → Google 账号登录
3. 选择 Plus 套餐（$29.99/月）或 Pro（$99.99/月）
4. 进入 Luma Agents 界面

**第 2 步：输入广告 Brief（1 分钟）**

直接在对话框输入，例如：

```
Create a 30-second luxury skincare product ad video.
Brand tone: elegant, minimal, warm.
Scenes: 1) Product hero shot on marble surface with golden light
2) Close-up of texture/cream being applied
3) Model with glowing skin, soft smile, morning light
4) Brand logo reveal with tagline "Your skin, elevated"
Style: cinematic, shallow depth of field, warm color grading.
Include voiceover in Chinese (female, gentle tone).
Aspect ratio: 9:16 vertical.
```

**第 3 步：Agent 自动执行**

Luma Agent 会自动：
- 选择最合适的模型（Ray3.14/Veo 3.1/Kling 等）
- 生成各场景视频+音频
- 保持角色和风格一致性
- 编排多镜头
- 输出成片

**第 4 步：微调（2-5 分钟）**

- 对不满意的镜头，在 Agent 对话框里说"重新生成第 2 个镜头，更多微距细节"
- Agent 会只重生成那个镜头，保持其余不变

**第 5 步：导出**

- 下载 MP4
- 如需加中文字幕 → 导入 [CapCut](https://capcut.com) → 自动字幕 → 导出

---

## 路线 2：Higgsfield Cinema Studio（多模型并行，15-30 分钟/条）

### 现在就做

**第 1 步：注册 Higgsfield（2 分钟）**

1. 打开 [higgsfield.ai](https://higgsfield.ai)
2. 创建账号 → 选择订阅套餐
3. 进入 Cinema Studio 2.0

**第 2 步：配置"摄影机"（2 分钟）**

Cinema Studio 模拟真实电影机身和镜头：

| 广告类型 | 推荐机身 | 推荐镜头 | 效果 |
|---------|---------|---------|------|
| 高端护肤/奢侈品 | ARRI ALEXA | 50mm f/1.4 | 奶油般虚化，肤色温暖 |
| 科技产品 | RED V-RAPTOR | 35mm | 锐利，冷色调 |
| 美食/生活方式 | Sony FX6 | 85mm f/1.2 | 极浅景深，氛围感 |
| 运动/动态 | ARRI ALEXA | 24mm wide | 广角动态感 |

**第 3 步：创建角色（如需要）（3 分钟）**

1. 点击 Character ID → 上传角色参考图
2. 启用 Soul ID → 锁定面部+体态+穿衣风格+表情习惯
3. 给角色命名（如 "Model_A"）

**第 4 步：逐镜头生成（10-20 分钟）**

每个镜头：
1. 写 prompt（英文，描述画面+运动+光照）
2. 选择同时跑的模型（勾选 Sora 2 + Veo 3.1 + Kling 2.6）
3. 点 Generate → 等待 1-2 分钟
4. 3 个模型各出一个结果 → **选最好的那个**
5. 对话场景：选 Veo 3.1 的结果（唇形同步最好）

**第 5 步：用 Shots 工具生成多机位（2 分钟）**

1. 选中一个满意的镜头
2. 点 Shots → 自动生成同一场景的不同机位（远景/中景/特写）
3. 挑选最佳角度

**第 6 步：导出+后期**

1. 导出所有镜头 → 导入 [Premiere Pro](https://adobe.com/premiere) 或 [DaVinci Resolve](https://blackmagicdesign.com/davinciresolve)
2. 排列时间线 → 添加转场
3. [ElevenLabs](https://elevenlabs.io) 生成配音 → 导入
4. [Artlist](https://artlist.io) 选正版配乐 → 导入
5. [CapCut Pro](https://capcut.com) 或 Premiere 加字幕
6. 调色 → 导出 9:16

---

## 路线 3：手动 Frankenstein（最高画质，1-2 小时/条）

### 现在就做

**第 1 步：写脚本（10 分钟）**

打开 [claude.ai](https://claude.ai)，输入：

```
你是资深广告创意总监。

请为以下产品写一个30秒竖版广告视频脚本：
产品：[你的产品名]
目标受众：[受众描述]
投放平台：抖音/小红书
视觉风格：[高端简约/活力时尚/温暖治愈]

要求：
1. 分4个场景，每场景5-8秒
2. 每场景包含：
   - 【时间码】
   - 【镜头】类型（特写/中景/远景）
   - 【画面描述】英文，80词，含光照和镜头运动
   - 【旁白】中文
   - 【音效提示】
3. 第一个场景必须是强视觉钩子
```

**第 2 步：生成首帧参考图（10 分钟）**

打开 [MidJourney](https://midjourney.com)（$30/月）

每个场景生成一张首帧图：
```
/imagine [粘贴脚本中的英文画面描述] --ar 9:16 --style raw --v 6.1
```

- 选最好的一张 → 下载高清版
- 确保 4 张首帧图的色调、风格统一（用 --sref 锁定风格种子）

**第 3 步：逐场景生成视频（30-40 分钟）**

**场景类型 → 选对应平台：**

| 场景类型 | 用哪个 | 操作 |
|---------|--------|------|
| 质感/微距/氛围 | [Runway Gen-4.5](https://runwayml.com)（$76/月 Unlimited） | 上传首帧图 → Image-to-Video → prompt 只写运动和镜头变化 |
| 角色/剧情/多镜头 | [Seedance 2.0 / 即梦](https://dreamina.capcut.com)（$42/月） | 上传首帧图标记 @Image1 → prompt 用 6 元素结构 → 动态幅度调低到 30-40% |
| 对话/唇形同步 | [Veo 3.1](https://aistudio.google.com)（$0.40/s） | prompt 末尾加对话文本 + "No background music" → 中近景构图 |
| 动作/运动/物理 | [Kling 3.0](https://klingai.com)（$26/月 Pro） | Motion Control 模式 → 上传首帧+动作参考视频 |

**每个场景操作：**
1. 上传首帧图
2. prompt 只描述**运动和变化**（不要重复描述画面内容，画面已经在首帧图里了）
3. 生成 **2-3 个候选**
4. 选最好的
5. 下载

**跨场景一致性——首尾帧接力：**
```
场景 1 完成 → 提取最后一帧（截图或 ffmpeg）
   → 作为场景 2 的首帧上传 → 生成场景 2
   → 提取最后一帧 → 作为场景 3 的首帧...
```

**第 4 步：配音（5 分钟）**

打开 [ElevenLabs](https://elevenlabs.io)（$99/月 Pro）

1. Speech → 选声音（中文推荐 Multilingual v2 模型）
2. 粘贴每个场景的旁白文本
3. 调整：语速 0.95-1.05x，关键卖点后加 0.5 秒停顿
4. 分场景导出 MP3

**或者：** 如果场景 3 用了 Veo 3.1 带对话，那个镜头不需要额外配音。

**第 5 步：配乐（3 分钟）**

打开 [Artlist](https://artlist.io)（$17/月）

1. 搜索匹配品牌调性的音乐（搜索关键词：elegant, minimal, cinematic）
2. 下载
3. **商业广告必须用正版授权音乐**

**第 6 步：剪辑合成（15-20 分钟）**

打开 [Premiere Pro](https://adobe.com/premiere) 或 [DaVinci Resolve](https://blackmagicdesign.com/davinciresolve)（免费版即够用）

```
操作顺序：
1. 导入所有视频片段 → 按场景排列时间线
2. 导入旁白音频 → 对齐到对应场景
3. 导入 BGM → 全片铺底
4. 混音：
   - 旁白：-10 至 -12 dBFS
   - BGM（有旁白时）：-24 至 -30 dBFS
   - BGM（无旁白时）：-12 至 -16 dBFS
5. 转场：场景间用直切或 0.5s 交叉溶解（不要花哨转场）
6. 调色：全片统一色调（DaVinci 调色面板）
7. 添加 Logo 结尾画面（3 秒）
```

**第 7 步：字幕（5 分钟）**

打开 [CapCut Pro](https://capcut.com)（$20/月）

1. 导入剪好的视频
2. 文本 → 自动字幕 → 选卡拉 OK 高亮样式
3. 修改字体为品牌字体
4. 品牌名/产品名/价格用品牌色高亮
5. 检查修正识别错误
6. 导出

**第 8 步：导出交付**

| 平台 | 画幅 | 分辨率 | 码率 |
|------|------|--------|------|
| 抖音 | 9:16 | 1080×1920 | 12-15 Mbps |
| 小红书 | 9:16 或 3:4 | 1080×1920 | 10-15 Mbps |
| 微信视频号 | 9:16 | 1080×1920 | 10 Mbps |
| 朋友圈广告 | 9:16 | 1080×1920 | 8-10 Mbps |
| 横版备份 | 16:9 | 1920×1080 | 15-20 Mbps |

---

## 交付前检查清单

```
□ 前 3 秒有强视觉钩子（不是静态图/文字开场）
□ 产品/品牌在前 5 秒内出现
□ 所有场景色调统一
□ 旁白清晰，BGM 不抢
□ 字幕无错字，关键词有高亮
□ 在手机上预览过（字幕够大？画面填满？）
□ 配乐有正版授权（Artlist/Epidemic Sound）
□ 无未授权真人面部
□ 标注 AI 生成内容（如需）
□ 已导出所有平台规格版本
```

---

## 月费汇总

| 工具 | 路线 1 | 路线 2 | 路线 3 |
|------|--------|--------|--------|
| Luma Agents | $100-300 | — | — |
| Higgsfield | — | ~$100 | — |
| Runway Unlimited | — | — | $76 |
| Seedance/即梦 | — | — | $42 |
| Veo 3.1 按需 | — | — | ~$30 |
| MidJourney | — | — | $30 |
| ElevenLabs | — | $99 | $99 |
| CapCut Pro | $20 | $20 | $20 |
| Artlist | $17 | $17 | $17 |
| **合计** | **$137-337** | **~$236** | **~$314** |

---

## 我该选哪条？

| 你的情况 | 选这条 |
|---------|--------|
| "我现在立刻要出一条广告，越快越好" | **路线 1 Luma Agents** |
| "我每天要出 5-10 条，需要稳定产出" | **路线 2 Higgsfield** |
| "客户要求电影级品质，时间不是问题" | **路线 3 Frankenstein** |
| "我想先免费试试效果" | Luma/Higgsfield 免费层 + [CapCut](https://capcut.com) |
