# Context Collapse：Summary、Commit 与请求边界

> 研究对象：本地 Claude Code 源码快照
> 版本边界：该快照尚未被证明与本机 Claude Code `2.1.224` 完全对应。
> 实现边界：调用点和持久化协议存在，但 `src/services/contextCollapse/` 内部实现目录
> 不在本地快照中。本文把可见源码事实、合理推断和未知项分开记录。

## 核心结论

Context Collapse 不是删除完整 Transcript，也不是向 REPL 新增一条普通 Summary
消息。它把一段历史映射为可重放的 Summary Placeholder，首先改变本次模型请求使用的
`messagesForQuery`：

```text
本地 Transcript：M1 M2 M3 M4 M5 M6 M7 M8
Collapse Commit：M1...M6 -> Summary S1
模型视图：      S1 M7 M8
```

## 请求前接入点

`src/query.ts` 的 `queryLoop()` 在 Microcompact 之后调用：

```ts
const collapseResult =
  await contextCollapse.applyCollapsesIfNeeded(
    messagesForQuery,
    toolUseContext,
    querySource,
  )

messagesForQuery = collapseResult.messages
```

随后，折叠后的 `messagesForQuery` 才进入 `deps.autocompact()` 和
`deps.callModel()`。

这里没有：

```ts
yield collapseResult.summary
```

因此没有把 Summary 作为普通可见消息交给 REPL、UI 或 SDK。更准确的边界是：

```text
yield message
= 向外层消费者输出一条运行消息

messagesForQuery = collapseResult.messages
= 改变下一次模型请求看到的消息视图
```

## 三种数据视图

| 视图 | Collapse 后的表示 | 主要职责 |
|---|---|---|
| REPL / UI | 仍可显示 M1...M8 | 用户可见的完整交互历史 |
| 本地 Transcript | M1...M8，加一条 Commit/Snapshot 记录 | Resume、审计和重放 |
| 模型视图 | S1 + M7 + M8 | 控制本次 Provider Request 的上下文大小 |

`buildConversationChain()` 恢复出的消息链仍不是最终模型请求。它必须继续经过 Tool
Result Budget、History Snip、Microcompact、Context Collapse 等 Context Pipeline。

## Collapse 的检查和 Commit 时机

### 正常路径

每轮模型请求前都会经过 `applyCollapsesIfNeeded()` 检查点，但调用不意味着必然生成
或提交新的 Collapse。

当前可见源码和类型表明系统区分两个阶段：

```text
提前选择区间并生成候选 Summary
→ Staged Snapshot

Token 压力达到内部条件
→ 正式 Commit 合适的候选区间
→ 投影 messagesForQuery
→ 发送模型请求
```

`src/services/compact/autoCompact.ts` 的注释提到 Context Collapse 负责约 90% Commit
Start 和约 95% Blocking Spawn 的上下文压力区间。这些数字是当前调用方注释，不是已
验证的稳定公开契约；精确计算公式位于缺失模块中。

### Overflow Recovery

如果模型请求已经返回 Prompt Too Long：

```text
第一次请求
→ API 413
→ recoverFromOverflow()
→ Drain 已有 Staged Collapse
→ Commit
→ 使用折叠后的 State 重试
```

因此，“Commit 发生在请求前”应精确表述为：Commit 在使用该折叠视图的请求之前完成。
正常路径是在首次请求前；Overflow 路径是在失败请求之后、重试请求之前。

## 异步与阻塞边界

“异步”不等于“当前请求不等待”。

| 阶段 | 当前结论 | 证据等级 |
|---|---|---|
| 候选 Summary 生成 | 支持提前准备和 Staged Queue，可能异步进行 | `INFERENCE` |
| 正式应用 Collapse | `queryLoop()` 使用 `await applyCollapsesIfNeeded()` | `SOURCE` |
| 当前模型请求 | 必须等待折叠后的 `messagesForQuery` 返回 | `SOURCE` |
| Commit 写入 API | `recordContextCollapseCommit()` 内部 `await appendEntry()` | `SOURCE` |
| 调用方是否等待磁盘写入 | 内部调用代码缺失 | `UNKNOWN` |
| API 413 Drain | 调用点同步取得 `recoverFromOverflow()` 返回结果 | `SOURCE` |

最适合的心智模型是：昂贵的 Summary 生成可能提前异步完成；正式应用通常消费已有候选
并投影消息，但它是当前模型请求之前的一道 `await` 屏障。磁盘持久化是否也阻塞请求
目前不能证明。

## Commit 是按历史区间渐进提交

这里的 Commit 不是 Git Commit，也不是数据库事务。每条 Commit 表示：

> 正式确认某个历史区间由某个 Summary 替代。

例如：

```text
Commit C1：M1...M6   -> Summary S1
Commit C2：M7...M12  -> Summary S2

模型视图：S1 S2 M13 M14
```

它是逐段、渐进式的，但不是逐条消息提交，也不是把 Summary 分块写入磁盘。

当前快照可以确认每条 Commit 带有一个首尾区间。一次
`applyCollapsesIfNeeded()` 最多提交多少个区间、相邻区间是否合并、嵌套区间如何处理，
仍为 `UNKNOWN`。

