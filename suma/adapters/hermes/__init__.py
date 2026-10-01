"""Suma Hermes adapter and safe MCP configuration materializer."""

import copy
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

ENVIRONMENTS = {
    "production": "https://app.sumanos.com",
    "development": "https://development.sumanos.com",
}
SKILLS = (
    "suma-playbook",
    "sumanos-capabilities",
    "agent-recipes",
    "writing-agent-souls",
)
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]{0,63}$")
_AGENT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._~-]{0,127}$")
_ENV_RE = re.compile(r"^[A-Z_][A-Z0-9_]{0,127}$")


def _server_name(name: str) -> str:
    slug = re.sub(r"[ ._]+", "-", name.strip()).lower()
    return f"suma-{slug}"


def _validate_descriptors(descriptors: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    validated = []
    names: set[str] = set()
    server_names: set[str] = set()
    agent_ids: set[str] = set()
    key_envs: set[str] = set()

    for item in descriptors:
        if not isinstance(item, Mapping):
            raise ValueError("Each Suma connection must be a mapping")
        name = item.get("name")
        environment = item.get("environment")
        agent_id = item.get("agentId")
        key_env = item.get("keyEnv")
        if not isinstance(name, str) or not _NAME_RE.fullmatch(name) or name != name.strip():
            raise ValueError("Connection name must be a trimmed, human-safe name")
        if environment not in ENVIRONMENTS:
            raise ValueError("Connection environment must be production or development")
        if not isinstance(agent_id, str) or not _AGENT_ID_RE.fullmatch(agent_id):
            raise ValueError("Agent ID must be a single safe path component")
        if not isinstance(key_env, str) or not _ENV_RE.fullmatch(key_env):
            raise ValueError("Key environment variable must be a valid environment variable name")
        normalized_name = name.casefold()
        server_name = _server_name(name)
        if normalized_name in names or server_name in server_names:
            raise ValueError("Connection names must be unique")
        if agent_id in agent_ids:
            raise ValueError("Agent IDs must be unique across connections")
        if key_env in key_envs:
            raise ValueError("Key environment variable names must be unique")
        names.add(normalized_name)
        server_names.add(server_name)
        agent_ids.add(agent_id)
        key_envs.add(key_env)
        validated.append({
            "name": name,
            "environment": environment,
            "agentId": agent_id,
            "keyEnv": key_env,
        })
    return validated


def materialize_connections(
    config: Mapping[str, Any], descriptors: Sequence[Mapping[str, str]]
) -> dict[str, Any]:
    """Return a copied Hermes config with one isolated HTTP MCP per descriptor.

    Only key variable names are accepted. The function never reads environment
    variables, so the key value cannot enter generated configuration.
    """
    validated = _validate_descriptors(descriptors)
    if not isinstance(config, Mapping):
        raise ValueError("Hermes config must be a mapping")
    existing = config.get("mcp_servers", {})
    if existing is None:
        existing = {}
    if not isinstance(existing, Mapping):
        raise ValueError("Hermes mcp_servers must be a mapping")

    updated = copy.deepcopy(dict(config))
    servers = copy.deepcopy(dict(existing))
    for descriptor in validated:
        server_name = _server_name(descriptor["name"])
        server = {
            "url": (
                f"{ENVIRONMENTS[descriptor['environment']]}/mcp/authoring/agents/"
                f"{descriptor['agentId']}"
            ),
            "headers": {"Authorization": f"Bearer ${{{descriptor['keyEnv']}}}"},
        }
        prior = servers.get(server_name)
        if prior is not None and not _is_suma_server(prior):
            raise ValueError(f"Hermes MCP server name already exists: {server_name}")
        servers[server_name] = server
    updated["mcp_servers"] = servers
    return updated


def _is_suma_server(server: Any) -> bool:
    if not isinstance(server, Mapping):
        return False
    url = server.get("url", "")
    headers = server.get("headers", {})
    authorization = headers.get("Authorization") if isinstance(headers, Mapping) else None
    return (
        isinstance(url, str)
        and "/mcp/authoring/agents/" in url
        and isinstance(authorization, str)
        and re.fullmatch(r"Bearer \$\{[A-Z_][A-Z0-9_]*\}", authorization) is not None
    )


def remove_connection(config: Mapping[str, Any], name: str) -> dict[str, Any]:
    """Remove only the deterministically named Suma server, idempotently."""
    if not isinstance(name, str) or not _NAME_RE.fullmatch(name) or name != name.strip():
        raise ValueError("Connection name must be a trimmed, human-safe name")
    if not isinstance(config, Mapping):
        raise ValueError("Hermes config must be a mapping")
    existing = config.get("mcp_servers", {}) or {}
    if not isinstance(existing, Mapping):
        raise ValueError("Hermes mcp_servers must be a mapping")
    updated = copy.deepcopy(dict(config))
    servers = copy.deepcopy(dict(existing))
    server_name = _server_name(name)
    if server_name in servers:
        if not _is_suma_server(servers[server_name]):
            raise ValueError(f"Refusing to remove unrelated Hermes MCP server: {server_name}")
        del servers[server_name]
    if servers:
        updated["mcp_servers"] = servers
    else:
        updated.pop("mcp_servers", None)
    return updated


def register(ctx: Any) -> dict[str, Any]:
    """Register all shipped skills through Hermes' public plugin context."""
    skill_dir = Path(__file__).parent / "skills"
    for skill in SKILLS:
        ctx.register_skill(skill, skill_dir / skill / "SKILL.md")
    return {"name": "suma", "skills": list(SKILLS)}
