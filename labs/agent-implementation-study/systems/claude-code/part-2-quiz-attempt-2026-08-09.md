# Part 2 Quiz Attempt — 2026-08-09

> 对应题库：[Part 2 Quiz](./part-2-quiz.md)
> 研究对象：本地 Claude Code 源码快照
> 本文保存第一次真实作答、阶段评分和心智模型校准。它不是标准答案文件。

## 作答状态

| 部分 | 状态 | 暂定得分 |
|---|---|---:|
| A. 主动回忆 | 已作答 | 5.5 / 12 |
| B. 案例推导 | 已作答 | 5 / 16 |
| C. 源码定位 | 未作答 | 暂不评分 |
| D. 跨实现迁移 | 未作答 | 暂不评分 |
| **闭卷阶段合计** | **A + B** | **10.5 / 28（约 38%）** |

当前不能计算完整的 50 分成绩，也不能判定 Part 2 是否通过。B4 和 C3 涉及尚未详细
学习的 Context Compression / Collapse，已登记为下一学习 TODO，不能简单归类为遗忘。

## A. 主动回忆：原始作答与校准

### A1 — Transcript 为什么不能按行直接发送

**我的原始回答：**

1. 因为用户的问题并不是一个线性的，是一个拓扑结构；
2. 一个最新执行单元包含 `user message -> assistant message -> tool message`；
3. 如果存在 Subagent 和 Parallel Tools，会得到不正确的上下文。

**评估：1 / 2。** 已认识到持久化拓扑不是简单线性聊天，但第二点没有直接回答为何
不能按行转换，且缺少非消息事件、分支选择和 Context Pipeline。

**校准后的心智模型：**

```text
JSONL 包含消息与辅助事件
→ 同一文件可能存在多条分支和 Sidechain
→ 必须选择当前 Leaf 并恢复有效链
→ 还要经过 Context Transformation
→ 才形成模型请求
```

### A2 — `uuid`、`parentUuid`、`sessionId`

**我的原始回答：**

- `uuid` 是每条 Message 的 ID；
- `parentUuid` 是每个 Message 的上一条消息；
- `sessionId` 是 Claude Session 的唯一 ID。

**评估：1.5 / 2。** 基本正确。`parentUuid` 更准确地表示父消息关系，不等于 JSONL
中物理上的上一行。

### A3 — Leaf

**我的原始回答：**

> Leaf 是最后的用户提问产生的数据集合；多个 Leaf 来自并行工具和 Subagent。

**评估：0.5 / 2。** Leaf 不是一轮数据集合，而是消息图中的分支末端或恢复候选 Tip。
多个 Leaf 还可能来自 Rewind、Fork、中断或持久化技术分叉。

### A4 — Resume、Rewind、Fork Session

**我的原始回答：**

```text
Resume：对话记录、工具记录、sessionId 不变；新开一个线程
Fork Session：对话记录、工具记录不变；sessionId 变化
Rewind：未完成
```

**评估：0.5 / 2。** “新开线程”应校准为重建进程、Runtime 和 Agent Loop。Fork 复制
的是选中的历史范围，不应笼统认为所有记录不变；Rewind 仍需重新学习。

| 操作 | Session ID | Transcript | 当前分支 |
|---|---|---|---|
| Resume | 保持 | 继续读取同一会话记录 | 恢复已有有效链 |
| Rewind | 保持 | 同一 Transcript 保留旧分支并写入新分支 | Tip 转到新 Leaf |
| Fork Session | 新建 | 新 Transcript 复制选中历史 | 在新会话中继续 |

### A5 — 三种数据视图

**我的原始回答：**

- 持久化视图：Agent 执行过程中的所有记录，包括完整对话和大型工具执行；
- 运行时视图：当前上下文下的 User、Assistant 和完整 Tool Result；
- 模型视图：有效上下文，过长时会压缩或替换。

**评估：1 / 2。** 三视图框架基本形成。但运行时视图不保证始终包含完整 Tool Result，
它可能已经应用持久化替换决定、分支选择或投影。

### A6 — Tool Result Replacement 与 Context Collapse

**我的原始回答摘要：**

- Tool Result Replacement 替换大段工具结果，避免工具输出占满上下文；
- Context Collapse 替换 User、Assistant 和 Tool Result，位于 Microcompact 之后。

**评估：1 / 2。** 总体目的和 Collapse 的大致位置已记住，但触发时机、持久化记录和
State/View 边界仍不明确。这部分已进入下一学习 TODO。

