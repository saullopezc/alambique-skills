# SPDX-License-Identifier: MIT
"""
harness.py
----------
Lo que extract_compact_summary.py sabe de Claude Code: dónde guarda sus
sesiones y cómo nombra el directorio de cada proyecto. Y la forma común de
terminar (Fin) y de diagnosticar (diag), que usan todos los módulos.

Author       : Saul López
Created Date : 2026-10-14
"""

import os
import sys
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
