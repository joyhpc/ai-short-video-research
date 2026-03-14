# 第 3 步：AI 视频画面生成

## 这一阶段的意义
**它是将文字转化为画面的核心执行步骤。**
在这个阶段，我们会拿着第 2 步（脚本撰写）中生成的“纯英文画面描述（Prompt）”，分段输入给像 Runway Gen-4.5 这样的 AI 工具。这就好比你作为一个导演，拿着分镜头脚本去指挥摄影师（AI）开机拍摄。

---

## 你的执行动作指令与 Prompt

对于脚本中的每一个镜头，你需要执行以下操作：

### Step A：首帧参考图生成（使用 Midjourney / DALL-E 3）
AI 视频工具直接“文生视频”容易不可控，最佳实践是先生成一张绝佳的图片。
> **Prompt 示例（复制脚本中的【画面】描述）：**
> `Extreme close-up shot of a thick, heavy string stretched to its absolute breaking point, fraying slightly. Cold, harsh cinematic blue lighting with sharp shadows. Shallow depth of field. The camera shakes slightly, conveying intense tension and stress. High contrast. --ar 16:9`

### Step B：图像生视频（使用 Runway Gen-4.5）
将 Step A 生成的最满意的一张图片传给 Runway，然后加上运动指令。
> **Prompt 示例：**
> `The stretched string suddenly goes completely slack and beautifully falls. Slow motion. The harsh blue light instantly transitions into a warm, glowing amber light.`
> **工具操作**：
> - 可以在 Runway 中使用 **Motion Brush（运动笔刷）**，涂抹绳子，让它往下掉。
> - 涂抹背景，锁定灯光的变化感。

### 阶段输出：
5 个（根据脚本）毫无关联但绝美的无声短片段（MP4）。