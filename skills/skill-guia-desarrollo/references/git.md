# Git: commits, ramas e higiene

## Commits convencionales

```
<tipo>[(<alcance>)][!]: <descripción breve, en presente, en el idioma del proyecto>

[cuerpo opcional]

[pie: referencias a tickets, BREAKING CHANGE]
```

| Tipo | Cuándo |
|---|---|
| `feat` | Funcionalidad nueva para el usuario |
| `fix` | Corrección; una vulnerabilidad también, con alcance |
| `perf`, `refactor` | Rendimiento, reestructuración: sin cambiar comportamiento |
| `test`, `docs`, `ci` | Pruebas, documentación, pipelines |
| `build`, `chore` | Build y dependencias; mantenimiento ajeno a producción y pruebas |

Un tipo propio como `security` es **extensión del proyecto**: solo si su convención lo
declara. Una ruptura de compatibilidad se marca con `!`, con un pie `BREAKING CHANGE` o con ambos.
**La descripción nombra el proceso afectado y qué cambia para él, no el cómo.** Sin
atribución a IA (`documentacion-codigo.md`).

## Ramas

```
main          <- producción (protegida, solo por PR)
develop       <- integración (opcional en equipos pequeños)
feature/XXX   fix/XXX   hotfix/XXX   release/x.y.z
```

- `main` y `develop` no reciben push directo.
- Squash o rebase; la rama se borra tras fusionarla.
- Entrega a cliente → `release/*`.

## Antes del PR

```
[ ] Compila/interpreta sin errores ni warnings
[ ] La suite existente pasa — sin regresiones
[ ] Hay pruebas del comportamiento nuevo
[ ] Sin código comentado ni TODOs sin ticket
[ ] Formateado según el estilo del proyecto
[ ] PR enfocada y de tamaño razonable (< 400 líneas de referencia)
[ ] La descripción explica QUÉ cambia y POR QUÉ
```

## Higiene

- `.gitignore`, `.gitattributes` (LF) y `.editorconfig` desde el primer commit.
- **Un comentario de `.gitignore` va en su propia línea:** al final de una línea pasa a
  ser parte del patrón.
- **Se ignoran siempre** `.env`, `*.key`, `*.pem`, `secrets/`, salidas de compilación,
  logs y temporales (secretos: `seguridad.md`).
- **Se versiona código y contrato, no datos ni evidencia.**
- **`_local/` se ignora por su contenido, nunca con el directorio a secas:** git no
  re-incluye nada dentro de un directorio excluido.

  ```
  _local/**
  !_local/**/
  !_local/**/.gitkeep
  !_local/README.md
  ```

  Efecto: `git check-ignore -v _local/<fichero>` nombra el patrón y, tras `git add -A`,
  `git ls-files _local/` lista solo el esqueleto.

**Esta lista no comprueba que no haya `C2` ni `C3`.** Con el marco alambique lo comprueba
en parte su puerta de commit, por ruta y por patrón, solo en los proyectos dados de alta y
en los commits hechos en el puesto; falla
en cerrado (R-02, R-03): si salta, se lee el motivo en vez de
buscar cómo pasar. Sin él, se lee lo preparado (`git diff --cached`) antes de cada commit.
La puerta solo ve lo que pasa por `pre-commit`: un merge sin conflictos o un
fast-forward, `rebase`, `cherry-pick`, `revert` y `git am` incorporan commits sin
ejecutarla. Después de cualquiera de ellos se barre el árbol entero, no lo preparado.
Un control local protege del descuido, no del empeño: saltárselo es posible y
ningún mecanismo lo registra, así que quien lo salta lo deja dicho en el commit.

## Un barrido empareja tokens; clasificar es leer el contexto

Un barrido dice **dónde mirar**, no la clase de lo que encuentra, y falla en silencio de
dos maneras: **el dato no contiene el token buscado** —la nomenclatura de un producto
identifica al titular sin nombrarlo— o **el nombre del cliente es una palabra común** y
diluye la señal. Antes de fiarse:

1. **Comprobar que el patrón detecta,** con control positivo: una copia que sí tiene el
   dato (`qa.md`).
2. **Si el nombre es común, buscar lo raro que lo acompaña:** dominio, prefijos, rutas,
   códigos.
3. **Leer las coincidencias, no contarlas:** clasifica la frase, no la palabra.
4. **Buscar también lo demasiado específico para ser inventado:** eso lo encuentra leer,
   no un patrón.

El barrido protege del descuido; del dato que no se parece a lo que se buscaba protege
leerlo.
