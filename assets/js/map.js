/* Mapa interactivo — Leaflet + OSM, carga places.geojson y agrupa por categoría */

(function () {
  const el = document.getElementById('mapa-general');
  if (!el || typeof L === 'undefined') return;

  // Edinburgh centroid as default. Auto-fit after data load.
  const map = L.map('mapa-general', {
    scrollWheelZoom: false,
  }).setView([55.953, -3.188], 13);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);

  const colors = {
    esoterico: '#5f4373',
    pub:       '#b78c2a',
    museo:     '#6b1d1d',
    ciencia:   '#6b1d1d',
    comida:    '#2e6a3d',
    romantico: '#b54a87',
    transporte:'#777',
    golf:      '#2a6b8c',
    correr:    '#c2660a',
    alojamiento:'#1b1816',
    default:   '#4a3f37',
  };

  function makeIcon(category) {
    const c = colors[category] || colors.default;
    return L.divIcon({
      className: 'place-icon',
      html: `<div style="background:${c};width:18px;height:18px;border-radius:50%;border:3px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);"></div>`,
      iconSize: [18, 18],
      iconAnchor: [9, 9],
    });
  }

  fetch('data/places.geojson')
    .then(r => r.json())
    .then(geo => {
      const layer = L.geoJSON(geo, {
        pointToLayer: function (feature, latlng) {
          return L.marker(latlng, { icon: makeIcon(feature.properties.category) });
        },
        onEachFeature: function (feature, layer) {
          const p = feature.properties;
          const cat = `<span class="tag ${p.category}">${p.category}</span>`;
          const link = p.url_detail ? `<a href="${p.url_detail}">leer más</a>` : '';
          const off = p.url_official ? ` · <a href="${p.url_official}" target="_blank" rel="noopener">sitio oficial</a>` : '';
          const cost = (p.cost_gbp != null) ? ` · £${p.cost_gbp}` : '';
          const dur = (p.duration_min != null) ? ` · ${p.duration_min} min` : '';
          const coords = feature.geometry.coordinates;
          const gmaps = `https://www.google.com/maps/search/?api=1&query=${coords[1]},${coords[0]}`;
          const gmapsBtn = `<a href="${gmaps}" target="_blank" rel="noopener" style="display:inline-block;background:#4285F4;color:#fff;padding:4px 8px;border-radius:4px;text-decoration:none;font-size:12px;margin-top:6px;">📍 Abrir en Google Maps</a>`;
          layer.bindPopup(`
            <div style="font-family:system-ui,sans-serif;min-width:220px;">
              <div style="margin-bottom:4px;">${cat}</div>
              <strong>${p.name}</strong><br>
              <span style="color:#666;font-size:12px;">${p.description_short || ''}</span><br>
              <span style="font-size:12px;color:#888;">${(p.day || []).join(', ')}${dur}${cost}</span><br>
              ${link}${off}<br>
              ${gmapsBtn}
            </div>
          `);
        },
      }).addTo(map);

      try {
        const bounds = layer.getBounds();
        if (bounds.isValid()) map.fitBounds(bounds, { padding: [30, 30] });
      } catch (e) { /* ignore */ }
    })
    .catch(err => {
      el.innerHTML = '<div style="padding:16px;text-align:center;color:#888;">No se pudo cargar el mapa.</div>';
      console.error(err);
    });
})();
