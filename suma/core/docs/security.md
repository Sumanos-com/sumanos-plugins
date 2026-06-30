# Suma security

- Never hardcode keys in manifests, prompts or docs.
- Use `SUMANOS_KEY` / operator key only as environment variables.
- Client auth can use browser login where the host supports OAuth.
- Operator auth uses Bearer against `https://api.sumanos.com/mcp/authoring`.
- Workspace/raw VM tools are operator-only and must be verified with logs or reads.
