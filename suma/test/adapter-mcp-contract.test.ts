import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  customerMcpUrl,
  dedicatedMcpUrl,
  resolveSumaEnv,
  SUMA_ENVIRONMENTS,
  SUMA_OAUTH_ORIGIN,
} from '../core/mcp-url.ts';

const root = join(import.meta.dir, '..');

function read(rel: string): string {
  return readFileSync(join(root, rel), 'utf8');
}

describe('customerMcpUrl', () => {
  test('pins the dedicated agent path on the OAuth host', () => {
    expect(customerMcpUrl(SUMA_OAUTH_ORIGIN, 'ag-1')).toBe(
      'https://app.sumanos.com/mcp/authoring/agents/ag-1',
    );
  });
});

describe('Suma environments', () => {
  test('prod and develop are distinct dedicated hosts', () => {
    expect(SUMA_ENVIRONMENTS.prod).toEqual({
      id: 'sumanos',
      origin: 'https://app.sumanos.com',
    });
    expect(SUMA_ENVIRONMENTS.develop).toEqual({
      id: 'sumanos-dev',
      origin: 'https://development.sumanos.com',
    });
  });

  test('resolveSumaEnv maps aliases and defaults to prod', () => {
    expect(resolveSumaEnv(undefined)).toBe('prod');
    expect(resolveSumaEnv('prod')).toBe('prod');
    expect(resolveSumaEnv('production')).toBe('prod');
    expect(resolveSumaEnv('develop')).toBe('develop');
    expect(resolveSumaEnv('development')).toBe('develop');
    expect(resolveSumaEnv('dev')).toBe('develop');
    expect(resolveSumaEnv('nope')).toBe('prod');
  });

  test('dedicatedMcpUrl builds each env', () => {
    expect(dedicatedMcpUrl('ag-1', 'prod')).toBe(
      'https://app.sumanos.com/mcp/authoring/agents/ag-1',
    );
    expect(dedicatedMcpUrl('ag-1', 'develop')).toBe(
      'https://development.sumanos.com/mcp/authoring/agents/ag-1',
    );
  });
});

describe('Suma adapters pin the dedicated customer MCP', () => {
  test('claude-code is OAuth on the dedicated URL (no Authorization header)', () => {
    const raw = read('adapters/claude-code/.mcp.json');
    const json = JSON.parse(raw) as { mcpServers: { sumanos: { url: string; headers?: unknown } } };
    expect(json.mcpServers.sumanos.url).toContain('/mcp/authoring/agents/');
    expect(json.mcpServers.sumanos.url).toContain('SUMANOS_AGENT_ID');
    expect(json.mcpServers.sumanos.url).toContain('app.sumanos.com');
    expect(json.mcpServers.sumanos.headers).toBeUndefined();
    expect(raw).not.toMatch(/Authorization|SUMANOS_KEY/);
  });

  test('codex uses the dedicated URL and optional admin API key env', () => {
    const json = JSON.parse(read('adapters/codex/.mcp.json')) as {
      mcpServers: { sumanos: { url: string; bearer_token_env_var?: string } };
    };
    expect(json.mcpServers.sumanos.url).toContain('/mcp/authoring/agents/');
    expect(json.mcpServers.sumanos.url).toContain('SUMANOS_AGENT_ID');
    expect(json.mcpServers.sumanos.bearer_token_env_var).toBe('SUMANOS_KEY');
  });

  test('opencode defaults to dedicated URL without a forced bearer (OAuth)', () => {
    const json = JSON.parse(read('adapters/opencode/opencode.json')) as {
      mcp: { sumanos: { url: string; headers?: unknown } };
    };
    expect(json.mcp.sumanos.url).toContain('/mcp/authoring/agents/');
    expect(json.mcp.sumanos.url).toContain('SUMANOS_AGENT_ID');
    expect(json.mcp.sumanos.headers).toBeUndefined();
  });

  test('hermes uses its supported config materializer instead of ignored manifest fields', () => {
    const manifest = read('adapters/hermes/plugin.yaml');
    const adapter = read('adapters/hermes/__init__.py');
    expect(manifest).not.toContain('mcp_servers:');
    expect(manifest).not.toContain('skills:');
    expect(adapter).toContain('materialize_connections');
    expect(adapter).toContain('ctx.register_skill');
  });

  test('core contract files use the dedicated path', () => {
    const manifest = read('core/manifest.yaml');
    expect(manifest).toContain('/mcp/authoring/agents/');
    expect(manifest).toContain('SUMANOS_AGENT_ID');
    const server = JSON.parse(read('core/mcp/server.json')) as { url: string };
    expect(server.url).toContain('/mcp/authoring/agents/');
  });
});

describe('Suma adapters ship prod and develop MCP servers', () => {
  test('claude-code registers both environments without a bearer header', () => {
    const json = JSON.parse(read('adapters/claude-code/.mcp.json')) as {
      mcpServers: Record<string, { url: string; headers?: unknown }>;
    };
    expect(json.mcpServers.sumanos.url).toBe(
      `https://app.sumanos.com/mcp/authoring/agents/\${SUMANOS_AGENT_ID}`,
    );
    expect(json.mcpServers['sumanos-dev']?.url).toBe(
      `https://development.sumanos.com/mcp/authoring/agents/\${SUMANOS_AGENT_ID}`,
    );
    expect(json.mcpServers.sumanos.headers).toBeUndefined();
    expect(json.mcpServers['sumanos-dev']?.headers).toBeUndefined();
  });

  test('codex registers both environments with SUMANOS_KEY', () => {
    const json = JSON.parse(read('adapters/codex/.mcp.json')) as {
      mcpServers: Record<string, { url: string; bearer_token_env_var?: string }>;
    };
    expect(json.mcpServers.sumanos.url).toContain('app.sumanos.com');
    expect(json.mcpServers['sumanos-dev']?.url).toContain('development.sumanos.com');
    expect(json.mcpServers.sumanos.bearer_token_env_var).toBe('SUMANOS_KEY');
    expect(json.mcpServers['sumanos-dev']?.bearer_token_env_var).toBe('SUMANOS_KEY');
  });

  test('opencode registers both environments', () => {
    const json = JSON.parse(read('adapters/opencode/opencode.json')) as {
      mcp: Record<string, { url: string }>;
    };
    expect(json.mcp.sumanos.url).toContain('app.sumanos.com');
    expect(json.mcp['sumanos-dev']?.url).toContain('development.sumanos.com');
  });

  test('hermes materializes both environments from explicit descriptors', () => {
    const adapter = read('adapters/hermes/__init__.py');
    const configure = read('adapters/hermes/configure.py');
    expect(adapter).toContain('https://app.sumanos.com');
    expect(adapter).toContain('https://development.sumanos.com');
    expect(adapter).toContain('/mcp/authoring/agents/');
    expect(configure).toContain('read_raw_config');
    expect(configure).toContain('save_config');
  });

  test('core manifest and server.json list both environments', () => {
    const manifest = read('core/manifest.yaml');
    expect(manifest).toContain('development.sumanos.com');
    expect(manifest).toContain('sumanos-dev');
    const server = JSON.parse(read('core/mcp/server.json')) as {
      url: string;
      environments?: Record<string, { id: string; url: string }>;
    };
    expect(server.url).toContain('app.sumanos.com');
    expect(server.environments?.prod.url).toContain('app.sumanos.com');
    expect(server.environments?.develop.url).toContain('development.sumanos.com');
    expect(server.environments?.develop.id).toBe('sumanos-dev');
  });
});
