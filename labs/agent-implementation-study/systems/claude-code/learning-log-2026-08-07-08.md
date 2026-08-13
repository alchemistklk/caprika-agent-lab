# Claude Code Agent Loop 学习记录：问题、当前记忆模型与待验证边界

> 学习日期：2026-08-07 至 2026-08-08
> 研究对象：本地 Claude Code 源码快照
> 证据限制：该源码快照尚未被证明与本机 Claude Code `2.1.224`
> 完全对应。本文记录的是当前学习理解，不是最终或跨版本实现声明。

## 这份记录如何使用

本文刻意保留两类内容：

1. **我提出的问题**：这些问题代表我当前知识结构中不熟悉、容易混淆或需要继续建立直觉的部分。
2. **我主动复述的结论**：这些是我目前真正记住的心智模型，但不保证百分之百正确。后续源码研究、运行时验证和跨 Agent 对比可以继续修正它们。

因此，本文不是考试答案，也不是把所有暂定说法包装成定论。它是一张可持续修订的学习地图。

## 当前完整心智模型

```text
query()
  -> 将运行委托给 queryLoop()
  -> 转发运行中的消息
  -> 接收 Terminal 并完成外围收尾

queryLoop()
  -> while (true)
  -> 构造有效上下文、System Prompt 和工具定义
  -> 调用模型并消费流式响应
  -> 从响应中识别 text / thinking / tool_use
  -> 执行工具并生成 tool_result
  -> 构造 next State
  -> 继续下一轮或返回 Terminal

单次 LLM Attempt
  -> 拥有自己的消息集合和 StreamingToolExecutor
  -> Streaming 失败时取消该底层请求
  -> 清理网络资源、Timer 和局部消息状态
  -> 通过 Tombstone 作废已经形成的旧消息
  -> 丢弃旧 Executor 的结果
  -> 可以重新发起 Non-streaming 请求，让 Agent Turn 继续
```

## 我主动复述并记住的结论

以下内容优先保留我的理解方式。每条结论都视为“当前记忆模型”，允许以后校准。

### 结论 1：Agent Loop 的基本循环

**我的当前记忆模型：**

> 通过 `while (true)`，我们把有效上下文、系统提示词和工具定义传给模型，查看模型返回的结构化结果，判断是否需要工具调用，以及是否需要进入下一轮。

**当前源码校准：**

- 模型响应是流式结构化事件，不是一次性返回的完整对象。
- 最常见的继续原因是 `tool_use`，但 Hook、Token Budget、输出恢复、上下文压缩和新通知也可能要求继续。
- 模型表达意图，Runtime 最终决定工具执行、权限、恢复、继续和终止。

### 结论 2：入口委托与真正消费位置

**我的当前记忆模型：**

> 我们已经看了两个部分：一个是入口委托和返回结果，另一个是 Agent Loop 如何消费上下文和模型返回。

**当前源码校准：**

- `query()` 负责入口委托、流式输出转发、`Terminal` 接收和外围命令生命周期收尾。
- `queryLoop()` 才负责组装上下文、调用模型、消费响应、执行工具和更新状态。
- `query()` 本身不是把全部命令直接送给模型的主要位置。

### 结论 3：完整对话与有效上下文不同

**我的当前记忆模型：**

> Claude Code 本地可以保存完整或较完整的对话记录，但每次模型调用使用的是经过选择、裁剪或压缩的有效上下文。

**当前源码校准：**

```text
本地 JSONL Transcript
  -> 当前内存消息链
  -> Compact / Snip / Collapse / Tool Result Budget
  -> messagesForQuery
  -> 模型请求
```

这条转换链仍是当前学习切片唯一保留的深入 TODO。

### 结论 4：一个模型 Stream，派生两种表示

**我的当前记忆模型：**

> `stream_event` 是即时消费并展示给用户的信息；`AssistantMessage` 是把多个流式事件累积后组装出来、供 Agent Loop 和工具调用消费的消息。

**当前源码校准：**

- 网络层只有一个模型 Stream，只被 `for await` 消费一次。
- 每个原始事件可以被包装成 `StreamEvent`，用于实时 UI。
- 多个 Delta 累积到 `content_block_stop` 后形成完整的
  `AssistantMessage`。
- `AssistantMessage` 更接近 Content Block 级的语义消息，不一定代表整个模型请求已经结束。

### 结论 5：Watchdog 检查的是流空闲，不是总耗时

**我的当前记忆模型：**

> 如果 Watchdog 已启用，并且超过默认90秒没有任何 Stream Event，当前 Stream 会被取消；模型处理超过两分钟本身不一定有问题，只要持续有事件进入客户端。

**当前源码校准：**

- 输入很大、还在等待 Response Headers 时，Streaming Watchdog 尚未开始工作。
- Response Headers 已经返回但长时间没有事件时，Idle Watchdog 才负责主动取消。
- 30秒 Stall Detection 主要记录停顿；它不是主动取消机制。
- 默认90秒只在 Watchdog 功能启用时生效。

### 结论 6：取消底层 Stream，不等于取消整个 Agent Turn

**我的当前记忆模型：**

