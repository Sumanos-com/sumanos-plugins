# Suma operator runbook

## Orden seguro

1. `list_agents` para resolver agente.
2. `read_soul` antes de cualquier `edit_soul`.
3. Tools typed primero: `edit_soul`, `set_model`, `install_plugin`, `set_credential`.
4. Workspace tools sólo si typed no alcanza.
5. Verificar con logs/lecturas después de aplicar.

## Riesgo

- Bajo: cambios de SOUL/modelo cuando el provider ya está configurado.
- Alto: instalar plugins, credenciales y cambios raw de VM.

## Cierre

Nunca digas “terminado” sin evidencia. Si algo queda staged o bloqueado, decilo explícitamente.
