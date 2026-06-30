# Suma — runbook operativo interno

## Objetivo

Usar Suma para mejorar o reparar un agente Sumanos de forma segura, auditada y reversible.

## Antes de tocar un agente

1. Confirmar el `accountId`/org objetivo.
2. Confirmar el `agentId`.
3. Confirmar el tier de la key:
   - cliente: cambios seguros, alto riesgo staged;
   - operador: cambios directos + workspace tools;
   - superadmin: mintea operator keys scopeadas.
4. No usar credenciales personales del cliente en texto plano.

## Flujo recomendado

1. `list_agents` para resolver el agente.
2. `read_soul` antes de editar identidad.
3. Preparar preview del cambio.
4. Aplicar con tool typed cuando exista.
5. Usar workspace tools sólo para diagnóstico/reparación técnica.
6. Verificar health/logs.
7. Dejar resumen de qué cambió y qué quedó pendiente.

## Criterio de comandos

- `/suma-connect` — entrar.
- `/suma-check` — mirar sin tocar.
- `/suma-improve` — mejorar comportamiento/configuración.
- `/suma-fix` — reparar algo roto.
- `/suma-install` — agregar capacidad aprobada.
- `/suma-report` — explicar estado y próximos pasos.

## Tools typed

- `list_agents`
- `read_soul`
- `edit_soul`
- `set_model`
- `install_plugin`
- `set_credential`

## Workspace tools de operador

- `read_file`
- `write_file`
- `list_dir`
- `run_command`
- `read_logs`
- `restart_gateway`

## Reglas duras

- No SSH.
- No secretos inline.
- No tocar otro org/agente.
- No instalar código de alto riesgo sin aprobación cuando el actor sea cliente.
- No hacer cambios manuales si existe una tool typed más segura.

## Evidencia mínima para cerrar una operación

- Tool usada.
- Agente afectado.
- Resultado observado.
- Si hubo restart, confirmación de health.
- Si algo quedó staged, quién debe aprobarlo.
