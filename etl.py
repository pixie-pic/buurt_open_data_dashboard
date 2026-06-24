"""
etl.py
──────
Load and clean the CBS 2022 kerncijfers buurten CSV.

Responsibilities:
  - Replace CBS missing-data markers (".") with NaN
  - Coerce all non-identifier columns to numeric
  - Rename Dutch column names to English equivalents (via column_map)

Returns a single cleaned pandas DataFrame ready for merging with geometries.
"""

import pandas as pd
import numpy as np

from column_map import COLUMN_TRANSLATIONS, ID_COLUMNS


def load_cbs_csv(path: str) -> pd.DataFrame:
    """
    Load the CBS buurten CSV, clean missing values, and rename columns.

    Parameters
    ----------
    path : str
        Path to the raw CBS kerncijfers buurten CSV file.

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe with English column names.
    """
    df = pd.read_csv(path, low_memory=False)

    df = _replace_missing_markers(df)
    df = _coerce_numeric(df)
    df = _rename_columns(df)

    return df


# ── Private helpers ───────────────────────────────────────────────────────────

def _replace_missing_markers(df: pd.DataFrame) -> pd.DataFrame:
    """Replace the CBS sentinel value '.' with NaN throughout the dataframe."""
    return df.replace(".", np.nan)


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cast all non-identifier columns to numeric, coercing unparseable
    values to NaN rather than raising.
    """
    for col in df.columns:
        if col not in ID_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the Dutch → English column name mapping (skipping absent columns)."""
    rename_map = {k: v for k, v in COLUMN_TRANSLATIONS.items() if k in df.columns}
    return df.rename(columns=rename_map)
