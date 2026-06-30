# Sumanos — marketplace de plugins

Marketplace privado de Sumanos. Hoy publica **Suma**: el plugin para conectar una IA de coding con Sumanos y operar agentes de forma segura.

## Instalar en Claude Code

```bash
/plugin marketplace add Sumanos-com/sumanos-plugins
/plugin install suma@sumanos
```

## Qué trae Suma

```txt
/suma-connect  conectar
/suma-check    revisar sin tocar
/suma-improve  mejorar
/suma-fix      reparar
/suma-install  instalar capacidad
/suma-report   explicar estado
```

## Otros hosts

Codex, opencode, Hermes y otras IAs se conectan al mismo MCP remoto:

```txt
https://api.sumanos.com/mcp/authoring
```

Ver `suma/CONNECT-ANY-AI.md`. La estructura publicable usa `suma/core/` + `suma/adapters/<host>/`.

## Mantenimiento

La fuente de trabajo vive en `sumanos-agents/plugins/suma/`. Este repo es la copia publicable para instalaciones externas.
