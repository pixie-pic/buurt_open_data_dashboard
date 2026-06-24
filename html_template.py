"""
html_template.py
────────────────
Render the self-contained Buurt data explorer HTML file.

The HTML embeds all GeoJSON and variable metadata as inline JSON, so the
resulting file can be opened directly in any browser with no local server.

The dashboard has two modes:
  - Missing data  : choropleth showing which buurten lack a given variable
  - Values        : heatmap choropleth with percentile / raw-value scaling,
                    a summary statistics panel, and a canvas histogram

External dependencies (loaded from CDN):
  - Leaflet 1.9.4
  - CartoDB light basemap tiles
"""

import json


# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, sans-serif; background: #f5f4f0; color: #1a1a1a; }

/* ── Layout ── */
#layout  { display: flex; height: 100vh; }
#sidebar { width: 290px; flex-shrink: 0; background: #fff;
           border-right: 1px solid #e0dfd8; padding: 1.25rem;
           overflow-y: auto; display: flex; flex-direction: column; gap: 1.25rem; }
#map     { flex: 1; }

h1 { font-size: 16px; font-weight: 500; line-height: 1.4; }

/* ── Mode toggle (Missing / Values) ── */
.mode-toggle { display: flex; background: #f5f4f0; border-radius: 8px; padding: 3px; gap: 3px; }
.mode-btn    { flex: 1; padding: 6px 8px; font-size: 12px; font-weight: 500;
               border: none; border-radius: 6px; cursor: pointer;
               background: transparent; color: #888; transition: all 0.15s; }
.mode-btn.active { background: #fff; color: #1a1a1a; box-shadow: 0 1px 3px rgba(0,0,0,.12); }

/* ── Dropdowns ── */
label  { font-size: 12px; color: #888; display: block; margin-bottom: 6px; }
select { width: 100%; padding: 7px 9px; font-size: 13px;
         border: 1px solid #ccc; border-radius: 7px; background: #fff; }

/* ── Stat cards ── */
.stat       { background: #f5f4f0; border-radius: 7px; padding: 10px 14px; }
.stat-label { font-size: 11px; color: #888; margin-bottom: 3px; }
.stat-val   { font-size: 20px; font-weight: 500; }
.red        { color: #a32d2d; }
.amber      { color: #854f0b; }

/* ── Legend & section labels ── */
.section-label { font-size: 12px; color: #888; margin-bottom: 8px; }
.legend-item   { display: flex; align-items: center; gap: 8px; font-size: 13px; margin-bottom: 7px; }
.swatch        { width: 13px; height: 13px; border-radius: 3px; flex-shrink: 0; }

/* ── Missing buurten tag list ── */
.tags      { display: flex; flex-wrap: wrap; gap: 5px; max-height: 200px; overflow-y: auto; }
.tag       { background: #fcebeb; color: #a32d2d; font-size: 11px; padding: 2px 7px; border-radius: 4px; }
.tag.more  { background: #f0efe8; color: #888; }

/* ── Values panel ── */
.val-stats     { display: flex; flex-direction: column; gap: 6px; }
.val-stat      { background: #f5f4f0; border-radius: 7px; padding: 8px 12px;
                 display: flex; justify-content: space-between; align-items: center; }
.val-stat-label { font-size: 11px; color: #888; }
.val-stat-val   { font-size: 14px; font-weight: 500; }

/* ── Heatmap colour-scale legend ── */
.heatmap-bar    { height: 12px; border-radius: 4px;
                  background: linear-gradient(to right, #f7fbff, #6baed6, #08306b);
                  margin-bottom: 4px; }
.heatmap-labels { display: flex; justify-content: space-between; font-size: 11px; color: #888; }

/* ── Distribution histogram canvas ── */
#dist-canvas { width: 100%; height: 110px; display: block;
               border-radius: 6px; background: #f5f4f0; }

/* ── Percentile / Raw sub-toggle ── */
.sub-toggle { display: flex; background: #f5f4f0; border-radius: 6px; padding: 2px; gap: 2px; }
.sub-btn    { flex: 1; padding: 4px 6px; font-size: 11px; font-weight: 500;
              border: none; border-radius: 5px; cursor: pointer;
              background: transparent; color: #888; transition: all 0.15s; }
.sub-btn.active { background: #fff; color: #1a1a1a; box-shadow: 0 1px 2px rgba(0,0,0,.1); }
"""


# ── HTML skeleton ─────────────────────────────────────────────────────────────

_HTML_BODY = """
<div id="layout">
  <div id="sidebar">
    <h1>Buurt data explorer<br><span style="color:#888;font-weight:400">CBS 2022</span></h1>

    <!-- Mode toggle -->
    <div class="mode-toggle">
      <button class="mode-btn active" id="btn-missing" onclick="setMode('missing')">Missing data</button>
      <button class="mode-btn"        id="btn-values"  onclick="setMode('values')">Values</button>
    </div>

    <!-- Area filter -->
    <div>
      <label for="gem-select">Area</label>
      <select id="gem-select"></select>
    </div>

    <!-- Variable selector -->
    <div>
      <label for="var-select">Variable</label>
      <select id="var-select"></select>
    </div>

    <!-- ── MISSING PANEL ────────────────────────────────────────── -->
    <div id="missing-panel" style="display:flex;flex-direction:column;gap:1.25rem">
      <div style="display:flex;flex-direction:column;gap:8px">
        <div class="stat"><div class="stat-label">Total buurten</div><div class="stat-val"       id="stat-total">—</div></div>
        <div class="stat"><div class="stat-label">Missing</div>       <div class="stat-val red"   id="stat-missing">—</div></div>
        <div class="stat"><div class="stat-label">% missing</div>     <div class="stat-val amber" id="stat-pct">—</div></div>
      </div>
      <div>
        <div class="section-label">Legend</div>
        <div class="legend-item"><div class="swatch" style="background:#e24b4a"></div>Missing data</div>
        <div class="legend-item"><div class="swatch" style="background:#639922"></div>Data present</div>
        <div class="legend-item"><div class="swatch" style="background:#ccc"></div>Not in dataset</div>
      </div>
      <div>
        <div class="section-label" id="missing-title">—</div>
        <div class="tags" id="tags"></div>
      </div>
    </div>

    <!-- ── VALUES PANEL ─────────────────────────────────────────── -->
    <div id="values-panel" style="display:none;flex-direction:column;gap:1.25rem">
      <div class="val-stats">
        <div class="val-stat"><span class="val-stat-label">Min</span>    <span class="val-stat-val" id="val-min">—</span></div>
        <div class="val-stat"><span class="val-stat-label">Median</span> <span class="val-stat-val" id="val-median">—</span></div>
        <div class="val-stat"><span class="val-stat-label">Mean</span>   <span class="val-stat-val" id="val-mean">—</span></div>
        <div class="val-stat"><span class="val-stat-label">Max</span>    <span class="val-stat-val" id="val-max">—</span></div>
      </div>
      <div>
        <div class="section-label" style="margin-bottom:6px">Colour scaling</div>
        <div class="sub-toggle">
          <button class="sub-btn active" id="btn-pct" onclick="setScaling('percentile')">Percentile</button>
          <button class="sub-btn"        id="btn-raw" onclick="setScaling('raw')">Raw value</button>
        </div>
      </div>
      <div>
        <div class="section-label">Colour scale</div>
        <div class="heatmap-bar"></div>
        <div class="heatmap-labels">
          <span id="leg-min">—</span><span id="leg-mid">—</span><span id="leg-max">—</span>
        </div>
      </div>
      <div>
        <div class="section-label">Distribution</div>
        <canvas id="dist-canvas"></canvas>
      </div>
      <div>
        <div class="legend-item"><div class="swatch" style="background:#ccc"></div>No data / not matched</div>
      </div>
    </div>

  </div><!-- /sidebar -->
  <div id="map"></div>
</div>
"""


# ── JavaScript ────────────────────────────────────────────────────────────────

_JS = """
const GEO  = {geo_json_str};
const VARS = {var_meta_str};

// ── Map initialisation ───────────────────────────────────────────────────────
const map = L.map('map', { zoomControl: true }).setView([52.3, 5.3], 8);
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; OpenStreetMap &copy; CartoDB',
}).addTo(map);

let geojsonLayer   = null;
let currentMode    = 'missing';
let currentScaling = 'percentile'; // 'percentile' | 'raw'


// ── Colour ramp: Blues (9-step ColorBrewer) ───────────────────────────────────
const RAMP = ['#f7fbff','#deebf7','#c6dbef','#9ecae1','#6baed6','#4292c6','#2171b5','#08519c','#08306b'];

/**
 * Interpolate a colour from RAMP given a normalised t ∈ [0, 1].
 * @param {number} t
 * @returns {string} CSS rgb() colour string
 */
function rampColor(t) {
  t = Math.max(0, Math.min(1, t));
  const n  = RAMP.length - 1;
  const i  = Math.min(Math.floor(t * n), n - 1);
  const f  = t * n - i;
  const h1 = RAMP[i], h2 = RAMP[i + 1];
  const hex = s => parseInt(s, 16);
  const lerp = (a, b) => Math.round(a + (b - a) * f);
  const r = lerp(hex(h1.slice(1,3)), hex(h2.slice(1,3)));
  const g = lerp(hex(h1.slice(3,5)), hex(h2.slice(3,5)));
  const b = lerp(hex(h1.slice(5,7)), hex(h2.slice(5,7)));
  return `rgb(${r},${g},${b})`;
}


// ── Number formatter ──────────────────────────────────────────────────────────
/**
 * Format a numeric value for display in the sidebar and tooltips.
 * Applies K/M suffixes for large numbers; rounds or shows 2 d.p. for small ones.
 * @param {number|null} v
 * @returns {string}
 */
function fmt(v) {
  if (v === null || v === undefined || isNaN(v)) return '—';
  if (Math.abs(v) >= 1e6) return (v / 1e6).toFixed(2) + 'M';
  if (Math.abs(v) >= 1e4) return (v / 1e3).toFixed(1) + 'K';
  if (Math.abs(v) < 10)   return (+v).toFixed(2);
  return Math.round(v).toLocaleString('nl-NL');
}


// ── Area filter ───────────────────────────────────────────────────────────────
let currentGemeente = ''; // empty string = all of the Netherlands

/** Return the features visible under the current gemeente filter. */
function activeFeatures() {
  if (!currentGemeente) return GEO.features;
  return GEO.features.filter(f => f.properties.gemeentenaam === currentGemeente);
}

/** Switch the gemeente filter and re-render; zoom to new bounds. */
function setGemeente(name) {
  currentGemeente = name;
  render(document.getElementById('var-select').value);
  if (!name) {
    map.setView([52.3, 5.3], 8);
  } else if (geojsonLayer) {
    map.fitBounds(geojsonLayer.getBounds(), { padding: [30, 30] });
  }
}


// ── Statistics helpers ────────────────────────────────────────────────────────
/** Collect finite values for a variable across currently-active features. */
function getVals(key) {
  return activeFeatures()
    .map(f => f.properties['val_' + key])
    .filter(v => v !== null && v !== undefined && isFinite(v));
}

function median(arr) {
  const s = [...arr].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

function mean(arr) {
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}


// ── Histogram renderer ────────────────────────────────────────────────────────
/**
 * Draw a colour-coded frequency histogram onto #dist-canvas.
 * Bars are coloured by the percentile rank of their midpoint value,
 * matching the heatmap colour ramp.
 * @param {string} key  column key (without 'val_' prefix)
 */
function drawHist(key) {
  const canvas = document.getElementById('dist-canvas');
  const ctx    = canvas.getContext('2d');
  const W      = canvas.offsetWidth || 246;
  const H      = 110;
  canvas.width  = W;
  canvas.height = H;
  ctx.clearRect(0, 0, W, H);

  const vals = getVals(key);
  if (!vals.length) return;

  const BINS  = 22;
  const TICKS = 5;
  const minV  = Math.min(...vals);
  const maxV  = Math.max(...vals);
  const range = maxV - minV || 1;

  // Count values into bins
  const counts = new Array(BINS).fill(0);
  vals.forEach(v => {
    let i = Math.floor((v - minV) / range * BINS);
    if (i >= BINS) i = BINS - 1;
    counts[i]++;
  });
  const maxC = Math.max(...counts);

  // Drawing area with margins for axis labels
  const pad = { t: 6, b: 18, l: 36, r: 4 };
  const dW  = W - pad.l - pad.r;
  const dH  = H - pad.t - pad.b;
  const bw  = dW / BINS;

  ctx.font      = '9px system-ui, sans-serif';
  ctx.fillStyle = '#aaa';

  // Y-axis: gridlines and count labels at 0%, 50%, 100% of max
  [0, 0.5, 1].forEach(frac => {
    const y     = pad.t + dH - frac * dH;
    const label = frac === 0 ? '0' : Math.round(frac * maxC).toLocaleString();
    ctx.strokeStyle = '#e8e8e8';
    ctx.lineWidth   = 0.5;
    ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(pad.l + dW, y); ctx.stroke();
    ctx.textAlign    = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillStyle    = '#aaa';
    ctx.fillText(label, pad.l - 4, y);
  });

  // Bars, coloured by percentile rank of bin midpoint
  let cumulative = 0;
  counts.forEach((c, i) => {
    const tStart  = cumulative / vals.length;
    cumulative   += c;
    const tEnd    = cumulative / vals.length;
    const t       = (tStart + tEnd) / 2;
    const bh      = (c / maxC) * dH;
    ctx.fillStyle = rampColor(t);
    ctx.fillRect(pad.l + i * bw + 1, pad.t + dH - bh, bw - 2, bh);
  });

  // X-axis baseline
  ctx.strokeStyle = '#ccc';
  ctx.lineWidth   = 0.75;
  ctx.beginPath();
  ctx.moveTo(pad.l, pad.t + dH);
  ctx.lineTo(pad.l + dW, pad.t + dH);
  ctx.stroke();

  // X-axis tick labels: min, 25%, 50%, 75%, max
  ctx.textAlign    = 'center';
  ctx.textBaseline = 'top';
  ctx.fillStyle    = '#aaa';
  for (let ti = 0; ti < TICKS; ti++) {
    const frac  = ti / (TICKS - 1);
    const val   = minV + frac * range;
    const x     = pad.l + frac * dW;
    const label = Math.abs(val) >= 1e4 ? (val / 1e3).toFixed(0) + 'K'
                : Math.abs(val) < 10   ? (+val).toFixed(1)
                : Math.round(val).toString();
    ctx.fillText(label, x, pad.t + dH + 3);
  }
}


// ── Mode & scaling controls ───────────────────────────────────────────────────
/** Switch between 'missing' and 'values' display modes. */
function setMode(mode) {
  currentMode = mode;
  document.getElementById('btn-missing').classList.toggle('active', mode === 'missing');
  document.getElementById('btn-values').classList.toggle('active',  mode === 'values');
  document.getElementById('missing-panel').style.display = mode === 'missing' ? 'flex' : 'none';
  document.getElementById('values-panel').style.display  = mode === 'values'  ? 'flex' : 'none';
  render(document.getElementById('var-select').value);
}

/** Switch between 'percentile' and 'raw' colour scaling in values mode. */
function setScaling(s) {
  currentScaling = s;
  document.getElementById('btn-pct').classList.toggle('active', s === 'percentile');
  document.getElementById('btn-raw').classList.toggle('active', s === 'raw');
  render(document.getElementById('var-select').value);
}


// ── Render: missing mode ──────────────────────────────────────────────────────
/**
 * Draw a choropleth showing which buurten have missing data for `key`,
 * and update the sidebar statistics and tag list.
 */
function renderMissing(key, meta) {
  if (geojsonLayer) map.removeLayer(geojsonLayer);

  const features    = activeFeatures();
  const filteredGeo = { type: 'FeatureCollection', features };

  geojsonLayer = L.geoJSON(filteredGeo, {
    style: f => {
      const v = f.properties['missing_' + key];
      return {
        fillColor:   v === 1 ? '#e24b4a' : v === 0 ? '#639922' : '#cccccc',
        fillOpacity: 0.75,
        color:       '#fff',
        weight:      0.3,
      };
    },
    onEachFeature: (f, layer) => {
      const p      = f.properties;
      const status = p['missing_' + key] === 1 ? '⚠ Missing'
                   : p['missing_' + key] === 0 ? '✓ Present'
                   : 'Not matched';
      layer.bindTooltip(
        `<strong>${p.buurtnaam || p.buurtcode}</strong><br>${p.gemeentenaam || ''}<br>${status}`,
        { sticky: true }
      );
    },
  }).addTo(map);

  // Sidebar statistics
  const n_total   = features.length;
  const n_missing = features.filter(f => f.properties['missing_' + key] === 1).length;
  document.getElementById('stat-total').textContent   = n_total;
  document.getElementById('stat-missing').textContent = n_missing;
  document.getElementById('stat-pct').textContent     = n_total
    ? Math.round(n_missing / n_total * 100) + '%'
    : '—';

  // Tag list: buurten with missing data (capped at 80)
  const bad = features.filter(f => f.properties['missing_' + key] === 1);
  document.getElementById('missing-title').textContent = n_missing > 0
    ? `Buurten missing "${meta.label}" (${n_missing})`
    : 'No missing buurten';

  const tagsEl = document.getElementById('tags');
  tagsEl.innerHTML = '';
  bad.slice(0, 80).forEach(f => {
    const t = document.createElement('span');
    t.className   = 'tag';
    t.textContent = `${f.properties.gemeentenaam || ''} · ${f.properties.buurtnaam || f.properties.buurtcode}`;
    tagsEl.appendChild(t);
  });
  if (bad.length > 80) {
    const t = document.createElement('span');
    t.className   = 'tag more';
    t.textContent = `+${bad.length - 80} more`;
    tagsEl.appendChild(t);
  }
}


// ── Render: values mode ───────────────────────────────────────────────────────
/**
 * Draw a heatmap choropleth for `key` using the current colour-scaling mode,
 * and update the summary statistics panel, legend, and histogram.
 */
function renderValues(key, meta) {
  if (geojsonLayer) map.removeLayer(geojsonLayer);

  const vals = getVals(key);
  if (!vals.length) return;

  const minV  = Math.min(...vals);
  const maxV  = Math.max(...vals);
  const range = maxV - minV || 1;

  // Build a percentile-rank lookup for this variable + filter combination
  const sorted = [...vals].sort((a, b) => a - b);
  function percentileRank(v) {
    let lo = 0, hi = sorted.length - 1;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (sorted[mid] < v) lo = mid + 1; else hi = mid;
    }
    return sorted.length === 1 ? 0.5 : lo / (sorted.length - 1);
  }

  function colorFor(v) {
    return currentScaling === 'percentile'
      ? rampColor(percentileRank(v))
      : rampColor((v - minV) / range);
  }

  const filteredGeo = { type: 'FeatureCollection', features: activeFeatures() };

  geojsonLayer = L.geoJSON(filteredGeo, {
    style: f => {
      const v = f.properties['val_' + key];
      if (v === null || v === undefined || !isFinite(v))
        return { fillColor: '#cccccc', fillOpacity: 0.55, color: '#fff', weight: 0.3 };
      return { fillColor: colorFor(v), fillOpacity: 0.82, color: '#fff', weight: 0.3 };
    },
    onEachFeature: (f, layer) => {
      const p   = f.properties;
      const v   = p['val_' + key];
      const str = (v !== null && v !== undefined && isFinite(v)) ? fmt(v) : 'No data';
      layer.bindTooltip(
        `<strong>${p.buurtnaam || p.buurtcode}</strong><br>${p.gemeentenaam || ''}<br>${meta.label}: <strong>${str}</strong>`,
        { sticky: true }
      );
    },
  }).addTo(map);

  // Summary statistics
  document.getElementById('val-min').textContent    = fmt(minV);
  document.getElementById('val-median').textContent = fmt(median(vals));
  document.getElementById('val-mean').textContent   = fmt(mean(vals));
  document.getElementById('val-max').textContent    = fmt(maxV);

  // Legend labels
  if (currentScaling === 'percentile') {
    document.getElementById('leg-min').textContent = '0th pct';
    document.getElementById('leg-mid').textContent = '50th pct';
    document.getElementById('leg-max').textContent = '100th pct';
  } else {
    document.getElementById('leg-min').textContent = fmt(minV);
    document.getElementById('leg-mid').textContent = fmt((minV + maxV) / 2);
    document.getElementById('leg-max').textContent = fmt(maxV);
  }

  // Defer histogram to next animation frame so the map renders first
  requestAnimationFrame(() => drawHist(key));
}


// ── Main render dispatcher ────────────────────────────────────────────────────
function render(key) {
  const meta = VARS.find(v => v.key === key);
  if (!meta) return;
  currentMode === 'missing' ? renderMissing(key, meta) : renderValues(key, meta);
}


// ── Boot: populate dropdowns and draw initial map ─────────────────────────────
(function boot() {
  // Gemeente dropdown
  const gemSel  = document.getElementById('gem-select');
  const gemeenten = [...new Set(
    GEO.features.map(f => f.properties.gemeentenaam).filter(Boolean)
  )].sort();

  const allOpt = document.createElement('option');
  allOpt.value = ''; allOpt.textContent = 'All of the Netherlands';
  gemSel.appendChild(allOpt);
  gemeenten.forEach(g => {
    const o = document.createElement('option');
    o.value = g; o.textContent = g;
    gemSel.appendChild(o);
  });
  gemSel.addEventListener('change', () => setGemeente(gemSel.value));

  // Variable dropdown
  const varSel = document.getElementById('var-select');
  VARS.forEach(v => {
    const o = document.createElement('option');
    o.value = v.key; o.textContent = v.label;
    varSel.appendChild(o);
  });
  varSel.addEventListener('change', () => render(varSel.value));

  render(varSel.value);
})();
"""


# ── Public function ───────────────────────────────────────────────────────────

def render_html(geo_json: dict, var_meta: list[dict]) -> str:
    """
    Render the complete self-contained HTML dashboard string.

    Parameters
    ----------
    geo_json  : dict   GeoJSON FeatureCollection (from geo_builder.build_geojson)
    var_meta  : list   Variable metadata list (from geo_builder.build_geojson)

    Returns
    -------
    str  Full HTML document, ready to write to disk.
    """
    geo_json_str = json.dumps(geo_json)
    var_meta_str = json.dumps(var_meta)

    js_block = _JS.replace("{geo_json_str}", geo_json_str) \
                  .replace("{var_meta_str}", var_meta_str)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Buurt data explorer — CBS 2022</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
{_CSS}
</style>
</head>
<body>
{_HTML_BODY}
<script>
{js_block}
</script>
</body>
</html>"""
