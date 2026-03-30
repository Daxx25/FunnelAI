"""
data_loader.py — CSV ingestion and validation
"""
import pandas as pd
import streamlit as st

REQUIRED_COLUMNS = {"lead_id", "company", "stage", "revenue", "owner", "created_date", "close_date"}

STAGE_ORDER = ["Lead", "MQL", "SQL", "Demo", "Closed Won", "Closed Lost"]


def load_csv(file) -> tuple[pd.DataFrame | None, list[str]]:
    """
    Load and validate a CSV file.
    Returns (cleaned_df, list_of_warnings).
    """
    warnings = []

    try:
        df = pd.read_csv(file)
    except Exception as e:
        return None, [f"❌ Could not read file: {e}"]

    # Normalise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Check required columns
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        return None, [f"❌ Missing required columns: {', '.join(sorted(missing))}"]

    # ── Date columns ─────────────────────────────────────────────────────────
    for col in ("created_date", "close_date"):
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # ── Revenue ───────────────────────────────────────────────────────────────
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)

    # ── Stage normalisation ───────────────────────────────────────────────────
    df["stage"] = df["stage"].astype(str).str.strip()
    unknown_stages = set(df["stage"].unique()) - set(STAGE_ORDER)
    if unknown_stages:
        warnings.append(f"⚠️ Unknown stages found (kept as-is): {', '.join(sorted(unknown_stages))}")

    # ── Owner ─────────────────────────────────────────────────────────────────
    df["owner"] = df["owner"].astype(str).str.strip()

    # ── Add helper columns ────────────────────────────────────────────────────
    df["close_month"] = df["close_date"].dt.to_period("M")
    df["created_month"] = df["created_date"].dt.to_period("M")

    # Deal velocity (days)
    df["deal_days"] = (df["close_date"] - df["created_date"]).dt.days

    return df, warnings
