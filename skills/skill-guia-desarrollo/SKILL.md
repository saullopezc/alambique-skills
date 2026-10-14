---
name: skill-guia-desarrollo
description: Baseline de ingeniería para cualquier lenguaje — proceso, arquitectura, seguridad, pruebas, revisión y documentación. Activar al crear, diseñar, refactorizar o estructurar código; y con "arquitectura", "clean architecture", "SOLID"; "seguridad", "OWASP", "secretos", "sanitizar input"; "tests", "cobertura", "casos límite", "validar el cambio", "evidencia de QA"; "code review", "revisa el PR"; "SQL", "query lenta", "N+1"; "Docker"; "logging"; "commit", "ramas", "CI", "pre-commit"; "contrato de salida"; "autoría"; "documenta este proyecto", "ADR"; "planifica este cambio", "multifase"; "buenas prácticas". Cubre TAMBIÉN el lenguaje concreto, como principios y sin recetas de framework — C (.c .h, punteros, memoria, embebido; de C++ solo lo común), Java/JVM (.java), Python (.py, asyncio), Perl (.pl .pm .t, regex) — activar igual con "revisar <lenguaje>"; el detalle, en references/lenguajes/<lenguaje>.md, bajo demanda. Es la capa base de cualquier trabajo de código.
---

# Baseline de Ingeniería

Reglas no negociables para tocar código. Este fichero **enruta** y fija lo que aplica
siempre; el criterio de cada materia vive en su referencia (`references/`) y aquí solo
se nombra. Leer la especificación vigente antes de escribir la primera línea.

## Enrutado

| Para | Dónde |
|---|---|
| Un error ya visto antes | Buscar el **síntoma literal** en la documentación del proyecto (`docs/`, sus `runbook-*`) — **PRIMERO**, antes de leer código o formular hipótesis |
| C — `.c` `.h`, punteros, memoria, embebido, firmware, drivers (de C++ solo lo común) | `references/lenguajes/c.md` |
| Java / JVM — `.java`: nulos, excepciones, inyección, persistencia, concurrencia | `references/lenguajes/java.md` |
| Python — `.py`: tipos, errores, asincronía, servicios, empaquetado | `references/lenguajes/python.md` |
| Perl — `.pl` `.pm` `.t`: contexto, errores, expresiones regulares, acceso a datos | `references/lenguajes/perl.md` |
| Módulos de un producto o dominio concreto | la guía del producto o del proyecto, si existe; si no, `references/validacion.md` |
| Todo lo demás (criterio de ingeniería) | las **referencias** de aquí abajo |

## Proceso

1. **Entender primero:** problema, usuarios, alcance y lo que queda **fuera** de
   alcance. Decisión que falta → preguntar; nunca suponer.
2. **Especificar antes de codificar:** criterios de aceptación numerados y
   comprobables ("cuando `<evento>`, el sistema `<respuesta>`"; "si `<fallo>`,
   entonces `<respuesta>`"), casos límite (vacío, duplicado, corrupto, límites,
   concurrencia), requisitos no funcionales y preguntas abiertas.
3. **Revisar la especificación como crítico:** ambigüedades, contradicciones, casos
   ausentes. Detectar, no resolver.
4. **Planificar:** módulos, modelo de datos, interfaces, decisiones con su
   alternativa descartada. Cada requisito mapea a un componente.
5. **Trocear** en tareas de <30 min, ordenadas por dependencia, cada una con su
   "terminado cuando" verificable.
6. **Implementar de una en una:** prueba primero, suite completa, marcar y parar.
   **Nunca avanzar en rojo** (`references/qa.md`).
7. **Validar requisito por requisito** → `references/qa.md`. Si el cambio toca una
   salida que otro sistema consume → `references/contrato-salida.md` antes de cerrar.
8. **Cambio de alcance:** primero la especificación, se enseña el diff, luego el código.

## Arquitectura

**Las dependencias apuntan hacia dentro:** la lógica de negocio no conoce el framework,
la UI, la base de datos ni la red. Capas, la prueba que lo verifica, atributos de
calidad, SOLID y patrones → `references/arquitectura.md`. Cada decisión se registra con
su motivo y con lo que se sacrificó (ADR: `references/documentar.md`).

