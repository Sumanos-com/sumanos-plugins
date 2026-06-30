# Suma en Codex

Codex puede usar Suma de dos maneras:

1. **Plugin Codex** cuando exista adapter publicado.
2. **MCP directo** hoy, usando el mismo endpoint de Sumanos.

## Instalación de plugins en Codex

Desde la CLI interactiva:

```txt
codex
/plugins
```

En el browser de plugins:

1. elegí el marketplace;
2. buscá `Suma`;
3. instalá el plugin;
4. abrí un hilo nuevo para que Codex cargue skills/MCP.

## MCP directo actual

Config en `~/.codex/config.toml`:

```toml
[mcp_servers.sumanos]
url = "https://api.sumanos.com/mcp/authoring"
bearer_token_env_var = "SUMANOS_KEY"
```

Uso:

```bash
export SUMANOS_KEY="tu_api_key_o_operator_key"
codex
```

## Marketplace local para desarrollo

Cuando exista `plugins/suma/adapters/codex/.codex-plugin/plugin.json`, el marketplace local debe apuntar a la carpeta que contiene `.codex-plugin`.

Ejemplo `./.agents/plugins/marketplace.json`:

```json
{
  "name": "sumanos-local",
  "interface": {
    "displayName": "Sumanos Local"
  },
  "plugins": [
    {
      "name": "suma",
      "source": {
        "source": "local",
        "path": "./plugins/suma/adapters/codex"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

Si el marketplace no es el personal default, instalarlo con:

```bash
codex plugin marketplace add ./.agents/plugins
```

## Validación esperada del adapter Codex

```bash
python3 /Users/gonza/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/suma/adapters/codex
```

## Prueba funcional mínima

1. `SUMANOS_KEY` cargada.
2. Codex abre sin error de config.
3. El MCP `sumanos` aparece disponible.
4. `list_agents` devuelve agentes del scope correcto.
5. Una key cliente no ve workspace tools.
6. Una operator key sí ve workspace tools.