> 当前 Streaming 请求被取消后，Claude Code会清理旧 Streaming 资源，并可能降级到 Non-streaming 路径；第一次请求已经取消，但这次 Agent Turn 仍然可以继续。

**当前源码校准：**

```text
取消第一次 Streaming HTTP 请求
  -> Abort Stream Controller
  -> Cancel Response Body
  -> 清理 Timer 和本地引用
  -> 作废失败 Attempt 的消息与结果
  -> 重新发起 Non-streaming 请求
  -> Agent Turn 继续
```

客户端可以保证自己停止读取，但不能仅根据客户端源码证明远端推理立即停止或停止计费。

### 结论 7：失败内容通过请求作用域和 ID 识别

**我的当前记忆模型：**

> Claude Code不是按照时间猜测哪些内容属于失败 Stream，而是通过当前 LLM Attempt 的局部消息、工具集合和 Executor 确定归属，再通过 Message UUID、Tool Use ID 和 Tool Result ID 精确处理。

**当前源码校准：**

```text
LLM Attempt A
├── assistantMessages
├── toolUseBlocks
├── toolResults
└── StreamingToolExecutor A
```

主要关联身份包括：

- `AssistantMessage.uuid`
- `requestId`
- `tool_use.id`
- `tool_result.tool_use_id`
- `sourceToolAssistantUUID`

### 结论 8：Tombstone 是补偿事件

**我的当前记忆模型：**

> 已经生成并展示的旧 Assistant 消息会通过 Tombstone 作废。消费 Tombstone 的 UI 和本地 Transcript 会删除对应消息。

**当前源码校准：**

- 原消息没有被原地改成 Tombstone。
- Runtime 额外发送 `{ type: 'tombstone', message }`。
- UI 通过目标消息对象将其移除。
- Transcript 通过 `message.uuid` 尝试删除对应 JSONL 行。
- 已经被用户看到、复制或被外部 SDK 保存的信息不能真正“时间倒流”；下游必须实现 Tombstone 语义。

### 结论 9：每个 LLM Attempt 拥有独立 Executor

**我的当前记忆模型：**

> 给每次 LLM 调用尝试分配一个独立 Executor 是一个新的、值得复用的设计。失败时可以整体作废旧执行域，不让新旧工具调用和结果串线。

**当前源码校准：**

```text
Attempt A -> Executor A
Fallback  -> Executor A discarded
Attempt B -> Executor B
下一轮    -> Executor C
```

这个设计提供：

- 清晰的所有权边界；
- Attempt 级消息和工具隔离；
- 简化的并发与结果管理；
- 更安全的重试和 fallback；
- 避免旧 Tool Use ID 污染新请求。

### 结论 10：能够定位工具，不代表能够回滚副作用

**我的当前记忆模型：**

> Assistant Message、Tool Use 和 Tool Result 之间存在直接 ID 映射，因此可以找到具体工具调用、结果和待执行任务；但能找到不等于能撤销已经发生的外部副作用。

**当前源码校准：**

```text
Invalidate
  -> 让消息和结果退出有效 Agent 状态

Cancel
  -> 尝试停止排队中或运行中的工具

Compensate
  -> 撤销已经完成的外部副作用
```

当前 fallback 机制主要覆盖前两层。文件写入、Shell 命令、数据库更新、消息发送和远端资源创建等副作用，需要工具自身支持 Abort、幂等、事务或补偿操作。

## 我提出的问题与暴露出的知识薄弱点

