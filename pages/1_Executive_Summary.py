import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Executive Summary",
    page_icon="☕",
    layout="wide"
)

# Premium Global Design System Injection (Cafe Corporate Theme)
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
        }
        /* Elegant unified executive container cards */
        .brand-container-box {
            background-color: #FDFBF7;
            border: 1px solid #EFEBE9;
            border-left: 6px solid #5D4037;
            padding: 22px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Corporate Theme Color Constants
COLOR_BEAN = "#3E2723"  # Deep Roasted Brown
COLOR_MOCHA = "#7B5E57"  # Warm Milk Mocha
COLOR_LATTE = "#A1887F"  # Muted Tan / Latte
COLOR_CREMA = "#D7CCC8"  # Cream / Soft Crema
CAFE_PALETTE = [COLOR_BEAN, COLOR_MOCHA, COLOR_LATTE, COLOR_CREMA, "#EFEBE9"]

# --------------------------------------------------
# ENVIRONMENT AND DIRECTORY RESOLUTION (Cloud-Safe Fix)
# --------------------------------------------------
ROOT_DIR = Path(os.getcwd())
DATA_PATH = ROOT_DIR / "outputs" / "cleaned" / "coffee_shop_fe.csv"
CSS_PATH = ROOT_DIR / "assets" / "style.css"

if CSS_PATH.exists():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------
@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        return pd.DataFrame(columns=[
            "revenue", "transaction_id", "transaction_qty", "unit_price",
            "product_id", "product_detail", "product_category", "store_location", "hour"
        ])
    return pd.read_csv(DATA_PATH)

df = load_data()
df = df.drop_duplicates()

def apply_theme(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13, color="#424242", family="'Helvetica Neue', Helvetica, Arial, sans-serif"),
        title_font=dict(size=15, color=COLOR_BEAN, family="'Helvetica Neue', Helvetica, Arial, sans-serif"),
        margin=dict(l=30, r=30, t=50, b=30)
    )
    fig.update_xaxes(showgrid=False, linecolor="#E0E0E0")
    fig.update_yaxes(showgrid=True, gridcolor="#F5F5F5", linecolor="#E0E0E0")
    return fig

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown(
    f"""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 25px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
        <h1 style="color: {COLOR_BEAN}; font-size: 3.5rem; font-weight: 800; margin: 0; letter-spacing: -0.5px;">
           🗐 Executive Summary
        </h1>
        <p style="color: #7B5E57; font-size: 1.80rem; font-weight: 500; margin: 10px 0 0 0; letter-spacing: 0.2px;">
            High-Level Operational Performance & Strategic Takeaways
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

st.title("💡 Strategic Insights")
st.subheader("Executive Recommendations from Product & Revenue Analysis")

# Sidebar Description
st.sidebar.markdown(
    """
    <h3 style="color:#3E2723; font-size:1.3rem; font-weight:600; margin-bottom:10px;">
         About This Page
    </h3>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    """
    This section transforms transaction-level data into actionable business intelligence.
    It highlights key revenue drivers, product concentration, store performance gaps, and strategic opportunities.
    """
)
st.sidebar.markdown("---")

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------
if not df.empty:
    total_revenue = df["revenue"].sum()
    total_transactions = df["transaction_id"].nunique()
    total_units = df["transaction_qty"].sum()
    total_products = df["product_id"].nunique()
    avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0
    product_efficiency_score = total_revenue / total_products if total_products > 0 else 0

    product_rev = df.groupby("product_detail")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
    top_product = product_rev.iloc[0]

    category_rev = df.groupby("product_category")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
    top_category = category_rev.iloc[0]

    store_rev = df.groupby("store_location")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
    top_store = store_rev.iloc[0]
else:
    total_revenue, total_transactions, total_units, total_products, avg_order_value = 0, 0, 0, 0, 0
    top_product = {"product_detail": "N/A", "revenue": 0}
    top_category = {"product_category": "N/A", "revenue": 0}
    top_store = {"store_location": "N/A", "revenue": 0}
    category_rev = pd.DataFrame(columns=["product_category", "revenue"])
    product_rev = pd.DataFrame(columns=["product_detail", "revenue"])
    product_efficiency_score = 0

# ---------------------------------------------------
# HIGH-PROMINENCE 5-COLUMN KPI CARDS GRID
# ---------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f'<div style="background-color: white; padding: 18px 15px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">Revenue</span><h2 style="color: {COLOR_BEAN}; margin: 6px 0 0 0; font-size: 24px; font-weight: 700;">${total_revenue:,.0f}</h2></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div style="background-color: white; padding: 18px 15px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">Transactions</span><h2 style="color: {COLOR_BEAN}; margin: 6px 0 0 0; font-size: 24px; font-weight: 700;">{total_transactions:,}</h2></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div style="background-color: white; padding: 18px 15px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">Units Sold</span><h2 style="color: {COLOR_BEAN}; margin: 6px 0 0 0; font-size: 24px; font-weight: 700;">{int(total_units):,}</h2></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div style="background-color: white; padding: 18px 15px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">Products</span><h2 style="color: {COLOR_BEAN}; margin: 6px 0 0 0; font-size: 24px; font-weight: 700;">{total_products:,}</h2></div>', unsafe_allow_html=True)
with c5:
    st.markdown(f'<div style="background-color: white; padding: 18px 15px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">Avg Order</span><h2 style="color: {COLOR_BEAN}; margin: 6px 0 0 0; font-size: 24px; font-weight: 700;">${avg_order_value:.2f}</h2></div>', unsafe_allow_html=True)

