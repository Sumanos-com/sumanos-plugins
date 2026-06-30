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
- Codex: `.codex-plugin`, marketplace y MCP config.
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

## Estructura objetivo

```txt
plugins/suma/
  core/
    manifest.yaml
    skills/
    prompts/
    mcp/
    docs/
  adapters/
    claude-code/
    codex/
    hermes/
    opencode/
```

## Estado actual

El repo ya tiene el paquete `plugins/suma/` con el adapter Claude Code en la raíz histórica. La siguiente mejora estructural es mover contenido a `core/` + `adapters/` sin duplicar skills.

## Invariantes

- No hardcodear keys.
- Usar variables de entorno para Bearer (`SUMANOS_KEY`).
- No cambiar `/mcp/authoring` sin spec nueva.
- No exponer SSH.
- No duplicar skills a mano entre adapters; generar o copiar desde core.