| 我提出的问题 | 暴露出的学习主题 | 当前获得的理解 |
|---|---|---|
| 每次是不是把所有对话记录传给 Agent？对话记录保存在本地吗？ | 无状态模型、会话持久化、上下文窗口 | 本地 Transcript 与实际模型上下文是两个视图；模型收到的是有效上下文 |
| `query()` 和 `queryLoop()` 各自做什么？ | 入口委托、生成器组合、生命周期边界 | 外层负责委托和收尾，内层负责真正编排 |
| 有效上下文是不是一个大话题？ | Context Engineering | 是，应独立研究完整转换链 |
| 如何保持 Streaming？如何判断超时？ | AsyncGenerator、SSE、Abort、Timeout | 单次消费 Raw Stream，多层 `yield*` 转发；超时必须分阶段 |
| 这里是一处生产两处消费，还是两处生产？ | 数据流拓扑、派生事件 | 一个上游源、一次消费、派生两种输出表示 |
| `stream_event` 是即时消费，`AssistantMessage` 是 Batch 组装吗？ | 原始事件与语义消息 | 基本正确，但组装边界通常是 Content Block，不是整次请求 |
| 模型服务静默处理两分钟会被 Watchdog 取消吗？ | Idle Timeout 与 Total Timeout | Headers 后连续无可消费事件可能触发；持续心跳则不会 |
| 取消当前流是什么意思？还会继续等待吗？ | Transport Cancellation 与 Agent 生命周期 | 不再等待原 Stream，但上层 Agent Turn 可以通过新请求继续 |
| 取消流后需要清理哪些资源？ | 资源所有权和 `finally` | 网络流、Response Body、Timer、局部消息、Executor、UI 和 Transcript |
| 已经生成、展示和存储的消息如何取消？ | 补偿事件、最终一致性 | Tombstone 通知下游作废，而不是原地修改或时间倒流 |
| 怎么判断消息属于这次失败的 Stream？ | Attempt Scope、Identity、Correlation | 先靠局部作用域确定集合，再用 UUID 和 Tool ID 精确定位 |
| Executor 丢弃后，Tool Use 和 Tool Result 能回滚吗？ | 逻辑回滚与外部副作用 | 能定位和作废状态；真正撤销依赖工具的补偿能力 |
| “选择 Leaf，再沿 `parentUuid` 恢复一条链”是什么意思？ | 追加式事件日志、树形会话、分支恢复 | 从选中的分支末端反向查找祖先消息，再反转为正常顺序；不是顺序读取全部 JSONL 行 |
| JSONL 是保存到本地的 Transaction File 吗？ | Transcript 与 Transaction 的术语边界 | 它是本地 Transcript File，即会话持久化事件集合，不是数据库事务日志 |
| File History Snapshot 会复制所有参考文件吗？ | 文件读取与文件修改、快照和备份 | 只为被追踪的修改文件保存可恢复副本；读取或参考文件本身不会因此全部归档 |
| 修改记录和副本会永久保存吗？ | Retention、后台清理、Git 边界 | 当前快照默认按30天清理旧会话备份，内存最多保留100个快照；它不是永久版本控制系统 |
| Attribution Snapshot、Tool Result Replacement、Context Collapse Commit 分别是什么？ | 恢复辅助状态、上下文投影 | 分别恢复修改归因、记录大型工具结果的轻量替代、记录历史区间到摘要的折叠决定 |
| 大型 Tool Result 在什么时候变成轻量引用？ | Turn 边界、API 消息预算 | 工具执行时先收集完整结果；下一轮构造 `messagesForQuery`、调用模型之前才检查和替换 |
| 历史被摘要替代是在上下文过程中吗？ | Context Pipeline、读取时投影 | 是；Context Collapse 在 Microcompact 后、Auto Compact 前修改模型视图，本地完整历史不等于模型视图 |
| Rewind、Subagent 和并行工具产生的多个 Leaf 是同一种分支吗？ | 语义分支、Sidechain、持久化拓扑 | 不是；Rewind 是对话分支，Subagent 是隔离 Sidechain，并行工具是同一模型响应在持久化层形成的技术分叉 |
| 并行工具为什么可能让单父节点回溯漏掉消息？ | Provider Message ID、Message UUID、Tool Correlation | 同一响应的多个 Assistant Block 可有不同 UUID，各自连接 Tool Result；恢复时需按共享 `message.id` 补回兄弟块和结果 |

## Part 2 — Transcript、Session Recovery 与 Effective Context

> 学习日期：2026-08-09
> 本部分研究 Claude Code 如何把本地持久化的会话记录恢复为当前对话链，再经过
> 多层上下文转换形成模型实际收到的请求。它与 Part 1 的 Agent Loop 主循环分开：
> Part 1 回答“循环如何继续”，Part 2 回答“每次循环究竟把什么交给模型”。

### 本部分学习目标

完成 Part 2 后，我应能独立解释：

1. 为什么 Transcript JSONL 是追加写入的会话事件集合，而不是可直接发送给模型的
   `Message[]`；
2. Claude Code 如何选择 Leaf，并沿 `parentUuid` 恢复当前对话分支；
3. Resume、Rewind、Fork Session、Subagent Sidechain 和并行工具技术分叉的区别；
4. File History Snapshot、Attribution Snapshot、Tool Result Replacement 和 Context
   Collapse Commit 分别解决什么问题；
5. 本地持久化视图、Agent 运行时视图和模型请求视图之间发生了哪些转换；
6. 如何在 Codex、Pi、OpenCode 或 LangGraph 中寻找等价机制，而不是寻找相同变量名。

### Part 2 章节结构

```text
2.1 Transcript 事件图、Leaf 选择与 parentUuid 链重建
2.2 File History Snapshot 与 Rewind 恢复边界
2.3 辅助 Transcript 记录及其职责
2.4 Tool Result Replacement 的时机与一致性
2.5 Context Reduction Pipeline
2.6 并行工具产生的技术分叉
2.7 测验、源码复查与开放问题
2.8 第一次测验结果与心智模型校准
2.9 通用 Interface 与 Claude Code 实现映射
```

### 三种必须分开的数据视图

| 视图 | 主要结构 | 主要用途 | 是否等于模型输入 |
|---|---|---|---|
| 持久化视图 | JSONL Transcript、备份文件及辅助记录 | Resume、Rewind、分支恢复和审计 | 否 |
| 运行时视图 | 当前消息链、Agent `State`、`messagesForQuery` 的中间形态 | 选择、替换、裁剪、折叠和注入上下文 | 不一定 |
| 模型视图 | System Prompt、工具定义和最终规范化消息 | 形成实际 Provider 请求 | 是 |

关键边界：`buildConversationChain()` 得到的是当前有效对话链，但它仍需进入 Context
Pipeline；它不是未经处理即可发送给模型的最终请求。

### 本阶段视觉总结

