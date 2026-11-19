# AI Agents from Node.js (client 7.2+)

`store.ai` wraps the HTTP surface in `../ai-agents.md`. Calls and examples: `../client-docs.md` (Creating AI agents: API). Vector search: `../rql-docs.md` (Vector search).

## Traps

- **A throwing `handle` or `receive` callback does not throw in your code.** The default, `AiHandleErrorStrategy.SendErrorsToModel`, sends the error text to the model and the turn goes on. Pass `AiHandleErrorStrategy.RaiseImmediately` as the third argument to get the error.
- **`receive` leaves the tool call open**, so `run()` resolves with `status: "ActionRequired"`, not `"Done"`: check `status` before reading `answer`. Close the call with `chat.addActionResponse(request.toolId, result)`, then run again.
