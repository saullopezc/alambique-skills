---
id: resumen-proyecto
tipo: resumen
proyecto: <nombre-del-proyecto>
actualizado: YYYY-MM-DD
estado: borrador                # borrador | vigente | retirado | reemplazado-por-<id>
version: 0.1                    # menor: corrección · mayor: cambia lo que el documento afirma
clasificacion: <C0-C3>          # clase del dato; sin valor por defecto: se decide antes de escribir
responsable: <persona real>     # nunca una herramienta
revision: YYYY-MM-DD            # cuando toca releerlo (6 meses por defecto)
tags: [resumen]
---

# <nombre-del-proyecto> — resumen

<2-4 frases: qué es el proyecto, qué problema resuelve, para quién.>

## Partes más importantes

| Parte | Dónde | Por qué importa |
|---|---|---|
| <componente crítico> | `src/...` | <razón — ej. punto de entrada, lógica de negocio central> |
| <segunda parte> | `...` | <razón> |

## Cómo navegar el proyecto

- Stack y cómo construir/ejecutar: [[stack]]
- Cómo encajan las piezas: [[arquitectura]]
- Detalle por componente: nodos `modulo-*` en el índice
- Decisiones tomadas y su porqué: nodos `decision-*`

## Estado actual

<1-3 bullets: fase del proyecto, qué funciona, qué está en curso. Fechas absolutas.>

## Contexto que no está en el código

<Restricciones, acuerdos con el cliente, deuda conocida, dependencias externas.
Si no hay nada, eliminar la sección.>