以下三张图记录当前学习结论。它们是阶段性理解，不替代后续源码证据；如果继续
追踪后发现实现细节变化，应同步修订图片和文字结论。

#### 1. Transcript 如何恢复有效对话链

![Transcript JSONL 到有效对话链](../../../../assets/agent-implementation-study/claude-code-transcript/01-transcript-to-conversation-chain.png)

读图校准：图中的“发送给模型”是压缩后的视觉表达。严格来说，恢复出的当前对话链
还要进入 Context Pipeline，只有最终规范化的消息和 System Prompt、工具定义等共同
形成 Provider Request。

#### 2. Resume、Rewind 与 Fork Session 的区别

![Resume、Rewind 与 Fork Session 对比](../../../../assets/agent-implementation-study/claude-code-transcript/02-resume-rewind-fork.png)

#### 3. Tool Result 替换与上下文缩减流水线

![Claude Code 上下文缩减流水线](../../../../assets/agent-implementation-study/claude-code-transcript/03-context-reduction-pipeline.png)

读图校准：图中的“完整保留”表示上下文缩减不会因为模型视图变短就立即抹除本地
持久化证据，不表示永久保存。File History、Session Backup 和外置 Tool Result 都受
各自的保留期限、清理策略和持久化成功条件约束。

### Resume、Rewind 与 Fork Session 的不变量对照

| 操作 | Session ID | Transcript | 运行时 | 当前分支 |
|---|---|---|---|---|
| Resume | 保持 | 继续读取同一会话记录 | 新进程和新 Agent Loop | 恢复选中的有效链 |
| Rewind | 保持 | 同一 Transcript 中保留旧分支并产生新分支 | 当前或后续运行时继续 | Tip/Leaf 改到新分支 |
| Fork Session | 新建 | 为新 Session 建立新记录并复制选中历史 | 新 Session 运行状态 | 从复制的历史片段继续 |

这三者解决的不是同一个问题：Resume 恢复运行，Rewind 改变同一会话的当前未来，Fork
则创建新的会话身份。Subagent Sidechain 又是另一层隔离，不能与 Rewind 分支混为一谈。

### 2.1 如何根据 Leaf 恢复对话？

**我的当前理解：**

> 根据选中的末端消息，沿着每条消息的 `parentUuid` 向前查找，恢复这条消息所属分支的祖先记录，最后反转为正常对话顺序。

**源码校准与案例：**

```text
A
└── B
    ├── C
    │   └── D  <- 旧 Leaf
    └── E
        └── F  <- 当前 Leaf
```

从 `F` 恢复时，回溯结果是 `F -> E -> B -> A`，反转后得到
`A -> B -> E -> F`。旧分支 `C -> D` 不进入当前消息链。JSONL 中还包含
Summary、Snapshot 和 Collapse Commit 等非消息事件，因此不能把文件行按顺序
全部发送给模型。

### 2.2 File History Snapshot 保存什么，会永久保存吗？

**当前结论：**

- 它不是所有“参考过或读取过”的文件集合。
- `fileHistoryTrackEdit()` 在实际修改前为受追踪文件创建本地副本。
- Session JSONL 保存 `messageId`、备份文件名、版本和时间等元数据；实际文件
  内容保存在独立的 File History Backup 文件中。
- 新文件在目标快照中可以用 `backupFileName: null` 表示“当时不存在”；Rewind
  时可据此删除后来创建的文件。
- 当前本地源码快照中，内存状态最多保留100个 Snapshot；后台清理默认以30天
  为期限递归删除过期的 Session Backup 目录，期限可由
  `cleanupPeriodDays` 调整。
- 清理是后台最佳努力机制，不保证到期瞬间删除；File History 不是永久归档，
  重要版本仍应使用 Git。

**案例：**

```text
Message M1 时：
  foo.ts 已存在  -> 修改前复制为 v1 Backup
  bar.ts 不存在  -> 记录 null Backup

Rewind 到 M1：
  foo.ts 从 v1 Backup 恢复
  bar.ts 被删除，恢复为当时不存在
```

### 2.3 三类辅助 Transcript 记录是什么？

#### Attribution Snapshot

保存文件内容 Hash、修改时间和 `claudeContribution` 等累计归因状态，并记录
Surface、Prompt 次数、权限询问次数和取消次数。它用于 Resume 后恢复修改归因，
不是完整文件备份。

#### Tool Result Content Replacement

保存 `toolUseId -> replacement`。大型工具输出被持久化后，模型上下文使用较短的
替代内容；Resume 时通过同一 `toolUseId` 重建和复用替换决定。

#### Context Collapse Commit

保存 `firstArchivedUuid`、`lastArchivedUuid`、`summaryUuid` 和 Summary，表示某段
历史在模型视图中应由哪个摘要替代。这里的 Commit 是折叠决定，不是 Git Commit。

### 2.4 大型 Tool Result 在何时触发替换？

**当前时序：**

```text
第 N 轮模型产生 tool_use
  -> Runtime 执行工具并收集完整 tool_result
  -> 完整结果进入下一 State
  -> 第 N+1 轮开始构造 messagesForQuery
  -> applyToolResultBudget()
  -> 必要时持久化原始结果并生成轻量替代
  -> deps.callModel()
```

