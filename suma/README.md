# Suma

Suma conecta tu IA de coding con Sumanos para leer, ajustar y reparar agentes de forma segura.

La idea simple:

```txt
Suma = plugin/paquete
sumanos = MCP server id
connect / improve = acciones del usuario
```

```txt
MCP server id: sumanos
Endpoint:      https://api.sumanos.com/mcp/authoring
Env var:       SUMANOS_KEY
```

## Qué incluye hoy

```txt
plugins/suma/
├─ .claude-plugin/plugin.json
├─ .mcp.json
├─ skills/
├─ commands/
└─ docs/
```

El adapter Claude Code vive en la raíz por compatibilidad histórica. El objetivo siguiente es separar `core/` + `adapters/` como describe `docs/architecture.md`.

## Comandos Claude Code

- `/suma-connect` — conectar Suma con login en navegador.
- `/suma-check` — revisar estado antes de tocar nada.
- `/suma-improve` — mejorar un agente Sumanos.
- `/suma-fix` — reparar algo roto.
- `/suma-install` — instalar una capacidad aprobada.
- `/suma-report` — resumir estado, cambios y próximos pasos.

## Conectar como cliente

Claude Code puede autenticarse por navegador usando el MCP sin header:

```bash
claude --plugin-dir ./plugins/suma
/plugin install suma@sumanos
```

El `.mcp.json` usa `https://app.sumanos.com/mcp/authoring` por OAuth/browser-login cuando corresponde.

## Conectar como operador

```bash
export SUMANOS_KEY="tu_operator_key"

claude mcp add --transport http sumanos \
  https://api.sumanos.com/mcp/authoring \
  --header "Authorization: Bearer $SUMANOS_KEY"
```

## Codex

Hasta publicar el adapter Codex, usar MCP directo:

```toml
[mcp_servers.sumanos]
url = "https://api.sumanos.com/mcp/authoring"
bearer_token_env_var = "SUMANOS_KEY"
```

Más detalle: `docs/codex.md`.

## Documentación interna

- `docs/architecture.md` — arquitectura, naming e invariantes.
- `docs/codex.md` — Codex plugin/MCP/marketplace local.
- `docs/operations.md` — runbook para operar agentes.
- `CONNECT-ANY-AI.md` — recetas rápidas por host.
- `TESTING.md` — pruebas E2E y protocolo MCP.

## Reglas

- No hardcodear keys.
- No usar nombres de prototipo en docs nuevas.
- `sumanos` es el server id del MCP.
- `Suma` es el producto/plugin.
- `/mcp/authoring` no cambia sin spec nueva.