## Código — principios que valen en cualquier lenguaje

Se citan por su identificador, con los niveles de `references/revision.md`. Los de
seguridad y de datos tienen su propio dueño: `references/seguridad.md` y
`references/base-datos.md`.

| # | Principio | Cómo falla | Nivel |
|---|-----------|------------|-------|
| **G-01** | **El idioma lo fija el proyecto, y es uno solo para cada cosa:** identificadores, ficheros y commits por un lado; comentarios y mensajes al usuario por otro. Sin convención previa, inglés para lo primero. | La mezcla obliga a adivinar en cada búsqueda. | DETALLE |
| **G-02** | **Nombres que revelan intención y salen del vocabulario del negocio, funciones cortas, sin duplicación, efectos ocultos ni código muerto.** Los comentarios explican el porqué, no el qué. | El siguiente cambio se hace sin entender y rompe lo que no se ve. | DEBERÍA; el código muerto o comentado, BLOQUEANTE |
| **G-03** | **Todo error se comprueba donde ocurre y nunca se descarta; al envolverlo se conserva la causa.** Fallar ruidosamente, nunca en silencio. | Se sigue con un estado inválido y el fallo aparece lejos de su origen. | BLOQUEANTE |
| **G-04** | **Todo recurso se libera en todos los caminos,** con la construcción del lenguaje que lo garantiza. | Con un error en medio no se cierra: conexiones o descriptores agotados bajo carga. | BLOQUEANTE |
| **G-05** | **Lo que comparten hilos o peticiones no guarda estado mutable sin protección; los cerrojos se toman siempre en el mismo orden; el contexto de una petición no viaja en globales ni queda en el hilo al terminar.** | Datos de una petición aparecen en otra, solo bajo carga; o bloqueo mutuo. | BLOQUEANTE |
| **G-06** | **Una declaración —anotación, tipo, opción de configuración— se comprueba por su efecto, no por estar escrita.** | Una protección o una validación que parece puesta y no actúa. | BLOQUEANTE |
| **G-07** | **Lo obligatorio de la configuración no tiene valor por defecto, y lo que viene del entorno se convierte explícitamente.** | Una variable de entorno es texto: «false» es verdadero. Un secreto por defecto llega a producción. | DEBERÍA |
| **G-08** | **Una sola fuente para la versión del lenguaje o del estándar y para las de las dependencias; lo declarado es lo que el código usa.** Ni dependencia nueva ni cambio de esquema sin actualizar antes la especificación. | Funciona en el puesto y falla en una instalación limpia. | DEBERÍA |
| **G-09** | **Un solo formateador, con el estilo que el proyecto ya tiene; las reglas del linter se declaran, no se heredan por defecto.** | Dos formateadores se deshacen el trabajo en cada guardado; las reglas por defecto cambian al actualizar. | DETALLE |
| **G-10** | **Ningún fichero de código pasa de 1000 líneas** (objetivo, menos de 600); se divide por responsabilidad, no por número de líneas. | Nadie lo lee entero y cada cambio toca lo que no entiende. | DEBERÍA |
| **G-11** | **Una sustitución de texto comprueba antes que el patrón existe** (`references/validacion.md`). | Un cambio perdido en silencio. | DEBERÍA |
| **G-12** | **La solución más simple que cumple el requisito real;** nada se añade por un requisito hipotético. | Cada indirección de más se paga en cada lectura y en cada cambio. | DEBERÍA |

Las guías de lenguaje (`references/lenguajes/`) siguen la misma forma y traen **solo lo
propio de cada lenguaje**: lo que esta tabla y las referencias ya dicen no se repite allí.
Son principios, sin código ni recetas de un framework: eso envejece y el principio no.

## Convenciones que usan estas guías

Valen con la skill sola; las referencias las usan sin volver a definirlas.

- **Clase del dato** — se decide antes de leer y antes de escribir: `C0` público ·
  `C1` interno · `C2` infraestructura del cliente · `C3` credenciales y datos reales.
  Ante la duda, la más alta.