当前源码快照按最终 API User Message 对多个 `tool_result` 做聚合预算；默认聚合
限制为 `200,000` 字符，但它可被动态配置影响，不应视为稳定公开契约。只有新的
Message Group 首次接受预算决策；以后通过 `seenIds` 和 Replacement Map 重放相同
决定，以保护恢复一致性和 Prompt Cache 稳定性。

**并行工具案例：**

```text
Tool Result A = 90K
Tool Result B = 80K
Tool Result C = 70K
聚合结果       = 240K

超过当前快照默认200K预算：
  -> 选择一个或多个较大结果持久化
  -> 在 API Message 中使用轻量替代
  -> 直到该 Message 回到预算以内
```

某些工具可声明独立的结果大小契约并跳过这层通用预算，因此不能把“所有超过某个
单项大小的 Tool Result 都会被替换”当成结论。

### 2.5 Context Collapse 是否属于上下文过程？

是。当前 `queryLoop()` 中的顺序是：

```text
Agent State messages
  -> Compact Boundary selection
  -> Tool Result Budget
  -> History Snip
  -> Microcompact
  -> Context Collapse
  -> Auto Compact
  -> System/User Context
  -> deps.callModel()
```

Context Collapse 是对模型视图的读取时投影：本地 Transcript 可以继续保留
`M1...M6`，但本次 `messagesForQuery` 只包含 `Summary(M1...M6)`。它位于
Microcompact 后、Auto Compact 前；若局部 Collapse 已经把上下文降到安全范围，
可以避免更激进的 Auto Compact。

**正常投影案例：**

```text
本地 Transcript：M1 M2 M3 M4 M5 M6 M7
模型上下文：     Summary(M1-M6) M7
```

**溢出恢复案例：**

```text
模型返回 Prompt Too Long
  -> recoverFromOverflow() 提交已准备的 Collapse
  -> 用折叠后的 State 重试
  -> 仍失败时尝试 Reactive Compact
  -> 无法恢复才返回终止错误
```

### 2.6 并行工具为什么会形成多个技术 Leaf？

**当前结论：**

并行工具产生的分叉不是用户选择了不同的对话未来。当前源码快照的 Streaming
路径可能在每个 `content_block_stop` 形成一个独立 `AssistantMessage`：多个
Assistant Block 拥有不同的消息 UUID，但共享同一个 Provider `message.id`。每个
`tool_result` 又通过自己的父 Assistant UUID 和 `tool_use.id` 建立关联，于是持久化
图看起来像多个分支。

**双工具案例：**

```text
同一次 Provider Assistant Response：message.id = response-123

Previous Message
├── Assistant Block aa
│   ├── uuid = aa
│   ├── tool_use A
│   └── Tool Result A  -> parentUuid = aa
│
└── Assistant Block ab
    ├── uuid = ab
    ├── tool_use B
    └── Tool Result B  -> parentUuid = ab
```

从其中一个 Leaf 仅沿 `parentUuid` 回溯，可能只看到 A 或 B 一侧。为避免遗漏，
`buildConversationChain()` 在完成普通单父节点回溯后调用
`recoverOrphanedParallelToolResults()`：

```text
共享 Provider message.id
  -> 找到同一次响应的兄弟 Assistant Block
  -> 根据各自 Assistant UUID 找到 Tool Result
  -> 按时间和写入顺序插回恢复链
  -> normalizeMessagesForAPI() 恢复为同一个语义 Turn
```

最终模型协议视图应接近：

```text
Assistant：tool_use A + tool_use B
User：tool_result A + tool_result B
```

因此需要区分：

```text
Rewind Leaf
  = 同一主会话的另一条语义未来

Subagent Leaf
  = 按 agentId / isSidechain 隔离的执行末端

Parallel Tool Leaf
  = 同一语义 Turn 在消息持久化结构中的技术分叉
```

当前仍需验证异常路径：其中一个工具被中断、缺失 Tool Result、Fallback 重试、
Resume、排序相同以及重复记录时，恢复逻辑是否始终保持正确关联。

### 2.7 学习出口：主动回忆与迁移

Part 2 不以“读完笔记”为完成标准，而以能否在不看笔记时重新推导关键机制为准。
闭卷主动回忆、案例推导、源码定位和跨实现迁移题已整理为独立测验：

[Part 2 Quiz：Transcript、Session Recovery 与 Effective Context](./part-2-quiz.md)

建议先完成测验的 A、B、D 部分，再打开源码完成 C 部分。答题后把错误归类为：

```text
术语混淆
生命周期边界混淆
持久化视图与模型视图混淆
正常路径会解释、异常路径不会推导
记得 Claude Code 符号，但不能迁移到其他实现
```

### 2.8 第一次测验结果与心智模型校准

第一次闭卷作答已保存为独立记录：

[Part 2 Quiz Attempt — 2026-08-09](./part-2-quiz-attempt-2026-08-09.md)

当前只完成 A、B，C、D 尚未作答，因此不计算完整50分成绩：

