#!/usr/bin/env python3
"""Rehace la letra de íconos del Gantt: los íconos que usa `plantilla.html`, recortados de Symbols Nerd Font Mono.

    uv run --with fonttools --with brotli python3 bin/iconos.py [ruta/a/SymbolsNerdFontMono-Regular.ttf]

Los íconos de la plantilla van como `&#xf0a33;` en el HTML o `\\u{f0a33}` en el JS (códigos de la zona privada de
Unicode, los de https://www.nerdfonts.com/cheat-sheet). Este script los busca, recorta la letra a solo esos (unos
pocos KB) y la escribe en base64 dentro de la plantilla, entre `/*ICONOS*/` y `/*/ICONOS*/`: el lienzo de telar no
tiene red, así que la letra va adentro. Correrlo cada vez que se agrega o se quita un ícono de la plantilla.
La letra es de Nerd Fonts (MIT) con los íconos de Codicons (CC BY 4.0), Material Design Icons (Apache 2.0) y
Octicons (MIT).
"""

from __future__ import annotations

import base64
import io
import re
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

AQUI = Path(__file__).resolve().parent.parent
PLANTILLA = AQUI / "plantilla.html"
LETRA = Path.home() / "Library" / "Fonts" / "SymbolsNerdFontMono-Regular.ttf"
MARCAS = re.compile(r"/\*ICONOS\*/.*?/\*/ICONOS\*/", re.S)


def usados(texto: str) -> list[int]:
    """Los códigos de la zona privada que aparecen en la plantilla, como entidad HTML o escape de JS."""
    pares = re.findall(r"&#x([0-9a-fA-F]{4,5});|\\u\{([0-9a-fA-F]{4,5})\}", texto)
    codigos = {int(html or js, 16) for html, js in pares}
    return sorted(c for c in codigos if 0xE000 <= c <= 0xF8FF or 0xF0000 <= c <= 0xFFFFD)


def main(argv: list[str]) -> int:
    letra = Path(argv[0]) if argv else LETRA
    texto = PLANTILLA.read_text(encoding="utf-8")
    codigos = usados(texto)
    fuente = TTFont(letra)
    faltan = [hex(c) for c in codigos if c not in fuente.getBestCmap()]
    if faltan:
        print(f"no están en {letra.name}: {', '.join(faltan)}", file=sys.stderr)
        return 1
    opciones = subset.Options()
    opciones.flavor = "woff2"
    opciones.layout_features = []
    opciones.name_IDs = []
    recorte = subset.Subsetter(options=opciones)
    recorte.populate(unicodes=codigos)
    recorte.subset(fuente)
    fuente.flavor = "woff2"
    salida = io.BytesIO()
    fuente.save(salida)
    b64 = base64.b64encode(salida.getvalue()).decode()
    regla = (f"/*ICONOS*/@font-face {{ font-family: iconos; src: url(data:font/woff2;base64,{b64}) format('woff2'); }}"
             "/*/ICONOS*/")
    if not MARCAS.search(texto):
        print("la plantilla no tiene las marcas /*ICONOS*/ … /*/ICONOS*/", file=sys.stderr)
        return 1
    PLANTILLA.write_text(MARCAS.sub(lambda _: regla, texto), encoding="utf-8")
    print(f"{len(codigos)} íconos, {len(salida.getvalue())} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
