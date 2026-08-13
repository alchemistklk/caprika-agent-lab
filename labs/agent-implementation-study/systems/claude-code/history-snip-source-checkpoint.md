# History Snip：选择性删除与 Resume 重放

> 研究对象：本地 Claude Code 源码快照
> 版本边界：该快照尚未被证明与本机 Claude Code `2.1.224` 完全对应。
> 实现边界：调用点、消息 ID 注入、Boundary 元数据和 Resume 过滤存在，但
> `src/services/compact/snipCompact.ts`、`snipProjection.ts` 和 `tools/SnipTool/`
> 不在当前快照中。精确工具协议和选择规则继续标记为 `UNKNOWN`。

## 核心结论

History Snip 是一种选择性历史删除机制。它允许模型引用旧 User Message 的短 ID，标记
已经失去后续价值的消息；运行时在 Provider Request 前应用这些删除：

```text
M1 M2 M3 M4 M5 M6
      └─ 已过时 ─┘

Snip 后模型视图：M1 M5 M6
```

它不生成 Summary，因此不同于 Context Collapse；它也不创建新的整体 Compact Boundary
和 Post-Compact Message Chain，因此不同于 Auto Compact。

## Agent Loop 中的位置

`src/query.ts` 在 Microcompact 之前调用：

```ts
let snipTokensFreed = 0

if (feature('HISTORY_SNIP')) {
  const snipResult =
    snipModule!.snipCompactIfNeeded(messagesForQuery)

  messagesForQuery = snipResult.messages
  snipTokensFreed = snipResult.tokensFreed

  if (snipResult.boundaryMessage) {
    yield snipResult.boundaryMessage
  }
}
```

当前顺序是：

```text
Tool Result Budget
→ History Snip
→ Microcompact
→ Context Collapse
→ Auto Compact
→ Provider Request
```

这里可以直接确认三种输出：剪除后的 `messages`、估算释放量 `tokensFreed`，以及可选的
`boundaryMessage`。

## 模型如何引用消息

`src/utils/messages.ts` 的 `appendMessageTagToUserMessage()` 只对 API-bound copy 追加：

```ts
const tag = `\n[id:${deriveShortMessageId(message.uuid)}]`
```

因此：

```text
存储消息：请分析这个错误

模型输入副本：
请分析这个错误
[id:a31f]
```

源码注释说明这些 ID 用于让 Claude 调用 Snip Tool 时引用消息。原始 Transcript Message
不会因为 ID 注入而被修改。

## 提醒、选择与应用

当前可见调用方支持以下模型：

```text
上下文持续增长且长时间未 Snip
→ 注入 Context Efficiency Nudge
→ 模型通过 SnipTool 引用旧消息 ID
→ snipCompactIfNeeded() 应用删除
```

`getContextEfficiencyAttachment()` 的注释提到大约每增加 10K Token 提醒一次，并在 Snip
Marker、Snip Boundary 或 Compact Boundary 后重置。但精确节奏位于缺失的
`shouldNudgeForSnips()` 中，当前不能把 10K 视为稳定契约。

快照中还存在 `/force-snip` 命令入口。精确 Tool Input Schema、允许选择的消息类型、
保护最近消息的规则，以及 Runtime 是否会自动补充选择，当前均为 `UNKNOWN`。

## 与 Auto Compact 的 Token 协作

History Snip 发生后，存活的 Assistant Message 可能仍携带 Snip 前的 API usage。因此
Auto Compact 使用：

```ts
tokenCountWithEstimation(messages) - snipTokensFreed
```

例如：

```text
旧 Usage：190K
Snip 释放：30K
校正估算：160K
```

如果不减去 `snipTokensFreed`，已经成功 Snip 的上下文仍可能因为旧 usage 被误判为超过
Auto Compact 阈值。

## 持久化与 Resume

Snip Boundary 保存实际删除的 UUID：

```ts
snipMetadata: {
  removedUuids: UUID[]
}
```

JSONL 是追加式存储，所以旧消息仍可留在磁盘。Resume 时
`src/utils/sessionStorage.ts` 的 `applySnipRemovals()`：

1. 收集所有 Boundary 中的 `removedUuids`；
2. 从内存 `Map<UUID, TranscriptMessage>` 删除这些消息；
3. 保存被删除消息原来的 `parentUuid`；
4. 把指向删除区间的存活消息重新连接到最近的未删除祖先；
5. 再交给 Conversation Chain 重建。

