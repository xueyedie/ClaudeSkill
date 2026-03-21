---
name: nano-banana-pro
description: 通过 Gemini 3 Pro Image（Nano Banana Pro）生成或编辑图片。Generate or edit images via Gemini 3 Pro Image.
homepage: https://ai.google.dev/
metadata:
  {
    "openclaw":
      {
        "emoji": "🍌",
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"] },
        "primaryEnv": "GEMINI_API_KEY",
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Nano Banana Pro (Gemini 3 Pro Image)

使用内置脚本生成或编辑图片。

发送图片

- 在聊天渠道里，生成完成后优先显式使用 `message` 工具发送图片，不要只依赖脚本输出的 `MEDIA:` 行。
- 推荐流程：先运行脚本生成图片，再用 `message.send` 把保存后的本地图片路径作为 `media` 发回当前用户或当前群。
- 给钉钉发图时，这种显式发送方式比只输出 `MEDIA:` 更稳。
- 回复文字里只需要简短说明图片已发送，不要再把图片内容读回文本。
- 如果当前任务就是“生成后立刻发回聊天”，优先使用 `generate_and_send.py`，不要拆成两步。

模型选择

- 默认值：`nano-banana-pro`（映射到 `gemini-3-pro-image-preview`）
- `nano-banana-2` / `nano-banana-pro2`（兼容别名）会映射到 `gemini-3.1-flash-image-preview`
- 如果要切换模型，传入 `--model`
- 也可以在 `~/.openclaw/openclaw.json` 中设置 `skills."nano-banana-pro".env.NANO_BANANA_MODEL`

生成图片

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "your image description" --filename "output.png" --resolution 1K
```

生成并发送回聊天

```bash
uv run {baseDir}/scripts/generate_and_send.py --prompt "white cartoon cat looking at a screen" --filename "output.png" --target "user:1112014757-2075222354" --caption "画好啦"
```

钉钉群里可把 `--target` 设为当前 `conversationId`；私聊里可使用当前用户 id。脚本也兼容 `user:<id>` / `group:<id>` 这种写法，并会自动转换成 CLI 可接受的目标格式。

编辑图片（单张）

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "edit instructions" --filename "output.png" -i "/path/in.png" --resolution 2K
```

多图合成（最多 14 张）

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "combine these into one scene" --filename "output.png" -i img1.png -i img2.png -i img3.png
```

API Key

- `GEMINI_API_KEY` env var
- 或者在 `~/.openclaw/openclaw.json` 中设置 `skills."nano-banana-pro".apiKey` / `skills."nano-banana-pro".env.GEMINI_API_KEY`

指定宽高比（可选）

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "portrait photo" --filename "output.png" --aspect-ratio 9:16
```

切换到 `Nano Banana 2`

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "portrait photo" --filename "output.png" --model nano-banana-2
```

或者直接使用 Google AI Studio 页面显示的官方模型名

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "portrait photo" --filename "output.png" --model gemini-3.1-flash-image-preview
```

说明

- 分辨率支持：`1K`（默认）、`2K`、`4K`；切到 `gemini-3.1-flash-image-preview` 后还支持 `512`。
- 宽高比支持：`1:1`、`1:4`、`1:8`、`2:3`、`3:2`、`3:4`、`4:1`、`4:3`、`4:5`、`5:4`、`8:1`、`9:16`、`16:9`、`21:9`。如果不传 `--aspect-ratio` / `-a`，则由模型自行决定，适合在头像、个人资料图或批量生成需要统一比例时显式指定。
- `nano-banana-pro`、`nano-banana-2`、`nano-banana-pro2` 都会保留为友好的别名；未知的 `--model` 值会直接透传给 Gemini API。
- 文件名建议带时间戳：`yyyy-mm-dd-hh-mm-ss-name.png`。
- 脚本会打印一行 `MEDIA:`。这可以作为附件线索，但在钉钉等聊天渠道里，优先显式调用 `message` 工具发送生成后的本地图片路径。
- 不要再把图片读回内容里，只需要报告保存路径即可。
