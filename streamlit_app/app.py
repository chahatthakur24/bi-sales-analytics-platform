# =============================================================================
# BUSINESS INTELLIGENCE & SALES ANALYTICS PLATFORM
# Streamlit Dashboard — 5 Pages
# Author: Chahat Thakur
# =============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os, warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BI & Sales Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background:#f8fafc; }
  [data-testid="stSidebar"]          { background:#1e293b; }
  [data-testid="stSidebar"] * { color:#e2e8f0 !important; }
  .kpi-card {
    background:white; border-radius:12px; padding:20px 24px;
    box-shadow:0 1px 3px rgba(0,0,0,0.08); border-left:4px solid #2563eb;
    margin-bottom:8px;
  }
  .kpi-label { font-size:12px; color:#64748b; text-transform:uppercase;
               letter-spacing:.08em; font-weight:600; margin-bottom:4px; }
  .kpi-value { font-size:26px; font-weight:700; color:#1e293b; line-height:1; }
  .kpi-delta { font-size:12px; margin-top:4px; }
  .kpi-delta.pos { color:#10b981; }
  .kpi-delta.neg { color:#ef4444; }
  .kpi-card.green { border-left-color:#10b981; }
  .kpi-card.red   { border-left-color:#ef4444; }
  .kpi-card.amber { border-left-color:#f59e0b; }
  .kpi-card.purple{ border-left-color:#8b5cf6; }
  .section-title {
    font-size:13px; font-weight:700; color:#64748b;
    text-transform:uppercase; letter-spacing:.1em;
    border-bottom:2px solid #e2e8f0; padding-bottom:6px; margin-bottom:16px;
  }
</style>
""", unsafe_allow_html=True)

# ── Data Loading ──────────────────────────────────────────────────────────────
ROOT = os.path.join(os.path.dirname(__file__), "..")

@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(
        os.path.join(ROOT, "data", "superstore.csv"),
        parse_dates=["order_date","ship_date"]
    )
    df["year"]           = df["order_date"].dt.year
    df["month"]          = df["order_date"].dt.month
    df["month_name"]     = df["order_date"].dt.strftime("%b")
    df["quarter"]        = df["order_date"].dt.quarter
    df["ym"]             = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["profit_margin"]  = df["profit"] / df["sales"] * 100
    df["ship_days"]      = (df["ship_date"] - df["order_date"]).dt.days
    return df

@st.cache_data(show_spinner=False)
def load_rfm():
    path = os.path.join(ROOT, "data", "rfm_scores.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

@st.cache_data(show_spinner=False)
def load_forecast():
    path = os.path.join(ROOT, "data", "revenue_forecast.csv")
    if os.path.exists(path):
        df = pd.read_csv(path, parse_dates=["month"])
        return df
    return None

df  = load_data()
rfm = load_rfm()
fct = load_forecast()

C = {"blue":"#2563eb","green":"#10b981","red":"#ef4444",
     "amber":"#f59e0b","purple":"#8b5cf6","gray":"#64748b"}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 BI Analytics")
    st.markdown("*Sales & Customer Intelligence*")
    st.divider()

    page = st.radio("Navigation", [
        "🏠 Executive Summary",
        "📈 Sales Performance",
        "👥 Customer Analytics",
        "📦 Product Intelligence",
        "🔮 Revenue Forecast"
    ], label_visibility="collapsed")

    st.divider()
    st.markdown("**Filters**")
    years = sorted(df["year"].unique())
    sel_years = st.multiselect("Year", years, default=years)
    regions   = sorted(df["region"].unique())
    sel_regions = st.multiselect("Region", regions, default=regions)
    segments  = sorted(df["segment"].unique())
    sel_segs  = st.multiselect("Segment", segments, default=segments)

    st.divider()
    st.caption("Built by [Chahat Thakur](https://github.com/chahatthakur24)")

# ── Filter ────────────────────────────────────────────────────────────────────
dff = df[
    df["year"].isin(sel_years) &
    df["region"].isin(sel_regions) &
    df["segment"].isin(sel_segs)
].copy()

def kpi(label, value, delta=None, color=""):
    delta_html = ""
    if delta is not None:
        cls = "pos" if delta >= 0 else "neg"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f'<div class="kpi-delta {cls}">{arrow} {abs(delta):.1f}% vs prev year</div>'
    return f"""
    <div class="kpi-card {color}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {delta_html}
    </div>"""

def plot_cfg(fig, height=380):
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font_color="#1e293b",
        margin=dict(t=40,b=20,l=10,r=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#f1f5f9", showgrid=True),
        yaxis=dict(gridcolor="#f1f5f9", showgrid=True)
    )
    return fig

# =============================================================================
# PAGE 1 — EXECUTIVE SUMMARY
# =============================================================================
if page == "🏠 Executive Summary":
    st.markdown("## 🏠 Executive Summary")
    st.caption(f"Showing {len(dff):,} orders across {', '.join(map(str,sel_years))}")

    # KPIs
    rev    = dff["sales"].sum()
    pft    = dff["profit"].sum()
    margin = pft/rev*100 if rev else 0
    orders = dff["order_id"].nunique()
    cust   = dff["customer_id"].nunique()
    aov    = rev/orders if orders else 0
    ret_rt = (dff["returned"]=="Yes").mean()*100

    # YoY delta (compare max year to previous)
    if len(sel_years) >= 2:
        yr_max  = max(sel_years)
        yr_prev = sorted(sel_years)[-2]
        rev_cur  = dff[dff["year"]==yr_max]["sales"].sum()
        rev_prev = dff[dff["year"]==yr_prev]["sales"].sum()
        pft_cur  = dff[dff["year"]==yr_max]["profit"].sum()
        pft_prev = dff[dff["year"]==yr_prev]["profit"].sum()
        rev_delta = (rev_cur-rev_prev)/rev_prev*100 if rev_prev else None
        pft_delta = (pft_cur-pft_prev)/pft_prev*100 if pft_prev else None
    else:
        rev_delta = pft_delta = None

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.markdown(kpi("Total Revenue",   f"₹{rev/1e6:.1f}M", rev_delta, ""),     unsafe_allow_html=True)
    c2.markdown(kpi("Total Profit",    f"₹{pft/1e6:.1f}M", pft_delta, "green"),unsafe_allow_html=True)
    c3.markdown(kpi("Profit Margin",   f"{margin:.1f}%",    None,       "amber"),unsafe_allow_html=True)
    c4.markdown(kpi("Total Orders",    f"{orders:,}",       None,       ""),    unsafe_allow_html=True)
    c5.markdown(kpi("Avg Order Value", f"₹{aov:,.0f}",      None,       "purple"),unsafe_allow_html=True)
    c6.markdown(kpi("Return Rate",     f"{ret_rt:.1f}%",    None,       "red"), unsafe_allow_html=True)

    st.markdown("---")
    left, right = st.columns([1.6, 1])

    with left:
        st.markdown('<div class="section-title">Monthly Revenue & Profit Trend</div>', unsafe_allow_html=True)
        monthly = dff.groupby("ym").agg(Revenue=("sales","sum"), Profit=("profit","sum")).reset_index()
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(x=monthly["ym"], y=monthly["Revenue"]/1e6,
                             name="Revenue", marker_color=C["blue"], opacity=0.8), secondary_y=False)
        fig.add_trace(go.Scatter(x=monthly["ym"], y=monthly["Profit"]/1e6,
                                 name="Profit", line=dict(color=C["green"],width=2),
                                 mode="lines+markers"), secondary_y=True)
        fig.update_yaxes(title_text="Revenue (₹M)", secondary_y=False)
        fig.update_yaxes(title_text="Profit (₹M)",  secondary_y=True)
        st.plotly_chart(plot_cfg(fig), use_container_width=True)

    with right:
        st.markdown('<div class="section-title">Revenue by Region</div>', unsafe_allow_html=True)
        reg = dff.groupby("region").agg(Revenue=("sales","sum")).reset_index().sort_values("Revenue")
        fig2 = go.Figure(go.Bar(
            x=reg["Revenue"]/1e6, y=reg["region"], orientation="h",
            marker_color=C["blue"], text=[f"₹{v/1e6:.1f}M" for v in reg["Revenue"]],
            textposition="outside"))
        st.plotly_chart(plot_cfg(fig2,300), use_container_width=True)

        st.markdown('<div class="section-title">Revenue by Segment</div>', unsafe_allow_html=True)
        seg = dff.groupby("segment")["sales"].sum().reset_index()
        fig3 = go.Figure(go.Pie(labels=seg["segment"], values=seg["sales"],
                                hole=0.5,
                                marker_colors=[C["blue"],C["green"],C["amber"]]))
        fig3.update_layout(height=220, paper_bgcolor="rgba(0,0,0,0)",
                           margin=dict(t=10,b=10,l=10,r=10),
                           showlegend=True, font_color="#1e293b")
        st.plotly_chart(fig3, use_container_width=True)

# =============================================================================
# PAGE 2 — SALES PERFORMANCE
# =============================================================================
elif page == "📈 Sales Performance":
    st.markdown("## 📈 Sales Performance")

    # Category performance
    st.markdown('<div class="section-title">Category Performance</div>', unsafe_allow_html=True)
    cat = dff.groupby("category").agg(
        Revenue=("sales","sum"), Profit=("profit","sum"), Orders=("order_id","count")
    ).reset_index()
    cat["Margin"] = cat["Profit"]/cat["Revenue"]*100

    c1,c2,c3 = st.columns(3)
    for col, metric, title, color in [
        (c1,"Revenue","Revenue by Category (₹M)",C["blue"]),
        (c2,"Profit","Profit by Category (₹M)",C["green"]),
        (c3,"Margin","Profit Margin % by Category",C["amber"])
    ]:
        with col:
            vals = cat[metric]/1e6 if metric!="Margin" else cat[metric]
            fmt  = [f"₹{v:.1f}M" for v in vals] if metric!="Margin" else [f"{v:.1f}%" for v in vals]
            fig = go.Figure(go.Bar(x=cat["category"], y=vals,
                                   marker_color=color, text=fmt, textposition="outside"))
            fig.update_layout(title=title, height=300,
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font_color="#1e293b", margin=dict(t=40,b=10,l=10,r=10))
            st.plotly_chart(fig, use_container_width=True)

    # Sub-category
    st.markdown('<div class="section-title">Sub-Category Profit Analysis</div>', unsafe_allow_html=True)
    sub = dff.groupby(["category","sub_category"]).agg(
        Profit=("profit","sum"), Revenue=("sales","sum")
    ).reset_index()
    sub["Margin"] = sub["Profit"]/sub["Revenue"]*100
    sub = sub.sort_values("Profit")

    fig = go.Figure(go.Bar(
        x=sub["Profit"]/1e3, y=sub["sub_category"], orientation="h",
        marker_color=[C["green"] if p>0 else C["red"] for p in sub["Profit"]],
        text=[f"₹{p/1e3:.1f}K" for p in sub["Profit"]], textposition="outside"
    ))
    fig.add_vline(x=0, line_color="#1e293b", line_width=1)
    fig.update_layout(title="Profit by Sub-Category (₹K)", height=400,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color="#1e293b", margin=dict(t=40,b=10,l=10,r=40))
    st.plotly_chart(fig, use_container_width=True)

    # Discount impact
    st.markdown('<div class="section-title">Discount Impact on Profit Margin</div>', unsafe_allow_html=True)
    dff["disc_bucket"] = pd.cut(dff["discount"],
        bins=[-0.01,0,0.10,0.20,0.30,1.0],
        labels=["No Discount","1–10%","11–20%","21–30%","30%+"])
    disc = dff.groupby("disc_bucket", observed=True).agg(
        Orders=("order_id","count"), Margin=("profit_margin","mean")
    ).reset_index()

    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Bar(x=disc["disc_bucket"], y=disc["Orders"],
                         name="Orders", marker_color=C["blue"], opacity=0.7), secondary_y=False)
    fig.add_trace(go.Scatter(x=disc["disc_bucket"], y=disc["Margin"],
                             name="Margin %", mode="lines+markers+text",
                             line=dict(color=C["red"],width=2),
                             text=[f"{m:.1f}%" for m in disc["Margin"]],
                             textposition="top center"), secondary_y=True)
    fig.add_hline(y=0, line_color=C["red"], line_dash="dash", secondary_y=True)
    fig.update_yaxes(title_text="Orders", secondary_y=False)
    fig.update_yaxes(title_text="Profit Margin %", secondary_y=True)
    st.plotly_chart(plot_cfg(fig,350), use_container_width=True)

# =============================================================================
# PAGE 3 — CUSTOMER ANALYTICS
# =============================================================================
elif page == "👥 Customer Analytics":
    st.markdown("## 👥 Customer Analytics")

    if rfm is not None:
        seg_colors = {
            "Champions":C["green"],"Loyal Customers":C["blue"],
            "Potential Loyalists":C["purple"],"New Customers":"#06b6d4",
            "At Risk":C["amber"],"Cant Lose Them":"#f97316",
            "Lost":C["red"],"Hibernating":C["gray"]
        }
        seg_summary = rfm.groupby("Segment").agg(
            Customers=("customer_id","count"),
            Avg_Recency=("recency","mean"),
            Avg_Frequency=("frequency","mean"),
            Total_Revenue=("monetary","sum")
        ).reset_index().sort_values("Total_Revenue", ascending=False)

        # KPIs
        c1,c2,c3,c4 = st.columns(4)
        c1.markdown(kpi("Total Customers", f"{len(rfm):,}", color=""), unsafe_allow_html=True)
        champ = len(rfm[rfm["Segment"]=="Champions"])
        c2.markdown(kpi("Champions", f"{champ}", color="green"), unsafe_allow_html=True)
        at_risk = len(rfm[rfm["Segment"].isin(["At Risk","Cant Lose Them"])])
        c3.markdown(kpi("At Risk", f"{at_risk}", color="red"), unsafe_allow_html=True)
        lost = len(rfm[rfm["Segment"]=="Lost"])
        c4.markdown(kpi("Lost Customers", f"{lost}", color="amber"), unsafe_allow_html=True)

        st.markdown("---")
        left, right = st.columns(2)

        with left:
            st.markdown('<div class="section-title">Customers by Segment</div>', unsafe_allow_html=True)
            fig = go.Figure(go.Bar(
                x=seg_summary["Customers"],
                y=seg_summary["Segment"],
                orientation="h",
                marker_color=[seg_colors.get(s,C["gray"]) for s in seg_summary["Segment"]],
                text=seg_summary["Customers"], textposition="outside"
            ))
            st.plotly_chart(plot_cfg(fig,380), use_container_width=True)

        with right:
            st.markdown('<div class="section-title">Revenue by Segment</div>', unsafe_allow_html=True)
            fig2 = go.Figure(go.Pie(
                labels=seg_summary["Segment"],
                values=seg_summary["Total_Revenue"],
                hole=0.45,
                marker_colors=[seg_colors.get(s,C["gray"]) for s in seg_summary["Segment"]]
            ))
            fig2.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)",
                               font_color="#1e293b", margin=dict(t=10,b=10,l=10,r=10))
            st.plotly_chart(fig2, use_container_width=True)

        # RFM scatter
        st.markdown('<div class="section-title">RFM Scatter — Recency vs Frequency</div>', unsafe_allow_html=True)
        fig3 = px.scatter(
            rfm, x="recency", y="frequency", size="monetary",
            color="Segment", color_discrete_map=seg_colors,
            hover_data=["customer_id","monetary"],
            size_max=30, opacity=0.7
        )
        fig3.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(248,250,252,1)",
                           font_color="#1e293b", margin=dict(t=20,b=20,l=10,r=10),
                           xaxis_title="Recency (days)", yaxis_title="Frequency (orders)")
        st.plotly_chart(fig3, use_container_width=True)

        # Segment table
        st.markdown('<div class="section-title">Segment Summary Table</div>', unsafe_allow_html=True)
        display = seg_summary.copy()
        display["Avg_Recency"]   = display["Avg_Recency"].round(0).astype(int)
        display["Avg_Frequency"] = display["Avg_Frequency"].round(1)
        display["Total_Revenue"] = display["Total_Revenue"].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("Run `python notebooks/02_customer_analytics.py` to generate RFM data first.")

# =============================================================================
# PAGE 4 — PRODUCT INTELLIGENCE
# =============================================================================
elif page == "📦 Product Intelligence":
    st.markdown("## 📦 Product Intelligence")

    c1,c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-title">Top 10 Sub-Categories by Revenue</div>', unsafe_allow_html=True)
        top_rev = dff.groupby("sub_category")["sales"].sum().nlargest(10).reset_index()
        fig = go.Figure(go.Bar(
            x=top_rev["sales"]/1e6, y=top_rev["sub_category"],
            orientation="h", marker_color=C["blue"],
            text=[f"₹{v/1e6:.1f}M" for v in top_rev["sales"]],
            textposition="outside"
        ))
        st.plotly_chart(plot_cfg(fig,350), use_container_width=True)

    with c2:
        st.markdown('<div class="section-title">Profit Margin by Category & Region</div>', unsafe_allow_html=True)
        heat = dff.groupby(["category","region"])["profit_margin"].mean().reset_index()
        heat_pivot = heat.pivot(index="category", columns="region", values="profit_margin")
        fig2 = go.Figure(go.Heatmap(
            z=heat_pivot.values.round(1),
            x=heat_pivot.columns.tolist(),
            y=heat_pivot.index.tolist(),
            colorscale="RdYlGn",
            text=[[f"{v:.1f}%" for v in row] for row in heat_pivot.values],
            texttemplate="%{text}",
            colorbar=dict(title="Margin %")
        ))
        fig2.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)",
                           font_color="#1e293b", margin=dict(t=20,b=20,l=10,r=10))
        st.plotly_chart(fig2, use_container_width=True)

    # Returns
    st.markdown('<div class="section-title">Return Rate by Sub-Category</div>', unsafe_allow_html=True)
    ret = dff.groupby("sub_category").apply(
        lambda x: pd.Series({
            "Return Rate %": (x["returned"]=="Yes").mean()*100,
            "Returns": (x["returned"]=="Yes").sum(),
            "Total Orders": len(x)
        })
    ).reset_index().sort_values("Return Rate %", ascending=True)

    fig3 = go.Figure(go.Bar(
        x=ret["Return Rate %"], y=ret["sub_category"], orientation="h",
        marker_color=[C["red"] if r>7 else C["amber"] if r>4 else C["green"]
                      for r in ret["Return Rate %"]],
        text=[f"{r:.1f}%" for r in ret["Return Rate %"]], textposition="outside"
    ))
    fig3.add_vline(x=5, line_dash="dash", line_color=C["gray"],
                   annotation_text="5% benchmark")
    st.plotly_chart(plot_cfg(fig3,400), use_container_width=True)

# =============================================================================
# PAGE 5 — REVENUE FORECAST
# =============================================================================
elif page == "🔮 Revenue Forecast":
    st.markdown("## 🔮 Revenue Forecast")

    monthly = df.groupby("ym").agg(Revenue=("sales","sum"), Profit=("profit","sum")).reset_index()

    if fct is not None:
        c1,c2,c3 = st.columns(3)
        next_m = fct.iloc[0]
        c1.markdown(kpi("Next Month Forecast", f"₹{next_m['forecast_revenue']/1e6:.2f}M",color=""), unsafe_allow_html=True)
        c2.markdown(kpi("6-Month Total",f"₹{fct['forecast_revenue'].sum()/1e6:.1f}M",color="green"), unsafe_allow_html=True)
        c3.markdown(kpi("Lower Bound",f"₹{next_m['lower_bound']/1e6:.2f}M",color="amber"), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="section-title">Revenue Forecast — Next 6 Months</div>', unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["ym"], y=monthly["Revenue"]/1e6,
            name="Historical", line=dict(color=C["blue"],width=2),
            mode="lines+markers", marker=dict(size=4)
        ))
        fig.add_trace(go.Scatter(
            x=fct["month"], y=fct["forecast_revenue"]/1e6,
            name="Forecast", line=dict(color=C["amber"],width=2,dash="dash"),
            mode="lines+markers+text",
            text=[f"₹{v/1e6:.1f}M" for v in fct["forecast_revenue"]],
            textposition="top center", marker=dict(size=8,symbol="diamond")
        ))
        fig.add_trace(go.Scatter(
            x=pd.concat([fct["month"], fct["month"].iloc[::-1]]),
            y=pd.concat([fct["upper_bound"]/1e6, fct["lower_bound"].iloc[::-1]/1e6]),
            fill="toself", fillcolor="rgba(245,158,11,0.12)",
            line=dict(color="rgba(0,0,0,0)"), name="90% Confidence"
        ))
        fig.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(248,250,252,1)",
                          font_color="#1e293b", margin=dict(t=20,b=20,l=10,r=10),
                          xaxis_title="Month", yaxis_title="Revenue (₹M)",
                          legend=dict(bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">Forecast Table</div>', unsafe_allow_html=True)
        display = fct.copy()
        display["month"] = display["month"].dt.strftime("%b %Y")
        display["forecast_revenue"] = display["forecast_revenue"].apply(lambda x: f"₹{x:,.0f}")
        display["lower_bound"]      = display["lower_bound"].apply(lambda x: f"₹{x:,.0f}")
        display["upper_bound"]      = display["upper_bound"].apply(lambda x: f"₹{x:,.0f}")
        display.columns = ["Month","Forecast Revenue","Lower Bound","Upper Bound"]
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("Run `python notebooks/03_forecasting.py` to generate forecasts first.")
        st.markdown("**In the meantime, here's the historical trend:**")
        fig = go.Figure(go.Scatter(
            x=monthly["ym"], y=monthly["Revenue"]/1e6,
            mode="lines+markers", line=dict(color=C["blue"],width=2),
            fill="tozeroy", fillcolor="rgba(37,99,235,0.08)"
        ))
        fig.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(248,250,252,1)",
                          font_color="#1e293b", margin=dict(t=20,b=20,l=10,r=10),
                          xaxis_title="Month", yaxis_title="Revenue (₹M)")
        st.plotly_chart(fig, use_container_width=True)
