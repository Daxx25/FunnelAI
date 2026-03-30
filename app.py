"""
app.py — AI Sales Dashboard
Run with: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import os

from modules.data_loader import load_csv
from modules.metrics import (
    get_funnel_counts,
    get_conversion_rates,
    get_monthly_revenue,
    get_rep_performance,
    get_summary_kpis,
    get_overall_conversion,
)
from modules.charts import (
    funnel_chart,
    conversion_bar,
    revenue_trend,
    cumulative_revenue_chart,
    rep_revenue_bar,
    rep_deals_bar,
)
from modules.ai_insights import generate_insights

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS — dark glassmorphism theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0F0C29 0%, #1a1040 50%, #0F0C29 100%);
    color: #E2E8F0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(15, 12, 41, 0.85);
    border-right: 1px solid rgba(124, 58, 237, 0.25);
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] .stMarkdown h2 {
    color: #A855F7;
}

/* ── KPI Cards ── */
.kpi-card {
    background: rgba(124, 58, 237, 0.12);
    border: 1px solid rgba(124, 58, 237, 0.3);
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(124, 58, 237, 0.25);
}
.kpi-label {
    font-size: 0.78rem;
    font-weight: 500;
    color: #94A3B8;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.1;
}
.kpi-sub {
    font-size: 0.75rem;
    color: #64748B;
    margin-top: 6px;
}

/* ── Section headers ── */
.section-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0;
    letter-spacing: -0.01em;
}
.section-subtitle {
    font-size: 0.85rem;
    color: #64748B;
    margin-top: 2px;
}
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 0 16px;
    border-bottom: 1px solid rgba(124,58,237,0.2);
    margin-bottom: 20px;
}
.section-icon {
    font-size: 1.4rem;
}

/* ── Chart containers ── */
.chart-box {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 16px;
    backdrop-filter: blur(8px);
}

/* ── Insight cards ── */
.insight-card {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 12px;
    transition: background 0.2s ease;
}
.insight-card:hover {
    background: rgba(124, 58, 237, 0.1);
    border-color: rgba(124, 58, 237, 0.3);
}
.insight-icon {
    font-size: 1.5rem;
    flex-shrink: 0;
    margin-top: 2px;
}
.insight-text {
    font-size: 0.9rem;
    color: #CBD5E1;
    line-height: 1.55;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(124,58,237,0.4), transparent);
    margin: 32px 0;
}

/* ── Hero ── */
.hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7C3AED, #A855F7, #EC4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    letter-spacing: -0.03em;
}
.hero-sub {
    font-size: 1.15rem;
    color: #94A3B8;
    margin-top: 12px;
    line-height: 1.6;
}

/* ── Template box ── */
.template-box {
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 12px;
    padding: 16px 20px;
    font-family: monospace;
    font-size: 0.82rem;
    color: #A5B4FC;
    line-height: 1.8;
}

/* ── Tags ── */
.tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-right: 6px;
}
.tag-green  { background: rgba(52,211,153,0.15); color: #34D399; border: 1px solid rgba(52,211,153,0.3); }
.tag-red    { background: rgba(248,113,113,0.15); color: #F87171; border: 1px solid rgba(248,113,113,0.3); }
.tag-yellow { background: rgba(250,204,21,0.15);  color: #FACC15; border: 1px solid rgba(250,204,21,0.3); }

/* ── Metric delta overrides ── */
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.4); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def kpi_card(label: str, value: str, sub: str = "") -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {'<div class="kpi-sub">' + sub + '</div>' if sub else ''}
    </div>
    """

def section_header(icon: str, title: str, subtitle: str = "") -> str:
    return f"""
    <div class="section-header">
        <span class="section-icon">{icon}</span>
        <div>
            <div class="section-title">{title}</div>
            {'<div class="section-subtitle">' + subtitle + '</div>' if subtitle else ''}
        </div>
    </div>
    """

def insight_html(icon: str, sentiment: str, text: str) -> str:
    tag_map = {"🟢": ("tag-green", "POSITIVE"), "🔴": ("tag-red", "ALERT"), "🟡": ("tag-yellow", "NEUTRAL")}
    cls, label = tag_map.get(sentiment, ("tag-yellow", "INFO"))
    return f"""
    <div class="insight-card">
        <div class="insight-icon">{icon}</div>
        <div style="flex:1">
            <span class="tag {cls}">{label}</span>
            <div class="insight-text" style="margin-top:6px">{text}</div>
        </div>
    </div>
    """

