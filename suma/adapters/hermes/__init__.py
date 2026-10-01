"""Suma Hermes adapter and safe MCP configuration materializer."""

import copy
import hashlib
import re
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

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
_OWNER_SCHEMA = "suma.hermes-connection/v1"
_OWNER_ADAPTER = "suma-hermes"
_OWNER_FIELDS = {
    "schema",
    "adapter",
    "connection_name",
    "environment",
    "agentId",
    "keyEnv",
}


def _server_name(name: str) -> str:
    canonical_name = name.casefold()
    slug = re.sub(r"[^a-z0-9]+", "-", canonical_name).strip("-")[:40].strip("-")
    suffix = hashlib.sha256(canonical_name.encode("utf-8")).hexdigest()[:16]
    return f"suma-{slug or 'connection'}-{suffix}"


def _ownership(server: Any) -> Optional[dict[str, str]]:
    """Read only an exact, versioned Suma ownership marker; reject malformed claims."""
    if not isinstance(server, Mapping):
        return None
    marker = server.get("suma")
    if not isinstance(marker, Mapping):
        return None
    if marker.get("adapter") != _OWNER_ADAPTER and marker.get("schema") != _OWNER_SCHEMA:
        return None
    if set(marker) != _OWNER_FIELDS:
        raise ValueError("Malformed Suma Hermes ownership metadata")
    owner = dict(marker)
    if (
        owner["schema"] != _OWNER_SCHEMA
        or owner["adapter"] != _OWNER_ADAPTER
        or not isinstance(owner["connection_name"], str)
        or not owner["connection_name"]
        or not isinstance(owner["environment"], str)
        or owner["environment"] not in ENVIRONMENTS
        or not isinstance(owner["agentId"], str)
        or not _AGENT_ID_RE.fullmatch(owner["agentId"])
        or not isinstance(owner["keyEnv"], str)
        or not _ENV_RE.fullmatch(owner["keyEnv"])
    ):
        raise ValueError("Malformed Suma Hermes ownership metadata")
    return owner


def _validate_descriptors(descriptors: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    if not isinstance(descriptors, Sequence) or isinstance(descriptors, (str, bytes)):
        raise ValueError("Suma connections must be provided as a sequence of descriptors")
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
        if not isinstance(environment, str) or environment not in ENVIRONMENTS:
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

    target_names = {item["name"].casefold() for item in validated}
    managed: list[tuple[str, dict[str, str]]] = []
    for current_id, current_server in existing.items():
        owner = _ownership(current_server)
        if owner is None:
            continue
        if current_id != _server_name(owner["connection_name"]):
            raise ValueError("Suma Hermes ownership metadata does not match its server ID")
        if owner["connection_name"] in target_names:
            continue
        managed.append((current_id, owner))

    used_names: set[str] = set()
    used_agent_ids: set[str] = set()
    used_key_envs: set[str] = set()
    for _current_id, owner in managed:
        owner_name = owner["connection_name"]
        if (
            owner_name in used_names
            or owner["agentId"] in used_agent_ids
            or owner["keyEnv"] in used_key_envs
        ):
            raise ValueError("Existing Suma connections violate the uniqueness contract")
        used_names.add(owner_name)
        used_agent_ids.add(owner["agentId"])
        used_key_envs.add(owner["keyEnv"])
    for item in validated:
        canonical_name = item["name"].casefold()
        if (
            canonical_name in used_names
            or item["agentId"] in used_agent_ids
            or item["keyEnv"] in used_key_envs
        ):
            raise ValueError("Suma connection name, agent ID, and key environment must be unique")
        used_names.add(canonical_name)
        used_agent_ids.add(item["agentId"])
        used_key_envs.add(item["keyEnv"])

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
            "suma": {
                "schema": _OWNER_SCHEMA,
                "adapter": _OWNER_ADAPTER,
                "connection_name": descriptor["name"].casefold(),
                "environment": descriptor["environment"],
                "agentId": descriptor["agentId"],
                "keyEnv": descriptor["keyEnv"],
            },
        }
        prior = servers.get(server_name)
        if prior is not None:
            owner = _ownership(prior)
            if owner is None or owner["connection_name"] != descriptor["name"].casefold():
                raise ValueError(f"Hermes MCP server name already exists: {server_name}")
        servers[server_name] = server
    updated["mcp_servers"] = servers
    return updated


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
        owner = _ownership(servers[server_name])
        if owner is None or owner["connection_name"] != name.casefold():
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
