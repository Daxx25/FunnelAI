"""
ai_insights.py — Rule-based AI insights engine (no API key required)
"""
import pandas as pd
from modules.metrics import (
    get_funnel_counts,
    get_conversion_rates,
    get_monthly_revenue,
    get_rep_performance,
    get_avg_velocity,
    get_overall_conversion,
)

# Sentiment tags
POSITIVE = "🟢"
NEGATIVE = "🔴"
NEUTRAL  = "🟡"


def _fmt_currency(val: float) -> str:
    if val >= 1_000_000:
        return f"${val/1_000_000:.1f}M"
    if val >= 1_000:
        return f"${val/1_000:.0f}K"
    return f"${val:,.0f}"


def generate_insights(df: pd.DataFrame) -> list[dict]:
    """
    Analyse the DataFrame and return a list of insight dicts:
      { "icon": str, "sentiment": str, "text": str }
    """
    insights = []

    funnel_df, lost_count = get_funnel_counts(df)
    conv_df = get_conversion_rates(funnel_df)
    monthly_rev = get_monthly_revenue(df)
    rep_df = get_rep_performance(df)
    overall_conv = get_overall_conversion(df)
    avg_velocity = get_avg_velocity(df)

    # ── 1. Overall conversion ─────────────────────────────────────────────────
    sentiment = POSITIVE if overall_conv >= 20 else NEGATIVE
    label = "strong" if overall_conv >= 20 else "low"
    insights.append({
        "icon": "🎯",
        "sentiment": sentiment,
        "text": f"Overall Lead → Closed Won conversion is **{overall_conv}%** — {label} relative to the 20% industry benchmark.",
    })

    # ── 2. Worst conversion bottleneck ────────────────────────────────────────
    if not conv_df.empty:
        worst = conv_df.loc[conv_df["rate_pct"].idxmin()]
        sentiment = NEGATIVE if worst["rate_pct"] < 40 else NEUTRAL
        insights.append({
            "icon": "⚠️",
            "sentiment": sentiment,
            "text": (
                f"Biggest pipeline bottleneck: **{worst['from_stage']} → {worst['to_stage']}** "
                f"at only **{worst['rate_pct']}%** conversion. Focus here for the highest impact."
            ),
        })

    # ── 3. Best conversion stage ──────────────────────────────────────────────
    if not conv_df.empty:
        best = conv_df.loc[conv_df["rate_pct"].idxmax()]
        insights.append({
            "icon": "✅",
            "sentiment": POSITIVE,
            "text": (
                f"Strongest stage: **{best['from_stage']} → {best['to_stage']}** "
                f"converts at **{best['rate_pct']}%** — a clear strength in your pipeline."
            ),
        })

    # ── 4. Top rep ────────────────────────────────────────────────────────────
    if not rep_df.empty:
        top = rep_df.iloc[0]
        insights.append({
            "icon": "🏆",
            "sentiment": POSITIVE,
            "text": (
                f"Top performer: **{top['owner']}** drives **{top['revenue_share_pct']}%** "
                f"of total Closed Won revenue — {_fmt_currency(top['total_revenue'])} across {int(top['deals'])} deals."
            ),
        })

    # ── 5. MoM revenue trend ──────────────────────────────────────────────────
    if len(monthly_rev) >= 2:
        last_month = monthly_rev.iloc[-1]
        mom = last_month["mom_growth_pct"]
        if pd.notna(mom):
            direction = "grew" if mom >= 0 else "dropped"
            sentiment = POSITIVE if mom >= 0 else NEGATIVE
            insights.append({
                "icon": "📈" if mom >= 0 else "📉",
                "sentiment": sentiment,
                "text": (
                    f"Monthly revenue **{direction} {abs(mom):.1f}%** in the most recent period "
                    f"({last_month['month_str']}): {_fmt_currency(last_month['revenue'])}."
                ),
            })

    # ── 6. Deal velocity ──────────────────────────────────────────────────────
    if avg_velocity > 0:
        sentiment = NEGATIVE if avg_velocity > 60 else NEUTRAL if avg_velocity > 30 else POSITIVE
        label = "long" if avg_velocity > 60 else "moderate" if avg_velocity > 30 else "short"
        insights.append({
            "icon": "⏱️",
            "sentiment": sentiment,
            "text": (
                f"Average deal cycle is **{avg_velocity} days** — a {label} sales cycle. "
                + ("Consider tightening follow-up cadence." if avg_velocity > 45 else "Good momentum in closing.")
            ),
        })

    # ── 7. Closed Lost rate ───────────────────────────────────────────────────
    total = len(df)
    if total > 0 and lost_count > 0:
        lost_rate = round(lost_count / total * 100, 1)
        sentiment = NEGATIVE if lost_rate > 25 else NEUTRAL
        insights.append({
            "icon": "🚨",
            "sentiment": sentiment,
            "text": (
                f"**{lost_count} deals ({lost_rate}%)** are Closed Lost. "
                + ("High churn — investigate objection patterns." if lost_rate > 25 else "Within acceptable range.")
            ),
        })

    # ── 8. Rep diversity ─────────────────────────────────────────────────────
    if not rep_df.empty and len(rep_df) > 1:
        top_share = rep_df.iloc[0]["revenue_share_pct"]
        if top_share > 50:
            insights.append({
                "icon": "⚡",
                "sentiment": NEGATIVE,
                "text": (
                    f"Revenue concentration risk: **{rep_df.iloc[0]['owner']}** holds "
                    f"**{top_share}%** of all revenue. Diversify rep contributions to reduce key-person dependency."
                ),
            })

    return insights[:8]  # Cap at 8 insights