st.divider()

# --------------------------------------------------
# BUSINESS HEALTH SNAPSHOT
# --------------------------------------------------
st.subheader("💼 Business Health Snapshot")
bh1, bh2, bh3, bh4 = st.columns(4)

with bh1:
    st.markdown(f'<div class="brand-container-box" style="padding: 16px; min-height: 140px;"><h4 style="margin: 0 0 8px 0; color: #3E2723; font-size: 1.1rem;">Revenue Performance</h4><p style="margin: 4px 0; font-size: 22px; font-weight: bold; color: #5D4037;">${total_revenue:,.0f}</p><p style="margin: 0; font-size: 14px; color: #757575;">generated across <b>{total_transactions:,} txns</b></p></div>', unsafe_allow_html=True)
with bh2:
    st.markdown(f'<div class="brand-container-box" style="padding: 16px; border-left-color: #2E7D32; min-height: 140px;"><h4 style="margin: 0 0 8px 0; color: #1B5E20; font-size: 1.1rem;">Product Portfolio</h4><p style="margin: 4px 0; font-size: 22px; font-weight: bold; color: #2E7D32;">{total_products:,} Products</p><p style="margin: 0; font-size: 14px; color: #757575;">generated <b>{int(total_units):,} Units Sold</b></p></div>', unsafe_allow_html=True)
with bh3:
    st.markdown(f'<div class="brand-container-box" style="padding: 16px; border-left-color: #E65100; min-height: 140px;"><h4 style="margin: 0 0 8px 0; color: #E65100; font-size: 1.1rem;">Average Basket Value</h4><p style="margin: 4px 0; font-size: 22px; font-weight: bold; color: #EF6C00;">${avg_order_value:.2f}</p><p style="margin: 0; font-size: 14px; color: #757575;">spent per customer checkout</p></div>', unsafe_allow_html=True)
with bh4:
    st.markdown(f'<div class="brand-container-box" style="padding: 16px; border-left-color: #0288D1; min-height: 140px;"><h4 style="margin: 0 0 8px 0; color: #01579B; font-size: 1.1rem;">Product Efficiency</h4><p style="margin: 4px 0; font-size: 22px; font-weight: bold; color: #0288D1;">${product_efficiency_score:,.2f}</p><p style="margin: 0; font-size: 14px; color: #757575;">average gross revenue earned per active SKU</p></div>', unsafe_allow_html=True)

# Data Integrity Expander
with st.expander("🛠️ Operational Ingestion Framework & Data Integrity Audit"):
    dq1, dq2, dq3 = st.columns(3)
    dq1.metric("Pipeline Frame Depth", f"{len(df):,}")
    dq2.metric("Null Structural Attributes", f"{df.isna().sum().sum():,}")
    dq3.metric("Redundant Row Arrays", f"{df.duplicated().sum():,}")

# Summary Highlight Box
try:
    top_store_val = df.groupby("store_location")["revenue"].sum().idxmax()
    top_cat_val = df.groupby("product_category")["revenue"].sum().idxmax()
except Exception:
    top_store_val, top_cat_val = "N/A", "N/A"

