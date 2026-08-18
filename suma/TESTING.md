# Suma — doc técnica + runbook E2E

Cómo subís el plugin, cómo se usa, y cómo se prueba de punta a punta. Esta es la
referencia para saber **cómo actuar** sobre la VM-Hermes de un cliente.

---

## 1. Qué es (en una frase)

Un plugin que cualquier IA de coding (Claude Code / Codex / opencode) instala con
una **API key de operador**. La key apunta al control plane de Sumanos, que expone
un **MCP** en `/mcp/authoring`. La key define el **tier**: operador = ve y ejecuta
las *workspace tools* (acceso crudo a la VM por SSM); cliente = solo *authoring*.
Nunca hay SSH ni red abierta al VM: todo va por SSM (identidad + auditoría).

```
Claude Code ──(.mcp.json: http + Bearer <SK>)──▶  POST /mcp/authoring
                                                       │  token → accountId + role
                                                       ▼
                                            AuthoringMcpHandler (tier-aware)
                                          operador → authoring + workspace tools
                                                       │
                                          workspace tool → SsmWorkspaceHost
                                                       │  aws ssm send-command
                                                       ▼
                                              EC2 del agente (sin :22)
```

---

## 2. Las 12 tools (lo que podés hacer)

`agentId` es un parámetro de cada tool que opera sobre UN agente (lo inyecta el
server en el `inputSchema`). `list_agents` NO lo lleva (listás para *encontrar* ids).

### Authoring (typed — pasan por el pipeline: scan→snapshot→[aprobación]→apply→healthcheck→rollback→audit)
| Tool | Args | Riesgo |
|------|------|--------|
| `list_agents` | — | lee |
| `read_soul` | `agentId` | lee |
| `edit_soul` | `agentId`, `content` (≤8000) | BAJO → aplica directo (reinicia gateway) |
| `set_model` | `agentId`, `provider`, `modelId` | BAJO → directo |
| `install_plugin` | `agentId`, `ref` | dedicated owner/admin → **applies**; shared `agent` actor → staged |
| `set_credential` | `agentId`, `name`, `value` | same; value never echoed |

### Workspace (raw VM — solo tier OPERADOR, sin pipeline; vos sos la red de contención)
| Tool | Args | Qué hace |
|------|------|----------|
| `read_file` | `agentId`, `path` | lee un archivo del workspace |
| `write_file` | `agentId`, `path`, `content` | crea/reemplaza (codifica base64 por dentro → shell-safe) |
| `list_dir` | `agentId`, `path` | lista un directorio |
| `run_command` | `agentId`, `command` | ejecuta y devuelve `{code, stdout}` |
| `read_logs` | `agentId`, `lines?` | últimas N líneas del log del gateway |
| `restart_gateway` | `agentId` | reinicia el gateway (aplica cambios manuales) |

---

## 3. Wire protocol (lo que mando yo, verificado contra el código)

MCP JSON-RPC sobre HTTP, **stateless**, respuesta JSON (no SSE). Auth por
`Authorization: Bearer <SK>`. Sin token → 401 `-32001`. (`apps/api/src/authoring-mcp-route.ts`)

Handshake estándar MCP: `initialize` → notificación `initialized` → `tools/list` /
`tools/call`. Lo más cómodo para drivear es un cliente MCP (el SDK, o el propio
Claude Code); por curl hay que respetar el handshake.

**Listar tools (operador ⇒ 12; cliente ⇒ 6):**
```jsonc
// → POST /mcp/authoring
{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
```

**Llamar una workspace tool (leer logs del agente):**
```jsonc
{"jsonrpc":"2.0","id":2,"method":"tools/call",
 "params":{"name":"read_logs","arguments":{"agentId":"<AGENT_ID>","lines":50}}}
```

**Escribir un archivo (contenido va verbatim; el host lo codifica base64):**
```jsonc
{"jsonrpc":"2.0","id":3,"method":"tools/call",
 "params":{"name":"write_file","arguments":{"agentId":"<AGENT_ID>","path":"/home/ubuntu/x.txt","content":"hola $(precio) 70.000"}}}
```
Respuesta: `{ isError, content:[{type:"text", text:"<summary>"}] }`. El summary es
**sanitizado** — nunca stack/paths/SQL/secretos (test de containment en
`core/builder/src/authoring-mcp.test.ts`).

---

## 4. Cómo lo SUBÍS / instalás

### Opción A — como plugin Claude Code
1. Publicá el marketplace (`plugins/.claude-plugin/marketplace.json`) — repo o ruta local.
   El source local de Suma apunta a `./suma/adapters/claude-code`.
2. En Claude Code:
   ```
   /plugin marketplace add <repo-o-ruta>
   /plugin install suma@sumanos
   ```
3. Usá `/suma-connect` para login de cliente por navegador.
4. Si necesitás modo operador, conectá el MCP con Bearer como en la opción B.
5. Quedan disponibles: el MCP `sumanos`, las skills y los comandos `/suma-*`.

### Opción B — MCP suelto (rápido, sin instalar el plugin)
```
claude mcp add sumanos --transport http <API_URL>/mcp/authoring \
  --header "Authorization: Bearer <SK>"
```
(Igual de funcional para las tools; te perdés las skills/comando del plugin.)

---

## 5. Runbook E2E (real, contra un agente con VM)

Necesitás: un agente con un sandbox EC2 vivo (su `<ACCOUNT_ID>`, `<AGENT_ID>` e
`<INSTANCE_ID>` salen de tu DB — NO se hardcodean acá). Migración 0020 (col
`operator`) aplicada.

