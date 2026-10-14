#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# instalar.sh — Pone las skills de este repositorio en cada harness del puesto.
#
# Uso:
#   ./instalar.sh                 todas las skills, en cada harness detectado
#   ./instalar.sh <skill> ...     solo las que se nombren
#   ./instalar.sh --dias=N ...    el alta del guardado de compactación vale N
#                                 días (1-366; por defecto, 90)
#   ./instalar.sh --quitar        retira el registro del guardado de compactación
#   ./instalar.sh --help          esta ayuda; no instala nada
#
# NO DEPENDE DE NINGÚN OTRO REPOSITORIO. Detecta el harness por su directorio de
# configuración (tabla de abajo) o usa SOLO el que diga $ALAMBIQUE_CONF, que
# tiene que ser una ruta absoluta y cuenta como Claude Code si acaba en `.claude`.
#
# QUÉ ESCRIBE, y nada más:
#   - cada skill, copiada a <conf>/skills/<skill>/ con un marcador de origen
#     (`.alambique-skills-origen`). Una del mismo nombre SIN marcador no la puso
#     este instalador: se respeta y se avisa. Una con ese marcador, o con el del
#     marco alambique (`.alambique-origen`), se sustituye ENTERA: lo que se
#     haya dejado dentro se va con ella, sin aviso.
#   - solo en Claude Code: el alta de `extract_compact_summary.py` como hook de
#     sesión al compactar, en la configuración del harness, con copia
#     `.previo.<sello>` antes de cada cambio, si el fichero ya existía. En los
#     demás harness ese guardado no aplica, y se dice. Tampoco se da de alta si
#     la skill instalada no la puso este instalador, ni si esta pasada no
#     instala `skill-asistente-colaborativo`: instalar otra skill no reactiva un
#     registro que se retiró con `--quitar`. El alta caduca: el comando del
#     hook lleva `--caduca AAAA-MM-DD` y, pasada esa fecha, el script no guarda
#     y dice cómo renovarla.
#
# Repetirlo deja el mismo contenido y un solo registro, con la caducidad
# renovada desde hoy; cada skill se vuelve a copiar y la fecha de su marcador
# se renueva. `--quitar` retira solo ese registro. Las skills se retiran a
# mano, moviendo fuera de <conf>/skills/ los directorios que contienen el
# marcador: nada de lo que se retira se borra.
#
# Salidas: 0 sin fallos (puede haber skills respetadas) · 1 alguna pieza falló.
#
# Author       : Saul López
# Created Date : 2026-10-11
# Modified By  : Saul López
# Modified Date: 2026-10-14

set -uo pipefail
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PATH
unset -f grep sed awk find cat cp rm mkdir basename dirname date 2>/dev/null || true

AQUI="$(cd "$(dirname "$0")" && pwd)"
MARCADOR=".alambique-skills-origen"
# Marcador con que el marco alambique repartía estas mismas skills cuando las
# traía: una copia que lo lleve también es sustituible.
MARCADOR_MARCO=".alambique-origen"
es_nuestra() { [ -e "$1/$MARCADOR" ] || [ -e "$1/$MARCADOR_MARCO" ]; }
SELLO="$(date +%Y%m%d_%H%M%S)"
SKILL_COMPACTA="skill-asistente-colaborativo"
HOOK_REL="scripts/extract_compact_summary.py"

# Harness conocidos: nombre | directorio de configuración bajo $HOME | directorio
# de skills dentro de él | `si` cuando admite el hook de compactación. ES DATO:
# si un harness cambia de ruta, se corrige aquí. Fuera de Claude Code las rutas
# no están probadas contra una instalación real.
harness_tabla() {
    cat <<'T'
claude|.claude|skills|si
codex|.codex|skills|-
gemini|.gemini|skills|-
cursor|.cursor|skills|-
opencode|.config/opencode|skills|-
T
}

say() { printf '%s\n' "$*"; }
ok()  { printf '  ok   %s\n' "$*"; }
avi() { printf '  AVISO %s\n' "$*"; }

MODO="instalar"; PEDIDAS=""; DIAS=90
for a in "$@"; do
    case "$a" in
        -h|--help) grep '^#' "$0" | sed -n '3,41p' | cut -c3-; exit 0 ;;
        --quitar)  MODO="quitar" ;;
        --dias=*)  DIAS="${a#--dias=}"
                   case "$DIAS" in ''|*[!0-9]*) DIAS=0 ;; esac
                   if [ "$DIAS" -lt 1 ] || [ "$DIAS" -gt 366 ]; then
                       echo "--dias tiene que ser un entero de 1 a 366: $a" >&2; exit 1
                   fi ;;
        -*) echo "opción desconocida: $a  (ver --help)" >&2; exit 1 ;;
        *)  if [ ! -r "$AQUI/skills/$a/SKILL.md" ]; then
                echo "no existe la skill: $a" >&2; exit 1
            fi
            PEDIDAS="$PEDIDAS $a" ;;
    esac
done
if [ "$MODO" = "quitar" ] && [ -n "$PEDIDAS" ]; then
    echo "--quitar no admite nombres de skill" >&2; exit 1
