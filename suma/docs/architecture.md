# Suma — arquitectura interna

Suma es el paquete de autoría técnica de Sumanos. Su objetivo es que una IA de programación pueda operar y mejorar agentes Sumanos sin abrir SSH ni exponer secretos.

## Decisión central

No existe un único formato de plugin universal. Lo universal es:

```txt
Sumanos Authoring MCP
https://api.sumanos.com/mcp/authoring
```

Los plugins son adapters por host:

- Claude Code: `.claude-plugin`, `.mcp.json`, `skills/`, `commands/`.
- Codex: `.codex-plugin`, `.mcp.json`, `skills/`.
- Hermes: `plugin.yaml` + `register(ctx)`.
- opencode: `opencode.json` con MCP remoto.

## Naming canónico

| Concepto | Nombre |
|---|---|
| Producto público | Suma |
| Slug del plugin | `suma` |
| MCP server id | `sumanos` |
| Endpoint | `/mcp/authoring` |
| Env var recomendada | `SUMANOS_KEY` |
| Prompt MCP | `suma-soul` |
| Skill principal | `suma-playbook` |
| Comandos Claude Code | `/suma-connect`, `/suma-check`, `/suma-improve`, `/suma-fix`, `/suma-install`, `/suma-report` |

No reintroducir nombres de prototipo en docs, manifests, comandos ni specs nuevas.

## Core neutral

```txt
plugins/suma/core/
├─ manifest.yaml
├─ skills/
├─ prompts/
├─ mcp/server.json
└─ docs/
```

El core describe el contrato compartido. No depende de Claude Code, Codex, Hermes ni opencode.

## Adapters

```txt
plugins/suma/adapters/
├─ claude-code/
├─ codex/
├─ hermes/
└─ opencode/
```

Cada adapter empaqueta lo que su host entiende, manteniendo el mismo MCP server id: `sumanos`.

## Contrato MCP

El MCP expone tres capas:

1. **Tools**: acciones de autoría y, para operador, workspace tools sobre VM.
2. **Resources**: manual/contexto que la IA puede leer.
3. **Prompts**: persona operativa (`suma-soul`).

El servidor id debe seguir siendo `sumanos` porque representa la plataforma, no el runtime del plugin.

## Modelo de permisos

| Tier | Actor | Capacidades |
|---|---|---|
| Cliente | Dueño del agente | Autoría segura; alto riesgo queda staged |
| Operador | Staff autorizado | Autoría directa + workspace tools auditadas |
| Superadmin | Plataforma | Mint de operator keys scopeadas; no ejecuta directo sobre VMs |

## Estado actual

- ✅ Core neutral existe.
- ✅ Adapter Claude Code existe en `adapters/claude-code`.
- ✅ Adapter Codex existe en `adapters/codex`.
- ✅ Adapter Hermes existe en `adapters/hermes`.
- ✅ Adapter opencode existe en `adapters/opencode`.
- ⏳ Falta evidencia E2E real contra host instalado y MCP autenticado.

## Invariantes

- No hardcodear keys.
- Usar variables de entorno para Bearer (`SUMANOS_KEY`).
- No cambiar `/mcp/authoring` sin spec nueva.
- No exponer SSH.
- Si una skill compartida cambia, sincronizar adapters desde `core/skills`.
