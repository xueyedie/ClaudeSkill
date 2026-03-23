---
name: opencli-bridge
user-invocable: true
description: >
  用于在本机通过 opencli 访问已登录网站、ChatGPT 桌面应用和结构化搜索结果。
  当用户希望读取 Chrome 已登录内容、控制 ChatGPT、或希望以更省夏夏 token 的方式搜索信息时使用。
  触发词：opencli、已登录网站、Chrome 登录态、ChatGPT 桌面版、站内搜索、复用登录态、低 token 搜索。
---

# OpenCLI Bridge Skill

这个 skill 用来把 `opencli` 当作“低 token 成本的信息读取和桌面应用控制层”。

## 两类任务

这个 skill 只处理两种完全不同的任务，执行时必须先分流，不要混用：

1. 浏览器 / 已登录站点任务
2. ChatGPT 桌面应用任务

如果当前任务属于其中一类，就只遵循对应分区的规则，不要把另一类的规则混进来。

## 何时使用

- 用户要查看自己已经登录的网站内容
- 用户要读取站内搜索结果，而不是做通用互联网检索
- 用户要控制 `ChatGPT` 桌面应用
- 用户明确说要“省 token”“少走网页搜索”“优先复用登录态”
- 用户提到“用 ChatGPT 处理一下”“发给 ChatGPT”“让 ChatGPT 改写/回答/分析”

## 总分流规则

1. 先判断这是“浏览器 / 已登录站点任务”还是“ChatGPT 桌面应用任务”
2. 浏览器类任务：走下面的“浏览器 / 已登录站点任务规则”
3. ChatGPT 类任务：走下面的“ChatGPT 桌面应用任务规则”
4. 不要在同一轮里把浏览器读取规则和 ChatGPT 控制规则混成一套状态机

## 浏览器 / 已登录站点任务规则

- 优先让 `opencli` 输出 `json`
- 优先读取最终结果，不做不必要的中间解释
- 不要把原始长文本整段复制进上下文，除非用户明确要求
- 如果是搜索类任务，先尝试 `opencli`，不要先用通用 web search
- 如果是站内内容读取，优先复用用户当前 Chrome 登录态
- 浏览器任务只关注“站点读取 / 站内搜索 / 登录态内容 / 结构化结果”，不要引入 ChatGPT 的等待、补读、线程管理规则
- 浏览器任务失败后，才考虑回退到 `web_fetch`、托管浏览器或其他抓取方式

### 浏览器任务常见命令

```bash
opencli list
opencli doctor --live
opencli <adapter> <subcommand> -f json
```

### B站关注分组约定

- 如果用户提到“B站 AI 分组”“我的关注分组”“分组里的博主”，优先把它当成 `opencli` 可直接处理的场景。
- 推荐顺序：
  - `opencli bilibili following --list-groups -f json`
  - `opencli bilibili following --group "AI" -f json`
  - 如果用户给的是分组 ID，则使用 `opencli bilibili following --group-id <tagid> -f json`
- 不要再默认认为 `opencli bilibili following` 只能读取整个关注列表。
- 只有在分组命令失败或目标数据不在分组 API 里时，才回退到托管浏览器页面操作。

### 浏览器任务失败时如何降级

- 若 `opencli` 不存在：明确说明未安装，并切换到传统抓取方案
- 若目标适配器不存在：说明平台未适配，再改用其他工具
- 若命令失败：先做一次最小重试，再决定是否回退
- 若用户只要一个快速结论：优先基于已有结构化结果给结论，不额外扩大抓取范围

## ChatGPT 桌面应用任务规则

- ChatGPT 相关任务，默认优先使用 `opencli chatgpt` 驱动本机 `ChatGPT.app`，不要先打开 `chatgpt.com`
- 如果 `ChatGPT.app` 当前未运行，优先先启动 app，再执行 `opencli chatgpt` 命令
- 只有用户明确要求网页版，或 `opencli chatgpt` 连续失败时，才允许回退到浏览器版 ChatGPT
- `opencli chatgpt` 走的是桌面 App 自动化，不依赖 Browser Bridge 扩展；不要把 `opencli doctor` 里的扩展/daemon 结果当成 ChatGPT.app 失败的原因
- 对 ChatGPT，默认优先使用单入口：`opencli chatgpt ask --fresh true --timeout 600 "..."`
- 如果是在同一个 ChatGPT 线程里继续追问，不要再 `new`，而是继续 `opencli chatgpt ask --timeout 600 "..."`
- 不要默认让模型自己发明复杂状态机；优先保持 ask 单入口
- `opencli chatgpt new / send / read` 主要用于排障，不是默认主路径
- 任何 `ChatGPT` 相关操作前，先执行一次 `opencli chatgpt state -f json`。
- 外部在任何需要判断状态的时候，都只基于 `State` 主状态决策。
- `opencli chatgpt state -f json` 的主状态只有 6 个：
  - `State=stopped`：ChatGPT.app 未运行，或当前没有可继续使用的会话；允许启动 app 或 fresh 新开一个对话窗口
  - `State=idle`：当前线程是空白可发送态；允许首问，或 `--fresh true` 新开
  - `State=draft`：输入框里已有未发送草稿；禁止 `ask/new`，必须先处理草稿
  - `State=generating`：上一条已经发出，正在生成；禁止 `ask/new`，只允许继续等待、`read` 或 `poll`
  - `State=success`：`opencli` 已确认上一轮生成收口，且当前线程有稳定可见回复；只有在这个状态下才允许继续同线程 `ask`
  - `State=error`：内部自动化异常、窗口不可读或状态无法可靠判断；禁止正常发送，先恢复或报错
