"""
geo_builder.py
──────────────
Merge CBS attribute data onto buurt geometries and export a GeoJSON payload
suitable for embedding in the self-contained dashboard HTML.

The exported GeoJSON feature properties follow a prefixed naming convention:
  - val_<key>     : the raw CBS value for a variable
  - missing_<key> : 1 if the value is NaN for that buurt, else 0

This makes the JavaScript side trivial: it can read either prefix without
knowing anything about the column schema.
"""

import json

import geopandas as gpd
import pandas as pd

from variables import DASHBOARD_VARIABLES


def build_geojson(
    df: pd.DataFrame,
    gpkg_path: str,
) -> tuple[dict, list[dict]]:
    """
    Merge CBS data onto buurt geometries and return a GeoJSON dict plus
    variable metadata list ready for JSON serialisation.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned CBS dataframe (output of etl.load_cbs_csv).
    gpkg_path : str
        Path to the buurt/gemeente GeoPackage (WGS84 or any CRS; will be
        re-projected to EPSG:4326 automatically).

    Returns
    -------
    geo_json : dict
        GeoJSON FeatureCollection with val_* and missing_* properties.
    var_meta : list[dict]
        List of {key, label, n_missing, n_total} dicts, one per variable.
    """
    gdf = _load_geometries(gpkg_path)
    merged = _merge_attributes(gdf, df)
    merged = _add_missing_flags(merged)
    merged = merged.to_crs(epsg=4326)

    geo_json = _serialise_geojson(merged)
    var_meta = _build_var_meta(merged)

    return geo_json, var_meta


# ── Private helpers ───────────────────────────────────────────────────────────

def _load_geometries(gpkg_path: str) -> gpd.GeoDataFrame:
    """Load buurt geometries and normalise string columns."""
    gdf = gpd.read_file(gpkg_path)
    for col in ("buurtcode", "buurtnaam", "gemeentenaam"):
        if col in gdf.columns:
            gdf[col] = gdf[col].astype(str).str.strip()
    print(f"Loaded {len(gdf):,} buurten from {gpkg_path}")
    return gdf


def _merge_attributes(gdf: gpd.GeoDataFrame, df: pd.DataFrame) -> gpd.GeoDataFrame:
    """Left-join CBS attributes onto the geometry layer by buurt code."""
    df = df.copy()
    df["neighbourhood_code"] = df["neighbourhood_code"].astype(str).str.strip()

    value_cols = [col for col, _ in DASHBOARD_VARIABLES if col in df.columns]
    subset = df[["neighbourhood_code"] + value_cols]

    merged = gdf.merge(
        subset,
        left_on="buurtcode",
        right_on="neighbourhood_code",
        how="left",
    )
    print(f"Merged: {len(merged):,} features ({len(merged) - len(gdf):+d} vs geometry layer)")
    return merged


def _add_missing_flags(merged: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Add a binary missing_<key> flag column for each dashboard variable."""
    for col, _ in DASHBOARD_VARIABLES:
        if col in merged.columns:
            merged[f"missing_{col}"] = merged[col].isna().astype(int)
    return merged


def _serialise_geojson(merged: gpd.GeoDataFrame) -> dict:
    """
    Serialise to a GeoJSON dict, keeping only the columns the dashboard needs.
    Value columns are prefixed with 'val_' so the JS can distinguish them from
    the missing flags.
    """
    value_cols   = [col for col, _ in DASHBOARD_VARIABLES if col in merged.columns]
    missing_cols = [f"missing_{col}" for col, _ in DASHBOARD_VARIABLES if f"missing_{col}" in merged.columns]
    extra_cols   = [c for c in ("gemeentenaam",) if c in merged.columns]

    keep = ["buurtcode", "buurtnaam", "geometry"] + extra_cols + missing_cols + value_cols

    export = (
        merged[keep]
        .rename(columns={col: f"val_{col}" for col in value_cols})
    )
    return json.loads(export.to_json())


def _build_var_meta(merged: gpd.GeoDataFrame) -> list[dict]:
    """Build the variable metadata list consumed by the dashboard sidebar."""
    return [
        {
            "key":       col,
            "label":     label,
            "n_missing": int(merged[f"missing_{col}"].sum()) if f"missing_{col}" in merged.columns else 0,
            "n_total":   len(merged),
        }
        for col, label in DASHBOARD_VARIABLES
        if f"missing_{col}" in merged.columns
    ]