def fmt_currency(val: float) -> str:
    if val >= 1_000_000:
        return f"${val/1_000_000:.1f}M"
    if val >= 1_000:
        return f"${val/1_000:.0f}K"
    return f"${val:,.0f}"

def divider():
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 AI Sales Dashboard")
    st.markdown("---")
    st.markdown("**Upload your CSV** or load sample data to begin.")
    st.markdown("")

    uploaded = st.file_uploader(
        "Upload CRM CSV",
        type=["csv"],
        help="Must contain: lead_id, company, stage, revenue, owner, created_date, close_date",
    )

    st.markdown("")
    use_sample = st.button("🧪 Load Sample Data", use_container_width=True)

    st.markdown("---")
    st.markdown("**Required columns:**")
    st.markdown("""
- `lead_id`
- `company`
- `stage`
- `revenue`
- `owner`
- `created_date`
- `close_date`
    """)

    st.markdown("**Supported stages:**")
    for s in ["Lead", "MQL", "SQL", "Demo", "Closed Won", "Closed Lost"]:
        st.markdown(f"• `{s}`")

    st.markdown("---")
    st.caption("Built with Streamlit + Plotly · Offline AI Insights")


# ─────────────────────────────────────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────────────────────────────────────
df = None
warnings = []

if use_sample:
    sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "sample_leads.csv")
    df, warnings = load_csv(sample_path)
    if df is not None:
        st.session_state["df"] = df
        st.session_state["source"] = "Sample Data"

if uploaded is not None:
    df, warnings = load_csv(uploaded)
    if df is not None:
        st.session_state["df"] = df
        st.session_state["source"] = uploaded.name

# Retrieve from session state
if "df" in st.session_state:
    df = st.session_state["df"]

for w in warnings:
    st.warning(w)