1. **Mint operator key** (API apagada — PGlite es 1-proceso). Expira sola a los 7
   días (override `EXPIRES_DAYS`); para matarla antes:
   `ACCOUNT_ID=… KEY_ID=… bun run scripts/revoke-operator-key.ts`.
   ```
   ACCOUNT_ID=<ACCOUNT_ID> bun run scripts/mint-operator-key.ts
   ```
2. **API con provider ec2 + creds AWS reales** (sin esto el factory NO existe →
   operador vería authoring-only; ver server.ts:178). En la raíz del repo:
   ```
   SUMANOS_SANDBOX_PROVIDER=ec2 bun run --env-file=.env apps/api/src/server.ts
   ```
   Requisitos: `aws` CLI con creds que alcancen `<INSTANCE_ID>` por SSM, y la
   config ec2 (AMI/SG/region/staging bucket/remote=ssm).
3. **Drive** (por curl o cliente MCP): `tools/list` → confirmar 12 tools →
   `read_logs` / `read_file` / `run_command` con `agentId: <AGENT_ID>`.
4. **Verificá la señal real** en el VM: el archivo de `write_file` apareció, el log
   de `read_logs` matchea `tail` real, `restart_gateway` reinició el proceso.
5. **Verificá la auditoría** (F52.5): cada op dejó una fila en `authoring_operations`
   (`actor_type='operator'`, `op_type`, `risk`, `status`, `source='mcp'`, scope).

---

## 6. Gates de packaging

```bash
python3 -m json.tool plugins/.claude-plugin/marketplace.json >/dev/null
python3 -m json.tool plugins/suma/core/mcp/server.json >/dev/null
python3 -m json.tool plugins/suma/adapters/claude-code/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/suma/adapters/claude-code/.mcp.json >/dev/null
python3 -m json.tool plugins/suma/adapters/codex/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/suma/adapters/codex/.mcp.json >/dev/null
python3 -m json.tool plugins/suma/adapters/opencode/opencode.json >/dev/null

PYTHONPATH=/tmp/codex-plugin-validate-py python3 \
  /Users/gonza/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/suma/adapters/codex
```

## 7. Gotchas (verificados / de memoria del repo)

- **`.env` con creds AWS placeholder** sombrea las reales → `Bun.spawn aws` falla.
  Para SSM hace falta que las creds del entorno sean reales, no las del `.env`.
- **PGlite es 1-proceso**: mintear la key exige la API apagada.
- **Un agente puede vivir en una VPC default (172.31.x)** y no en la subnet sandbox
  (10.0.30.x) — p. ej. una VM adoptada. SSM funciona igual SI el agente SSM está
  instalado y el rol/region son los correctos; si no, el host falla **sanitizado**
  (y eso también valida la contención).
- **`restart_gateway` corre como root por SSM**: ojo con `HOME`/`PATH` del proceso
  (el patrón reusa ec2.ts:306).
- **El engine falla en silencio**: validá antes de escribir y verificá con
  `read_logs` que el cambio TOMÓ efecto (no solo "running").

---

## 8. Evidencia 2026-06-30 — packaging/E2E local

### ✅ Claude adapter load

```bash
claude --plugin-dir plugins/suma/adapters/claude-code plugin details suma
```

Resultado:

```txt
Suma (suma) 0.2.0
Skills (4) agent-recipes, suma-playbook, sumanos-capabilities, writing-agent-souls
MCP servers (2) sumanos, sumanos-dev
```

### ✅ Gates locales

- JSON manifests válidos.
- `claude plugin validate plugins/suma/adapters/claude-code` pasó.
- `claude plugin validate plugins/.claude-plugin/marketplace.json` pasó.
- `validate_plugin.py plugins/suma/adapters/codex` pasó.
- Naming guard sin hits legacy en superficies publicables.

### ✅ Instalación desde marketplace en HOME temporal

```bash
HOME=/private/tmp/suma-claude-home claude plugin marketplace add /private/tmp/sumanos-plugins-close
HOME=/private/tmp/suma-claude-home claude plugin install suma@sumanos --scope user
HOME=/private/tmp/suma-claude-home claude plugin details suma
```

Resultado:

```txt
Successfully added marketplace: sumanos
Successfully installed plugin: suma@sumanos
Source: suma@sumanos
Skills (4) agent-recipes, suma-playbook, sumanos-capabilities, writing-agent-souls
MCP servers (2) sumanos, sumanos-dev
```

### ✅ MCP registrado en Claude

```bash
HOME=/private/tmp/suma-claude-home claude mcp list
```

Resultado:

```txt
plugin:suma:sumanos: https://app.sumanos.com/mcp/authoring/agents/${SUMANOS_AGENT_ID} (HTTP)
plugin:suma:sumanos-dev: https://development.sumanos.com/mcp/authoring/agents/${SUMANOS_AGENT_ID} (HTTP)
```

### 🟡 Bloqueos para E2E MCP autenticado

- OAuth/browser-login no puede completarse en este runner porque `stdin` no es TTY:
  `stdin isn't a terminal, so authentication can't be completed here`.
- `SUMANOS_KEY` / `SUMANOS_OPERATOR_KEY` no están presentes en el entorno, por lo que no se puede llamar `list_agents` autenticado.
- El endpoint MCP productivo responde correctamente el boundary de auth sin token:
  `401 unauthorized: missing bearer token`.

Conclusión: instalación, carga del plugin y registro MCP están verificados. Falta una corrida interactiva de OAuth o una `SUMANOS_KEY` válida para ejecutar `list_agents` real.
