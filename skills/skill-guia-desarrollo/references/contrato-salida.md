# Contrato de salida

Aplica cuando un cambio toca lo que **otro sistema consume** —fichero, columnas, esquema,
API, evento—: el código puede ser impecable y el cambio, un fallo. Antes de cerrarlo, seis
preguntas **respondidas por escrito**.

| Pregunta | Por qué |
|---|---|
| **¿Algún dato deja de llegar?** | Una etapa que solo propaga lo declarado lo pierde en silencio: se rastrea etapa por etapa. |
| **¿Alguna posición cambia de significado?** | En un formato posicional, el hueco que se ocupa ha de ser el mismo en todas las salidas equivalentes; si no, el consumidor necesita un parser por variante. |
| **¿El formato es retrocompatible?** | Cambiar la representación de un identificador rompe a quien lo parsea. |
| **¿Cada concepto ocupa el mismo sitio en todas las salidas?** | Homologar ahora cuesta una línea; después, una migración. |
| **¿Hay un consumidor con el mapeo montado?** | Sin nada en producción, corregir es barato: se dice al proponerlo. |
| **¿El valor nuevo se suma o se desglosa?** | Un subconjunto sin declarar se cuenta dos veces: se documenta con el campo. |

**El cambio no termina en el commit:** la entrega incluye decirle al consumidor qué
cambia y qué tiene que tocar, con el antes y el después reales. Validarlo: `validacion.md`.