```text
Snip 前：M1 ← M2 ← M3 ← M4 ← M5
删除：        M2   M3   M4
重连后：M1 ← M5
```

只删除而不重连会让 `buildConversationChain()` 在中间缺口停止回溯，错误地孤立删除区间
之前仍应保留的消息。

## REPL、Headless 与磁盘视图

| 视图 | History Snip 后的行为 |
|---|---|
| 磁盘 JSONL | 原消息继续存在，追加记录删除 UUID 的 Boundary |
| REPL / UI | 可以保留完整 Scrollback，通过 `projectSnippedView()` 投影 |
| Provider Request | 被选中的消息不再进入模型输入 |
| Headless / SDK 内存 | 可以直接缩减 Mutable Message Store |
| Resume 内存链 | 根据 `removedUuids` 删除并跨区间重连 |

因此“Snip 删除消息”必须同时说明删除发生在哪一层。它不是简单地从所有存储和 UI 中
物理擦除历史。

## 三种机制的最小区别

| 机制 | 核心动作 | 是否生成 Summary | 主要范围 |
|---|---|---:|---|
| History Snip | 直接移除已经无用的消息 | 否 | 精确选择的旧消息或区间 |
| Context Collapse | 用 Summary 投影替代旧 Span | 是 | 一个或多个局部 Span |
| Auto Compact | 创建 Boundary 并重建消息链 | 是 | 较大的当前上下文 |

```text
History Snip    = 从工作台拿走无用草稿
Context Collapse = 把旧资料整理成摘要
Auto Compact     = 重建工作台并设置新起点
```

## 当前证据矩阵

| 问题 | 状态 |
|---|---|
| Snip 位于 Microcompact 之前 | `SOURCE` |
| Snip 返回 messages、tokensFreed 和可选 Boundary | `SOURCE` |
| API 副本注入短消息 ID | `SOURCE` |
| 原始存储消息不因 ID 注入而改变 | `SOURCE` |
| Boundary 保存 `removedUuids` | `SOURCE` |
| Resume 删除消息并重连 `parentUuid` | `SOURCE` |
| REPL 保留 Scrollback、Headless 可缩减内存 | `SOURCE` |
| SnipTool 精确输入 Schema | `UNKNOWN` |
| 消息选择、资格和保护区间算法 | `UNKNOWN` |
| Token Nudge 的最终稳定阈值 | `UNKNOWN` |
| 当前快照是否等于安装版 `2.1.224` | `UNKNOWN` |

## 第一阶段学习成果 — 2026-08-12

本阶段按照共享的
[Agent Implementation Learning Pattern](../../LEARNING-PATTERN.md)，完成了
`伪代码 → 抽象规范 → Claude Code 调用侧实现 → 案例与反例 → Teach-back` 的第一轮。

### 我的原始 Teach-back

1. History Snip 解决了在对话过程中清理无关对话和工具历史的问题，提高上下文的
   利用效率。
2. 它保存被删除消息的 Message ID，恢复时使用同一份持久化结果。
3. 如果被删除消息的依赖关系没有处理干净，会让模型误解上下文。

### 校准后的三句话心智模型

> History Snip 从模型有效上下文中精确删除已经无关的对话或工具历史，提高有限
> 上下文的利用效率。它通过 Snip Boundary 持久化 `removedUuids`，Resume 时重放
> 相同删除决定并修复 `parentUuid`。它最大的风险是破坏消息的结构或语义依赖，
> 造成孤儿工具消息、上下文误解或 Provider 拒绝。

### 已建立的抽象规范

History Snip 可以抽象成一个 `SelectiveHistoryRemoval` 合约：

```text
SelectiveHistoryRemoval.apply({
  messages,
  selection,
  protectedRegion,
  protocolConstraints
}) ->
    Unchanged
  | Rejected { reason }
  | Removed {
      messages,
      removedIds,
      tokensFreed,
      replayEvidence
    }
```

恢复不是重新计算选择，而是重放已经持久化的决定：

```text
load Transcript
→ collect Boundary.removedUuids
→ remove the same message identities
→ relink parentUuid across removed ranges
→ rebuild the effective conversation chain
```

### 已掌握的六个不变量

