#!/usr/bin/env python3
"""
Genera:
1. data/places.kml — todas las paradas como puntos categorizados (importable a Google Maps).
2. data/gmaps-day-urls.json — URL de Google Maps por día con waypoints.

Uso: python3 scripts/build-gmaps.py
"""

import json
import os
import urllib.parse
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "data" / "places.geojson"
KML_OUT = ROOT / "data" / "places.kml"
URLS_OUT = ROOT / "data" / "gmaps-day-urls.json"

# Color por categoría para Google Earth/Maps (AABBGGRR)
COLORS = {
    "esoterico": "ff734347",       # thistle/purple
    "pub": "ff2a8cb7",             # gold
    "museo": "ff1d1d6b",           # red
    "ciencia": "ff1d1d6b",
    "comida": "ff3d6a2e",          # green
    "romantico": "ff874ab5",       # pink
    "transporte": "ff7f7f7f",
    "golf": "ff8c6b2a",            # blue
    "correr": "ff0a66c2",          # orange
    "alojamiento": "ff16181b",
}

# Orden de los días → para construir circuitos
DAY_ORDER = {
    "jue-21": 1, "vie-22": 2, "sáb-23": 3, "dom-24": 4,
    "lun-25": 5, "mar-26": 6, "mié-27": 7,
}
DAY_LABELS = {
    "jue-21": "Jueves 21 — Llegada",
    "vie-22": "Viernes 22 — Old Town + esotérico",
    "sáb-23": "Sábado 23 — Britannia + carb-load",
    "dom-24": "Domingo 24 — Maratón",
    "lun-25": "Lunes 25 — Rosslyn + St Andrews",
    "mar-26": "Martes 26 — Golf en Strathtyrum",
    "mié-27": "Miércoles 27 — Vuelta",
}


def build_kml(features):
    """Genera KML para importar a Google Maps."""
    by_cat = defaultdict(list)
    for f in features:
        cat = f["properties"].get("category", "default")
        by_cat[cat].append(f)

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<kml xmlns="http://www.opengis.net/kml/2.2">',
           '<Document>',
           '<name>Edimburgo 2026 — Itinerario</name>',
           '<description>Paradas para Matías y Daniela, 20-27 mayo 2026. https://edimbra.podeley.ar</description>']

    # Estilos por categoría
    for cat, color in COLORS.items():
        out.append(f'<Style id="{cat}">')
        out.append('  <IconStyle>')
        out.append(f'    <color>{color}</color>')
        out.append('    <Icon>')
        out.append('      <href>https://maps.google.com/mapfiles/kml/paddle/wht-circle.png</href>')
        out.append('    </Icon>')
        out.append('  </IconStyle>')
        out.append('</Style>')

    # Carpetas por categoría
    for cat, items in sorted(by_cat.items()):
        out.append(f'<Folder>')
        out.append(f'  <name>{cat}</name>')
        for f in items:
            p = f["properties"]
            coords = f["geometry"]["coordinates"]  # [lon, lat]
            name = p.get("name", "Sin nombre")
            desc = p.get("description_short", "")
            days = ", ".join(p.get("day", []))
            cost = f" · £{p['cost_gbp']}" if p.get("cost_gbp") is not None else ""
            dur = f" · {p['duration_min']} min" if p.get("duration_min") is not None else ""
            full_desc = f"{desc}\n\nDías: {days}{dur}{cost}"
            if p.get("url_official"):
                full_desc += f"\nOficial: {p['url_official']}"
            out.append(f'  <Placemark>')
            out.append(f'    <name>{escape_xml(name)}</name>')
            out.append(f'    <description><![CDATA[{full_desc}]]></description>')
            out.append(f'    <styleUrl>#{cat}</styleUrl>')
            out.append(f'    <Point>')
            out.append(f'      <coordinates>{coords[0]},{coords[1]},0</coordinates>')
            out.append(f'    </Point>')
            out.append(f'  </Placemark>')
        out.append('</Folder>')

    out.append('</Document>')
    out.append('</kml>')
    return "\n".join(out)


def escape_xml(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_day_urls(features):
    """Para cada día, genera URL de Google Maps con waypoints."""
    by_day = defaultdict(list)
    for f in features:
        p = f["properties"]
        for d in p.get("day", []):
            if d in DAY_ORDER:
                by_day[d].append(f)

    urls = {}
    for day, items in by_day.items():
        # Excluir alojamientos del circuito
        items = [f for f in items if f["properties"].get("category") != "alojamiento"]
        if not items:
            continue

        # Orden simple por longitud (NO óptimo pero suficiente)
        items.sort(key=lambda f: f["geometry"]["coordinates"][0])

        # Construir URL — máximo 9 waypoints en Google Maps
        if len(items) > 10:
            items = items[:10]

        coords_list = [f["geometry"]["coordinates"] for f in items]
        if len(coords_list) < 2:
            continue
        origin = f"{coords_list[0][1]},{coords_list[0][0]}"
        destination = f"{coords_list[-1][1]},{coords_list[-1][0]}"
        waypoints = "|".join([f"{c[1]},{c[0]}" for c in coords_list[1:-1]])

        url_params = {
            "api": "1",
            "origin": origin,
            "destination": destination,
            "travelmode": "walking",
        }
        if waypoints:
            url_params["waypoints"] = waypoints

        url = "https://www.google.com/maps/dir/?" + urllib.parse.urlencode(url_params, safe="|,")
        urls[day] = {
            "label": DAY_LABELS.get(day, day),
            "url": url,
            "stops": [f["properties"]["name"] for f in items],
            "stops_count": len(items),
        }

    return urls


def main():
    geo = json.loads(GEO.read_text())
    features = geo["features"]

    kml = build_kml(features)
    KML_OUT.write_text(kml)
    print(f"✓ Wrote {KML_OUT} ({len(kml)} bytes, {len(features)} features)")

    urls = build_day_urls(features)
    URLS_OUT.write_text(json.dumps(urls, indent=2, ensure_ascii=False))
    print(f"✓ Wrote {URLS_OUT} ({len(urls)} day circuits)")
    for day, info in urls.items():
        print(f"  {day}: {info['stops_count']} stops")


if __name__ == "__main__":
    main()
