# AI Agents from Python (client 7.2+; sub-agents and typed parameters client 7.2.3+)

`store.ai` wraps the HTTP surface in `../ai-agents.md`. Calls and examples: `../client-docs.md` (Creating AI agents: API). Vector search: `../rql-docs.md` (Vector search).

## Traps

- **A throwing callback does not throw in your code** under `AiHandleErrorStrategy.SEND_ERRORS_TO_MODEL`, the default for `receive`: the exception text goes to the model and the turn goes on. `handle` takes the strategy as a required third argument; pass `RAISE_IMMEDIATELY` to get the exception.
- **`receive` leaves the tool call open**, so `run()` returns `status == AiConversationStatus.ACTION_REQUIRED`, not `DONE`: check `status` before reading `answer`. Close the call with `chat.add_action_response(request.tool_id, result)`, then run again.

## Python names

Use these with the C# examples on the routed pages.

- Sub-agents `(client 7.2.3+)`: `sub_agents` on `AiAgentConfiguration`. `../client-docs.md` (Multi-agents).
- Stored messages `(7.2.5+)` `(client 7.2.6+)`: `store.ai.get_conversation_messages(conversation_id)`. `../client-docs.md` (Reading conversation history).
- Attachments `(client 7.2.3+)`: `chat.add_attachment(name, bytes_or_stream, content_type)`, `chat.copy_attachment_from(doc_id, file_name)`.
- `store.ai.delete_agent(identifier)`, `chat.add_artificial_action_with_response(tool_id, response)`, `chat.on_unhandled_action`.
