# Connect any AI to Suma

```txt
MCP server id: sumanos (prod) | sumanos-dev (develop)
Endpoint prod: https://app.sumanos.com/mcp/authoring/agents/${SUMANOS_AGENT_ID}
Endpoint dev:  https://development.sumanos.com/mcp/authoring/agents/${SUMANOS_AGENT_ID}
Auth:          OAuth (owner/admin) or admin API key in SUMANOS_KEY
Agent env:     SUMANOS_AGENT_ID
```

Each host uses its own adapter. The server rejects member, operator, and superadmin on this URL.