## Summary 的三层结构

### 1. Staged Candidate

`ContextCollapseSnapshotEntry` 保存：

```ts
staged: Array<{
  startUuid: string
  endUuid: string
  summary: string
  risk: number
  stagedAt: number
}>
```

它表达候选区间、普通 Summary 文本、Risk 和准备时间，还没有完整 Commit 身份。

### 2. Model Placeholder Content

Commit 保存：

```ts
summaryContent: string
```

源码注释说明它是完整的 Collapse 标签：

```xml
<collapsed id="C1">Summary text...</collapsed>
```

标签告诉模型这段文本是旧历史的压缩表示，而不是用户刚输入的新消息。

### 3. Persisted Commit

`ContextCollapseCommitEntry` 的结构是：

```ts
type ContextCollapseCommitEntry = {
  type: 'marble-origami-commit'
  sessionId: UUID
  collapseId: string
  summaryUuid: string
  summaryContent: string
  summary: string
  firstArchivedUuid: string
  lastArchivedUuid: string
}
```

它同时记录 Collapse 身份、Summary 消息身份、模型占位内容和被替代区间。

当前能确认 `summary` 是字符串，不能确认其内部是否要求 Goal、Files、Decisions 等固定
章节；Summary Prompt 和输出 Schema 位于缺失模块中。

## Commit 与 Snapshot 的区别

| 结构 | 含义 | 重放语义 |
|---|---|---|
| Snapshot | 准备折叠什么，以及当前触发状态 | 较新状态覆盖较旧状态 |
| Commit | 已经决定哪个区间由哪个 Summary 替代 | 追加记录并按顺序重放 |

Snapshot 还保存：

```ts
armed: boolean
lastSpawnTokens: number
```

这说明候选生成与 Token 增长和内部触发状态有关，但精确规则无法从快照证明。

## 本地持久化与 Resume

`recordContextCollapseCommit()` 把 Commit 作为 `marble-origami-commit` 追加到当前 Session
记录；`recordContextCollapseSnapshot()` 写入最新 Staged Queue 状态。

Resume 时，`restoreSessionStateFromLog()` 在第一次 `query()` 之前调用：

```ts
restoreFromEntries(
  result.contextCollapseCommits ?? [],
  result.contextCollapseSnapshot,
)
```

随后 `projectView()` 根据 Commit 的首尾 UUID，在恢复出来的 Message Chain 上重建折叠
视图。Commit 不复制 M1...M6，因为原始消息已经是普通 Transcript Message。

## 与 Auto Compact 的关系校准

Context Collapse 开启时，`shouldAutoCompact()` 返回 `false`，主动 Auto Compact 被抑制：

```text
Context Collapse 开启
→ Collapse 接管正常上下文压力
→ Proactive Auto Compact 关闭
→ Manual /compact 仍存在
→ Reactive Compact 仍作为真实 API 413 的后备恢复
```

所以它不是“Collapse 不够就立刻主动 Auto Compact”的简单串行关系。API 413 路径是先
Drain Staged Collapse；仍失败时再进入 Reactive Compact。

## 当前证据矩阵

| 问题 | 状态 |
|---|---|
| `queryLoop()` 中的接入顺序 | `SOURCE` |
| Summary 不向 REPL `yield` | `SOURCE` |
| `messagesForQuery` 被替换后再请求模型 | `SOURCE` |
| Commit/Snapshot 字段和 Transcript 写入 | `SOURCE` |
| Resume 前恢复 Commit Store | `SOURCE` |
| Collapse 开启时抑制主动 Auto Compact | `SOURCE` |
| API 413 → Collapse Drain → Reactive Compact | `SOURCE` |
| 候选 Summary 后台异步生成 | `INFERENCE` |
| 精确 Token 阈值公式 | `UNKNOWN` |
| Span 选择、Risk 算法和 Summary Prompt | `UNKNOWN` |
| `projectView()` 的最终 Message Role 和拼接细节 | `UNKNOWN` |
| Commit 磁盘写入是否阻塞模型请求 | `UNKNOWN` |

## 视觉总结

![Context Collapse：分段式 Summary Commit](../../../../assets/agent-implementation-study/claude-code-transcript/04-context-collapse-summary-commit.png)

第二张图把重点收束到“完整 Transcript 与模型投影视图的分离”：

![Context Collapse：局部历史投影](../../../../assets/agent-implementation-study/claude-code-transcript/06-context-collapse-local-projection.png)

配套的 Auto Compact 学习记录：
[Auto Compact：触发判断与上下文重建](./auto-compact-trigger-and-context-rebuild.md)

## 下一学习切片

Auto Compact 已完成第一轮源码学习。下一步先复习它的 Guard Tree 和消息链重建，再学习
Reactive Compact：

1. 闭卷复述 `shouldAutoCompact()` 的触发条件；
2. 对照 `buildPostCompactMessages()` 重画新消息链；
3. 追踪 Reactive Compact 如何处理真实 API 413；
4. 完成 Context Collapse、Auto Compact 和 Reactive Compact 的最终对照。
