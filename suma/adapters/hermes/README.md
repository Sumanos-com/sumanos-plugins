# Suma for Hermes

Install the Hermes adapter from the canonical [`Sumanos-com/sumanos-plugins`](https://github.com/Sumanos-com/sumanos-plugins) repository:

```bash
git clone https://github.com/Sumanos-com/sumanos-plugins.git
mkdir -p ~/.hermes/plugins/suma
cp -R sumanos-plugins/suma/adapters/hermes/. ~/.hermes/plugins/suma/
```

Hermes installs plugins from a plugin root; the Suma adapter is a subdirectory of the
canonical monorepo, so copy that adapter directory into Hermes' user plugin directory.
Restart Hermes after installation. The plugin registers the four bundled skills using
the public plugin context API.

## Add or update a connection

Run the adapter's config helper once per named connection. The descriptor binds one
human-safe name to one environment, exact agent ID, and environment-variable **name**:

```bash
python3 ~/.hermes/plugins/suma/configure.py add \
  --name "Acme Production" \
  --environment production \
  --agent-id agent-123 \
  --key-env ACME_PROD_KEY
```

Use `development` for `https://development.sumanos.com`; `production` targets
`https://app.sumanos.com`. Re-running `add` with the same name updates that connection.
The helper writes one Hermes `mcp_servers.<name>` entry with the dedicated
`/mcp/authoring/agents/<agentId>` path and `Authorization: Bearer ${ACME_PROD_KEY}`.
Hermes supports this `url`/`headers` syntax and expands `${VAR}` references when loading
its config. Unrelated Hermes config and MCP entries are preserved.

## Inject secrets

Inject each key into the Hermes process environment using the variable name configured
above, through the existing secret manager, service manager, or shell environment.
For example, inject `ACME_PROD_KEY` and `ACME_DEV_KEY` separately. Never put key values
in `config.yaml`, plugin files, shell history, or this repository. The helper accepts
variable names only; it does not read the environment or key values.

## Remove a connection

Remove only the named Suma server, leaving other Hermes MCP servers untouched:

```bash
python3 ~/.hermes/plugins/suma/configure.py remove --name "Acme Production"
```

Removal is idempotent. If you rename a connection, remove the old name separately.

## Isolation boundary

Every connection has its own MCP server name, key variable, selected environment, and
exact agent ID. A request goes only to that dedicated agent endpoint. Suma does not
fall back to another connection, union permissions, reuse another key, or broadcast
across connections. Configure only agents you intentionally authorize.
