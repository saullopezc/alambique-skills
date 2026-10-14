---
id: modulo-<nombre>
tipo: modulo
proyecto: <nombre-del-proyecto>
actualizado: YYYY-MM-DD
estado: borrador                # borrador | vigente | retirado | reemplazado-por-<id>
version: 0.1                    # menor: corrección · mayor: cambia lo que el documento afirma
clasificacion: <C0-C3>          # clase del dato; sin valor por defecto: se decide antes de escribir
responsable: <persona real>     # nunca una herramienta
revision: YYYY-MM-DD            # cuando toca releerlo (6 meses por defecto)
tags: [modulo, <tema>]
---

# Módulo: <nombre>

<1-2 frases: qué hace y por qué existe.>

## Ubicación y entry points

- Código: `src/<...>`
- Entry points: `<función/clase/script principal>`

## Entradas y salidas

| Dirección | Qué | Formato / contrato | Origen / destino |
|---|---|---|---|
| Entrada | <datos> | <formato> | [[modulo-<otro>]] o `<externo>` |
| Salida | <datos> | <formato> | [[modulo-<otro>]] o `<externo>` |

## Configuración

- <Parámetros, archivos de config, variables de entorno. Valores reales →
  placeholders + `*.example`.>

## Particularidades

- <Gotchas, límites conocidos, deuda técnica, comportamiento no obvio.
  Lo que le ahorraría una tarde de debugging al siguiente.>

Relacionado: [[arquitectura]]
