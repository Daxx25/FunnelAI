"""
charts.py — Plotly chart builders with consistent dark theme
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Design tokens ──────────────────────────────────────────────────────────────
PALETTE = ["#7C3AED", "#A855F7", "#EC4899", "#F97316", "#FACC15"]
BG        = "rgba(0,0,0,0)"      # transparent (Streamlit handles bg)
GRID_CLR  = "rgba(255,255,255,0.07)"
TEXT_CLR  = "#E2E8F0"
FONT      = "Inter, sans-serif"

BASE_LAYOUT = dict(
    paper_bgcolor=BG,
    plot_bgcolor=BG,
    font=dict(family=FONT, color=TEXT_CLR, size=13),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(
        bgcolor="rgba(255,255,255,0.05)",
        bordercolor="rgba(255,255,255,0.1)",
        borderwidth=1,
    ),
)


def _apply_base(fig: go.Figure) -> go.Figure:
    fig.update_layout(**BASE_LAYOUT)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 1. Pipeline Funnel
# ─────────────────────────────────────────────────────────────────────────────

def funnel_chart(funnel_df: pd.DataFrame) -> go.Figure:
    colors = ["#7C3AED", "#9333EA", "#A855F7", "#C084FC", "#34D399"]
    fig = go.Figure(go.Funnel(
        y=funnel_df["stage"],
        x=funnel_df["count"],
        textinfo="value+percent initial",
        marker=dict(color=colors, line=dict(width=1.5, color="rgba(255,255,255,0.15)")),
        connector=dict(line=dict(color="rgba(255,255,255,0.1)", width=1)),
        textfont=dict(family=FONT, size=14, color="#FFFFFF"),
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Pipeline Funnel", font=dict(size=16, color=TEXT_CLR)),
        height=380,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 2. Conversion rates bar
# ─────────────────────────────────────────────────────────────────────────────

def conversion_bar(conv_df: pd.DataFrame) -> go.Figure:
    labels = conv_df.apply(lambda r: f"{r['from_stage']} → {r['to_stage']}", axis=1)
    colors = [
        "#34D399" if r >= 50 else "#FACC15" if r >= 30 else "#F87171"
        for r in conv_df["rate_pct"]
    ]
    fig = go.Figure(go.Bar(
        x=conv_df["rate_pct"],
        y=labels,
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(width=0),
        ),
        text=[f"{v}%" for v in conv_df["rate_pct"]],
        textposition="outside",
        textfont=dict(color=TEXT_CLR, size=13),
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Stage-to-Stage Conversion Rates", font=dict(size=16, color=TEXT_CLR)),
        xaxis=dict(
            title="Conversion %",
            range=[0, 115],
            gridcolor=GRID_CLR,
            showgrid=True,
            ticksuffix="%",
        ),
        yaxis=dict(automargin=True, gridcolor=GRID_CLR),
        height=300,
        bargap=0.35,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 3. Monthly revenue trend
# ─────────────────────────────────────────────────────────────────────────────

def revenue_trend(monthly_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    # Area fill
    fig.add_trace(go.Scatter(
        x=monthly_df["month_str"],
        y=monthly_df["revenue"],
        fill="tozeroy",
        mode="lines+markers",
        line=dict(color="#7C3AED", width=2.5, shape="spline"),
        fillcolor="rgba(124,58,237,0.18)",
        marker=dict(size=7, color="#A855F7", line=dict(width=2, color="#7C3AED")),
        name="Monthly Revenue",
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Monthly Closed Won Revenue", font=dict(size=16, color=TEXT_CLR)),
        xaxis=dict(gridcolor=GRID_CLR, tickangle=-30),
        yaxis=dict(gridcolor=GRID_CLR, tickprefix="$", tickformat=",.0f"),
        height=350,
        showlegend=False,
    )
    return fig


def cumulative_revenue_chart(monthly_df: pd.DataFrame) -> go.Figure:
    monthly_df = monthly_df.copy()
    monthly_df["cumulative"] = monthly_df["revenue"].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_df["month_str"],
        y=monthly_df["cumulative"],
        fill="tozeroy",
        mode="lines+markers",
        line=dict(color="#EC4899", width=2.5, shape="spline"),
        fillcolor="rgba(236,72,153,0.15)",
        marker=dict(size=7, color="#F472B6", line=dict(width=2, color="#EC4899")),
        name="Cumulative Revenue",
        hovertemplate="<b>%{x}</b><br>Cumulative: $%{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Cumulative Revenue Over Time", font=dict(size=16, color=TEXT_CLR)),
        xaxis=dict(gridcolor=GRID_CLR, tickangle=-30),
        yaxis=dict(gridcolor=GRID_CLR, tickprefix="$", tickformat=",.0f"),
        height=350,
        showlegend=False,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 4. Rep performance
# ─────────────────────────────────────────────────────────────────────────────

def rep_revenue_bar(rep_df: pd.DataFrame) -> go.Figure:
    colors = ["#7C3AED", "#A855F7", "#EC4899", "#F97316", "#FACC15"]
    n = len(rep_df)
    bar_colors = [colors[i % len(colors)] for i in range(n)]

    fig = go.Figure(go.Bar(
        x=rep_df["owner"],
        y=rep_df["total_revenue"],
        marker=dict(color=bar_colors, line=dict(width=0)),
        text=[f"${v/1000:.0f}K<br>({p}%)" for v, p in zip(rep_df["total_revenue"], rep_df["revenue_share_pct"])],
        textposition="outside",
        textfont=dict(color=TEXT_CLR, size=12),
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Revenue by Sales Rep", font=dict(size=16, color=TEXT_CLR)),
        xaxis=dict(gridcolor=GRID_CLR),
        yaxis=dict(gridcolor=GRID_CLR, tickprefix="$", tickformat=",.0f"),
        height=330,
        bargap=0.3,
    )
    return fig


def rep_deals_bar(rep_df: pd.DataFrame) -> go.Figure:
    colors = ["#34D399", "#6EE7B7", "#10B981", "#059669", "#047857"]
    n = len(rep_df)
    bar_colors = [colors[i % len(colors)] for i in range(n)]
    sorted_df = rep_df.sort_values("deals", ascending=False)

    fig = go.Figure(go.Bar(
        x=sorted_df["owner"],
        y=sorted_df["deals"],
        marker=dict(color=bar_colors, line=dict(width=0)),
        text=sorted_df["deals"],
        textposition="outside",
        textfont=dict(color=TEXT_CLR, size=13),
        hovertemplate="<b>%{x}</b><br>Deals: %{y}<extra></extra>",
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Closed Won Deals by Rep", font=dict(size=16, color=TEXT_CLR)),
        xaxis=dict(gridcolor=GRID_CLR),
        yaxis=dict(gridcolor=GRID_CLR),
        height=330,
        bargap=0.3,
    )
    return fig
