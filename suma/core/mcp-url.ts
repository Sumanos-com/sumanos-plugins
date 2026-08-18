/** OAuth / dedicated-route origin. API keys use the same host so resource metadata matches. */
export const SUMA_OAUTH_ORIGIN = 'https://app.sumanos.com';
export const SUMA_AGENT_ID_ENV = 'SUMANOS_AGENT_ID';
export const SUMA_KEY_ENV = 'SUMANOS_KEY';

export const SUMA_ENVIRONMENTS = {
  prod: { id: 'sumanos', origin: 'https://app.sumanos.com' },
  develop: { id: 'sumanos-dev', origin: 'https://development.sumanos.com' },
} as const;

export type SumaEnv = keyof typeof SUMA_ENVIRONMENTS;

export function resolveSumaEnv(raw?: string): SumaEnv {
  const value = (raw ?? '').trim().toLowerCase();
  if (value === 'develop' || value === 'development' || value === 'dev') return 'develop';
  return 'prod';
}

export function customerMcpUrl(origin: string, agentId: string): string {
  return `${origin.replace(/\/+$/, '')}/mcp/authoring/agents/${encodeURIComponent(agentId)}`;
}

export function dedicatedMcpUrl(agentId: string, env: SumaEnv = 'prod'): string {
  return customerMcpUrl(SUMA_ENVIRONMENTS[env].origin, agentId);
}
