# 🔌 Conectá Sumanos Builder en CUALQUIER IA

Lo que viaja a todas las IAs es **UNA sola cosa: el MCP** (1 URL + 1 key).
**No hay un "plugin" único** que se instale en todas — el formato *plugin* es solo de
Claude Code. Pero **todas las IAs apuntan al mismo MCP remoto**; lo único que cambia es
el archivo de config de cada una. Acá están todos, copy-paste.

## Lo único que necesitás
- **URL:** `https://api.sumanos.com/mcp/authoring`  (Bearer — sirve para TODAS las IAs)
- **Key:** tu **operator key** (la mintea el superadmin, scoped a 1 org) o una **api_key de cliente**.
  Guardala en la env var `SUMANOS_KEY`.
- *(Solo Claude Code, opcional: login por navegador SIN key — usa `https://app.sumanos.com/mcp/authoring`.)*

## 🧩 Receta genérica (cualquier IA con MCP remoto: Cursor, Windsurf, VS Code, etc.)
En la config MCP de la herramienta, agregá un server **remoto/http** así:
- type: `http` (o `remote`)
- url: `https://api.sumanos.com/mcp/authoring`
- header: `Authorization: Bearer <tu-key>`

Si la IA soporta "remote MCP server", esto alcanza. Lo demás son las variantes exactas:

---

### 🟣 Claude Code — CLIENTE (login navegador, sin key)
Instalá el plugin (trae skills + comandos). Sin header → dispara OAuth:
```bash
claude --plugin-dir ./plugins/sumanos-builder      # local
# o publicado:  /plugin install sumanos-builder@sumanos
```
> `.mcp.json` del plugin: `url = https://app.sumanos.com/mcp/authoring`, **sin** Authorization.

### 🟣 Claude Code — OPERADOR (con key)
```bash
claude mcp add --transport http sumanos \
  https://api.sumanos.com/mcp/authoring \
  --header "Authorization: Bearer $SUMANOS_KEY"
```

### 🟢 Codex — `~/.codex/config.toml`
```toml
[mcp_servers.sumanos]
url = "https://api.sumanos.com/mcp/authoring"
bearer_token_env_var = "SUMANOS_KEY"
```

### 🔵 opencode — `opencode.json`
```json
{
  "mcp": {
    "sumanos": {
      "type": "remote",
      "url": "https://api.sumanos.com/mcp/authoring",
      "headers": { "Authorization": "Bearer {env:SUMANOS_KEY}" }
    }
  }
}
```

### ⚙️ Hermes (el engine) — `config.yaml`
```yaml
mcp_servers:
  - url: https://api.sumanos.com/mcp/authoring
    headers:
      Authorization: "Bearer ${SUMANOS_KEY}"
```

---

## ¿Qué da cada tier?
| Tier | Cómo conecta | Qué puede |
|---|---|---|
| **Cliente** | OAuth (Claude Code) o api_key de cliente (Bearer) | tools de autoría; lo de alto riesgo queda en cola de aprobación |
| **Operador** | operator key (Bearer) | apply directo + las 6 workspace tools sobre la VM por SSM |

## 📦 Resumen
- **El "paquete universal" = URL + key.** Funciona en toda IA con MCP remoto.
- **El plugin de Claude Code** = ese MCP **+** skills + comandos `/sumanos-*` (extra, solo Claude Code).
- Las demás IAs: pegás el bloque de arriba, listo.
