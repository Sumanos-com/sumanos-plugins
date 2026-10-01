# Suma Hermes Multi-Organization Plugin

## Objective

Make the canonical Suma plugin installable and usable in Hermes with multiple named
organization/agent connections, while keeping every request bound to exactly one key.

## Problem

The published Hermes adapter declares MCP servers and skills in `plugin.yaml`, but Hermes does
not consume those fields. The Python adapter also depends on a plugin-context MCP registration
method that Hermes does not expose, so the plugin can install without making Suma tools available.

## Scope

- Materialize multiple named Hermes MCP connections from explicit connection descriptors.
- Keep raw keys outside generated configuration; generated headers use environment references.
- Route each connection independently to the existing production or development authoring endpoint.
- Register the four shipped Suma skills through Hermes' supported plugin context.
- Document and test install, add, update, remove, and validation behavior.

## Constraints

- Never store or print key values in repository files, generated config, logs, or test fixtures.
- Never combine permissions, retry with another connection, or fall back across organizations.
- Do not use Hermes private MCP registration internals.
- Preserve existing Claude Code, Codex, and OpenCode adapters.
- Target the canonical `Sumanos-com/sumanos-plugins` repository only.

## Authorization

- User authorized implementation and push to `Sumanos-com/sumanos-plugins` using the current
  authenticated GitHub session.
- Production or customer VM changes are not authorized by this feature.

## Delivery

- Branch: `feat/hermes-multi-org-collaborator`
- Strategy: `ask-on-risk`
- Forecast: approximately 350 authored changed lines, excluding generated fixtures.
- Pull request target: `main` (the canonical plugin repository has no `develop` branch).

## TDD

- Mode: strict, required by the parent Sumanos repository instructions.
- Runner: `bun test suma/test/adapter-mcp-contract.test.ts suma/test/sync-skills.test.ts`

## Tasks

- [x] **PLUGIN-1 — Define the connection contract**
  - Route: delegated; mapping and preparation triggers fired because the behavior spans adapter,
    configuration, tests, and documentation.
  - Add RED contract tests for multiple named connections, environment-only key references,
    deterministic add/update/remove behavior, and invalid descriptor rejection.
  - Acceptance: tests prove no raw key is written and no connection can inherit another key.
  - RED evidence: `python3 -m unittest suma/test/test_hermes_adapter.py` failed as expected:
    `materialize_connections`/`remove_connection` were absent and no skills were registered.

- [x] **PLUGIN-2 — Implement the supported Hermes adapter path**
  - Route: delegated writer; multiple non-trivial files are required.
  - Materialize Hermes MCP configuration without private PluginContext APIs and register all four
    shipped skills through supported APIs.
  - Acceptance: N descriptors produce N isolated MCP servers and all skills are discoverable.
  - Hermes syntax verified in the pinned host: `mcp_servers.<name>.url` and `.headers` are
    supported in `config.yaml`; `${VAR}` is expanded by Hermes config loading. The adapter uses
    `read_raw_config`/`save_config` to avoid reading expanded key values.
  - GREEN evidence: Python contract tests 4/4; focused Bun tests 16/16; skill sync check passed.

- [x] **PLUGIN-3 — Document installation and operation**
  - Route: delegated with the implementation so commands match tested behavior.
  - Document canonical install, named connections, secret injection, removal, and prod/dev URLs.
  - Acceptance: instructions contain no secret values and identify the canonical repository.
  - Evidence: documented canonical monorepo installation, descriptor commands, safe secret
    injection, prod/dev routing, explicit removal, and the one-key/one-agent boundary.

- [ ] **PLUGIN-4 — Verify and publish**
  - Route: delegated verification plus parent structural spot check.
  - Run focused tests, skill sync check, and any formatter/type checks declared by the repository.
  - Commit each completed work unit conventionally, then push the authorized feature branch.

## Verification Evidence

- Pending.

## Progress

- Completed: read-only repository and Hermes host mapping.
- Current: PLUGIN-4.
- Next: run final checks, review diff, and report exact repository status to the parent.
