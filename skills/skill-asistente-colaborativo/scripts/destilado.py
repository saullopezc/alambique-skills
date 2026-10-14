# SPDX-License-Identifier: MIT
"""
destilado.py
------------
El ciclo de destilado: de N resúmenes de compactación a UNA memoria
persistente. Cuenta los pendientes, avisa al llegar al umbral y anota el
cierre del ciclo. El destilado en sí lo escribe el asistente, no este código.

Author       : Saul López
Created Date : 2026-10-14
"""

import json
import os
from datetime import datetime
from pathlib import Path

from alcance import PATRON_RESUMEN, directorio_contexto
from harness import cwd_to_claude_slug, diag, find_claude_projects_dir

# Cada compactación deja su .md (detalle). Al llegar al umbral, los pendientes
# se consolidan en una sola memoria. El número es alto a propósito: destilar
# cada sesión produce crónica, no lineamiento.
UMBRAL_POR_DEFECTO = 10
ESTADO_DESTILADO = ".destilado_estado.json"

# La orden que cierra el ciclo la da el script de entrada, no este módulo.
SCRIPT = Path(__file__).resolve().with_name("extract_compact_summary.py")


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
        f"  python3 {SCRIPT} --marcar-destilado <nombre-memoria> {project_dir}",
    ])