st.markdown(f"""
    <div style="background-color: #F5ECE1; padding: 26px; border-radius: 14px; border: 1.5px solid #E6D5C3; border-left: 8px solid #3E2723; margin-top: 10px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(62, 39, 35, 0.08); font-family: 'Helvetica Neue', sans-serif;">
        <h3 style="margin: 0 0 12px 0; color: #3E2723; font-size: 1.8rem; font-weight: 700; letter-spacing: -0.3px;">𓂃🖊 Core Executive Summary Snapshot</h3>
        <p style="margin: 8px 0; font-size: 16px; color: #3E2723; line-height: 1.6;">
            ➤ <b>Revenue Anchor Footprint:</b> <span style="font-weight: 700;">{top_store_val}</span> &nbsp;|&nbsp; ➤ <b>Primary Portfolio Segment:</b> <span style="font-weight: 700;">{top_cat_val}</span>
        </p>
        <p style="margin: 16px 0 0 0; color: #5D4037; font-size: 14px; line-height: 1.6; font-weight: 600; border-top: 1px dashed #E6D5C3; padding-top: 12px;">
             ⚠️ The percentage share of total sales handled across store hubs highlights structural concentration risk limits.
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# --------------------------------------------------
# VISUALIZATIONS
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Category")
    if not category_rev.empty:
        fig = px.bar(category_rev, x="product_category", y="revenue", labels={"product_category": "Category", "revenue": "Revenue ($)"})
        fig.update_traces(marker_color=COLOR_BEAN, hovertemplate="<b>Category:</b> %{x}<br><b>Sales:</b> $% {y:,.0f}<extra></extra>")
        fig = apply_theme(fig)
        fig.update_layout(title="Total Sales Across Main Product Lines", title_x=0.02, height=420, showlegend=False)
        st.plotly_chart(fig, use_container_width=True, theme=None)

with col2:
    st.subheader("Revenue Share")
    if not category_rev.empty:
        fig = px.pie(category_rev, names="product_category", values="revenue", hole=0.5, color_discrete_sequence=CAFE_PALETTE)
        fig.update_traces(textposition="inside", textinfo="percent+label", hovertemplate="<b>Category:</b> %{label}<br><b>Mix Share:</b> %{percent}<extra></extra>")
        fig = apply_theme(fig)
        fig.update_layout(title="Percentage Breakdown of Category Revenue", title_x=0.02, height=420)
        st.plotly_chart(fig, use_container_width=True, theme=None)

st.divider()

st.subheader("Top 10 Products")
if not product_rev.empty:
    top10 = product_rev.head(10)
    fig = px.bar(top10, x="revenue", y="product_detail", orientation="h", labels={"revenue": "Revenue ($)", "product_detail": "Product Menu Item"})
    fig.update_traces(marker_color=COLOR_MOCHA, texttemplate="$%{x:,.0f}", textposition="outside", hovertemplate="<b>Product:</b> %{y}<br><b>Sales:</b> $% {x:,.0f}<extra></extra>")
    fig = apply_theme(fig)
    fig.update_layout(height=500, title="Best Selling Coffee Shop Products", title_x=0.02, xaxis_title="Revenue ($)", yaxis_title="", yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True, theme=None)

st.divider()

# ---------------------------------------------------
# MANAGEMENT RECOMMENDATIONS PANEL
# ---------------------------------------------------
st.markdown(
    f"""
    <div style="background-color: #FDFBF7; padding: 24px; border-radius: 12px; border: 1px solid #EFEBE9; border-left: 8px solid {COLOR_BEAN}; margin-top: 15px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(62, 39, 35, 0.04); font-family: 'Helvetica Neue', sans-serif;">
        <h2 style="text-align: left; margin: 0 0 24px 0; color: {COLOR_BEAN}; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px;">
            Management Recommendations
        </h2>
        <div style="color: #4E342E; font-size: 16px; line-height: 1.8; display: flex; flex-direction: column; gap: 16px;">
            <div>
                <b style="font-size: 18px; color: {COLOR_BEAN}; display: block; margin-bottom: 4px;">➯ Revenue Growth</b>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Increase promotion of top-selling products.</li>
                    <li>Cross-sell high-performing categories.</li>
                </ul>
            </div>
            <div style="border-top: 1px dashed #EFEBE9; padding-top: 14px;">
                <b style="font-size: 18px; color: {COLOR_BEAN}; display: block; margin-bottom: 4px;">➯ Menu Optimization</b>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Review low-volume SKUs.</li>
                    <li>Simplify products with minimal revenue impact.</li>
                </ul>
            </div>
            <div style="border-top: 1px dashed #EFEBE9; padding-top: 14px;">
                <b style="font-size: 18px; color: {COLOR_BEAN}; display: block; margin-bottom: 4px;">➯ Store Operations</b>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Replicate best-performing store strategies.</li>
                    <li>Optimize staffing around peak demand periods.</li>
                </ul>
            </div>
            <div style="border-top: 1px dashed #EFEBE9; padding-top: 14px;">
                <b style="font-size: 18px; color: {COLOR_BEAN}; display: block; margin-bottom: 4px;">➯ Risk Management</b>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Reduce over-dependence on a single category.</li>
                    <li>Monitor product concentration through Pareto analysis.</li>
                </ul>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Footer Layout
st.markdown(
    """
    <div style="text-align: center; padding: 15px 0 25px 0; color: #7B5E57; font-size: 14px; font-weight: 500; letter-spacing: 0.3px; font-family: 'Helvetica Neue', sans-serif;">
        ☕ <b>Afficionado Coffee Roasters</b> | Executive Performance Briefing
        <br>
        <span style="color: #A1887F; font-size: 14px; font-weight: 400; display: inline-block; margin-top: 5px;">
           Core Operational Health Matrix • Strategic Takeaways & Management Insights © 2026
        </span>
        <br>
        <span style="color: #BAA6A1; font-size: 13px; font-weight: 400; display: inline-block; margin-top: 6px; letter-spacing: 0.5px; text-transform: uppercase;">
            ⚡ Powered by: Python • Streamlit • Pandas • Plotly Express
        </span>
    </div>
    """,
    unsafe_allow_html=True
)