# Sumanos Builder — plugin de Claude Code

EL Plugin Sumanos: lo conectás a tu IA de coding (Claude Code, Codex, opencode) y al
toque **entiende sumanos.com** y puede **mejorar y reparar un agente Hermes**
(SOUL / modelo / plugins / credenciales), por **MCP remoto** sobre `/mcp/authoring`.
El cerebro lo pone TU suscripción de coding → costo ~0 para Sumanos.
Ver `specs/052-sumanos-builder-plugin/spec.md`.

## Dos tiers, dos formas de conectarse

El control plane deriva el **tier** del cómo te autenticás. Esto define **qué podés hacer**:

| Tier | Quién | Cómo conecta | Qué puede |
|------|-------|--------------|-----------|
| **Cliente** | el dueño del agente (no técnico) | **login en el navegador** (OAuth, sin pegar keys) | tools de autoría: `edit_soul`, `set_model`, `read_soul`, `list_agents`, e `install_plugin`/`set_credential` que **quedan en cola de aprobación** (alto riesgo) |
| **Operador** | staff de Sumanos | **operator key** (Bearer) | autoría con **apply directo** de alto riesgo + las **6 workspace tools** sobre la VM por SSM: `read_file`, `write_file`, `list_dir`, `run_command`, `read_logs`, `restart_gateway` |

> El operator key la mintea el superadmin (scoped a 1 org, con expiry y auditada). Es la
> única diferencia entre "ayudo a configurar" (cliente) y "entro a la VM y la reparo" (operador).

## Conectar — CLIENTE (Claude Code, login en el navegador)

Instalás el plugin; la primera vez que una tool se usa, Claude Code abre el navegador
para que inicies sesión en Sumanos (OAuth). No pegás ninguna key.

```bash
# local (POC):
claude --plugin-dir ./plugins/sumanos-builder
# o, publicado:
/plugin marketplace add <repo-o-path-de-plugins/>
/plugin install sumanos-builder@sumanos
```

El `.mcp.json` del plugin NO lleva header `Authorization` a propósito: sin header,
Claude Code dispara el flujo OAuth (RFC 9728) y resolvés al **tier cliente** de TU org.

## Conectar — OPERADOR (Claude Code, con tu operator key)

El plugin no puede meter un header condicional, así que el operador agrega el MCP a mano
con su SK (esto **reemplaza** la conexión OAuth y desbloquea las workspace tools):

```bash
claude mcp add --transport http sumanos \
  https://api.sumanos.com/mcp/authoring \
  --header "Authorization: Bearer $SUMANOS_OPERATOR_KEY"
```

Podés seguir instalando el plugin para tener las **skills** (el corpus) y los **comandos**
`/sumanos-*`; la conexión con header gana sobre la OAuth.

## Las otras IAs (misma URL, Bearer)

Codex y opencode no hacen el login-browser: usan un **Bearer estático** (operator key, o una
api_key de cliente). Pegá tu key en la env var `SUMANOS_KEY` y usá estos bloques verbatim.

**Codex** — `~/.codex/config.toml`:
```toml
[mcp_servers.sumanos]
url = "https://api.sumanos.com/mcp/authoring"
bearer_token_env_var = "SUMANOS_KEY"
```

**opencode** — `opencode.json`:
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

> opencode NO carga MCP desde un plugin — el bloque `mcp` va aparte en `opencode.json`.

## Qué trae el plugin
```
sumanos-builder/
├─ .claude-plugin/plugin.json   🧾 manifest (userConfig: sumanos_api_url)
├─ .mcp.json                    🔌 conexión OAuth al Builder MCP (tier cliente, sin header)
├─ skills/                      🧠 el corpus 047 (playbook, escribir SOULs, capacidades, recetas)
└─ commands/                    ⌨️ /sumanos-mejorar, /sumanos-conectar
```

El servidor `/mcp/authoring` además expone **resources** (el manual de Sumanos = el corpus)
y **prompts** (la persona del builder) para que la IA "entienda completo" sin pegar nada.

## Estado (spec 052)
- ✅ F52.0 workspace tools sobre SSM · F52.1 tiers + key-gen · F52.2 resources + prompts
- ✅ F52.7 superadmin (mint de operator keys) · F52.8 onboarding OAuth (server) · F52.9 panel Conectores
- 🔨 Pendiente: hornear el contexto en el golden AMI (F52.4) y el "último metro" del login-browser en prod (F52.8, deploy del admin).
