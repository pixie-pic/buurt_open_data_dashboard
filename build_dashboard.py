"""
build_dashboard.py
──────────────────
Entry point for the Buurt data explorer build pipeline.

Usage
-----
    python build_dashboard.py

Configuration is read from the constants at the top of this file.
Output is a single self-contained HTML file that can be opened directly
in any browser — no local server required.

Pipeline steps
--------------
1. Load & clean CBS CSV           (etl.py)
2. Merge with buurt geometries    (geo_builder.py)
3. Render self-contained HTML     (html_template.py)
4. Write to output path
"""

import sys
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).parent / "data_processing"))

from etl import load_cbs_csv
from geo_builder import build_geojson
from html_template import render_html


# ── Configuration ─────────────────────────────────────────────────────────────

CBS_CSV_PATH   = "data/buurt_data_merged.csv"
GPKG_PATH      = "data/buurten_2022.gpkg"
OUTPUT_HTML    = "output/dashboard.html"


# ── Pipeline ──────────────────────────────────────────────────────────────────

def main() -> None:
    print("── Buurt data explorer build ──────────────────────────────")

    # Step 1: load and clean CBS tabular data
    print(f"\n[1/3] Loading CBS data from {CBS_CSV_PATH} …")
    df = load_cbs_csv(CBS_CSV_PATH)
    print(f"      {len(df):,} rows, {len(df.columns)} columns after cleaning")

    # Step 2: merge with geometries and build GeoJSON payload
    print(f"\n[2/3] Merging with geometries from {GPKG_PATH} …")
    geo_json, var_meta = build_geojson(df, GPKG_PATH)
    print(f"      {len(geo_json['features']):,} features, {len(var_meta)} variables exported")

    # Step 3: render and write HTML
    print(f"\n[3/3] Rendering dashboard to {OUTPUT_HTML} …")
    Path(OUTPUT_HTML).parent.mkdir(parents=True, exist_ok=True)
    html = render_html(geo_json, var_meta)
    Path(OUTPUT_HTML).write_text(html, encoding="utf-8")

    size_mb = Path(OUTPUT_HTML).stat().st_size / 1_048_576
    print(f"\n✓  Done — {OUTPUT_HTML} ({size_mb:.1f} MB)")
    print("   Open in a browser to explore.\n")


if __name__ == "__main__":
    main()
