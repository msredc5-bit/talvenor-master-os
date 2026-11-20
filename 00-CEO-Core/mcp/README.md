# MCP — Model Context Protocol (Phase 9)

## MCP কী? (এক অনুচ্ছেদে)

MCP হলো AI agent-এর জন্য একটা standard plug — যেমন USB দিয়ে যেকোনো
device একই port-এ লাগে, তেমন MCP দিয়ে যেকোনো tool (Gmail, Calendar,
n8n, database) একই নিয়মে AI-এর সাথে লাগে। Client (যে চায়) আর server
(যে দেয়) JSON-RPC 2.0-তে কথা বলে — `initialize`, `tools/list`,
`tools/call`। এই folder-এ Master OS-এর নিজের ছোট MCP server + client
আছে (stdio, কোনো network নয়): server Master OS-এর ৭টা mock tool-কে
MCP tool হিসেবে দেখায়, client সেগুলোকে ডাকে।

## এই folder-এ যা আছে

- `mcp_server.py` — stdio MCP server: ৭ mock tool expose করে
  (draft-only)। live-ready gated tool (gmail_send, n8n_trigger)
  এখানে নেই — live connection শুধু ApprovalGateway দিয়ে।
- `mcp_client.py` — stdio MCP client: server subprocess হিসেবে
  চালায়, `initialize()` / `list_tools()` / `call_tool()` দেয়।
- `check_mcp.py` — self-check: server subprocess চালিয়ে initialize,
  tools/list (ঠিক ৭টা), tools/call (status_read + draft_email),
  unknown tool + bad args-এ error, ping, no-network, real store
  untouched। TEMP approvals/log path ব্যবহার করে।

## পরে আসল MCP server-এ client লাগানো (key file-এ নয়)

```python
from mcp_client import MCPClient

# উদাহরণ: একটা আসল MCP server (command + env — key শুধু env-এ)
client = MCPClient("npx", ["-y", "some-mcp-server"], env={
    "SOME_API_KEY": os.environ["SOME_API_KEY"],  # env থেকে, file-এ নয়
})
client.initialize()
print(client.list_tools())
print(client.call_tool("tool-name", {"arg": "value"}))
client.close()
```

নিয়ম: server command + env var-এর নাম README-তে লেখা যাবে, কিন্তু
key/token/URL-এর value কখনো কোনো file-এ লেখা যাবে না — শুধু
environment variable থেকে আসবে।

## অবস্থা

- MCP wiring: **CODE — Phase 9** (stdio client + server, self-check)।
- Live MCP server connection: **NOT CONNECTED** — কোনো বাইরের MCP
  server-এর সাথে এখনো যুক্ত করা হয়নি; Boss-এর সিদ্ধান্তে হবে।
- Brain এখনো mock — MCP tool-গুলো draft-only, কিছু পাঠায় না।