| 部分 | 状态 | 暂定得分 |
|---|---|---:|
| 主动回忆 | 已完成 | 5.5 / 12 |
| 案例推导 | 已完成 | 5 / 16 |
| 源码定位 | 未完成 | 暂不评分 |
| 跨实现迁移 | 未完成 | 暂不评分 |
| **闭卷阶段** | **A + B** | **10.5 / 28（约38%）** |

这次结果说明：整体概念已经形成，但精确时序、拓扑方向和生命周期不变量尚未稳定。

**已经形成的能力：**

- 能区分持久化、运行时和模型三种数据视图；
- 能识别 Message、Parent 和 Session 的基本身份层次；
- 知道 Sidechain 不应成为主会话默认 Tip；
- 知道 Tool Result Replacement 和 Context Collapse 服务于模型上下文控制；
- 已开始区分 Rewind 语义分支与 Parallel Tool 技术分叉。

**本次需要校准的重点：**

```text
Leaf = 消息图中的分支末端，不是一轮数据集合

回溯方向：F -> D -> A
最终正序：A -> D -> F

Resume = 同一 Session / Transcript，重建运行时
Rewind = 同一 Transcript，旧分支保留，新建 Leaf
Fork = 新 Session / 新 Transcript，复制选中历史

Parallel Tool 恢复后的模型协议：
Assistant: tool_use A + tool_use B
User:      tool_result A + tool_result B
```

B4 涉及尚未详细学习的 Context Compression / Collapse，不能简单视为“学过但忘记”。
它已被提升为下一学习优先级；完成源码学习后再重做 B4 和 C3。

### 2.9 通用 Interface 与 Claude Code 实现映射

为了让 Claude Code 的结论可以迁移到 Codex、Pi、OpenCode 和 LangGraph，当前研究被
整理成两层：通用 Interface 定义系统责任，Claude Code Mapping 填入具体实现。

完整说明：
[Agent Session and Context Interface with Claude Code Mapping](./agent-session-context-interface-and-claude-mapping.md)

#### 通用 Agent Session / Context Interface

![通用 Agent Session 与 Context Interface](../../../../assets/agent-implementation-study/agent-session-context-interface/01-agent-session-context-interface.png)

这层不规定 JSONL、`parentUuid` 或语言框架，只要求每个实现回答：持久化、身份与顺序、
当前位置、分支隔离、恢复、Runtime State、Context Transformation、Provider Boundary、
Tool Continuation 和 Evidence 分别由谁负责。

#### Claude Code 当前实现映射

![Claude Code Session 与 Context 的当前实现映射](../../../../assets/agent-implementation-study/agent-session-context-interface/02-claude-code-session-context-implementation.png)

当前映射状态：

| Interface 层 | Claude Code 当前证据 |
|---|---|
| Persistence Read | `loadTranscriptFile()`，SOURCE |
| Identity / Ordering | `uuid`、`parentUuid`、`sessionId`，SOURCE |
| Leaf / Tip | `leafUuids`、排除 Sidechain、`buildConversationChain()`，SOURCE |
| Resume | `loadConversationForResume()`，SOURCE / PARTIAL |
| Runtime State | `queryLoop()` 与 `state = next`，SOURCE |
| Context Transformation | 已知高层顺序，详细语义为 TODO |
| Provider Boundary | 已定位 `deps.callModel()`，完整字段映射为 PARTIAL |
| Tool Continuation | `StreamingToolExecutor` / `runTools()` / `tool_result`，SOURCE / PARTIAL |
| Transcript Write-back | 完整写回和 Crash 一致性尚未追踪，TODO |

以后研究其他 Agent 时，不应只问“有没有 `parentUuid`”，而应问“它如何表示消息顺序、
当前位置和分支”。这使不同语言和存储模型仍能进行同一 Interface 层面的比较。

### 2.10 Context Collapse 与 Auto Compact 第一轮源码校准

本轮完成了 Part 2 中两种上下文缩减机制的第一轮源码学习。完整记录分为：

- [Context Collapse：Summary、Commit 与请求边界](./context-collapse-summary-and-commit.md)
- [Auto Compact：触发判断与上下文重建](./auto-compact-trigger-and-context-rebuild.md)

当前形成的最小心智模型是：

```text
Context Collapse
= 一个或多个局部历史 Span
→ Staged Summary
→ Collapse Commit
→ 可重放的模型视图投影

Auto Compact
= 较大的当前消息链
→ 整体 Summary
→ Compact Boundary
→ Boundary + Summary + Attachments
→ 后续 Agent State
```

这修正了一个容易出现的模糊表述：两者都会影响最终 `messagesForQuery`，但它们的状态
语义不同。Context Collapse 的 Summary 不向 REPL yield，主要通过 Commit Store 在读取时
投影历史；Auto Compact 创建并 yield 新消息，明确构成后续工作消息链。

两张配套视觉总结：

![Auto Compact：一次上下文重建](../../../../assets/agent-implementation-study/claude-code-transcript/05-auto-compact-context-rebuild.png)

![Context Collapse：局部历史投影](../../../../assets/agent-implementation-study/claude-code-transcript/06-context-collapse-local-projection.png)

当前还要保留以下校准：