fi
if [ -z "$PEDIDAS" ]; then
    for s in "$AQUI"/skills/*/; do
        [ -r "$s/SKILL.md" ] && PEDIDAS="$PEDIDAS $(basename "$s")"
    done
fi

# Destinos: una línea `nombre|conf|dir de skills|hook` por harness presente.
destinos() {
    if [ -n "${ALAMBIQUE_CONF:-}" ]; then
        _c="$ALAMBIQUE_CONF"
        while [ "${_c%/}" != "$_c" ] && [ -n "${_c%/}" ]; do _c="${_c%/}"; done
        case "$_c" in
            */.claude) printf 'claude|%s|skills|si\n' "$_c" ;;
            *)         printf 'declarado|%s|skills|-\n' "$_c" ;;
        esac
        return 0
    fi
    harness_tabla | while IFS='|' read -r nombre dir skills hook; do
        [ -d "$HOME/$dir" ] && printf '%s|%s|%s|%s\n' "$nombre" "$HOME/$dir" "$skills" "$hook"
    done
}

# El registro del hook vive en la configuración de Claude Code. Se fusiona, no
# se pisa: si el fichero no es JSON válido no se toca, y se escribe a través de
# un enlace simbólico conservando el modo.
#   registro_hook <conf> poner|quitar <ruta del script>
# Un hook es nuestro si su comando empieza por la ruta del script, con o sin
# caducidad: así poner renueva la fecha en su sitio y quitar lo encuentra.
# Devuelve 0 hecho o ya estaba · 1 error · 2 falta python3 · 3 configuración ilegible.
registro_hook() {
    command -v python3 >/dev/null 2>&1 || return 2
    python3 - "$1" "$2" "$3" "$SELLO" "$DIAS" <<'PY'
import datetime, json, os, shlex, shutil, stat, sys
conf, modo, ruta, sello, dias = sys.argv[1:6]
caduca = (datetime.date.today() + datetime.timedelta(days=int(dias))).isoformat()
comando = "%s --caduca %s" % (shlex.quote(ruta), caduca)
fichero = os.path.join(conf, "settings.json")
real = os.path.realpath(fichero)
previo = None
if os.path.exists(real):
    with open(real, encoding="utf-8") as f:
        previo = f.read()
if previo is None or not previo.strip():
    cfg = {}
else:
    try:
        cfg = json.loads(previo)
    except ValueError:
        print("  AVISO %s no es JSON válido: no se toca" % fichero)
        sys.exit(3)
    if not isinstance(cfg, dict):
        print("  AVISO %s no es un objeto JSON: no se toca" % fichero)
        sys.exit(3)
antes = json.dumps(cfg, sort_keys=True)
def nuestro(h):
    if not isinstance(h, dict) or not isinstance(h.get("command"), str):
        return False
    try:
        partes = shlex.split(h["command"])
    except ValueError:
        return False
    return bool(partes) and partes[0] == ruta
hooks = cfg.get("hooks")
grupos = hooks.get("SessionStart") if isinstance(hooks, dict) else None
esta = False
if isinstance(grupos, list):
    for g in grupos:
        for h in (g.get("hooks") or []) if isinstance(g, dict) else []:
            if nuestro(h):
                esta = True
                if modo == "poner":
                    h["command"] = comando      # renueva la caducidad
if modo == "poner":
    if not esta:
        if not isinstance(hooks, dict):
            hooks = cfg["hooks"] = {}
        if not isinstance(hooks.get("SessionStart"), list):
            hooks["SessionStart"] = []
        hooks["SessionStart"].append(
            {"matcher": "compact",
             "hooks": [{"type": "command", "command": comando}]})
    print("  alta hasta el %s (inclusive)" % caduca)
else:
    if isinstance(grupos, list):
        nuevos = []
        for g in grupos:
            if isinstance(g, dict) and isinstance(g.get("hooks"), list):
                resto = [h for h in g["hooks"] if not nuestro(h)]
                if len(resto) != len(g["hooks"]):
                    if not resto:
                        continue        # el grupo era solo este hook
                    g = dict(g, hooks=resto)
            nuevos.append(g)
        if nuevos:
            hooks["SessionStart"] = nuevos
        else:
            del hooks["SessionStart"]
            if not hooks:
                del cfg["hooks"]
if json.dumps(cfg, sort_keys=True) == antes:
    sys.exit(0)
modo_fichero = None
if previo is not None:
    copia = "%s.previo.%s" % (real, sello)
    n = 1
    while os.path.exists(copia):      # dos pasadas en el mismo segundo no se pisan
        n += 1
        copia = "%s.previo.%s.%d" % (real, sello, n)
    shutil.copy2(real, copia)
    modo_fichero = stat.S_IMODE(os.stat(real).st_mode)
    print("  copia previa: %s" % os.path.basename(copia))
os.makedirs(os.path.dirname(real), exist_ok=True)
tmp = real + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
    f.write("\n")
if modo_fichero is not None:
    os.chmod(tmp, modo_fichero)
os.replace(tmp, real)
PY
}

