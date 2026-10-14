---
id: decision-YYYYMMDD-<slug>
tipo: decision
proyecto: <nombre-del-proyecto>
actualizado: YYYY-MM-DD
estado: borrador                # borrador | vigente | retirado | reemplazado-por-<id>
version: 0.1                    # menor: corrección · mayor: cambia lo que el documento afirma
clasificacion: <C0-C3>          # clase del dato; sin valor por defecto: se decide antes de escribir
responsable: <persona real>     # nunca una herramienta
revision: YYYY-MM-DD            # cuando toca releerlo (6 meses por defecto)
tags: [decision, <tema>]
---

# Decisión: <título corto>

<!-- Estado y fecha son los de la cabecera, y no se repiten aquí: `borrador` mientras
     es propuesta, `vigente` cuando se acepta. La fecha de la decisión va en el nombre
     del fichero. -->

- **Decisores:** <quién la tomó — personas reales, nunca herramientas>

## Contexto

<Qué problema o disyuntiva había. 2-4 frases.>

## Decisión

<Qué se decidió, en una frase afirmativa.>

## Atributos de calidad

- **Priorizado:** <qué atributo gana con esta decisión: rendimiento,
  disponibilidad, mantenibilidad...>
- **Sacrificado:** <qué atributo se paga a cambio, y por qué es aceptable.>

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| <opción B> | <razón> |

## Consecuencias

- <Qué gana el proyecto, qué costo asume, qué queda condicionado por esto.>

Afecta a: [[modulo-<nombre>]], [[arquitectura]]

<!-- Solo si sustituye a otra, que pasa a `estado: reemplazado-por-<este id>`: -->
Reemplaza a: [[decision-YYYYMMDD-<anterior>]]
