#!/usr/bin/env bash
# Build script — genera sitio HTML estático + ePub desde content/*.md
# Uso: bash scripts/build.sh

set -euo pipefail

cd "$(dirname "$0")/.."
ROOT="$(pwd)"

# Detect pandoc
if command -v pandoc >/dev/null 2>&1; then
  PANDOC="pandoc"
elif [ -x "$HOME/.local/bin/pandoc" ]; then
  PANDOC="$HOME/.local/bin/pandoc"
else
  echo "ERROR: pandoc no encontrado. Instalalo o ponelo en ~/.local/bin/pandoc." >&2
  exit 1
fi

GH_USER="${GH_USER:-mpodeley}"

echo "→ Limpiando salida..."
# Sólo borramos los .html generados (no los assets ni el repo)
find . -maxdepth 1 -name '*.html' -type f -delete
rm -f ebook/edimburgo-2026.epub

TEMPLATE="scripts/template.html"
MD_DIR="content"
TRACKS_DIR="content/tracks"

# Páginas que cargan el mapa
NEEDS_MAP_FILES=("00-overview.md")

needs_map() {
  local name="$1"
  for m in "${NEEDS_MAP_FILES[@]}"; do
    [ "$m" = "$name" ] && return 0
  done
  return 1
}

build_page() {
  local md="$1"
  local out="$2"
  local extra_meta=()

  local basename
  basename="$(basename "$md")"
  if needs_map "$basename"; then
    extra_meta+=("--metadata=needs-map:true")
  fi

  echo "  $md → $out"
  "$PANDOC" \
    --from markdown+yaml_metadata_block+pipe_tables+fenced_divs+bracketed_spans+link_attributes+raw_html \
    --to html5 \
    --template "$TEMPLATE" \
    --standalone \
    --metadata "gh-user:$GH_USER" \
    "${extra_meta[@]}" \
    -o "$out" \
    "$md"
}

echo "→ Generando index.html..."
build_page "$MD_DIR/00-overview.md" "index.html"

echo "→ Generando páginas de cada día..."
for md in "$MD_DIR"/dia-*.md; do
  name="$(basename "$md" .md)"
  build_page "$md" "${name}.html"
done

echo "→ Generando tracks..."
for md in "$TRACKS_DIR"/*.md; do
  name="track-$(basename "$md" .md)"
  build_page "$md" "${name}.html"
done

echo "→ Generando KML y URLs de Google Maps..."
python3 scripts/build-gmaps.py

echo "→ Generando ePub..."
EPUB_META="content/epub-metadata.yaml"
EPUB_FILES=(
  "$MD_DIR/00-overview.md"
  "$MD_DIR"/dia-*.md
  "$TRACKS_DIR"/*.md
)

mkdir -p ebook
# Use --metadata-file if present, otherwise basic metadata.
PANDOC_EPUB_ARGS=(
  --from markdown+yaml_metadata_block+pipe_tables+fenced_divs+bracketed_spans+link_attributes+raw_html
  --to epub3
  --toc
  --toc-depth=2
  --split-level=1
  -o ebook/edimburgo-2026.epub
)

if [ -f "$EPUB_META" ]; then
  PANDOC_EPUB_ARGS+=(--metadata-file="$EPUB_META")
fi

if [ -f "assets/img/cover.jpg" ]; then
  PANDOC_EPUB_ARGS+=(--epub-cover-image=assets/img/cover.jpg)
fi

"$PANDOC" "${PANDOC_EPUB_ARGS[@]}" "${EPUB_FILES[@]}"

echo
echo "✓ Build completo."
echo "  Sitio:    $ROOT/index.html"
echo "  ePub:     $ROOT/ebook/edimburgo-2026.epub"
echo "  Servir:   python3 -m http.server 8000  (luego abrir http://<tu-ip>:8000 en el celu)"
