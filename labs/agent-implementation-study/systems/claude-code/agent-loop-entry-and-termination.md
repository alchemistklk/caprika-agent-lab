# Claude Code Agent Loop：入口委托与终止机制

> Evidence: `SOURCE` from the local Claude Code source snapshot. The snapshot
> has not been proven to match the locally installed Claude Code runtime
> version exactly.

## 本次研究的问题

1. `query()` 为什么把执行委托给 `queryLoop()`？
2. `consumedCommandUuids` 中的 UUID 是什么？
3. `terminal` 是什么？
4. 不同 `Terminal reason` 分别代表什么？
5. 哪些情况下 Agent Loop 不会进入下一轮？

## 1. `query()` 的职责

```ts
const terminal = yield* queryLoop(params, consumedCommandUuids)
```

`query()` 是 Agent Loop 的外围入口，主要负责：

- 转发 `queryLoop()` 产生的流式消息；
- 接收 `queryLoop()` 最终返回的终止结果；
- 将循环期间消费的异步命令更新为 `completed`。

真正的模型调用、工具执行和循环状态转换位于 `queryLoop()`。

## 2. UUID 的含义

`uuid` 是命令队列中一条命令的唯一 ID，用于追踪：

```text
started → completed
```

实际输入包括：

- 用户在 Agent 执行期间追加的新指令；
- Subagent 或后台 Agent 完成后发来的 `task-notification`；
- 其他进入命令队列、准备放入下一轮上下文的异步输入。

它不是 Session ID、Agent ID 或 Tool Use ID。

如果 `queryLoop()` 抛出异常或被外部关闭，外围的 `completed` 通知不会执行。此时可能留下 `started` 但没有 `completed`，表示该命令对应的执行没有正常结束。

## 3. Terminal 的含义

`Terminal` 是 Agent Loop 的终止结果，回答：

> Agent Loop 为什么不再进入下一轮？

它不是操作系统终端。这里的 `Terminal` 来自状态机语义：

```text
Continue transition → 构造新 State，继续下一轮
Terminal transition → 返回终止原因，结束循环
```

在 `AsyncGenerator<YieldedMessage, Terminal>` 中：

- `YieldedMessage` 是运行期间不断输出的流式消息；
- `Terminal` 是生成器结束时的最终 `return` 值。

因此 `yield* queryLoop(...)` 既转发内层生成器产生的消息，也取得它最后返回的 `Terminal`。

## 4. 主要终止原因

| Reason | 意义 |
|---|---|
| `completed` | 循环正常结束；通常是模型没有产生需要跟进的工具调用，Hook 和恢复机制也未要求继续 |
| `max_turns` | 达到允许的最大 Agent 轮数，系统阻止继续循环 |
| `aborted_streaming` | 模型正在流式生成时收到用户或系统的中断信号 |
| `aborted_tools` | 模型已经请求工具，但工具执行期间收到中断信号 |
| `model_error` | 模型调用、流式处理或相关运行时代码出现不可恢复异常 |
| `prompt_too_long` | API 判定上下文过长，并且上下文压缩等恢复策略失败 |
| `blocking_limit` | 调用模型之前，本地 Token 检查已经达到硬限制，因此提前阻止请求 |
| `stop_hook_prevented` | 模型准备结束时，Stop Hook 明确禁止后续继续 |
| `hook_stopped` | 工具相关 Hook 要求停止后续执行 |

`completed` 表示 Agent Loop 正常结束，但不一定等于业务任务完全成功。某些已经被转换为可展示 Assistant 错误消息的 API 错误，也可能在消息输出后正常结束循环。

## 5. 不会进入下一轮的情况

Agent Loop 在以下四类情况下返回 `Terminal`：

### 模型已经完成

- 没有产生需要跟进的 `tool_use`；
- Stop Hook 没有要求重试；
- Token Budget 和恢复机制没有要求继续。

### 达到执行限制

- 达到 `max_turns`；
- 本地检查达到 `blocking_limit`；
- 上下文过长并且自动恢复失败。

### 用户或系统主动中断

- 模型流式生成期间中断；
- 工具执行期间中断。

### 异常或 Hook 明确终止

- 模型调用发生不可恢复异常；
- Stop Hook 或工具相关 Hook 要求停止。

## 6. 哪些情况会进入下一轮

只有仍需处理时，循环才会构造新的状态：

```ts
state = next
```

典型情况包括：

- 模型产生 `tool_use`，工具结果需要交还模型；
- Stop Hook 返回阻塞错误，要求模型修正；
- Token Budget 决定继续；
- 输出 Token 达到上限，系统注入恢复消息；
- 上下文压缩或模型 fallback 后需要重试；
- 新的用户指令或后台 Agent 通知被加入上下文。

## 核心理解

```text
UUID 追踪的是：哪一条异步命令被处理了。

Terminal 记录的是：Agent Loop 为什么结束。

State 决定的是：Agent Loop 是否进入下一轮。
```

## Follow-up TODO：完整会话记录如何转换为有效上下文

- [ ] 追踪本地 JSONL transcript 到 `queryLoop()` 中 `messages` 的加载和消息链重建过程。
- [ ] 解释 `messages` 如何经过 compact boundary、tool-result budget、History Snip、Microcompact、Context Collapse 和 Auto Compact，最终形成 `messagesForQuery`。
- [ ] 区分以下三种数据视图及其生命周期：
  - 本地保存的完整 transcript；
  - Agent Loop 内存中的当前消息链；
  - 实际传给 `deps.callModel()` 的有效上下文。
- [ ] 记录每个转换阶段的输入、输出、触发条件、信息损失和对应源码位置。
- [ ] 用一个包含工具调用和上下文压缩的最小会话，验证 `/resume` 后重建的消息链与模型实际收到的上下文之间的关系。

完成产物：一张转换流程图、一张数据结构对照表，以及每个关键阶段的核心代码截图。
