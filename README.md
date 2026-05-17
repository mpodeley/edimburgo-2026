# Edimburgo 2026 — Itinerario detallado

Sitio web + ePub para el viaje de Matías y Daniela a Edimburgo y St Andrews (20-27 mayo 2026).

🌐 **Producción**: [https://edimbra.podeley.ar/](https://edimbra.podeley.ar/)

## Estructura

```
content/        # Markdown (single source of truth)
  00-overview.md
  dia-01.md ... dia-07.md
  tracks/        # esoterico, ciencia-ia, pubs-whisky, correr, ortodoncia, romantico
assets/
  css/style.css  # mobile-first
  js/map.js      # Leaflet + OpenStreetMap
  img/           # imágenes (Wikimedia Commons + ImageMagick)
data/
  places.geojson # 44 lugares categorizados
  places.kml     # mismo, importable a Google My Maps
  books.json     # libros recomendados por track
  videos.json    # links a YouTube
scripts/
  build.sh       # pandoc → HTML + ePub
  template.html  # template HTML5 con nav, footer, soporte mapa
  build-gmaps.py # genera KML + URLs de Google Maps por día
*.html          # generados por build.sh
ebook/*.epub    # generado por build.sh
CNAME           # custom domain
```

## Build

```bash
bash scripts/build.sh
```

Requiere:
- `pandoc` 3.x — descargable desde [github.com/jgm/pandoc/releases](https://github.com/jgm/pandoc/releases) si no está en el sistema.
- `python3` para `build-gmaps.py`.

## Servir local

```bash
python3 -m http.server 8000 --bind 0.0.0.0
```

Abrir desde el celu en la misma red: `http://<tu-ip>:8000/`.

## Deploy

GitHub Pages sirve desde `main` branch, root del repo. El archivo `CNAME` configura el custom domain `edimbra.podeley.ar`.

## Licencia

Para uso personal de los viajeros. Imágenes son de Wikimedia Commons (atribución implícita en cada caso).
