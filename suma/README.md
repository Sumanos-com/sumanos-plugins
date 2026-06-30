# Suma

Suma conecta tu IA de coding con Sumanos para leer, ajustar y reparar agentes de forma segura.

```txt
Producto:      Suma
Plugin slug:   suma
MCP server id: sumanos
Endpoint:      https://api.sumanos.com/mcp/authoring
Env var:       SUMANOS_KEY
```

## Estructura

```txt
plugins/suma/
├─ core/                 # contrato neutral: manifest, skills, prompts, docs, MCP metadata
├─ adapters/
│  ├─ claude-code/       # .claude-plugin + comandos /suma-*
│  ├─ codex/             # .codex-plugin + MCP + skills
│  ├─ hermes/            # plugin.yaml + register(ctx)
│  └─ opencode/          # opencode.json
├─ docs/
├─ CONNECT-ANY-AI.md
└─ TESTING.md
```

La raíz es el paquete madre. Cada host instala desde su adapter.

## Claude Code

El adapter vive en:

```txt
plugins/suma/adapters/claude-code/
```

Comandos:

- `/suma-connect` — conectar Suma con login en navegador.
- `/suma-check` — revisar estado antes de tocar nada.
- `/suma-improve` — mejorar un agente Sumanos.
- `/suma-fix` — reparar algo roto.
- `/suma-install` — instalar una capacidad aprobada.
- `/suma-report` — resumir estado, cambios y próximos pasos.

Marketplace local:

```txt
plugins/.claude-plugin/marketplace.json → ./suma/adapters/claude-code
```

## Codex

El adapter vive en:

```txt
plugins/suma/adapters/codex/
```

Config MCP directa equivalente:

```toml
[mcp_servers.sumanos]
url = "https://api.sumanos.com/mcp/authoring"
bearer_token_env_var = "SUMANOS_KEY"
```

## Hermes

El adapter vive en:

```txt
plugins/suma/adapters/hermes/
```

Registra metadata/plugin y MCP `sumanos`. La lógica de negocio sigue en el MCP de Sumanos.

## opencode

El adapter vive en:

```txt
plugins/suma/adapters/opencode/opencode.json
```

## Reglas

- No hardcodear keys.
- No usar nombres de prototipo en docs nuevas.
- `sumanos` es el server id del MCP.
- `Suma` es el producto/plugin.
- `/mcp/authoring` no cambia sin spec nueva.
