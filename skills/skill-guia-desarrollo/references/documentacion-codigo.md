# Dentro de los ficheros — comentarios, autoría y cabecera

El `docs/` del proyecto: `documentar.md`.

## Comentarios

**Explican el porqué, nunca el qué:** lo que el código no puede contar.

| Se documenta siempre | Motivo |
|---|---|
| API pública | Contrato con otro módulo |
| Algoritmo no trivial | Abarata mantenerlo |
| Decisión contraintuitiva | Nadie «corrige» lo intencional |
| Apaño | Su motivo, con referencia |
| Precondiciones y postcondiciones | Contrato de uso |
| Efectos secundarios no obvios | Escrituras, eventos, caché invalidada |

**Ruido que se elimina:** lo autoexplicativo, el comentario vacío, el historial de
cambios en comentarios y el código comentado.

## Autoría

De cada artefacto responde una persona identificada (R-11 del marco alambique), nunca una
herramienta: **sin atribución a IA** en cabeceras, commits, documentos ni comentarios.

| Regla | Cómo se aplica |
|---|---|
| **Todo documento y todo código que ya trae cabecera llevan firma.** | En un documento, su campo `responsable`; donde el puesto lo use, vale también la firma al pie con el correo de quien firma. Al código sin cabecera no se le inventa una. |
| **Quién firma sale de un fichero de datos del puesto, fuera del repositorio.** | Con el marco alambique, `<conf>/_local/negocio.conf` (`<conf>`: configuración del harness); un proyecto o un cliente que firma con otra identidad lleva su propio `_local/negocio.conf`, y gana el más cercano al fichero escrito. Si no hay ninguno, se pregunta: no se inventa ni se deduce. La identidad no se escribe en una skill ni en una guía reutilizable. |
| **El nombre se escribe como lo escribe su titular.** | Conserva sus tildes aunque el fichero escriba sin ellas. |
| **Al modificar un fichero cuya cabecera ya lleva `Author:` y `Modified Date:`, se sella** con un par nuevo tras el último. | Con el estilo y el formato de fecha del fichero; el par vacío se rellena. |

```
Modified By   : <autor_nombre>
Modified Date : <fecha de hoy, formato del propio fichero>
```

Con el marco alambique, un mecanismo vigila la firma, el sello y que ninguna IA figure
como autor, solo en los harness para los que trae adaptador: si avisa, se lee el motivo y
no se sella por inercia. Sin él, depende de quien escribe. El mecanismo tampoco ve el
mensaje de commit —un `Co-Authored-By` entra sin aviso—, lo escrito por redirección de
shell ni las extensiones que no mira: eso se revisa al preparar el commit.

## Cabecera mínima

Todo documento declara `clasificacion` y `responsable` (R-01 y R-11). La llevan tal cual
los que no son nodos —los ficheros de un plan (`fases.md`), el reporte de una
evidencia (`validacion.md`)—; un nodo añade los campos de `documentar.md`.

```
---
clasificacion: <C0-C3>
responsable: <persona real>
---
```

La documentación vive en el repositorio del código: un cambio de API no se integra sin
la suya.