- 如果 `ask` 返回 `Prompt delivery succeeded, but no stable visible reply appeared within ...`，必须理解为“消息已送达，但复杂回答还没稳定出现”，这不算失败
- 上述情况下，必须继续留在同一个 ChatGPT 线程里，自动补 `opencli chatgpt read --wait 20 --exclude "原问题"` 1 到 2 轮；只有补读仍然拿不到正式回复，才允许汇报超时或切备用方案
- 对复杂研究、搜索、资料整理、带链接汇总这类任务，不要把 `ask --timeout 600` 的超时本身当作失败，而要把它理解为“进入补读阶段”
- 外层调用 `ask` 时，也必须让命令本身或后续 `process poll` 等到 10 分钟以上，不能在 30 秒、60 秒或 5 分钟时就改判失败
- 如果用户明确要求“持续对话探索”或“你和 ChatGPT 多轮聊完再给我结论”，必须在同一个 ChatGPT 线程里继续追问，不要拿第一轮阶段性结果就提前结束
- 上一轮仍在生成中时，只允许继续在同一个线程里等待、`read` 或 `poll`；不要因为“内容没读完”就继续追问。
- 如果已经存在一个运行中的 `opencli chatgpt ask` session，不要再启动第二个 ask。必须先等待当前 ask 完成、明确失败，或主人要求中断后再重开。
- 如果已经存在一个运行中的 `opencli chatgpt ask` session，默认也不要并行再起独立的 `opencli chatgpt read` 去插队；优先继续 `process poll` 同一个 ask。只有 ask 已经结束并明确进入补读阶段，才允许单独 `read`。
- 原始 ask 仍在运行时，不要因为一次 `process log` 看到瞬时 AppleScript / AX 错误，就立即 fresh 新开第二个 ask 或切到 browser / web_fetch fallback。先继续等待原 ask，直到它明确结束、明确失败，或超过既定等待窗口。
- 如果追问文本已经进入输入框但没有真正发送出去，要明确判定为“追问未发送”，而不是“ChatGPT 没回复”。
- 对复杂问题，只有在 `ask` 已确认送达、`600` 秒等待已结束、同线程补 `read` 1 到 2 轮后仍无正式正文时，才允许改走 fallback
- 如果后续追问没有真正发进对话区，或者还停留在输入框里，这应被视为发送失败，而不是成功
- 如果 `send` 连续失败两次，不要立刻改用 `ask` 在同一轮继续折腾前台窗口；先尝试恢复窗口/重开会话，或者明确切到备用方案

### ChatGPT 任务常见命令

```bash
opencli chatgpt status
opencli chatgpt state -f json
opencli chatgpt ask --fresh true --timeout 600 "..."
opencli chatgpt ask --timeout 600 "..."
```

### ChatGPT ask 何时算完成

- 这里的“完成”必须优先对齐 `opencli chatgpt ask` 的代码判定，不要靠内容语义猜测。
- `ask` 只有在同时满足下面两类条件时，才算这一轮完成：
  - 送达条件：prompt 已确认进入可见对话区
  - 结束条件：`opencli` 已观察到当前线程从生成态收口；如果在外部读取状态，应以 `opencli chatgpt state -f json` 返回 `State=success` 为准
- 在上述结束条件成立后，`opencli` 会做结束态扫描；只有当结束态扫描拿到稳定正文并成功返回时，这一轮才算完成。
- 如果用户要求“持续对话探索”或“继续追问”，那么单轮 `ask` 完成只表示“当前这一问已经按 `opencli` 的结束态规则收口”；整个多轮任务是否完成，还要看用户目标是否已经满足。

### ChatGPT ask 何时明确失败

- `ask` 明确返回“消息没有进入可见对话区”“prompt 仍停留在输入框里”“composer 无法接收内容”这类结果时，属于送达失败，这一轮算失败。
- `ask` 已确认送达，但直到 `600` 秒主等待结束，`opencli` 仍然没有把当前线程收口到 `State=success`。只有这种情况持续到主等待结束且后续补读阶段也没有成功收口，这一轮才算明确失败。
- `ask` 已确认送达，当前线程也已经回到 `State=success`，但结束态扫描仍然拿不到稳定正文，且后续同线程补 `read` 1 到 2 轮后仍无正式正文，这一轮才算明确失败。
- 如果已有运行中的 ask，但窗口/AX 瞬时异常只发生在一次 `process log`、某次轮询或某次补读里，这不算明确失败；必须优先继续等原 ask 结束。
- 如果上一轮仍在生成中，后续追问只停留在输入框里没发出去，这应判定为“追问未发送失败”，不是上一轮 ask 失败。
- 只有在明确失败后，才允许 fresh 新开对话或切到 browser / `web_fetch` fallback。

### ChatGPT ask 不算失败的情况

- `Prompt delivery succeeded, but no stable visible reply appeared within ...`
- prompt 已确认送达，但 `opencli chatgpt state -f json` 返回 `State=generating`
- 原 ask 仍在运行中，只是暂时还没等到 `opencli chatgpt state -f json` 返回 `State=success`
- 某次单独 `read`、`process log`、瞬时 AX/AppleScript 错误，但原 ask 还没结束
