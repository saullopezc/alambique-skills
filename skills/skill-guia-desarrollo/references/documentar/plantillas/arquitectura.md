---
id: arquitectura
tipo: arquitectura
proyecto: <nombre-del-proyecto>
actualizado: YYYY-MM-DD
estado: borrador                # borrador | vigente | retirado | reemplazado-por-<id>
version: 0.1                    # menor: corrección · mayor: cambia lo que el documento afirma
clasificacion: <C0-C3>          # clase del dato; sin valor por defecto: se decide antes de escribir
responsable: <persona real>     # nunca una herramienta
revision: YYYY-MM-DD            # cuando toca releerlo (6 meses por defecto)
tags: [arquitectura]
---

# Arquitectura

<1-2 frases: estilo de la arquitectura (pipeline, capas, monolito modular,
microservicios...) y la razón de fondo.>

## Componentes

| Componente | Responsabilidad | Código | Nodo |
|---|---|---|---|
| <nombre> | <una línea> | `src/...` | [[modulo-<nombre>]] |

## Flujo de datos

```mermaid
graph LR
    IN[<entrada>] --> C1[<componente>]
    C1 --> C2[<componente>]
    C2 --> OUT[<salida>]
```

<Describir el flujo en 2-4 frases: qué entra, qué transformaciones sufre,
qué sale y hacia dónde.>

## Fronteras y contratos

- <Interfaces entre componentes, formatos de intercambio, contratos con
  sistemas externos que NO se pueden romper.>

## Decisiones que dieron esta forma

- [[decision-YYYYMMDD-<slug>]] — <una línea>

Relacionado: [[resumen-proyecto]], [[stack]]
