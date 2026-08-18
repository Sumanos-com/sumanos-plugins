# Sumanos — marketplace de plugins

Publica **Suma**: el plugin para conectar Claude Code, Codex, opencode o Hermes a **un** agente Sumanos.

## Instalar en Claude Code

```bash
/plugin marketplace add Sumanos-com/sumanos-plugins
/plugin install suma@sumanos
```

Luego, en el dashboard (Connectors) copiá el `agentId` y autenticá:

```bash
export SUMANOS_AGENT_ID="<agentId>"
# OAuth (owner/admin):
#   /mcp → sumanos → Authenticate
# o API key admin:
export SUMANOS_KEY="sk_live_..."
```

## Entornos

| Server | URL |
|---|---|
| `sumanos` | `https://app.sumanos.com/mcp/authoring/agents/${SUMANOS_AGENT_ID}` |
| `sumanos-dev` | `https://development.sumanos.com/mcp/authoring/agents/${SUMANOS_AGENT_ID}` |

Para probar usá **sumanos-dev**. Prod es **sumanos**.

## Qué trae

```txt
/suma-connect  conectar
/suma-check    revisar sin tocar
/suma-improve  mejorar
/suma-fix      reparar
/suma-install  instalar capacidad
/suma-report   explicar estado
```

Owner/admin en la URL dedicada puede SOUL, modelo, plugins del catálogo, keys, skills y VM. Member queda afuera.

## Codex

```bash
codex plugin add suma-codex@sumanos
```

La fuente de trabajo vive en `sumanos-agents/plugins/suma/`. Este repo es la copia publicable.
