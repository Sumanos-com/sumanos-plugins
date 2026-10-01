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
- Strategy: `exception-ok`
- Forecast: approximately 350 authored changed lines, excluding generated fixtures.
- Actual: 584 authored changed lines excluding this task document; the maintainer explicitly
  approved a single-PR `size:exception` because splitting the adapter contract, implementation,
  and tests would create artificial intermediate states.
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

- [x] **PLUGIN-4 — Verify and publish**
  - Route: delegated verification plus parent structural spot check.
  - Run focused tests, skill sync check, and any formatter/type checks declared by the repository.
  - Commit each completed work unit conventionally, then push the authorized feature branch.
  - Evidence: independent verification passed with no high/medium findings; the native medium-risk
    review was approved and acknowledged under `review-8f804c926a0e8429`; branch published and
    PR `Sumanos-com/sumanos-plugins#6` opened against `main`.

## Verification Evidence

- Correction RED: `python3 -m unittest` for the two new regressions failed as expected:
  alias-colliding names yielded one server instead of two, and removal did not refuse a
  lookalike server without Suma ownership metadata.
- Correction GREEN: Python contract tests passed 8/8; focused Bun tests passed 16/16;
  skill sync check, Python compilation, and `git diff --check` passed.
- Server IDs include a bounded 16-hex SHA-256 suffix of the casefolded exact connection name;
  alias slug collisions remain distinct while case-only updates keep the same ID. Add/update
  scans owned markers to enforce name, agent-ID, and key-env uniqueness across prior entries.
- Ownership marker is namespaced and versioned; it stores only canonical name, environment,
  agent ID, and key variable name, not a key value, and is never sent as an HTTP header.
  Hermes host source confirmation in the pinned checkout: `hermes_cli/config.py` declares
  `mcp_servers` open-dict; `tools/mcp_tool.py` recursively interpolates values and preserves
  unknown fields, then its HTTP runner reads documented transport settings such as `url` and
  `headers`. Its security validator inspects known command/args/env fields, not marker metadata.
- Native review advisory `R3-001` is non-blocking follow-up work: removal should reject falsey
  non-mapping `mcp_servers` values instead of normalizing them to an empty mapping.

## Progress

- Completed: read-only repository and Hermes host mapping.
- Completed: PLUGIN-1 through PLUGIN-4.
- Current: PR review and CI for `Sumanos-com/sumanos-plugins#6`.
- Next: merge only after ordinary repository checks and maintainer review.