- **`_local/`** — directorio del proyecto que **no se versiona** (cómo se ignora:
  `references/git.md`). Ahí vive todo `C2` y `C3`; la evidencia de cada validación,
  en `_local/qa/`.
- **Alias, nunca coordenadas** — en código, documentos y mensajes va un nombre estable
  (`<alias-bd>`). La coordenada —IP, host, ruta de servidor— vive fuera del repositorio,
  en la configuración local de lo que conecta (`~/.ssh/config`, el entorno); la
  credencial, en el entorno o en un gestor de secretos (`references/seguridad.md`), y
  con el marco alambique, lo que el agente no debe leer, en `__restriccion/`.
- **De cada artefacto responde una persona identificada**, nunca una herramienta: sin
  atribución a IA en commits, cabeceras ni documentos
  (`references/documentacion-codigo.md`).

Coinciden con R-01, R-02, R-03 y R-11 del marco alambique; las citas `(R-xx)` de estas
guías son trazabilidad hacia su norma, y no hace falta tenerlo instalado. Donde el
puesto lo usa, un mecanismo comprueba parte de ellas; donde no, dependen de quien
escribe.

## Cierre de cualquier tarea

Suite y linters en verde, reportar el resultado **real**, decir qué cambió y qué
queda abierto. Orden de prioridad ante un conflicto: corrección, seguridad,
legibilidad, mantenibilidad, testabilidad, rendimiento.

**Nada está terminado hasta estar documentado:** lo que cambió, en el nodo de `docs/`
que lo describe; un fallo resuelto, con su síntoma literal, la causa, la solución y
cómo verificar que quedó resuelto. Dónde cae cada cosa, y cuándo no toca documentar
todavía → `references/documentar.md`.

**Ahí acaba el desarrollo.** Desplegar, operar sobre un servidor, hacer push a un
remoto, publicar un paquete o entregar al cliente ya no son parte de la tarea de
código. Son acciones irreversibles o dirigidas al exterior: cada una necesita
aprobación explícita en el turno que la origina, y el permiso dado para una tarea no
cubre la siguiente (R-08 y R-10). Haber terminado el cambio no las autoriza.

## Referencias — leer solo la que amplía el tema en curso

Cada una es compacta: las reglas necesarias de su materia y, donde hace falta, el formato que se copia para trabajar.

| Fichero | Amplía |
|---|---|
| `arquitectura.md` | Cómo se decide, **atributos de calidad y sus trade-offs**, capas, SOLID, patrones, contratos |
| `qa.md` | Matriz de pruebas, diseño, el instrumento que debe verse detectar, defectos, informe final |
| `revision.md` | El criterio de code review: orden, niveles de hallazgo, veredicto |
| `seguridad.md` | Modelado de amenazas (STRIDE), los fallos de siempre por tema, validación en frontera, secretos |
| `base-datos.md` | Esquema, índices y **el método para diagnosticar rendimiento** (y sus cinco reglas) |
| `docker.md` | Capas, no-root, multi-stage, imagen que soporta QA |
| `documentar.md` | Grafo de conocimiento en `docs/`, proporcionalidad, frontmatter, dónde cae un incidente (+ `documentar/plantillas/`) |
| `documentar/grafo-conocimiento.md` | Nodos y enlaces del grafo, y el script que lo valida |
| `fases.md` | Plan por fases: cuándo toca, su estructura, las fases y el registro de cambios |
| `validacion.md` | Validar sin framework de test, A/B contra la versión liberada, evidencia en `_local/qa/` |
| `contrato-salida.md` | Cambiar algo que otro sistema consume: las 6 preguntas de la pérdida de información |
| `documentacion-codigo.md` | Comentarios, autoría y sellado `Modified By`, cabecera mínima de documento |
| `checklists.md` | Listas de comprobación de complejidad y de rendimiento |
| `git.md` | Commits convencionales, ramas, checklist pre-PR, higiene del repo, barrido antes de versionar |
| `tooling.md` | SAST y secretos, editor, `.editorconfig`, hooks de pre-commit, pipeline CI/CD |
| `logging.md` | Niveles, qué se loguea y qué no, trazas, anti-patrones |
