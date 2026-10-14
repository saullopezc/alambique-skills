---
id: procedencia
titulo: Procedencia
tipo: referencia
clasificacion: C0
responsable: Saul López
---

# Procedencia

Este repositorio es obra personal de Saul López bajo licencia MIT, con una excepción
que conserva la licencia y la atribución de su origen.

## Obra de terceros: `skill-asistente-colaborativo` §Forma de la respuesta — i-have-adhd

| | |
|---|---|
| **Origen** | [`i-have-adhd`](https://github.com/ayghri/i-have-adhd), skill de Claude Code |
| **Titular del copyright** | Ayoub Ghriss (`ayghri`) — © 2026 |
| **Licencia** | MIT — texto completo en [`LICENSE-MIT-i-have-adhd.txt`](../skills/skill-asistente-colaborativo/LICENSE-MIT-i-have-adhd.txt), dentro de la skill: así viaja con ella cuando se instala o se copia sola |
| **Dónde** | `skills/skill-asistente-colaborativo/SKILL.md`, sección «Forma de la respuesta» |

**Qué se tomó.** Las **diez reglas** del original y su arquitectura en tres partes: las
reglas, las excepciones y la comprobación previa al envío. Es una adaptación, no una cita:
el esqueleto es del original.

**Qué se cambió:**

1. Traducido al español y reescrito para encajar con las directrices de la skill.
2. Las excepciones pasan de seis a cuatro: no se incorporan la de ambigüedad en la
   petición, que cubre la directriz 2 de la skill, ni la de conflicto con el harness.
3. El tope de cinco items es regla de presentación, con excepción explícita donde la
   completitud es el requisito.
4. La regla de borrar coberturas no alcanza a las que llevan incertidumbre real.
5. Sin persistencia con interruptor (`stop adhd mode`), sin el `description` del original
   y sin sus ejemplos en inglés.

---

Saul López — github.com/saullopezc