## B. 案例推导：原始作答与校准

### B1 — Leaf 与 Sidechain

**我的原始回答：**

```text
从 isSidechain=false 恢复
正序链：F -> D -> A
不能选择 E，因为它来自 Subagent
F 断链会导致上下文缺失
```

**评估：2.5 / 4。** 应明确选择 `F`。`F -> D -> A` 是回溯方向，反转后的正序链是：

```text
A -> D -> F
```

排除 Sidechain 和识别断链风险是正确的。

### B2 — Resume、Rewind 与 Fork

**我的原始回答：**

```text
Resume：M1 -> M2 -> M3 -> M4 -> M5
Rewind：M3 -> M4 -> M5
Fork：M1 -> M2 -> M3
```

**评估：0.5 / 4。** 只写出了部分消息片段，没有回答 Session ID、Transcript 和分支
拓扑。Rewind 的正确结构应体现旧分支仍然保留：

```text
原分支：M1 -> M2 -> M3 -> M4  -> M5
新分支：M1 -> M2 -> M3 -> M4' -> M5'
```

Fork 则需要新 Session ID、新 Transcript，并从复制的 `M1...M3` 继续。

### B3 — 并行工具技术分叉

**我的原始回答摘要：**

- 单父链遗漏另一侧是因为两个工具并行；
- `response-123` 表示同一次响应，`tool-A/tool-B` 表示具体 Tool Call；
- 模型协议形状写成 `tool-A, tool-B -> aa, ab -> response-123`；
- 缺失 `rb` 未作答。

**评估：1.5 / 4。** ID 基本识别正确，但需要补充实际机制：兄弟 Assistant Block
拥有不同 UUID，共享 Provider `message.id`，各自的 Tool Result 又挂在不同 Assistant
UUID 下，因此只沿一条 Parent Chain 会漏掉另一侧。

恢复后的语义协议视图应接近：

```text
Assistant: tool_use A + tool_use B
User:      tool_result A + tool_result B
```

若 `rb` 缺失，不能仅靠正常路径保证结果完整、排序正确、不会重复执行或 Resume 后仍能
保持正确关联；这些需要异常 Case 验证。

### B4 — Context Reduction 时序

**我的原始回答：**

```text
完整 Tool Result：Agent 主动读取工具执行结果
Budget：工具执行完成时
Pipeline 顺序：不知道
模型视图：Auto Compact + M7
200K 不是契约：因为太大
```

**评估：0.5 / 4。** 已意识到工具结果先由 Runtime 收集，但详细时序和内部配置边界
尚未掌握。当前只能保留以下高层顺序，详细语义等待下一学习单元校准：

```text
第 N 轮执行工具并收集完整结果
→ 结果进入下一 State
→ 第 N+1 轮构造 messagesForQuery
→ Tool Result Budget
→ History Snip
→ Microcompact
→ Context Collapse
→ Auto Compact
→ deps.callModel()
```

`200K` 不能视为稳定公开契约，是因为它属于当前源码快照中的内部默认值，可能受到动态
配置、工具级例外和版本变化影响，而不是因为数值本身太大。

## 本次测验暴露的知识结构

### 已形成的能力

- 能区分持久化、运行时和模型三种数据视图；
- 能识别 Message、Parent 和 Session 的基本身份层次；
- 知道 Sidechain 不应成为主会话默认 Tip；
- 知道 Tool Result Replacement 和 Context Collapse 都服务于模型上下文控制；
- 已开始区分语义分支与并行工具技术分叉。

### 下一步需要巩固

1. Leaf 的严格定义；
2. Parent 回溯方向与最终正序消息链；
3. Resume、Rewind、Fork 的不变量；
4. Provider Message ID、Assistant UUID 和 Tool Use ID 的关联；
5. Context Pipeline 的精确顺序与每步契约；
6. 内部默认值和公开稳定契约的区别。

## 下一次作答计划

1. 先复习 A3、A4、B1、B2 和 B3；
2. 完成 Context Compression / Collapse 源码学习；
3. 24 小时后只重做错题；
4. 完成 C 的源码定位；
5. 最后用 Codex、Pi 或 OpenCode 完成 D 的跨实现迁移。

## 完成记录

```text
第一次闭卷日期：2026-08-09
第一次闭卷得分：10.5 / 28
主要错题类型：生命周期边界、拓扑方向、Context Pipeline、异常路径

24 小时复测日期：
复测得分：

源码定位完成日期：
跨 Agent 迁移对象：
```