1. 调用 `deps.autocompact()` 不代表一定压缩，必须通过 `shouldAutoCompact()`；
2. 当前快照中 Context Collapse 开启会抑制主动 Auto Compact；
3. Auto Compact 新消息链的顺序是 Boundary、Summary、可选近期消息、Attachments、Hooks；
4. 真实 API 413 后先尝试 Drain Staged Collapse，仍失败才进入 Reactive Compact；
5. Collapse 的 Span 选择、Risk 算法、Summary Prompt 和投影内部实现仍为 `UNKNOWN`。

下一次复习不再同时展开所有细节。先根据图闭卷回答三个问题：

1. 哪些 Guard 会阻止 Auto Compact？
2. 为什么 Auto Compact 是 Agent State 重建，而不只是请求参数变化？
3. 为什么 Context Collapse 的 Summary 可以持久化，却不需要作为普通消息向 REPL yield？

### 2.11 History Snip 第一轮源码检查点

本轮把 History Snip 从笼统的“压缩”中分离出来。完整记录：

[History Snip：选择性删除与 Resume 重放](./history-snip-source-checkpoint.md)

当前最小心智模型：

```text
模型通过 API-only [id:...] 引用旧消息
→ SnipTool 标记已经无用的历史
→ queryLoop 在 Microcompact 前应用删除
→ 记录 tokensFreed 和 Snip Boundary
→ Provider Request 不再包含这些消息
```

它与另外两种机制的区别是：

```text
History Snip     = 删除，不生成 Summary
Context Collapse = 局部 Span 变成 Summary 投影
Auto Compact     = 创建 Boundary 并重建消息链
```

本轮还校准了“删除”的数据层含义：磁盘 JSONL 仍是追加式历史；REPL 可以保留完整
Scrollback；Headless SDK 可以缩减 Mutable Message Store；Resume 根据 Snip Boundary 的
`removedUuids` 从内存 Map 删除消息，并跨越缺口重连 `parentUuid`。

当前仍需深入的问题集中在缺失的 `snipCompact.ts`、`snipProjection.ts` 和 `SnipTool`：

1. SnipTool 的精确 Input Schema、验证、权限和 Tool Result；
2. 哪些消息允许删除，以及 Protected Tail 如何定义；
3. 多个、重叠或不连续的删除区间如何规范化；
4. 删除是否始终保持 Tool Use / Tool Result 配对；
5. History Snip 与 Microcompact 同时发生时如何组合；
6. REPL、Headless 和 Resume 三条路径的具体 Before/After 案例。

这部分登记为独立 TODO，不因为第一轮可见源码已经读完而标记为完全掌握。

### 2.12 Microcompact 第一轮 Pattern 学习检查点

本轮按照“伪代码 → 抽象规范 → Agent 具体实现”的通用 Pattern，完成了
Microcompact 的第一轮学习。完整记录：

[Microcompact：工具结果 Payload 缩减与缓存编辑](./microcompact-tool-result-payload-reduction.md)

同时补充了 Tool Use、Tool Result 和语义依赖的前置对照：

[Tool Message Dependencies and Context Reduction](./tool-message-dependencies-and-context-reduction.md)

当前最小心智模型：

```text
Microcompact 只缩减旧 Tool Result 的 Payload
→ 保留 Assistant tool_use 与 User tool_result 的协议结构
→ Time-based 路径可以改变本地模型消息视图
→ Cached 路径准备 Provider Cache Editing
→ 只有 cache_deleted_input_tokens 的增量才能确认 Provider 已实际应用编辑
```

本轮已经分清 Transcript、当前内存消息视图、Provider 实际缓存状态三个层次，也确认
“结构仍合法”不等于“删除在语义上安全”。`cachedMicrocompact.ts` 的状态机与 Provider
服务端 Cache Editing 实现不在当前快照中，继续标记为 `UNKNOWN`。

## 当前特别需要加强的基础概念

这些问题共同指向几个值得在后续对比中反复练习的主题：

1. **异步生成器和事件流**：`yield`、`yield*`、`for await`、Raw Event 与语义对象。
2. **作用域与所有权**：Turn、LLM Attempt、Executor、Message 和 Tool Call 的生命周期边界。
3. **身份与关联**：Request ID、Message UUID、Tool Use ID、Tool Result ID 的不同用途。
4. **取消语义**：停止等待、Abort 网络请求、取消任务、丢弃结果不是同一个动作。
5. **补偿式一致性**：Tombstone、Invalidate、Cancel、Compensate 的区别。
6. **Context Engineering**：完整历史、内存消息链和实际模型上下文之间的转换。

这些不是“答错的问题”，而是后续研究其他 Coding Agent 时最值得主动对照的知识坐标。

## Part 2 当前深入 TODO

### 完整 Transcript 如何转换为有效上下文

- [ ] 追踪 JSONL Transcript 的加载和消息链重建。
- [x] 区分 Transcript、内存消息链和 `messagesForQuery`。
- [x] 追踪 Compact Boundary、Tool Result Budget、History Snip、
      Microcompact、Context Collapse 和 Auto Compact。
- [ ] 解释 System Context、User Context、附件、Skills 和 Memory 如何注入。
- [ ] 说明每一步保留、删除、替换或总结了什么信息。
- [ ] 验证 `/resume` 后的消息链如何再次形成有效上下文。