case "${ALAMBIQUE_CONF:-/}" in
    /*) ;;
    *)  echo "ALAMBIQUE_CONF tiene que ser una ruta absoluta: $ALAMBIQUE_CONF" >&2; exit 1 ;;
esac
FALLOS=0
DESTINOS="$(destinos)"
say ""
if [ -z "$DESTINOS" ]; then
    avi "no detecto ningún harness en $HOME, y \$ALAMBIQUE_CONF no está definida. Nada que hacer."
    avi "  Declara el destino:  ALAMBIQUE_CONF=<directorio de configuración> ./instalar.sh"
    avi "  O a mano: cp -r skills/* <conf>/skills/"
    exit 1
fi

if [ "$MODO" = "quitar" ]; then
    say "alambique-skills — retirada del guardado de compactación"
    while IFS='|' read -r nombre conf skills hook; do
        [ "$hook" = "si" ] || continue
        registro_hook "$conf" quitar "$conf/$skills/$SKILL_COMPACTA/$HOOK_REL"; r=$?
        case $r in
            0) ok "$nombre: registro retirado, o no estaba" ;;
            2) avi "$nombre: falta python3; el registro no se ha tocado"; FALLOS=$((FALLOS+1)) ;;
            *) avi "$nombre: no pude retirar el registro"; FALLOS=$((FALLOS+1)) ;;
        esac
    done <<EOF
$DESTINOS
EOF
    say ""
    say "Las skills se retiran a mano: se mueven fuera de <conf>/skills/ los directorios con $MARCADOR"
    [ "$FALLOS" -gt 0 ] && exit 1
    exit 0
fi

say "alambique-skills — instalación"
say "=============================="
PUESTAS=0; RESPETADAS=0; ST_HOOK="no aplica"
while IFS='|' read -r nombre conf skills hook; do
    destino="$conf/$skills"
    say ""
    say "$nombre → $destino"
    if ! mkdir -p "$destino" 2>/dev/null; then
        avi "no puedo crear $destino"; FALLOS=$((FALLOS+1)); continue
    fi
    for n in $PEDIDAS; do
        if [ -e "$destino/$n" ] && ! es_nuestra "$destino/$n"; then
            avi "$n ya existe y no la puso este instalador: se respeta"
            RESPETADAS=$((RESPETADAS+1)); continue
        fi
        # Sustituir solo lo que es nuestro: el marcador lo garantiza.
        es_nuestra "$destino/$n" && rm -rf "${destino:?}/${n:?}"
        if cp -R "$AQUI/skills/$n" "$destino/$n" 2>/dev/null; then
            find "$destino/$n" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
            printf 'origen: %s\nfecha: %s\n' "$AQUI" "$(date '+%Y-%m-%d %H:%M:%S')" > "$destino/$n/$MARCADOR"
            ok "$n"; PUESTAS=$((PUESTAS+1))
        else
            avi "no pude copiar $n a $destino"; FALLOS=$((FALLOS+1))
        fi
    done
    # El guardado de compactación, donde el harness lo admite y la skill está,
    # y solo si esta pasada la instala: si no, el registro no se toca.
    script="$destino/$SKILL_COMPACTA/$HOOK_REL"
    case " $PEDIDAS " in
        *" $SKILL_COMPACTA "*) pide_compacta=si ;;
        *)                     pide_compacta=no ;;
    esac
    if [ "$hook" = "si" ] && [ "$pide_compacta" = "no" ]; then
        ST_HOOK="sin tocar: esta pasada no instala $SKILL_COMPACTA"
    elif [ "$hook" = "si" ] && [ -r "$script" ] && [ -e "$destino/$SKILL_COMPACTA/$MARCADOR" ]; then
        chmod +x "$script" 2>/dev/null
        registro_hook "$conf" poner "$script"; r=$?
        case $r in
            0) ST_HOOK="activo"; ok "guardado de compactación dado de alta ($nombre)" ;;
            2) ST_HOOK="NO ACTIVO"; avi "falta python3: el guardado de compactación no se ha dado de alta"; FALLOS=$((FALLOS+1)) ;;
            3) ST_HOOK="NO ACTIVO"; FALLOS=$((FALLOS+1)) ;;
            *) ST_HOOK="NO ACTIVO"; avi "no pude dar de alta el guardado de compactación"; FALLOS=$((FALLOS+1)) ;;
        esac
    elif [ "$hook" = "si" ] && [ -e "$destino/$SKILL_COMPACTA" ]; then
        ST_HOOK="sin dar de alta"
        avi "$nombre: $SKILL_COMPACTA no la puso este instalador; el guardado de compactación no se da de alta"
    elif [ "$hook" != "si" ] && [ -r "$script" ]; then
        avi "$nombre: el guardado de compactación solo vale en Claude Code; aquí no se da de alta"
    fi
done <<EOF
$DESTINOS
EOF

say ""
say "skills: $PUESTAS puestas · $RESPETADAS respetadas · $FALLOS fallos"
say "guardado de compactación: $ST_HOOK"
say "Para retirarlas: mover fuera de <conf>/skills/ los directorios que contengan $MARCADOR"
[ "$FALLOS" -gt 0 ] && exit 1
exit 0