1. **稳定身份不变量**：按 UUID 删除，不能依赖会随投影和分支变化的数组位置。
2. **顺序不变量**：未删除消息之间的相对顺序不能改变。
3. **引用不变量**：存活消息的 `parentUuid` 不能指向已经删除的节点。
4. **工具协议不变量**：`tool_use` 与对应的 `tool_result` 不能被拆成孤儿消息。
5. **重放不变量**：相同 Transcript 加相同 Boundary 应恢复出相同的有效消息链。
6. **Token 决策不变量**：Auto Compact 的后续判断必须扣除 `snipTokensFreed`，
   不能继续把 Snip 前的旧 API Usage 当成当前上下文大小。

### 结构安全与语义安全

本阶段通过以下工具调用案例区分了两层安全性：

```text
A: User prompt
B: Assistant tool_use(T1)
C: User tool_result(T1)
D: Assistant analysis based on C
E: User follow-up
```

- 删除 `B` 或 `C` 中的任意一个都会破坏 Provider 工具协议。
- `B + C` 是最小的协议安全删除范围。
- 如果 `D` 强依赖工具结果，删除 `B + C` 虽然结构合法，语义仍可能不连贯；删除
  整个旧调查过程通常还需考虑 `D`。
- 工具协议配对可以由确定性代码验证；后续自然语言结论的语义依赖更难判断。

当前快照缺少核心选择模块，因此只能把这些写成通用不变量；Claude Code 如何扩张、
拒绝或修复具体删除范围仍为 `UNKNOWN`。

### Resume 重连案例

```text
原消息链：M1 ← M2 ← M3 ← M4 ← M5 ← M6
删除范围：          M3   M4
恢复结果：M1 ← M2 ← M5 ← M6
```

`M5.parentUuid` 必须从 `M4` 修复为 `M2`。如果错误地设为 `null`，从 `M6`
回溯只会得到 `M5 ← M6`，使本应保留的 `M1 ← M2` 也从当前分支中消失。

如果更早的 Compact Boundary 已使某个被删节点不在加载结果中，重连过程只能跨越
当前仍有父链接证据的节点。遇到证据缺口时停止并以 `null` 作为链根，不能猜测不存在
于当前加载视图中的祖先关系。

### 第一阶段掌握状态

| 学习环节 | 状态 | 说明 |
|---|---|---|
| 伪代码与直觉模型 | `COMPLETE` | 能解释选择性删除、Boundary 和 Resume 重放 |
| 通用抽象规范 | `COMPLETE` | 能说明输入、输出、信息政策和关键不变量 |
| Claude Code 调用侧 | `COMPLETE` | 能追踪短 ID、`snipCompactIfNeeded()` 和三个返回产物 |
| Resume 重放 | `COMPLETE` | 能解释 `removedUuids`、删除和 `parentUuid` 重连 |
| Token 协作 | `COMPLETE` | 能解释 `snipTokensFreed` 对 Auto Compact 的校正作用 |
| 工具协议反例 | `COMPLETE` | 能识别最小协议安全范围与语义依赖风险 |
| Snip Tool 和选择算法 | `UNKNOWN` | 当前源码快照缺失核心实现 |
| Protected Tail 与范围归一化 | `UNKNOWN` | 等待更完整源码或可验证 Runtime Trace |

**阶段结论：** History Snip 第一轮学习通过，但完整实现研究尚未结束。后续找到核心
模块后，需要补完选择协议、Protected Tail、范围归一化与语义依赖处理，再进行第二轮
闭卷复测。

## 后续深入 TODO

配套基础比较：
[Tool Message Dependencies and Context Reduction](./tool-message-dependencies-and-context-reduction.md)

- [ ] 找到包含 `snipCompact.ts`、`snipProjection.ts` 和 `SnipTool` 的完整源码版本。
- [ ] 记录 SnipTool 的 Input Schema、权限规则和 Tool Result。
- [ ] 追踪模型发出 SnipTool 后，Marker、Boundary 和删除实际发生的完整时序。
- [ ] 验证哪些消息允许删除，哪些消息属于 Protected Tail。
- [ ] 解释多个不连续 Snip 区间如何合并、排序和去重。
- [ ] 验证 Snip 是否保持 Tool Use / Tool Result 协议完整性。
- [ ] 分别构造 REPL、Headless SDK 和 `/resume` 的 Before/After 案例。
- [ ] 研究 Snip 与 Microcompact 同时发生时的组合语义。
- [ ] 生成一张 History Snip 视觉总结，并添加闭卷复习题。
