"""
metrics.py — All KPI and metric computations
"""
import pandas as pd

FUNNEL_STAGES = ["Lead", "MQL", "SQL", "Demo", "Closed Won"]


# ─────────────────────────────────────────────────────────────────────────────
# 1. Funnel counts
# ─────────────────────────────────────────────────────────────────────────────

def get_funnel_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Return count of deals per funnel stage (in order)."""
    counts = df["stage"].value_counts()
    result = []
    for stage in FUNNEL_STAGES:
        result.append({"stage": stage, "count": int(counts.get(stage, 0))})
    # Also grab Closed Lost separately
    lost = int(counts.get("Closed Lost", 0))
    return pd.DataFrame(result), lost


# ─────────────────────────────────────────────────────────────────────────────
# 2. Conversion rates
# ─────────────────────────────────────────────────────────────────────────────

def get_conversion_rates(funnel_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate stage-to-stage conversion percentages.
    Returns a DataFrame with columns: from_stage, to_stage, rate_pct
    """
    rows = []
    for i in range(len(funnel_df) - 1):
        from_count = funnel_df.iloc[i]["count"]
        to_count = funnel_df.iloc[i + 1]["count"]
        from_stage = funnel_df.iloc[i]["stage"]
        to_stage = funnel_df.iloc[i + 1]["stage"]
        rate = round((to_count / from_count * 100), 1) if from_count > 0 else 0.0
        rows.append({"from_stage": from_stage, "to_stage": to_stage, "rate_pct": rate})
    return pd.DataFrame(rows)


def get_overall_conversion(df: pd.DataFrame) -> float:
    """Lead → Closed Won overall conversion %."""
    total_leads = len(df)
    closed_won = len(df[df["stage"] == "Closed Won"])
    return round((closed_won / total_leads * 100), 1) if total_leads > 0 else 0.0


# ─────────────────────────────────────────────────────────────────────────────
# 3. Revenue trends
# ─────────────────────────────────────────────────────────────────────────────

def get_monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly Closed Won revenue, sorted by month."""
    won = df[df["stage"] == "Closed Won"].copy()
    won = won.dropna(subset=["close_date"])
    won["month"] = won["close_date"].dt.to_period("M")
    monthly = (
        won.groupby("month")["revenue"]
        .sum()
        .reset_index()
        .sort_values("month")
    )
    monthly["month_str"] = monthly["month"].astype(str)
    # MoM growth
    monthly["mom_growth_pct"] = monthly["revenue"].pct_change() * 100
    return monthly


def get_cumulative_revenue(monthly_df: pd.DataFrame) -> pd.DataFrame:
    """Cumulative closed revenue over time."""
    df = monthly_df.copy()
    df["cumulative"] = df["revenue"].cumsum()
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 4. Rep performance
# ─────────────────────────────────────────────────────────────────────────────

def get_rep_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue and deal count per owner for Closed Won deals."""
    won = df[df["stage"] == "Closed Won"]
    rep = (
        won.groupby("owner")
        .agg(total_revenue=("revenue", "sum"), deals=("lead_id", "count"))
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )
    total_rev = rep["total_revenue"].sum()
    rep["revenue_share_pct"] = round(rep["total_revenue"] / total_rev * 100, 1) if total_rev > 0 else 0
    return rep


# ─────────────────────────────────────────────────────────────────────────────
# 5. Velocity
# ─────────────────────────────────────────────────────────────────────────────

def get_avg_velocity(df: pd.DataFrame) -> float:
    """Average deal close time in days (closed deals only)."""
    closed = df[df["stage"].isin(["Closed Won", "Closed Lost"])].dropna(subset=["deal_days"])
    if closed.empty:
        return 0.0
    return round(closed["deal_days"].mean(), 1)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Summary KPIs
# ─────────────────────────────────────────────────────────────────────────────

def get_summary_kpis(df: pd.DataFrame) -> dict:
    total_revenue = df[df["stage"] == "Closed Won"]["revenue"].sum()
    total_deals = len(df)
    closed_won = len(df[df["stage"] == "Closed Won"])
    closed_lost = len(df[df["stage"] == "Closed Lost"])
    win_rate = round(closed_won / (closed_won + closed_lost) * 100, 1) if (closed_won + closed_lost) > 0 else 0
    avg_deal_size = round(total_revenue / closed_won, 0) if closed_won > 0 else 0
    return {
        "total_revenue": total_revenue,
        "total_deals": total_deals,
        "closed_won": closed_won,
        "win_rate": win_rate,
        "avg_deal_size": avg_deal_size,
        "avg_velocity": get_avg_velocity(df),
    }
