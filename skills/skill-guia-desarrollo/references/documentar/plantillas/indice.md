---
id: README
tipo: indice
proyecto: <nombre-del-proyecto>
actualizado: YYYY-MM-DD
estado: borrador                # borrador | vigente | retirado | reemplazado-por-<id>
version: 0.1                    # menor: corrección · mayor: cambia lo que el documento afirma
clasificacion: <C0-C3>          # clase del dato; sin valor por defecto: se decide antes de escribir
responsable: <persona real>     # nunca una herramienta
revision: YYYY-MM-DD            # cuando toca releerlo (6 meses por defecto)
tags: [indice]
---

# Documentación de <nombre-del-proyecto>

Punto de entrada del grafo de conocimiento. Empieza por [[resumen-proyecto]].

## Nodos

| Nodo | Tipo | Qué contiene | Relacionado |
|---|---|---|---|
| [[resumen-proyecto]] | resumen | Propósito y partes más importantes | [[stack]], [[arquitectura]] |
| [[stack]] | stack | Tecnologías, versiones, build/run | [[arquitectura]] |
| [[arquitectura]] | arquitectura | Componentes y flujo de datos | modulos |
| [[modulo-<nombre>]] | modulo | <una línea> | <nodos> |
| [[decision-YYYYMMDD-<slug>]] | decision | <una línea> | <nodos> |
| [[runbook-<slug>]] | runbook | <una línea> | <nodos> |

## Grafo

```mermaid
graph LR
    R[resumen-proyecto] --> S[stack]
    R --> A[arquitectura]
    A --> M1[modulo-...]
    M1 -.-> D1[decision-...]
```

<!-- Flechas sólidas: "se apoya en / contiene". Punteadas: "motivado por / ver también". -->

## Pendientes

Nodos referenciados con un wiki-link que aún no existen:

- (ninguno)
