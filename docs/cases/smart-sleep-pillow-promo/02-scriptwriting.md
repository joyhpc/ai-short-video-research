# 第 2 步：脚本撰写 (Scriptwriting)

## 脚本撰写阶段的意义与输出用途
**脚本撰写是将“抽象策略”转化为“具象蓝图”的阶段。**
1. **生成施工图**：AI 视频生成工具（如 Runway、Sora、Veo）看不懂“极致爽感”、“高级生活方式”这种抽象的策划词汇。它们需要的是：“特写镜头（Close-up shot）”、“暖色调侧光（Warm side lighting）”、“慢动作推镜头（Slow dolly-in）”等具体的画面参数。
2. **承上启下**：这一步直接使用了**第 1 步策划**的输出作为输入。它产出的成果（特别是精准的英文画面描述 `prompt`），将直接复制粘贴给下一步的 AI 视频生成器和配音工具使用。

---

### 给 AI 生成脚本的 Prompt（基于第一步的方向一）

我们现在将第一步中决定的**【方向一：极致物理爽感】**喂给 AI，让它生成最终的脚本：

```markdown
基于以下创意方向，写一个 30 秒的商业广告视频脚本。

创意方向：【感官解构】极致物理爽感的具象化（强调 1-50Hz 振波穿透肌肉的酥麻解压感）
品牌/产品：智能减压枕头（纯 VCM 物理体感）
视觉风格：微距/特写为主，冷色调向温暖琥珀色渐变，极速压抑到极慢舒缓。

脚本要求：
1. 严格按照以下结构输出，包含精确到秒的时间码：
   [00:00-00:03] Hook — 画面描述 | 旁白文案 | 音效/配乐提示
   [00:03-00:08] Build — 同上
   [00:08-00:23] Body — 同上（可分多个子场景）
   [00:23-00:30] CTA — 同上

2. 每个场景包含：
   - 【镜头】：镜头类型
   - 【画面】：详细的英文视觉描述（用于 AI 视频生成，Runway Gen-4.5，60-80 words）
   - 【旁白】：中文旁白文案
   - 【音效】：配乐/音效提示
   - 【情感】：该场景的情感基调

3. 画面描述必须是英文，用电影化语言，包含：
   - 具体的视觉元素和构图
   - 光照方向和色温
   - 镜头运动
   - 景深和焦点
```

---

### 生成的最终分镜头脚本参考（你的生产蓝图）

**[00:00-00:03] Hook：紧绷的临界点**
- **【镜头】**：极度特写 (Extreme Close-up)
- **【画面】**：`Extreme close-up shot of a thick, heavy string stretched to its absolute breaking point, fraying slightly. Cold, harsh cinematic blue lighting with sharp shadows. Shallow depth of field. The camera shakes slightly, conveying intense tension and stress. High contrast.`
- **【旁白】**：每天的大脑，就像这根弦？直到……
- **【音效】**：极度刺耳的、不断升调的低频嗡嗡声（代表高压）。
- **【情感】**：压抑、焦虑、共鸣。

**[00:03-00:08] Build：释放的瞬间**
- **【镜头】**：慢动作推镜头 (Slow Dolly-in)
- **【画面】**：`Slow-motion dolly-in shot. The stretched string suddenly goes completely slack and gracefully falls into a soft, luxurious memory foam surface. The harsh blue light instantly transitions into a warm, glowing amber light. Beautiful bokeh, extremely satisfying and calming visual.`
- **【旁白】**：触碰它的瞬间，一切开始瓦解。
- **【音效】**：一声深沉有力的“嗡”（Bass drop），随之刺耳声彻底消失，切入空灵舒缓的氛围音（Ambient pad）。
- **【情感】**：如释重负、瞬间解脱。

**[00:08-00:15] Body 1：物理振波的可视化**
- **【镜头】**：微距平移 (Macro Panning)
- **【画面】**：`Macro shot of a smooth liquid surface or fine kinetic sand. Gentle, perfect concentric rhythmic ripples (1-50Hz frequency visualization) spreading smoothly across the surface. Warm golden hour side lighting highlighting the textures. Slow, mesmerizing panning movement. Cinematic and elegant.`
- **【旁白】**：纯净的 50 赫兹低频振波，直接穿透紧绷的肌肉。
- **【音效】**：低沉、带有节奏感的 ASMR 级别酥麻低音震动声（Sub-bass pulse）。
- **【情感】**：深度的感官愉悦、沉浸。

**[00:15-00:23] Body 2：人物沉浸状态**
- **【镜头】**：中景，缓慢推镜头 (Medium shot, slow push-in)
- **【画面】**：`Medium shot of a professional man in his 30s lying comfortably on a sleek, high-end pillow in a dimly lit, luxurious bedroom. His facial expression is deeply relaxed, eyes closed, tension completely gone from his jaw and shoulders. Soft cinematic ambient lighting. Slow push-in.`
- **【旁白】**：这不是睡眠，这是一场头等舱级别的感官 SPA。
- **【音效】**：轻柔的呼吸声，配乐变得开阔且温暖。
- **【情感】**：奢华、享受、高级感。

**[00:23-00:30] CTA：产品定格与转化**
- **【镜头】**：产品特写与留白 (Product shot, static)
- **【画面】**：`Elegant product shot of a minimalist smart pillow on a premium dark gray bedsheet. Soft moody lighting. A subtle golden glow emanates from the edge of the pillow. Perfect studio composition, text space on the left. Highly professional commercial look.`
- **【旁白】**：全新智能减压枕。你的私人沉浸舱。
- **【音效】**：干净利落的产品出场音（Soft impact/whoosh）。
- **【情感】**：品质感、值得拥有。