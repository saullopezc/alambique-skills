---
id: runbook-<slug>
tipo: runbook
proyecto: <nombre-del-proyecto>
actualizado: YYYY-MM-DD
estado: borrador                # borrador | vigente | retirado | reemplazado-por-<id>
version: 0.1                    # menor: corrección · mayor: cambia lo que el documento afirma
clasificacion: <C0-C3>          # clase del dato; sin valor por defecto: se decide antes de escribir
responsable: <persona real>     # nunca una herramienta
revision: YYYY-MM-DD            # cuando toca releerlo (6 meses por defecto)
tags: [runbook, operacion]
---

# Runbook: <procedimiento>

- **Cuándo se usa:** <situación que dispara este procedimiento; si documenta un
  incidente, el fragmento estable del síntoma, con sus palabras exactas y con alias o
  marcadores en lugar de host, ruta e identificador>
- **Riesgo:** bajo | medio | alto — <qué puede salir mal>
- **Reversible:** sí / no — <cómo se revierte>

## Prerequisitos

- <Accesos por alias (nunca hosts ni credenciales reales), estado esperado del sistema.>

## Pasos

1. <paso — un comando o acción verificable por paso>
   ```bash
   <comando>
   ```
   Resultado esperado: <qué debe verse>
2. <paso>

## Verificación final

- <Cómo confirmar que el procedimiento terminó bien.>

## Si algo falla

| Síntoma | Causa probable | Acción |
|---|---|---|
| <fragmento estable del error, sin coordenadas> | <causa, y cómo confirmarla> | <acción o nodo a consultar> |

Relacionado: [[stack]], [[modulo-<nombre>]]
