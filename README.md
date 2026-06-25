# Sumanos — marketplace de plugins (Claude Code)

Marketplace privado de Sumanos. Hoy contiene **`sumanos-builder`**: conectás tu IA de
coding a un agente Hermes y lo mejorás/reparás (SOUL, modelo, plugins, skills) por MCP.

## Instalar (Claude Code)

```bash
/plugin marketplace add Sumanos-com/sumanos-plugins
/plugin install sumanos-builder@sumanos
```

> Repo **privado**: tu Claude Code usa tus credenciales git (`gh auth login` /
> `GITHUB_TOKEN`) para bajarlo, igual que un `git clone`.

- **Cliente** (dueño del agente): al usar una tool, Claude Code abre el navegador y te
  logueás en Sumanos (OAuth, sin pegar keys). Conecta a `https://app.sumanos.com/mcp/authoring`.
- **Operador** (staff): conectás con tu operator key (Bearer) — ver `sumanos-builder/README.md`.

## Otras IAs (Codex, opencode)

No usan plugins: pegás un bloque de config que apunta al mismo MCP remoto. Ver
`sumanos-builder/CONNECT-ANY-AI.md`.

## Mantenimiento

La fuente canónica del plugin vive en el monorepo (`plugins/sumanos-builder/`). Este repo
es la copia publicable para que las IAs lo descarguen; se actualiza re-publicando.
