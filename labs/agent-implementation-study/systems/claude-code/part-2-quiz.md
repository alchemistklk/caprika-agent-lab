# Part 2 Quiz: Transcript, Session Recovery, and Effective Context

> 研究对象：本地 Claude Code 源码快照
> 证据边界：该快照尚未被证明与本机 Claude Code `2.1.224` 完全对应。
> 目的：检验能否脱离笔记重新推导机制，而不是检验是否记住某段表述。

## 作答方法

测验分两轮完成：

1. **闭卷轮**：不查看笔记或源码，完成 A、B、D；
2. **源码轮**：允许查看源码，完成 C，并为每个答案记录文件、符号和关键行号。

不要在第一次作答前生成或查看标准答案。每题先写“我的推导”，校准后再补充“源码证据”
和“需要修正的心智模型”。

```text
我的推导：

源码证据：

需要修正的心智模型：
```

## 评分结构

| 部分 | 题量 | 分值 |
|---|---:|---:|
| A. 主动回忆 | 6 | 12 |
| B. 案例推导 | 4 | 16 |
| C. 源码定位 | 4 | 12 |
| D. 跨实现迁移 | 1 | 10 |
| **总计** | **15** | **50** |

建议通过线为 40 分。分数不是最终目的；低于满分的题目应按“术语、生命周期、数据
视图、异常路径、跨实现迁移”分类，并在 24 小时后只重做错题。

## A. 主动回忆（每题 2 分）

### A1

为什么不能把 Transcript JSONL 按文件行顺序直接转换为模型输入？至少说出三个原因。

### A2

分别解释 `uuid`、`parentUuid`、`sessionId` 的作用。它们各自回答的是哪一个身份或
关系问题？

### A3

什么是 Leaf？为什么同一个 Transcript 中可能同时存在多个 Leaf？

### A4

用“不变量发生了什么变化”的方式比较 Resume、Rewind 和 Fork Session。至少比较：
进程、Session ID、Transcript 文件和当前分支。

### A5

分别定义持久化视图、运行时视图和模型视图。为什么“本地仍然保存”不能推出“模型
本次仍然看见”？

### A6

Tool Result Content Replacement 和 Context Collapse 都会缩小模型上下文。它们替换的
对象、触发时机、持久化记录和主要目的分别有什么不同？

## B. 案例推导（每题 4 分）

### B1：Leaf 与 Sidechain

给定以下消息图：

```text
A
├── B
│   └── C  timestamp=10:00, isSidechain=false
└── D
    ├── E  timestamp=10:05, isSidechain=true
    └── F  timestamp=10:03, isSidechain=false
```

假设 `C`、`E`、`F` 都被识别为 Leaf：

1. 从 JSONL 路径恢复主会话时，默认应选择哪个 Tip？
2. 恢复出的正序消息链是什么？
3. 为什么不能只选择时间最新的 `E`？
4. 如果 `F` 的 `parentUuid` 指向不存在的消息，会暴露什么恢复风险？

### B2：Resume、Rewind 与 Fork

当前 Session 为 `S1`，Transcript 为 `S1.jsonl`，当前分支为
`M1 → M2 → M3 → M4 → M5`。

分别推导以下操作后的 Session ID、Transcript 和分支拓扑：

1. 进程退出后执行 Resume；
2. Rewind 到 `M3`，然后产生 `M4' → M5'`；
3. 从 `M3` Fork Session，并在新 Session 中继续。
指出哪些历史仍保留，哪些只是退出当前有效链，而不是被物理删除。

### B3：并行工具的技术分叉

同一次 Provider Assistant Response 产生两个 `tool_use`：

```text
provider message.id = response-123

Assistant Block aa, uuid=aa, tool_use.id=tool-A
Assistant Block ab, uuid=ab, tool_use.id=tool-B
Tool Result ra, parentUuid=aa, tool_use_id=tool-A
Tool Result rb, parentUuid=ab, tool_use_id=tool-B
```

回答：

1. 为什么只沿其中一个 Leaf 的 `parentUuid` 回溯可能遗漏另一侧？

2. 哪些 ID 表示“同一次 Provider Response”，哪些 ID 表示具体 Tool Call？

3. 恢复后的模型协议视图应该是什么形状？

4. 如果 `rb` 缺失，不能仅靠正常路径结论保证什么？
### B4：上下文缩减时序

第 N 轮产生三个 Tool Result：90K、80K、70K 字符。下一轮开始时，当前快照的聚合
预算假设为 200K。较早历史 `M1...M6` 同时已满足 Context Collapse 条件，`M7` 是近期
关键消息。

请按顺序推导：

1. 完整 Tool Result 何时进入 Agent State？

2. Tool Result Budget 何时处理聚合超限？

3. History Snip、Microcompact、Context Collapse、Auto Compact 的相对顺序是什么？

4. 模型请求可能看到什么，而本地持久化视图仍保留什么？

5. 为什么不能把 200K 当成稳定的公开契约？
## C. 源码定位（每题 3 分）

每题必须记录：绝对或仓库相对文件路径、符号名、关键行号，以及不超过五行的核心
逻辑摘要。只写文件名不给分。

### C1：Transcript 读取与 Leaf 计算

定位负责读取 JSONL、分类消息与辅助记录、建立 UUID Map，并计算 Leaf UUID 的实现。
说明大型 Transcript 在读取阶段可能进行的预边界优化为什么不等于删除原文件。

### C2：对话链恢复与 Resume

定位：

1. Leaf 到 Root 的 `parentUuid` 回溯；
2. JSONL 路径恢复时的 Tip 选择；
3. Resume 后的 Skill 状态恢复、中断检测和 Session Start Hook 注入。

把三个符号串成一条调用与数据转换链。

### C3：Tool Result Budget 与 Context Pipeline

从 `queryLoop()` 出发，定位并记录以下顺序对应的调用点：

```text
Compact Boundary
→ Tool Result Budget
→ History Snip
→ Microcompact
→ Context Collapse
→ Auto Compact
→ deps.callModel()
```

说明哪一步主要改变模型视图，哪类记录还可能在本地持久化层保留。

### C4：并行工具恢复

定位 `recoverOrphanedParallelToolResults()`，说明它如何利用 Provider Message ID、
Assistant UUID 和 Tool Use ID 补回普通单父节点回溯遗漏的消息。列出至少两个仍需测试
验证的异常情况。

## D. 跨实现迁移（10 分）

你开始研究另一个 Coding Agent，但没有找到 `parentUuid`、`buildConversationChain()` 或
JSONL。请设计一套与具体符号无关的源码调查顺序，用来回答：

> 这个 Agent 如何保存会话、表示当前分支、恢复执行状态，并把历史转换成模型上下文？

答案必须覆盖：

1. 持久化单位与写入时机；
2. 消息身份、顺序或父子关系；
3. 当前 Tip、Cursor 或等价状态；
4. 分支、Fork 和 Subagent 隔离；
5. Resume 和异常恢复；
6. Context Reduction；
7. 最终 Provider Request；
8. 可以支持结论的 Source、Test、Trace 或 Runtime Evidence。

不能只回答“搜索类似变量名”。应描述即使实现采用数组、事件日志、数据库或状态机，也
能继续追踪的结构性问题。

## 完成记录

```text
第一次闭卷日期：
第一次得分：
主要错题类型：

24 小时复测日期：
复测得分：

跨 Agent 迁移对象：
迁移后需要修正的 Claude Code 心智模型：
```
