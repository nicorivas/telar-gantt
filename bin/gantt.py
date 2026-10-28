#!/usr/bin/env python3
"""El Gantt de los proyectos, para telar: dibuja lo que da `telar fechas`, sin saber de dónde vino cada fecha.

    bin/gantt.py pagina     la subpestaña de telar: genera el Gantt y lo devuelve como un lienzo
    bin/gantt.py datos      lo que va a dibujar, en JSON (para revisar)

Cada proyecto es una fila: su barra es su `plazo` (la fecha de clase `plazo`, si alguna fuente la da) o, si no, de
su primera a su última actividad; en ella van sus hitos y sus tareas; adentro, sus actividades, sesiones y entregas.
Los nombres, el cliente y el área salen de `telar proyectos`; los colores, del orden de las áreas del perfil.

Se ven los proyectos con alguna fecha entre seis meses atrás y un año adelante, menos los terminados: los que tienen
su plazo hecho o cancelado, o un estado cerrado en su documento. Solo biblioteca estándar.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
TERMINADO = re.compile(r"cerrad|terminad|finalizad|perdid|cancelad", re.I)
ACTIVO = re.compile(r"^(activo|en curso|en ejecuci[oó]n|ganado)", re.I)
#: las clases que van adentro de un proyecto, una fila cada una
ADENTRO = ("actividad", "sesion", "entrega", "evento")


def _estado_dir() -> Path:
    d = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state") / "telar-gantt"
    d.mkdir(parents=True, exist_ok=True)
    return d


def telar(*args: str) -> dict:
    """Lo que dice una orden de telar, en JSON; {} si no contesta."""
    try:
        r = subprocess.run(["telar", *args, "--json"], capture_output=True, text=True, timeout=60)
        return json.loads(r.stdout or "{}") if r.returncode == 0 else {}
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return {}


def datos(hoy: date | None = None) -> dict:
    hoy = hoy or date.today()
    desde, hasta = hoy - timedelta(days=183), hoy + timedelta(days=366)
    f = telar("fechas")
    p = telar("proyectos")
    unidades = {u["ruta"]: u for u in p.get("proyectos", [])}
    por_proyecto: dict[str, list[dict]] = {}
    for x in f.get("fechas", []):
        if x.get("proyecto"):
            por_proyecto.setdefault(x["proyecto"], []).append(x)

    proyectos = []
    for ruta, fechas in por_proyecto.items():
        u = unidades.get(ruta, {})
        plazo = next((x for x in fechas if x["clase"] == "plazo"), None)
        if plazo and plazo["estado"] in ("hecho", "cancelado"):
            continue
        if TERMINADO.search(f"{u.get('arquetipo', '')} {u.get('estado', '')}"):
            continue
        if not any(x["fin"] >= desde.isoformat() and x["inicio"] <= hasta.isoformat() for x in fechas):
            continue
        adentro = sorted((x for x in fechas if x["clase"] in ADENTRO), key=lambda x: (x["inicio"], x["fin"]))
        inicio = plazo["inicio"] if plazo else min((x["inicio"] for x in adentro), default="")
        fin = plazo["fin"] if plazo else max((x["fin"] for x in adentro), default="")
        proyectos.append({
            "ruta": ruta, "titulo": u.get("nombre") or ruta.rsplit("/", 1)[-1], "cliente": u.get("cliente", ""),
            "area": u.get("area", ""), "estado": u.get("estado", ""), "inicio": inicio, "fin": fin,
            "barra": "plazo" if plazo else ("actividades" if adentro else ""),
            "plazo": plazo,
            "actividades": adentro,
            "hitos": [x for x in fechas if x["clase"] == "hito"],
            "tareas": [x for x in fechas if x["clase"] == "tarea"],
        })
    # lo que está activo y no tiene ninguna fecha: se lista abajo, para que alguien se las ponga
    sin_fechas = sorted(u["nombre"] for r, u in unidades.items()
                        if r not in por_proyecto and ACTIVO.match(u.get("estado") or "") and not TERMINADO.search(u.get("arquetipo", "")))
    return {"hoy": hoy.isoformat(), "areas": p.get("areas", []), "proyectos": proyectos, "sin_fechas": sin_fechas,
            "saltadas": len(f.get("saltadas", [])), "fallas": f.get("fallas", []) + ([] if p else ["telar proyectos no contestó"])}


def main(argv: list[str]) -> int:
    orden = argv[0] if argv else "pagina"
    d = datos()
    if orden == "datos":
        print(json.dumps(d, ensure_ascii=False, indent=1))
        return 0
    plantilla = (AQUI / "plantilla.html").read_text(encoding="utf-8")
    html = plantilla.replace("/*DATOS*/null", json.dumps(d, ensure_ascii=False).replace("</", "<\\/"))
    destino = _estado_dir() / "gantt.html"
    destino.write_text(html, encoding="utf-8")
    con = sum(1 for p in d["proyectos"] if p["actividades"])
    print(json.dumps({
        "titulo": "Gantt",
        "subtitulo": f"{len(d['proyectos'])} proyectos · {con} con actividades · {sum(len(p['tareas']) for p in d['proyectos'])} tareas",
        "bloques": [{"lienzo": {"archivo": str(destino), "alto": "lleno", "memoria": str(_estado_dir() / "memoria.json")}}],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
