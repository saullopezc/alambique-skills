# Validación — cómo se cierra un cambio

**Ningún cambio termina sin validación;** la forma depende del stack. El criterio de pruebas:
`qa.md`.

| Situación | Validación mínima |
|---|---|
| Con framework de test | Prueba unitaria del cambio + suite en verde |
| Sin framework viable | Compilación limpia + prueba de humo + **comparación A/B de salidas** (misma entrada, base frente a nueva) |
| Módulo de un producto propietario | Su guía; si no existe, entorno local + comparación A/B |
| Solo configuración o documentación | Sintaxis + verificación del **efecto** |

**Si no se sabe cómo se prueba, se CONSULTA,** y la respuesta se documenta (`documentar.md`):

```
Antes de dar el cambio por terminado necesito saber cómo se valida aquí:
1. ¿Hay pruebas automatizadas? ¿Con qué se corren? (comando exacto)
2. ¿Existe entorno de QA/staging, o se prueba con datos reales de qué fuente?
```

| Regla | Cómo falla |
|---|---|
| **Una sustitución de texto comprueba antes que el patrón existe, busca después los identificadores nuevos, y va una por una.** | Un patrón que no coincide deja el fichero intacto sin avisar. |
| **La versión base de una comparación A/B es la LIBERADA.** | El árbol de trabajo ya lleva medio cambio. |
| **Antes de medir se verifica que lo medido está instalado,** comparando sumas de comprobación. | Se mide la versión vieja sin saberlo. |
| **Los registros se emparejan antes de comparar.** | El orden distinto parece hallazgo. |
| **Una optimización se valida por equivalencia de salida.** | Cambia el resultado, no solo el tiempo. |

```sh
# compilar la base desde el commit de la versión liberada, en un workspace aparte
git archive <commit-liberado> <ruta-del-modulo>/ | tar x -C <workspace>/base/
```

**Evidencia.** Siempre en `_local/qa/`, nunca solo en la conversación ni en el árbol
versionado:

```
_local/qa/
  YYYYMMDD_HHMMSS_<asunto>/
    REPORTE.md          <- qué se validó, cómo, resultado (PASS/FAIL), hora real
    salidas/            <- output de la suite, logs, md5, diffs A/B
```

`REPORTE.md` abre con la cabecera mínima (`clasificacion` y `responsable`:
`documentacion-codigo.md`); su clase es `C2` como mínimo, y `C3` si alguna salida lo contiene. Registra cambio
validado, comandos, entorno, resultado por prueba y **hora real** obtenida con `date`, nunca
estimada. La evidencia es de **solo lectura**. De datos sensibles se guardan hashes, conteos y
diferencias, no los datos crudos; las salidas de más de 1 MB se comprimen dejando
`REPORTE.md` en claro, y su suma de comprobación se calcula antes de comprimir y se anota
en el reporte. Una entrega referencia
su evidencia en el registro de cambios o en la nota de entrega.
