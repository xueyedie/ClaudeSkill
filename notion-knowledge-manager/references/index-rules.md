# Knowledge Index 规则

## 一、定位

`Knowledge Index` 是内容层的结构化索引，不是工作区里所有页面的总清单。

它的职责是：

- 给内容对象建立稳定的索引
- 让用户和 AI 能更快定位、判断、更新知识
- 追踪来源、关系和维护状态

## 二、什么应该进入索引表

通常应该进入索引表的对象包括：

- 内容层的主题页
- canonical 手册页
- 重要的 guide
- 应该被发现和复用的 diagram
- case
- 需要被追踪的 source 页面

## 三、什么不应该进入索引表

默认不要把以下对象作为普通内容条目纳入索引表：

- `Knowledge Hub`
- `Knowledge Index`
- `Inbox`
- `Index Archive`

这些对象属于管理层基础设施。

只有当用户明确要求“把系统页也当作内容页管理”时，才例外处理。

## 四、各字段的意图

### `Domain`

顶层分类。

当前推荐值：

- `AI`
- `游戏`

### `Parent Topic`

上一级专题归属。

示例：

- `OpenClaw`
- `SLG游戏拆解`
- `后续游戏创意`

### `Topic`

更细一级的语义主题。

### `Type`

内容形态。

示例：

- `handbook`
- `guide`
- `diagram`
- `case`
- `source`
- `note`

### `Canonical`

是否为该主题的正式主页面。

### `Confidence`

成熟度和可信度信号。

### `Source Type`

来源加工方式：

- `original`
- `curated`
- `synthesized`

### `Source Pages`

来源页面集合。

### `Related Pages`

相关页面集合。

### `Review Cycle`

维护频率。

### `Last Reviewed`

最近一次确认其有效性的时间。

### `URL`

索引回跳到原始页面的链接。

## 五、填写索引时的决策顺序

当需要新增或更新一行索引时，按这个顺序判断：

1. 先确定 `Domain`
2. 再确定 `Parent Topic`
3. 再判断它是不是一个独立主题
4. 能复用已有 canonical 页面时优先复用
5. 只有主题明显独立时才新建 canonical 条目
6. `Related Pages` 保持有用但不要过度堆积
7. 不要把管理层页面误记成内容层条目
