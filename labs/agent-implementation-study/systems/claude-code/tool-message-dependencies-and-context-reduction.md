# Tool Message Dependencies and Context Reduction

> Study role: prerequisite comparison between History Snip and Microcompact.
> Evidence boundary: the message protocol is a general Agent abstraction; the
> Claude Code mappings cite the current local source snapshot. Exact History
> Snip selection and Protected Tail behavior remain `UNKNOWN` because their
> core modules are absent from the snapshot.

## The Basic Tool Exchange

```text
U1  User Message
    "Read config.ts"

A1  Assistant Message
    text: "I will inspect the file."
    tool_use { id: T1, name: Read, input: ... }

U2  User Message
    tool_result { tool_use_id: T1, content: ... }

A2  Assistant Message
    "The problem is in the database configuration."
```

`tool_result` uses the API `user` role because it is external input returned to
the Assistant after the runtime executes the requested action. It is not a
claim that a human manually wrote the result.

## Three Dependency Systems

| Dependency | Concrete identity | Connects | Main purpose |
|---|---|---|---|
| Conversation graph | `message.uuid` / `parentUuid` | Whole transcript messages | Resume, Leaf reconstruction, Fork, Rewind, Snip relinking |
| Tool protocol | `tool_use.id` / `tool_result.tool_use_id` | Tool request and result content blocks | Keep provider messages structurally valid |
| Semantic reasoning | Usually implicit natural-language dependence | Tool result and later Assistant analysis | Preserve the evidence needed to understand or verify a conclusion |

The IDs are not interchangeable:

```text
parentUuid != tool_use_id
```

The first two dependencies are explicit and mechanically checkable. The third
is usually implicit and therefore harder to validate deterministically.

## Hard Protocol Dependency

```text
Assistant tool_use { id: T1 }
             ⇅
User tool_result { tool_use_id: T1 }
```

For completed historical exchanges, this pair is the smallest protocol unit.
Context reduction must not leave an orphan result or an unresolved historical
request:

```text
Invalid: tool_result(T1) without tool_use(T1)
Invalid: completed historical tool_use(T1) without tool_result(T1)
```

A currently executing tool request can temporarily lack a result in runtime
state. That transient state must not be confused with a complete historical
message chain prepared for a new provider request.

## Soft Semantic Dependency

```text
tool_result(T1)
      ↓
Assistant: "Based on the file, the error is on line 20."
```

The later Assistant message may depend strongly on the result without storing
an explicit `dependsOn: T1` field. Consequently, a transformation may remain
protocol-valid while becoming semantically confusing.

Example:

```text
Delete:  tool_use(T1) + tool_result(T1)
Retain:  "Based on the file..."
```

The provider can accept this chain, but the model can no longer inspect the
evidence behind the retained conclusion.

## How Reduction Mechanisms Treat the Exchange

| Mechanism | Main transformation | Tool pair | Later Assistant analysis | Main information loss |
|---|---|---|---|---|
| Tool Result Replacement | Replace large `tool_result.content` with a smaller persisted reference or substitute | Retained | Retained | Full payload leaves the current model view |
| Microcompact | Clear or replace eligible old tool-result payloads | Retained | Retained | Model cannot re-inspect old raw output |
| History Snip | Remove selected messages or ranges | Must be removed or retained as a valid unit | May remain, but can become semantically unsupported | Selected original messages have no summary substitute |
| Context Collapse | Project an old span into a summary | Original pair can leave the model view together | Its useful conclusion can be represented in the summary | Original detail is reduced to summary semantics |
| Auto Compact | Rebuild a larger context around a compact summary boundary | Old exchange can be represented by the rebuilt summary chain | Important conclusions should survive through summary generation | Broad historical detail is compressed |

## The Microcompact Intuition

Microcompact does not need to remove the Assistant message that requested the
tool. It can preserve the protocol shell and reduce only the expensive payload:

```text
Before:
  Assistant tool_use { id: T1, name: Read, input: ... }
  User tool_result { tool_use_id: T1, content: <100K chars> }

After:
  Assistant tool_use { id: T1, name: Read, input: ... }
  User tool_result { tool_use_id: T1, content: <cleared/replacement text> }
```

This retains three facts:

1. the Assistant requested a tool;
2. the runtime returned a result;
3. request and result still match through `T1`.

It gives up the model's ability to re-read the complete old payload. A later
Assistant conclusion may remain as a useful semantic residue, but it is not a
lossless substitute for the original evidence.

## Safe-Boundary Checklist

For every context-reduction mechanism, ask two groups of questions.

### Protocol safety

1. Does every visible `tool_result` have its matching `tool_use`?
2. Does a completed historical `tool_use` still have a result?
3. Does the transformation cut between request and result?
4. Are message ordering and provider role constraints still valid?

### Semantic safety

1. Does a retained Assistant conclusion depend on removed evidence?
2. Can the model still understand where the conclusion came from?
3. Will the model need to re-check the raw result later?
4. Should the payload be retained, externally referenced, summarized, cleared,
   or should the whole investigation span be removed?

## Compact Mental Model

```text
Assistant tool_use
        ⇅ hard, machine-checkable protocol dependency
User tool_result
        ↓ soft, often implicit semantic dependency
Assistant analysis
```

Context reduction must first preserve hard protocol validity, then deliberately
choose how much semantic evidence to retain.

## Claude Code Source Pointers

- The API message normalization and tool block handling are in
  `src/utils/messages.ts`.
- History Snip runs before Microcompact in `src/query.ts`.
- History Snip Resume replay removes stable message UUIDs and repairs
  `parentUuid` in `src/utils/sessionStorage.ts`.
- The precise History Snip rule for extending or rejecting a range around tool
  exchanges remains `UNKNOWN` in this snapshot.

## Visual Summary

![Tool message dependencies and context reduction](../../../../assets/agent-implementation-study/claude-code-transcript/07-tool-message-dependencies-and-context-reduction.png)
