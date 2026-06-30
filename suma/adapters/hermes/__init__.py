"""Suma Hermes adapter.

This adapter registers Suma metadata only. Business logic lives in the Sumanos
Authoring MCP and shared core skills, not in the Hermes runtime plugin.
"""

PLUGIN = {
    "name": "suma",
    "mcp_server_id": "sumanos",
    "mcp_url": "https://api.sumanos.com/mcp/authoring",
    "bearer_env": "SUMANOS_KEY",
}


def register(ctx):
    """Register Suma with a Hermes-like plugin context when supported."""
    if hasattr(ctx, "register_mcp_server"):
        ctx.register_mcp_server(
            "sumanos",
            url=PLUGIN["mcp_url"],
            headers={"Authorization": "Bearer ${SUMANOS_KEY}"},
        )
    if hasattr(ctx, "register_plugin"):
        ctx.register_plugin(PLUGIN)
    return PLUGIN