# ─────────────────────────────────────────────────────────────────────────────
# Hero / Landing screen
# ─────────────────────────────────────────────────────────────────────────────
if df is None:
    st.markdown("")
    col1, col2 = st.columns([1.4, 1])

    with col1:
        st.markdown("""
        <div class="hero-title">AI-Powered<br>Sales Dashboard</div>
        <div class="hero-sub">
            Drop in your CRM CSV to instantly generate a full RevOps dashboard —<br>
            pipeline funnel, conversion rates, revenue trends &amp; AI insights.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        st.info("👈 Upload your CSV in the sidebar, or click **Load Sample Data** to see a live demo.")

        st.markdown("")
        st.markdown("**Your CSV must follow this template:**")
        st.markdown("""
        <div class="template-box">
            lead_id &nbsp;|&nbsp; company &nbsp;|&nbsp; stage &nbsp;|&nbsp; revenue &nbsp;|&nbsp; owner &nbsp;|&nbsp; created_date &nbsp;|&nbsp; close_date<br>
            L001 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp; Acme Corp &nbsp;|&nbsp; Closed Won &nbsp;|&nbsp; 45000 &nbsp;|&nbsp; Sarah &nbsp;|&nbsp; 2025-09-01 &nbsp;|&nbsp; 2025-10-15<br>
            L002 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp; BrightPath &nbsp;|&nbsp; Demo &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp; 28000 &nbsp;|&nbsp; John &nbsp;&nbsp;|&nbsp; 2025-09-07 &nbsp;|&nbsp;
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("")
        st.markdown("""
        <div style="background: rgba(124,58,237,0.1); border: 1px solid rgba(124,58,237,0.3); border-radius: 20px; padding: 28px;">
            <div style="font-size:1rem; font-weight:600; color:#A855F7; margin-bottom:16px">📋 Dashboard Sections</div>
            <div style="display:flex; flex-direction:column; gap:12px">
                <div style="display:flex; gap:12px; align-items:center; color:#CBD5E1; font-size:0.9rem">
                    <span style="font-size:1.4rem">🔻</span> <div><b>Pipeline Funnel</b><br><span style="color:#64748B; font-size:0.8rem">Visual lead progression</span></div>
                </div>
                <div style="display:flex; gap:12px; align-items:center; color:#CBD5E1; font-size:0.9rem">
                    <span style="font-size:1.4rem">📊</span> <div><b>Conversion Rates</b><br><span style="color:#64748B; font-size:0.8rem">Stage-to-stage & overall %</span></div>
                </div>
                <div style="display:flex; gap:12px; align-items:center; color:#CBD5E1; font-size:0.9rem">
                    <span style="font-size:1.4rem">📈</span> <div><b>Revenue Trends</b><br><span style="color:#64748B; font-size:0.8rem">Monthly & cumulative charts</span></div>
                </div>
                <div style="display:flex; gap:12px; align-items:center; color:#CBD5E1; font-size:0.9rem">
                    <span style="font-size:1.4rem">🤖</span> <div><b>AI Insights</b><br><span style="color:#64748B; font-size:0.8rem">8 auto-generated findings</span></div>
                </div>
                <div style="display:flex; gap:12px; align-items:center; color:#CBD5E1; font-size:0.9rem">
                    <span style="font-size:1.4rem">🏆</span> <div><b>Rep Performance</b><br><span style="color:#64748B; font-size:0.8rem">Revenue & deal leaderboard</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# Compute all metrics
# ─────────────────────────────────────────────────────────────────────────────
funnel_df, lost_count   = get_funnel_counts(df)
conv_df                 = get_conversion_rates(funnel_df)
monthly_rev             = get_monthly_revenue(df)
rep_df                  = get_rep_performance(df)
kpis                    = get_summary_kpis(df)
overall_conv            = get_overall_conversion(df)
insights                = generate_insights(df)


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard Header
# ─────────────────────────────────────────────────────────────────────────────
src = st.session_state.get("source", "Uploaded Data")
st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:space-between; padding:8px 0 4px">
    <div>
        <div style="font-size:1.8rem; font-weight:800; background:linear-gradient(135deg,#7C3AED,#A855F7,#EC4899);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
            📊 Sales Dashboard
        </div>
        <div style="font-size:0.85rem; color:#64748B; margin-top:2px">
            Source: <span style="color:#A855F7">{src}</span> &nbsp;·&nbsp; {len(df):,} records loaded
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

divider()


# ─────────────────────────────────────────────────────────────────────────────
# KPI Row
# ─────────────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
kpi_data = [
    (c1, "Total Revenue", fmt_currency(kpis["total_revenue"]), "Closed Won"),
    (c2, "Total Deals", f"{kpis['total_deals']:,}", "All stages"),
    (c3, "Closed Won", f"{kpis['closed_won']}", "Deals"),
    (c4, "Win Rate", f"{kpis['win_rate']}%", "Won / (Won+Lost)"),
    (c5, "Avg Deal Size", fmt_currency(kpis["avg_deal_size"]), "Closed Won"),
    (c6, "Avg Velocity", f"{kpis['avg_velocity']}d", "Days to close"),
]
for col, label, value, sub in kpi_data:
    with col:
        st.markdown(kpi_card(label, value, sub), unsafe_allow_html=True)


divider()


# ─────────────────────────────────────────────────────────────────────────────
# Section 1: Pipeline Funnel
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("🔻", "Pipeline Funnel", "Deal counts across each stage"), unsafe_allow_html=True)

col_funnel, col_stage_table = st.columns([1.6, 1])

with col_funnel:
    st.plotly_chart(funnel_chart(funnel_df), use_container_width=True, config={"displayModeBar": False})

with col_stage_table:
    st.markdown("")
    st.markdown("**Stage Breakdown**")
    all_stages = funnel_df.copy()
    # Add Closed Lost row
    all_stages = pd.concat([
        all_stages,
        pd.DataFrame([{"stage": "Closed Lost", "count": lost_count}])
    ], ignore_index=True)
    total = all_stages["count"].sum()
    all_stages["share_pct"] = (all_stages["count"] / total * 100).round(1).astype(str) + "%"
    st.dataframe(
        all_stages.rename(columns={"stage": "Stage", "count": "Count", "share_pct": "Share"}),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(f"""
    <div style="background:rgba(124,58,237,0.1); border-radius:10px; padding:12px 16px; margin-top:10px;
         border:1px solid rgba(124,58,237,0.25);">
        <div style="font-size:0.8rem; color:#94A3B8; margin-bottom:4px">OVERALL CONVERSION</div>
        <div style="font-size:2rem; font-weight:700; color:#fff">{overall_conv}%</div>
        <div style="font-size:0.75rem; color:#64748B">Lead → Closed Won</div>
    </div>
    """, unsafe_allow_html=True)


divider()


# ─────────────────────────────────────────────────────────────────────────────
# Section 2: Conversion Rates
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("📊", "Conversion Rates", "Stage-to-stage and overall conversion %"), unsafe_allow_html=True)

col_bar, col_tbl = st.columns([1.6, 1])

with col_bar:
    if not conv_df.empty:
        st.plotly_chart(conversion_bar(conv_df), use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Not enough stage data to compute conversion rates.")

with col_tbl:
    if not conv_df.empty:
        st.markdown("**Conversion Table**")
        display_conv = conv_df.copy()
        display_conv["Transition"] = display_conv.apply(
            lambda r: f"{r['from_stage']} → {r['to_stage']}", axis=1
        )
        display_conv = display_conv[["Transition", "rate_pct"]].rename(columns={"rate_pct": "Rate %"})
        st.dataframe(display_conv, use_container_width=True, hide_index=True)

        # Colour legend
        st.markdown("""
        <div style="margin-top:12px; font-size:0.8rem; color:#64748B">
            <span style="color:#34D399">■</span> ≥50% &nbsp;
            <span style="color:#FACC15">■</span> 30–49% &nbsp;
            <span style="color:#F87171">■</span> &lt;30%
        </div>
        """, unsafe_allow_html=True)


divider()


# ─────────────────────────────────────────────────────────────────────────────
# Section 3: Revenue Trends
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("📈", "Revenue Trends", "Monthly Closed Won revenue and cumulative growth"), unsafe_allow_html=True)

if monthly_rev.empty:
    st.info("No Closed Won deals with valid close dates found.")
else:
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.plotly_chart(revenue_trend(monthly_rev), use_container_width=True, config={"displayModeBar": False})
    with col_r2:
        st.plotly_chart(cumulative_revenue_chart(monthly_rev), use_container_width=True, config={"displayModeBar": False})

    # Monthly table
    with st.expander("📋 Monthly Revenue Breakdown", expanded=False):
        tbl = monthly_rev[["month_str", "revenue", "mom_growth_pct"]].copy()
        tbl.columns = ["Month", "Revenue ($)", "MoM Growth (%)"]
        tbl["Revenue ($)"] = tbl["Revenue ($)"].apply(lambda x: f"${x:,.0f}")
        tbl["MoM Growth (%)"] = tbl["MoM Growth (%)"].apply(
            lambda x: f"+{x:.1f}%" if pd.notna(x) and x >= 0 else (f"{x:.1f}%" if pd.notna(x) else "—")
        )
        st.dataframe(tbl, use_container_width=True, hide_index=True)


divider()


# ─────────────────────────────────────────────────────────────────────────────
# Section 4: AI Insights
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("🤖", "AI Insights", "Auto-generated findings from your pipeline data"), unsafe_allow_html=True)

if insights:
    # Two-column layout for insights
    n = len(insights)
    mid = (n + 1) // 2
    left_insights  = insights[:mid]
    right_insights = insights[mid:]

    col_i1, col_i2 = st.columns(2)
    with col_i1:
        for ins in left_insights:
            import re
            text_html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", ins["text"])
            st.markdown(insight_html(ins["icon"], ins["sentiment"], text_html), unsafe_allow_html=True)
    with col_i2:
        for ins in right_insights:
            import re
            text_html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", ins["text"])
            st.markdown(insight_html(ins["icon"], ins["sentiment"], text_html), unsafe_allow_html=True)
else:
    st.info("Upload data with more variety to unlock AI insights.")


divider()


# ─────────────────────────────────────────────────────────────────────────────
# Section 5: Rep Performance
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(section_header("🏆", "Rep Performance", "Revenue and deal count breakdown by sales owner"), unsafe_allow_html=True)

if rep_df.empty:
    st.info("No Closed Won deals found for rep performance analysis.")
else:
    col_rv, col_dl = st.columns(2)
    with col_rv:
        st.plotly_chart(rep_revenue_bar(rep_df), use_container_width=True, config={"displayModeBar": False})
    with col_dl:
        st.plotly_chart(rep_deals_bar(rep_df), use_container_width=True, config={"displayModeBar": False})

    # Leaderboard table
    st.markdown("**Rep Leaderboard**")
    lb = rep_df.copy()
    lb["total_revenue"] = lb["total_revenue"].apply(lambda x: f"${x:,.0f}")
    lb["revenue_share_pct"] = lb["revenue_share_pct"].astype(str) + "%"
    lb.columns = ["Owner", "Total Revenue", "Deals", "Revenue Share"]
    lb.index = range(1, len(lb) + 1)
    st.dataframe(lb, use_container_width=True)


divider()


# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#334155; font-size:0.78rem; padding:8px 0 24px">
    AI Sales Dashboard &nbsp;·&nbsp; Built with Streamlit + Plotly &nbsp;·&nbsp; Fully offline · No API key required
</div>
""", unsafe_allow_html=True)
