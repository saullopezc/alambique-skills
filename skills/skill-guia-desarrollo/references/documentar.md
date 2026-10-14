# Documentar un proyecto — el grafo de `docs/`

Cómo se enlazan y se validan los nodos: `documentar/grafo-conocimiento.md`. Lo que va
dentro de los ficheros: `documentacion-codigo.md`.

| Regla | Por qué importa |
|---|---|
| **Lo mínimo que el proyecto necesita.** Una prueba o un script suelto no se documenta todavía, y se dice; un proyecto sin forma espera a tener más de un módulo, un consumidor u otra persona. | Los nodos vacíos, creados por completitud, no los mantiene nadie. |
| **Antes de crear se mira qué hay.** Documentación con convención propia: se adapta uno a ella, y la migración al grafo solo se hace si el usuario la aprueba. Ya es un grafo: se actualiza, no se regenera. Lo que no encaja se mueve a `_local/`, nunca se borra. | Sobrescribir a ciegas deshace lo que el proyecto ya había decidido. |
| **No se inventa estructura ni tipo:** se usa la plantilla de `documentar/plantillas/`. | El índice y la validación dependen de esa forma. |
| **Al cerrar una sesión que cambió código, configuración o estructura se comprueba qué nodo queda desactualizado.** | La documentación desactualizada es un bug. |

## Nodos

| Nodo | Plantilla | Para qué |
|---|---|---|
| `docs/README.md` | `indice.md` | Índice: tabla de nodos y diagrama |
| `docs/resumen-proyecto.md` | `resumen-proyecto.md` | Propósito, partes importantes, cómo navegar |
| `docs/stack.md` | `stack.md` | Tecnologías con su evidencia; cómo construir y ejecutar |
| `docs/arquitectura.md` | `arquitectura.md` | Componentes, flujo de datos, contratos |
| `docs/modulo-<nombre>.md` | `modulo.md` | Uno por módulo importante |
| `docs/decision-YYYYMMDD-<slug>.md` | `decision.md` | ADR: una decisión, con el atributo priorizado y el sacrificado |
| `docs/runbook-<slug>.md` | `runbook.md` | Procedimientos operativos |

Lo que no tiene tipo propio:

- **Incidente o fallo resuelto** → un `runbook-<slug>`, o una fila en «Si algo falla»
  del runbook que ya cubre ese procedimiento. Lleva el síntoma literal, la causa, cómo
  confirmarla, la solución y cómo verificar que quedó resuelto; si el síntoma engañaba,
  la pista real.
- **As-built** → `arquitectura` o el `modulo-*` afectado; si hubo elección, además una
  `decision-*`.

## Frontmatter — su única definición

Todo nodo, índice incluido, abre con estos campos, en este orden, entre dos líneas `---`.
La validación exige los obligatorios; los demás, si se dejan, llevan un valor real, no un
marcador.

| Campo | Obligatorio | Valor |
|---|---|---|
| `id` | **sí** | Nombre del fichero sin `.md`, en kebab-case; el índice, `README` |
| `tipo` | **sí** | `indice` · `resumen` · `stack` · `arquitectura` · `modulo` · `decision` · `runbook` |
| `proyecto` | no | Nombre del proyecto |
| `actualizado` | no | `YYYY-MM-DD` del último cambio de contenido |
| `estado` | no | `borrador` · `vigente` · `retirado` · `reemplazado-por-<id>`; el cuerpo no declara otro |
| `version` | no | Menor: corrección; mayor: cambia lo que el documento afirma |
| `clasificacion` | **sí** | `C0`..`C3` (`../SKILL.md`; R-01 del marco alambique), sin valor por defecto. Un nodo `C2` o `C3` no va en el `docs/` versionado: vive en `_local/` |
| `responsable` | **sí** | Una persona identificada, nunca una herramienta (R-11) |
| `revision` | no | `YYYY-MM-DD` en que toca releerlo (seis meses por defecto) |
| `tags` | no | Lista de temas |

## Antes de dar por terminado

- Validación de `documentar/grafo-conocimiento.md` ejecutada, sin más aviso que el de los
  enlaces a nodos pendientes.
- Frontmatter obligatorio completo y ningún marcador sin rellenar, tampoco en el cuerpo,
  que la validación no mira.
- Índice sincronizado con los nodos; el README raíz apunta a `docs/README.md`, no lo
  duplica.
- Fechas absolutas, nunca «hoy»: compactas en el nombre del fichero, ISO en el
  frontmatter y en el cuerpo.
- Cero secretos, y alias en vez de coordenadas (R-03); cero rutas de máquina local.
