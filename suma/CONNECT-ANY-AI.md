# Conectá Suma en cualquier IA

El contrato del cliente es **un MCP por agente**.

```
prod:     https://app.sumanos.com/mcp/authoring/agents/<agentId>          (server id: sumanos)
develop:  https://development.sumanos.com/mcp/authoring/agents/<agentId>  (server id: sumanos-dev)
```

Auth: **OAuth** (owner/admin) o **API key admin** en `SUMANOS_KEY`.
Env del agente: `SUMANOS_AGENT_ID`. Para probar, conectá `sumanos-dev`.

Staff / operator sigue usando la URL compartida `/mcp/authoring` (no esta).

## Receta

- type: `http` / `remote`
- url prod: `https://app.sumanos.com/mcp/authoring/agents/${SUMANOS_AGENT_ID}`
- url develop: `https://development.sumanos.com/mcp/authoring/agents/${SUMANOS_AGENT_ID}`
- OAuth: sin header → login en el navegador
- API key: `Authorization: Bearer $SUMANOS_KEY` (rol admin)

### Claude Code

```bash
export SUMANOS_AGENT_ID="<agentId>"
claude --plugin-dir ./plugins/suma/adapters/claude-code
# o: /plugin install suma@sumanos
# luego: /mcp → sumanos → Authenticate
```

API key:

```bash
claude mcp add sumanos --transport http \
  https://app.sumanos.com/mcp/authoring/agents/$SUMANOS_AGENT_ID \
  --header "Authorization: Bearer $SUMANOS_KEY"
```

### Codex

Adapter: `plugins/suma/adapters/codex`.

```toml
[mcp_servers.sumanos]
url = "https://app.sumanos.com/mcp/authoring/agents/${SUMANOS_AGENT_ID}"
bearer_token_env_var = "SUMANOS_KEY"
```

OAuth: `codex mcp login sumanos` (sin key). Con key: exportá `SUMANOS_KEY`.

### opencode

```json
{
  "mcp": {
    "sumanos": {
      "type": "remote",
      "url": "https://app.sumanos.com/mcp/authoring/agents/${SUMANOS_AGENT_ID}",
      "enabled": true
    }
  }
}
```

API key: agregá `"headers": { "Authorization": "Bearer $SUMANOS_KEY" }`.

### Hermes

```yaml
mcp_servers:
  - url: https://app.sumanos.com/mcp/authoring/agents/${SUMANOS_AGENT_ID}
    headers:
      Authorization: "Bearer ${SUMANOS_KEY}"
```
