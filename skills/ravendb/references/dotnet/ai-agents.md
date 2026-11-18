# AI Agents from .NET (client 7.2+; sub-agents client 7.2.2+)

`store.AI` wraps the HTTP surface in `../ai-agents.md`. Calls and examples: `../client-docs.md` (Creating AI agents: API). Sub-agents: `../client-docs.md` (Multi-agents). Stored messages `(7.2.5+)` `(client 7.2.5+)`: `../client-docs.md` (Reading conversation history). Vector search from LINQ: `../rql-docs.md` (Vector search).

## Traps

- **A throwing `Handle` or `Receive` callback does not throw in your code.** The default, `AiHandleErrorStrategy.SendErrorsToModel`, sends the exception text to the model and the turn goes on. Pass `AiHandleErrorStrategy.RaiseImmediately` to get the exception.
- **`Receive` leaves the tool call open**, so `RunAsync` returns `Status == AiConversationResult.ActionRequired`, not `Done`: check `Status` before reading `Answer`. Close the call with `AddActionResponse(toolId, response)`, from this or a new `Conversation` instance on the same id, then run again.
- **A sub-agent's action registers under its path** `(client 7.2.2+)`: `Handle("<sub-agent-id>/<ActionName>", ...)`. Under the bare action name the callback never fires.
