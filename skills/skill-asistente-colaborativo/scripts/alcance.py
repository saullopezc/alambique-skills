# SPDX-License-Identifier: MIT
"""
alcance.py
----------
Lo que acota al guardado de compactación, que corre sin turno: dónde puede
escribir (solo una _local/ que git ignora), hasta cuándo vale su alta (la
caducidad que el instalador pone en el comando del hook) y dónde deja
constancia de cada ejecución (el registro).

Author       : Saul López
Created Date : 2026-10-14
"""

import subprocess
from datetime import date, datetime
from pathlib import Path

from harness import Fin, diag, find_claude_projects_dir

PATRON_RESUMEN = "*_compact_summary*.md"

# Lo que se pregunta a git: un fichero con el nombre de los que se guardan.
PRUEBA_IGNORADO = "_local/context/00000000_000000_compact_summary.md"

REGISTRO = ".registro_compactacion.log"


# ---------------------------------------------------------------------------
# Dónde: la capa local ignorada
# ---------------------------------------------------------------------------

def directorio_contexto(project_dir: Path) -> Path:
    """
    Destino de los resúmenes: {project_dir}/_local/context/, la capa local.
    Lo que se guarda es el resumen crudo, con comandos, salidas y rutas reales:
    project_dir tiene que venir de capa_local(), que comprueba que git lo ignora.
    """
    return project_dir / "_local" / "context"


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


# ---------------------------------------------------------------------------
# Hasta cuándo: la caducidad del alta
# ---------------------------------------------------------------------------

RENOVAR = "renuévala con `instalar.sh skill-asistente-colaborativo`"


def comprobar_alta(caduca: "str | None", hoy: "date | None" = None) -> None:
    """
    El alta del hook es la aprobación previa de una ejecución sin turno, y
    tiene que caducar: el instalador escribe la fecha en el comando del hook
    (`--caduca AAAA-MM-DD`). Sin fecha, con una ilegible o con una pasada no
    se guarda nada: Fin. El último día de validez es la propia fecha.
    """
    if caduca is None:
        raise Fin(1, f"el alta del hook no declara caducidad; {RENOVAR}")
    try:
        limite = date.fromisoformat(caduca)
    except ValueError:
        raise Fin(1, f"la caducidad del alta no es una fecha AAAA-MM-DD: {caduca!r}; {RENOVAR}")
    if (hoy or date.today()) > limite:
        raise Fin(1, f"el alta del hook caducó el {limite.isoformat()}; {RENOVAR}")


# ---------------------------------------------------------------------------
# Constancia: el registro de cada ejecución
# ---------------------------------------------------------------------------

def ruta_registro() -> Path:
    """
    <conf>/projects/.registro_compactacion.log: junto a los transcripts de
    Claude Code, que ya guardan la sesión entera. Es el único sitio que existe
    en toda ejecución, también en la que no encuentra una capa ignorada donde
    guardar; las líneas llevan rutas del puesto, la misma clase que lo que
    tienen al lado.
    """
    return find_claude_projects_dir() / REGISTRO


def registrar(modo: str, resultado: str, detalle: str) -> None:
    """Una línea por ejecución: fecha, modo, resultado y detalle. Si falla, solo se dice."""
    linea = " ".join(detalle.split())        # una línea, pase lo que pase en el motivo
    ruta = ruta_registro()
    try:
        ruta.parent.mkdir(exist_ok=True)
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {modo} {resultado} {linea}\n")
    except OSError as e:
        diag(f"AVISO: no se pudo escribir el registro de ejecución en {ruta}: {e}")
