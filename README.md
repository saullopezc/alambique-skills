# alambique-skills

Tres skills en formato abierto [Agent Skills](https://agentskills.io): una forma de
trabajar con un agente, una base de conocimiento por síntoma y un baseline de ingeniería.
Acompañan al marco [alambique](https://github.com/saullopezc/alambique), pero no lo
necesitan.

| Skill | Qué aporta |
|---|---|
| `skill-asistente-colaborativo` | Modo compañero de trabajo y forma de respuesta accionable. Trae el guardado del resumen de compactación, que solo vale en Claude Code |
| `base-conocimiento-operacion` | Documentar por síntoma literal y consultarlo antes de investigar |
| `skill-guia-desarrollo` | Baseline de ingeniería, con guías de C, Java, Perl y Python como referencias bajo demanda: principios, sin código ni recetas de framework |

## Instalación

```sh
./instalar.sh                 # las tres skills, en cada harness detectado
./instalar.sh <skill> ...     # solo las que se nombren
./instalar.sh --dias=N ...    # el alta del guardado de compactación vale N días (por defecto, 90)
./instalar.sh --quitar        # retira el registro del guardado de compactación
```

No depende de ningún otro repositorio. Detecta el harness por su directorio de
configuración (`~/.claude`, `~/.codex`, `~/.gemini`, `~/.cursor`, `~/.config/opencode`) o
usa solo el que diga `$ALAMBIQUE_CONF`, que tiene que ser una ruta absoluta y cuenta como Claude Code si acaba en
`.claude`. Fuera de Claude Code las rutas no están probadas contra
una instalación real.

**Qué escribe, y nada más:** cada skill, copiada a `<conf>/skills/` con un marcador de
origen; una del mismo nombre que no lleve marcador se respeta. La que lleve el de este
repositorio o el del marco alambique se sustituye entera, con lo que haya dentro. Y solo en Claude Code,
el alta del guardado de compactación en la configuración del harness, con copia
`.previo.<sello>` antes de cada cambio, si el fichero ya existía.

Una vez dado de alta, tras cada compactación guarda el resumen en `_local/context/`, y
solo donde git lo ignora: desde el directorio de trabajo de la sesión sube hasta la raíz
del repositorio y usa el primer nivel cuyo `_local/` esté ignorado. Si ninguno lo está, no
guarda nada y lo dice. Ignorarlo lo pone el marco, o una línea propia en `.gitignore`;
este instalador no.

Corre sin nadie al teclado, así que su alta está acotada: caduca a los 90 días
(`--dias=N` para otro plazo). Pasada la fecha no guarda y dice cómo renovarla;
reinstalar la renueva y `--quitar` la retira antes. Cada ejecución, guarde o no, deja
una línea en `<conf>/projects/.registro_compactacion.log`, junto a los transcripts.
Al juntarse diez resúmenes avisa de que toca destilarlos a la memoria
persistente, y el ciclo se cierra con
`extract_compact_summary.py --marcar-destilado <memoria> [project_dir]`.

Para probarlo sin tocar tu máquina:

```sh
T=$(mktemp -d); mkdir -p "$T/.claude"
env -i PATH="$PATH" HOME="$T" ./instalar.sh    # todo queda bajo $T
```

## Cada skill es autosuficiente

Instalada sola, se entiende y funciona: ninguna necesita a otra ni al marco. Donde una
skill cita una regla `R-xx`, es trazabilidad hacia el marco alambique para quien lo use; la
frase dice la regla con sus palabras.

`skill-asistente-colaborativo` trae un fichero `.arranque`: donde el puesto tenga un
arranque de sesión que lo atienda —el del marco lo hace—, se pide cargarla al abrir cada
sesión. Sin él, el harness la carga por su `description`.

## Licencia y procedencia

MIT (ver [LICENSE](LICENSE)). La sección «Forma de la respuesta» de
`skill-asistente-colaborativo` adapta una obra de terceros: qué se tomó y qué se cambió
está en [`licencias/PROCEDENCIA.md`](licencias/PROCEDENCIA.md), y el texto de su licencia
viaja dentro de la skill.

---

Saul López — github.com/saullopezc
