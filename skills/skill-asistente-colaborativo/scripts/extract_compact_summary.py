#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
extract_compact_summary.py
--------------------------
Guarda el resumen de la última compactación de una sesión de Claude Code en
{project_dir}/_local/context/, con sello de tiempo, como punto de retorno.
Al acumularse cierto número de resúmenes avisa de que toca destilarlos a una
memoria persistente; el destilado lo escribe el asistente, no este script.

HERRAMIENTA DE UN SOLO HARNESS: Claude Code. Lee el formato JSONL de sus
transcripts (<conf>/projects/<slug>/*.jsonl); en otro harness no aplica. La
regla que sirve —guardar el punto de retorno al compactar y anotar el estado
antes de seguir— vale para cualquiera; lo que está atado es el formato que se
lee.

Uso:
  extract_compact_summary.py [project_dir]                   (manual)
  echo "$HOOK_JSON" | extract_compact_summary.py             (hook SessionStart:compact)
  extract_compact_summary.py --marcar-destilado <memoria> [project_dir]
  extract_compact_summary.py --help

  Sin project_dir, el directorio de trabajo actual.

  El destino es <capa>/_local/context/ (se crea si falta). El resumen lleva
  comandos y salidas reales y este script no lo sanea, así que solo se escribe
  donde git lo ignora. Dentro de un repositorio, <capa> es el primer nivel,
  desde project_dir subiendo hasta la raíz del repositorio, cuyo
  `_local/context/` ignora git; si ninguno lo ignora, o no se puede preguntar
  a git, no se guarda nada y se dice. Fuera de un repositorio, <capa> es
  project_dir. Un resumen idéntico a uno ya guardado no se duplica.

  Cada ejecución que guarda el resumen, o lo encuentra ya guardado, deja una
  línea en <capa>/_local/context/.registro_compactacion.log. La que no llega
  a guardar no tiene dónde escribir sin riesgo: deja solo su aviso.

  --marcar-destilado cierra el ciclo de destilado: da por consolidados en
  <memoria> (un nombre, no una ruta) los resúmenes pendientes y lo anota en
  _local/context/.destilado_estado.json.

  Entorno:
    ALAMBIQUE_CONF              directorio de configuración del harness
                                (por defecto, ~/.claude)
    ALAMBIQUE_DESTILADO_UMBRAL  resúmenes pendientes que disparan el aviso
                                (entero >= 1; por defecto, 10)

  Códigos de salida en uso manual: 0 guardado o ya guardado, 1 no se guardó
  nada, 2 argumentos incorrectos. En modo hook, siempre 0.

Como hook va en SessionStart con matcher "compact" — después de compactar, que
es cuando el resumen existe en el transcript; en PreCompact aún no se ha
escrito. Corre sin turno, y su alcance es ese: leer el transcript de la sesión
y escribir en la capa local ignorada; nada más. El alta no caduca sola: dura
hasta `instalar.sh --quitar`.

En modo hook lee por stdin el JSON del evento y usa su transcript_path y su
cwd. No busca otro transcript si ese falta: el más reciente por fecha puede
ser el de otra sesión abierta a la vez. Su stdout entra al contexto del
modelo, así que por ahí sale solo lo que el modelo debe saber —dónde quedó el
resumen, o que no se guardó—; los diagnósticos van a stderr. Termina siempre
con código 0: un fallo aquí no puede romper el arranque de la sesión.

Requisitos: Python 3.8+, sin dependencias externas.

Author       : Saul López
Created Date : 2026-08-24
Modified By  : Saul López
Modified Date: 2026-10-14
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class Fin(Exception):
    """Final previsto sin nada guardado: código de salida manual y motivo."""

    def __init__(self, codigo: int, motivo: str):
        super().__init__(motivo)
        self.codigo = codigo
        self.motivo = motivo


def diag(texto: str) -> None:
    """Diagnóstico: a stderr, para que en un hook no entre al contexto del modelo."""
    print(texto, file=sys.stderr)


# ---------------------------------------------------------------------------
# Configuración del harness
# ---------------------------------------------------------------------------

def conf_harness() -> Path:
    """
    Directorio de configuración del harness. ALAMBIQUE_CONF manda; si no,
    ~/.claude: este script solo entiende el formato de Claude Code.
    """
    conf = os.environ.get("ALAMBIQUE_CONF")
    if conf:
        return Path(conf)
    return Path.home() / ".claude"


def cwd_to_claude_slug(cwd: str) -> str:
    """
    Convierte una ruta absoluta de proyecto al slug que Claude Code usa en
    <conf>/projects/.

    Ejemplos:
      C:\\Users\\<usuario>\\Proyectos\\mi_app  ->  c--Users-<usuario>-Proyectos-mi-app
      /home/<usuario>/proyectos/mi-app         ->  -home-<usuario>-proyectos-mi-app

    Cubre cuatro caracteres: "_", "/", "\\" y los ":" de la unidad de Windows.
    El resto (punto, espacio, letras con tilde, ñ...) pasa tal cual, y la regla
    del harness para ellos no está comprobada: con una ruta que los contenga
    el slug puede no coincidir con el directorio real. En ese caso el uso
    manual no encuentra la sesión y lo dice; el modo hook no depende del slug
    para leer el transcript, solo para nombrar el directorio de memoria.
    """
    path = cwd.replace("\\", "/").replace("_", "-")

    # Windows: C:/... -> c--...
    if len(path) >= 2 and path[1] == ":":
        drive = path[0].lower()
        rest = path[2:].lstrip("/")
        path = drive + "--" + rest

    # Unix: la barra inicial no se descarta; se traduce a "-".
    return path.replace("/", "-")


def find_claude_projects_dir() -> Path:
    """Retorna <conf>/projects/"""
    return conf_harness() / "projects"


def find_most_recent_jsonl(project_slug: str) -> "Path | None":
    """
    El .jsonl más reciente (por fecha de modificación) de
    <conf>/projects/{slug}/, sin contar sesiones casi vacías (< 10 KB).
    Solo para uso manual: con varias sesiones abiertas puede no ser la propia.
    """
    project_dir = find_claude_projects_dir() / project_slug

    if not project_dir.is_dir():
        diag(f"WARN: directorio de transcripts no encontrado: {project_dir}")
        return None

    jsonl_files = [f for f in project_dir.glob("*.jsonl") if f.stat().st_size > 10_000]
    if not jsonl_files:
        return None
    return max(jsonl_files, key=lambda f: f.stat().st_mtime)


# ---------------------------------------------------------------------------
# Extracción del resumen compactado
# ---------------------------------------------------------------------------

# El harness envuelve el resumen entre estas dos frases fijas, en inglés sea
# cual sea el idioma del resumen. La segunda abre la coda que apunta al
# transcript; se recorta para no copiar esa ruta.
MARCA_INICIO = "This session is being continued"
MARCA_FIN = "If you need specific details"


def texto_de(content) -> str:
    """El texto de un `content`, llegue como cadena o como lista de bloques."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            b["text"] for b in content
            if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str)
        )
    return ""


def extract_summary(jsonl_path: Path) -> tuple:
    """
    Recorre el transcript y devuelve (resumen, sello, hubo_frontera):
      - resumen       : texto del último resumen de compactación, o None
      - sello         : timestamp ISO del último evento compact_boundary, o None
      - hubo_frontera : si el transcript registra alguna compactación

    Un mensaje de usuario es el resumen si el harness lo marca con
    isCompactSummary o si su texto trae MARCA_INICIO. Gana el marcado: la
    frase sola también aparece cuando alguien la cita en un mensaje.

    Las líneas que no son un objeto JSON, o que traen campos con otra forma,
    se saltan: un transcript a medio escribir no es motivo para no guardar.
    """
    marcado = por_frase = sello = None
    hubo_frontera = False

    with open(jsonl_path, "r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                obj = json.loads(raw_line)
            except ValueError:
                continue
            if not isinstance(obj, dict):
                continue

            tipo = obj.get("type")
            if tipo == "system" and obj.get("subtype") == "compact_boundary":
                hubo_frontera = True
                sello = obj.get("timestamp")
                continue
            if tipo != "user":
                continue

            mensaje = obj.get("message")
            texto = texto_de(mensaje.get("content")) if isinstance(mensaje, dict) else ""
            inicio = texto.find(MARCA_INICIO)
            es_marcado = obj.get("isCompactSummary") is True
            if inicio == -1 and not es_marcado:
                continue
            if inicio != -1:
                fin = texto.find(MARCA_FIN, inicio)
                texto = texto[inicio: fin if fin != -1 else len(texto)]
            # Un par suelto de un emoji partido no se puede escribir en UTF-8.
            texto = texto.strip().encode("utf-8", "replace").decode("utf-8")
            if not texto:
                continue
            if es_marcado:
                marcado = texto
            else:
                por_frase = texto

    return (marcado or por_frase), sello, hubo_frontera


# ---------------------------------------------------------------------------
# Guardado del resumen
# ---------------------------------------------------------------------------

PATRON_RESUMEN = "*_compact_summary*.md"


def directorio_contexto(project_dir: Path) -> Path:
    """
    Destino de los resúmenes: {project_dir}/_local/context/, la capa local.
    Lo que se guarda es el resumen crudo, con comandos, salidas y rutas reales:
    project_dir tiene que venir de capa_local(), que comprueba que git lo ignora.
    """
    return project_dir / "_local" / "context"


# Lo que se pregunta a git: un fichero con el nombre de los que se guardan.
PRUEBA_IGNORADO = "_local/context/00000000_000000_compact_summary.md"


def _git(nivel: Path, *orden: str) -> "subprocess.CompletedProcess | None":
    """Una orden git en `nivel`; None si git no está o no responde."""
    try:
        return subprocess.run(
            ["git", "-C", str(nivel), *orden],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def capa_local(project_dir: Path) -> Path:
    """
    El nivel cuya _local/ recibe lo que este script escribe.

    Fuera de un repositorio git, project_dir. Dentro, el primer nivel desde
    project_dir hasta la raíz del repositorio cuyo `_local/context/` ignora
    git: un `_local/**` en el .gitignore de la raíz solo casa en la raíz, y
    con el directorio de trabajo en un subdirectorio el resumen quedaría sin
    ignorar. Si ninguno lo ignora, o git no responde, no se escribe: Fin.
    """
    if not any((d / ".git").exists() for d in (project_dir, *project_dir.parents)):
        return project_dir
    r = _git(project_dir, "rev-parse", "--show-toplevel")
    if r is None or r.returncode != 0 or not r.stdout.strip():
        raise Fin(1, f"no puedo preguntar a git si _local/ está ignorado en {project_dir}")
    raiz = Path(r.stdout.strip()).resolve()
    nivel = project_dir
    while True:
        r = _git(nivel, "check-ignore", "-q", PRUEBA_IGNORADO)
        if r is not None and r.returncode == 0:
            return nivel
        if nivel == raiz or nivel.parent == nivel:
            break
        nivel = nivel.parent
    raise Fin(
        1,
        f"git no ignora _local/ ni en {project_dir} ni subiendo hasta {raiz}; "
        "añade `_local/**` a su .gitignore",
    )


def registrar(capa: Path, linea: str) -> None:
    """Una línea por ejecución en el registro de la capa; si falla, solo se dice."""
    try:
        with open(directorio_contexto(capa) / ".registro_compactacion.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {linea}\n")
    except OSError as e:
        diag(f"AVISO: no se pudo escribir el registro de ejecución: {e}")


def cuerpo_de(texto: str) -> str:
    """El resumen guardado, sin su línea de título."""
    if texto.startswith("# "):
        texto = texto.partition("\n")[2]
    return texto.strip()


def ya_guardado(context_dir: Path, summary: str) -> "Path | None":
    """El fichero que ya contiene este mismo resumen, si lo hay."""
    for f in sorted(context_dir.glob(PATRON_RESUMEN)):
        try:
            if cuerpo_de(f.read_text(encoding="utf-8", errors="replace")) == summary:
                return f
        except OSError:
            continue
    return None


def save_summary(project_dir: Path, summary: str, compact_timestamp) -> tuple:
    """
    Guarda el resumen como YYYYMMDD_HHMMSS_compact_summary.md, en hora local,
    y devuelve (ruta, es_nuevo).

    Un resumen de contenido idéntico a uno ya guardado no se escribe otra vez:
    cada fichero cuenta para el umbral de destilado, y un duplicado lo
    adelanta sin que haya nada nuevo que destilar. Dos resúmenes distintos con
    el mismo sello conviven con sufijo numérico.
    """
    context_dir = directorio_contexto(project_dir)
    context_dir.mkdir(parents=True, exist_ok=True)

    previo = ya_guardado(context_dir, summary)
    if previo is not None:
        return previo, False

    try:
        dt = datetime.fromisoformat(compact_timestamp.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.astimezone()      # el transcript sella en UTC
    except (ValueError, AttributeError, TypeError):
        dt = datetime.now()           # sin sello legible, la hora del guardado
    ts = dt.strftime("%Y%m%d_%H%M%S")

    output_path = context_dir / f"{ts}_compact_summary.md"
    counter = 1
    while output_path.exists():
        output_path = context_dir / f"{ts}_compact_summary_{counter}.md"
        counter += 1

    output_path.write_text(
        f"# Resumen de compactación — {ts}\n\n{summary}\n", encoding="utf-8"
    )
    return output_path, True


# ---------------------------------------------------------------------------
# Invocación como hook
# ---------------------------------------------------------------------------

def leer_evento_hook() -> tuple:
    """
    Devuelve (evento, es_hook).

    Uso manual es una terminal interactiva o un stdin vacío. Cualquier otra
    cosa por stdin es un hook, aunque el evento llegue ilegible: se devuelve
    vacío y marcado como hook, porque en la duda vale más no guardar nada que
    ir a buscar el transcript de otra sesión.
    """
    if sys.stdin is None or sys.stdin.isatty():
        return {}, False
    try:
        crudo = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    except (OSError, ValueError, AttributeError):
        return {}, False
    if not crudo.strip():
        return {}, False
    try:
        evento = json.loads(crudo)
    except ValueError:
        return {}, True
    return (evento if isinstance(evento, dict) else {}), True


# ---------------------------------------------------------------------------
# Destilado: de N resúmenes a UNA memoria persistente
# ---------------------------------------------------------------------------

# Cada compactación deja su .md (detalle). Al llegar al umbral, los pendientes
# se consolidan en una sola memoria. El número es alto a propósito: destilar
# cada sesión produce crónica, no lineamiento.
UMBRAL_POR_DEFECTO = 10
ESTADO_DESTILADO = ".destilado_estado.json"


def umbral_destilado() -> int:
    """ALAMBIQUE_DESTILADO_UMBRAL si es un entero >= 1; si no, el de por defecto."""
    crudo = os.environ.get("ALAMBIQUE_DESTILADO_UMBRAL")
    if crudo is None or not crudo.strip():
        return UMBRAL_POR_DEFECTO
    try:
        valor = int(crudo)
    except ValueError:
        valor = 0
    if valor < 1:
        diag(
            f"WARN: ALAMBIQUE_DESTILADO_UMBRAL={crudo!r} no es un entero >= 1; "
            f"se usa {UMBRAL_POR_DEFECTO}"
        )
        return UMBRAL_POR_DEFECTO
    return valor


def _ruta_estado(context_dir: Path) -> Path:
    return context_dir / ESTADO_DESTILADO


def leer_estado(context_dir: Path) -> dict:
    """El estado del destilado; uno vacío si falta o no tiene la forma esperada."""
    vacio = {"destilados": [], "memorias": []}
    try:
        estado = json.loads(_ruta_estado(context_dir).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return vacio
    if not isinstance(estado, dict):
        return vacio
    for clave in vacio:
        if not isinstance(estado.get(clave), list):
            estado[clave] = []
    return estado


def pendientes_de_destilar(context_dir: Path) -> list:
    """Resúmenes guardados que aún no se han consolidado en una memoria."""
    ya = {n for n in leer_estado(context_dir)["destilados"] if isinstance(n, str)}
    return sorted(
        f.name for f in context_dir.glob(PATRON_RESUMEN) if f.name not in ya
    )


def marcar_destilado(project_dir: Path, memoria: str) -> int:
    """
    Cierra el ciclo: da por destilados los resúmenes pendientes y anota qué
    memoria los resume; sin esto el aviso se repite en cada compactación.
    Si no hay pendientes no escribe nada.
    """
    context_dir = directorio_contexto(project_dir)
    pendientes = pendientes_de_destilar(context_dir)
    if not pendientes:
        return 0
    estado = leer_estado(context_dir)
    estado["destilados"] = sorted(
        {n for n in estado["destilados"] if isinstance(n, str)} | set(pendientes)
    )
    estado["memorias"].append({
        "memoria": memoria,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "compactaciones": len(pendientes),
    })
    _ruta_estado(context_dir).write_text(
        json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return len(pendientes)


def aviso_destilado(project_dir: Path, context_dir: Path) -> str:
    """
    Una línea de cuenta mientras no se llega al umbral; al llegar, el bloque
    completo. El criterio va escrito aquí porque es lo que separa una memoria
    útil de un anecdotario.
    """
    umbral = umbral_destilado()
    pendientes = pendientes_de_destilar(context_dir)
    if len(pendientes) < umbral:
        return f"(destilado: {len(pendientes)}/{umbral} compactaciones pendientes)"

    # La ruta solo se da si existe: el slug puede no coincidir con el real.
    memoria = find_claude_projects_dir() / cwd_to_claude_slug(str(project_dir)) / "memory"
    destino = (
        f"{memoria}/ (más su línea en el índice MEMORY.md)"
        if memoria.parent.is_dir()
        else "la memoria persistente del proyecto"
    )
    return "\n".join([
        "",
        f"TOCA DESTILAR — hay {len(pendientes)} compactaciones sin consolidar.",
        f"Conviértelas en UNA sola memoria. Va en: {destino}",
        "",
        "Criterio, y es lo que decide si la memoria sirve:",
        "  SÍ  — lo que cambia cómo se trabaja en este proyecto: lineamientos,",
        "        decisiones vigentes, trampas del entorno, qué instrumento hay",
        "        que mirar antes de concluir, qué no se toca.",
        "  NO  — la crónica: quién hizo qué, en qué sesión, en qué orden, con",
        "        cuántos intentos. Eso ya está en los resúmenes.",
        "  Prueba: si la frase solo sirve para contar la historia y no cambia",
        "  cómo se trabaja la próxima vez, no es memoria.",
        "",
        f"Fuentes a leer antes de escribirla, en {context_dir}:",
    ] + [f"  - {n}" for n in pendientes] + [
        "",
        "Al terminar, cierra el ciclo o el aviso se repetirá:",
        f"  python3 {Path(__file__).resolve()} --marcar-destilado <nombre-memoria> {project_dir}",
    ])


# ---------------------------------------------------------------------------
# Lo que el hook devuelve al contexto del modelo
# ---------------------------------------------------------------------------

MAX_ITEMS_LISTADOS = 15
ORDEN_ATENCION = ("urgencias", "seguimiento", "pendientes", "planificacion", "sugerencias")


def items_abiertos(operacion: Path) -> list:
    """
    Los .md de un directorio de estado: los de su raíz y los de sus
    subdirectorios directos. No cuentan `historico/`, que guarda lo cerrado, ni
    los directorios `YYYYMMDD_HHMMSS_<tema>/`, que guardan lo retirado de una
    tarea y no son items.

    En el orden de atención —urgencias, seguimiento, pendientes, planificación,
    sugerencias—, después los de la raíz y al final otros subdirectorios: la
    lista se corta en MAX_ITEMS_LISTADOS, y lo que se corta es lo que menos urge.
    """
    subs = sorted(d for d in operacion.iterdir() if d.is_dir() and d.name != "historico"
                  and not re.match(r"\d{8}_\d{6}_", d.name))
    conocidos = [d for n in ORDEN_ATENCION for d in subs if d.name == n]
    otros = [d for d in subs if d.name not in ORDEN_ATENCION]

    def de(sub: Path) -> list:
        return sorted(f"{sub.name}/{f.name}" for f in sub.glob("*.md"))

    items = [i for sub in conocidos for i in de(sub)]
    items += sorted(f.name for f in operacion.glob("*.md"))
    items += [i for sub in otros for i in de(sub)]
    return items


def recordatorio_operacion(project_dir: Path, output_path: Path) -> str:
    """
    El resumen automático no distingue lo que se vigila de lo que solo se
    hizo, y separarlo exige criterio: lo escribe el asistente o se pierde.
    Aquí se le recuerda y, si el proyecto guarda su estado en
    _local/operacion/, se le ponen delante los items abiertos. El aviso de
    destilado va siempre: no depende de dónde guarde el proyecto su estado.
    """
    operacion = project_dir / "_local" / "operacion"
    con_estado = operacion.is_dir()
    donde = f"actualiza el estado en {operacion}/:" if con_estado else "anota donde el proyecto lleve su estado"
    lineas = [
        "Sesión compactada. El resumen completo quedó en:",
        f"  {output_path}",
        "",
        f"ANTES de seguir con la tarea, {donde}",
        "qué quedó corriendo y CÓMO re-chequearlo, qué quedó a medias y qué se",
        "esperaba. El resumen no lo hace: no distingue lo que se vigila de lo",
        "que solo se hizo.",
    ]
    if con_estado:
        items = items_abiertos(operacion)
        visibles = ", ".join(items[:MAX_ITEMS_LISTADOS]) if items else "(ninguno)"
        if len(items) > MAX_ITEMS_LISTADOS:
            visibles += f" y {len(items) - MAX_ITEMS_LISTADOS} más"
        lineas.append(f"Items abiertos ahora mismo: {visibles}")
    lineas.append("Si algo quedó sin cubrir, el transcript de la sesión sigue entero en su .jsonl.")
    lineas.append(aviso_destilado(project_dir, directorio_contexto(project_dir)))
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Entrada principal
# ---------------------------------------------------------------------------

def ayuda() -> str:
    """El bloque de uso del docstring, sin repetirlo: una sola fuente."""
    doc = __doc__ or ""
    inicio = doc.find("Uso:")
    fin = doc.find("Como hook")
    return doc[inicio:fin].rstrip() if inicio != -1 else doc


def directorio_proyecto(crudo) -> Path:
    if not isinstance(crudo, str) or not crudo.strip():
        raise Fin(2, "falta el directorio del proyecto")
    ruta = Path(crudo).resolve()
    if not ruta.is_dir():
        raise Fin(2, f"el directorio del proyecto no existe: {ruta}")
    return ruta


def cli_marcar_destilado(args: list) -> int:
    """--marcar-destilado <memoria> [project_dir], en ese orden y sin nada más."""
    if (
        args[0] != "--marcar-destilado"
        or not 2 <= len(args) <= 3
        or any(a.startswith("-") for a in args[1:])
    ):
        raise Fin(2, "uso: --marcar-destilado <memoria> [project_dir], en ese orden")

    memoria = args[1].strip()
    es_ruta = "/" in memoria or "\\" in memoria or memoria in (".", "..")
    if not memoria or es_ruta or (len(args) == 2 and Path(memoria).is_dir()):
        raise Fin(
            2,
            f"<memoria> es el nombre de la memoria, no una ruta: {args[1]!r}. "
            "Uso: --marcar-destilado <memoria> [project_dir]",
        )

    project_dir = capa_local(directorio_proyecto(args[2] if len(args) == 3 else os.getcwd()))
    n = marcar_destilado(project_dir, memoria)
    if n == 0:
        raise Fin(
            1,
            "no hay compactaciones pendientes de destilar en "
            f"{directorio_contexto(project_dir)}: no se registra nada",
        )
    print(f"Destiladas {n} compactaciones en la memoria: {memoria}")
    return 0


def guardar(args: list, evento: dict, es_hook: bool) -> int:
    """Localiza el transcript, extrae el resumen y lo guarda."""
    if any(a.startswith("-") for a in args) or len(args) > 1:
        raise Fin(2, "argumentos no reconocidos; ver --help")

    # Directorio del proyecto: argumento > cwd del evento > cwd del proceso
    if args:
        project_dir = directorio_proyecto(args[0])
    elif es_hook and evento.get("cwd"):
        project_dir = directorio_proyecto(evento.get("cwd"))
    else:
        project_dir = directorio_proyecto(os.getcwd())

    if es_hook:
        # Solo el transcript que nombra el evento: es el de ESTA sesión.
        ruta = evento.get("transcript_path")
        if not isinstance(ruta, str) or not ruta.strip():
            raise Fin(1, "el evento del hook no trae transcript_path")
        jsonl_path = Path(ruta)
        if not jsonl_path.is_file():
            raise Fin(1, f"el transcript del evento no existe: {jsonl_path}")
    else:
        jsonl_path = find_most_recent_jsonl(cwd_to_claude_slug(str(project_dir)))
        if jsonl_path is None:
            raise Fin(1, "no se encontró ningún transcript de este proyecto")
        print(f"Proyecto : {project_dir}")
        print(f"Sesión   : {jsonl_path.name}  ({jsonl_path.stat().st_size // 1024} KB)")

    # El hook corre justo al cerrar la compactación y el resumen puede no
    # estar volcado aún al .jsonl: se reintenta antes de darlo por ausente.
    intentos = 5 if es_hook else 1
    summary = compact_ts = None
    hubo_frontera = False
    for n in range(intentos):
        summary, compact_ts, hubo_frontera = extract_summary(jsonl_path)
        if summary:
            break
        if n + 1 < intentos:
            time.sleep(1)

    if not summary:
        if hubo_frontera:
            raise Fin(1, "el transcript registra una compactación pero no se reconoce su resumen")
        raise Fin(1, "el transcript no contiene ningún resumen de compactación")

    capa = capa_local(project_dir)
    output_path, es_nuevo = save_summary(capa, summary, compact_ts)
    registrar(capa, f"{'hook' if es_hook else 'manual'} {jsonl_path.name} "
                    f"{'guardado' if es_nuevo else 'ya-guardado'} {output_path.name}")

    if es_hook:
        print(recordatorio_operacion(capa, output_path))
    elif es_nuevo:
        print(f"Guardado : {output_path}")
    else:
        print(f"Sin cambios: este resumen ya estaba guardado en {output_path}")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--help" in args or "-h" in args:
        print(ayuda())
        return 0

    es_hook = False
    try:
        if "--marcar-destilado" in args:
            return cli_marcar_destilado(args)
        evento, es_hook = leer_evento_hook()
        return guardar(args, evento, es_hook)
    except Fin as e:
        motivo, codigo = e.motivo, e.codigo
    except Exception as e:  # ningún fallo imprevisto termina en traza
        motivo, codigo = f"error inesperado, {type(e).__name__}: {e}", 1

    if not es_hook:
        diag(f"ERROR: {motivo}")
        return codigo
    # En un hook, stdout es el único canal que llega al modelo: una línea para
    # que sepa que no hay punto de retorno y lo escriba él.
    print(
        f"Sesión compactada, pero NO se guardó su resumen ({motivo}). "
        "Anota ahora lo que quedaba a medias y lo que se estaba vigilando."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