计划产物：一张转换流程图、一张数据结构对照表，以及关键代码截图。

### 大型 Tool Result 的持久化与轻量替换

- [ ] 深入追踪 Tool Result 聚合预算、选择策略、持久化、替换和 Resume 重放。
- [ ] 验证并行工具 Case、工具级例外、动态阈值和持久化失败行为。

### History Snip 深入研究

当前源码检查点：
[History Snip：选择性删除与 Resume 重放](./history-snip-source-checkpoint.md)

- [ ] 补齐 Snip 核心模块和 SnipTool 的完整源码证据。
- [ ] 追踪选择、验证、执行、Boundary 持久化和 Resume 重放的端到端时序。
- [ ] 验证 Protected Tail、多个区间以及 Tool Use / Tool Result 不变量。
- [ ] 对比 REPL Projection 与 Headless Mutable State 的不同所有权。
- [ ] 完成 History Snip × Microcompact 组合案例、视觉图和复习题。

### 并行工具的持久化拓扑与恢复合并

- [ ] 深入追踪共享 Provider `message.id` 的多个 Assistant UUID 如何连接各自的
      Tool Use 和 Tool Result。
- [ ] 验证 `recoverOrphanedParallelToolResults()` 在正常、缺失结果、中断、Fallback
      和 Resume Case 中的分组、排序、去重和重新插入行为。
- [ ] 对比持久化消息图与 `normalizeMessagesForAPI()` 后的语义模型消息。

### 下一学习 TODO（优先级 1）：Context Compression 与 Context Collapse

**当前状态：Context Collapse 可见源码边界已完成第一轮学习。** 已理解请求前投影、
Staged Summary、分段 Commit、Commit/Snapshot 持久化、Resume 重放，以及 API 413 后的
Collapse Drain。精确 Span 选择、Risk 计算、Summary 生成和 `projectView()` 实现因本地
快照缺失内部模块，继续标记为 `UNKNOWN`。

当前源码学习记录：
[Context Collapse Summary、Commit 与请求边界](./context-collapse-summary-and-commit.md)

当前视觉总结：
[Context Collapse 分段式 Summary Commit](../../../../assets/agent-implementation-study/claude-code-transcript/04-context-collapse-summary-commit.png)

- [x] 区分 Tool Result Replacement、History Snip、Microcompact、Context Collapse、
      Auto Compact 和 Reactive Compact，避免把它们统称为“压缩”。
- [ ] 为每个机制记录：触发条件、输入、输出、删除或保留的信息、持久化证据、对
      Prompt Cache 的影响，以及是否改变 Agent State 或只改变模型视图。
- [ ] 深入追踪 Collapse Span 的选择、Summary 生成、Commit 持久化和 `/resume` 重放。
- [x] 解释 Context Collapse 为什么位于 Microcompact 之后、Auto Compact 之前，以及
      Collapse 成功后何时可以避免 Auto Compact。
- [ ] 对比正常的请求前缩减、Prompt Too Long 后的 Overflow Recovery、Reactive
      Compact 和最终终止路径。
- [ ] 产出一张“Compression vs Collapse”对照图，以及正常路径和溢出恢复各一个
      Before/After 案例。
- [ ] 完成源码学习后重新闭卷回答 Part 2 Quiz 的 B4 和 C3。

## 后续跨 Coding Agent 对比时的复用模板

研究 Codex、Pi、OpenCode 和 LangGraph 时，继续记录两部分：

### 我的提问

- 哪个地方让我产生了疑问？
- 这个问题暴露了哪个基础概念不熟？
- 它是该 Agent 特有的问题，还是通用 Agent Runtime 问题？

### 我的暂定结论

- 我目前如何用自己的话复述这个机制？
- 哪些部分有源码直接支持？
- 哪些部分只是为了帮助记忆的简化模型？
- 新系统是否支持、反驳或细化了这个模型？

建议保持以下统一对比维度：

| 对比维度 | 需要观察的内容 |
|---|---|
| Loop ownership | 谁拥有主循环和下一轮状态 |
| Model boundary | 如何构造请求和消费流式响应 |
| Event representation | Raw Event 如何转换为语义消息 |
| Attempt isolation | 是否存在 Attempt-scoped 状态或 Executor |
| Tool correlation | Tool Use 和 Tool Result 如何关联 |
| Cancellation | 如何区分用户取消、超时和内部失败 |
| Cleanup | 网络、Timer、消息、工具和持久化如何回收 |
| Compensation | 已完成副作用是否支持撤销或幂等 |
| Context pipeline | 完整历史如何变成有效上下文 |
| Persistence | Session 如何保存、恢复、分支和重放 |

## 当前阶段总结

我现在形成的核心认识是：

> Coding Agent 不是简单地循环调用模型。它需要为每次模型尝试建立清晰的消息、工具和资源所有权；把原始流式事件转换为稳定语义消息；在失败时通过取消、Tombstone 和 Executor 隔离恢复一致状态；同时承认已经发生的外部副作用并不能仅靠消息 ID 自动回滚。

这套理解仍是可修订模型。后续研究其他 Coding Agent 时，应保留新的问题和主动复述，用跨实现证据逐步改进它。
