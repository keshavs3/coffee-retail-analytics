import os
from pathlib import Path
import pandas as pd
import streamlit as st

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Insights | Afficionado Coffee Roasters",
    page_icon="💡",
    layout="wide"
)

# ---------------------------------------------------
# PREMIUM CORPORATE COLORS (Theme Palette Constants)
# ---------------------------------------------------
COLOR_BEAN = "#3E2723"  # Deep Roasted Brown
COLOR_MOCHA = "#7B5E57"  # Warm Milk Mocha
COLOR_LATTE = "#A1887F"  # Muted Tan / Latte
COLOR_CREMA = "#D7CCC8"  # Cream / Soft Crema
CAFE_PALETTE = [[0, COLOR_CREMA], [0.5, COLOR_LATTE], [1, COLOR_BEAN]]

# --------------------------------------------------
# ENVIRONMENT AND DIRECTORY RESOLUTION (Cloud-Safe Fix)
# --------------------------------------------------
CURRENT_SCRIPT_DIR = Path(__file__).resolve().parent
DATA_PATH = CURRENT_SCRIPT_DIR.parent / "outputs" / "cleaned" / "coffee_shop_fe.csv"
CSS_PATH = CURRENT_SCRIPT_DIR.parent / "assets" / "style.css"

# ---------------------------------------------------
# LOAD CSS
# ---------------------------------------------------
if CSS_PATH.exists():
    with open(CSS_PATH, encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# ---------------------------------------------------
# DATA VALIDATION
# ---------------------------------------------------
if not DATA_PATH.exists():
    st.error(f"Dataset not found at targeted cloud route: {DATA_PATH}")
    st.stop()

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

df = load_data()

# ---------------------------------------------------
# HEADER (CENTERED & BRAND-STYLED)
# ---------------------------------------------------
st.markdown(
    f"""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 25px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
        <h1 style="color: #3E2723; font-size: 3.50rem; font-weight: 800; margin: 0;">
            💡 Strategic Insights
        </h1>
        <p style="color: #7B5E57; font-size: 1.60rem; font-weight: 600; margin: 8px 0 0 0;">
            Executive Recommendations from Product & Revenue Analysis
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

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
    This executive command panel consolidates strategic business discoveries, evaluates operational performance gaps, and provides data-driven recommendations to support long-term portfolio management, menu simplification, and growth resilience.
    """
)
st.sidebar.markdown("---")

# ---------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------
total_revenue = df["revenue"].sum()

top_product = df.groupby("product_detail")["revenue"].sum().sort_values(ascending=False)
top_category = df.groupby("product_category")["revenue"].sum().sort_values(ascending=False)
top_store = df.groupby("store_location")["revenue"].sum().sort_values(ascending=False)

hero_product = top_product.index[0]
hero_product_rev = top_product.iloc[0]

hero_category = top_category.index[0]
hero_category_rev = top_category.iloc[0]

hero_store = top_store.index[0]
hero_store_rev = top_store.iloc[0]

# Advanced Insight Calculations
product_rev = df.groupby("product_detail")["revenue"].sum().sort_values(ascending=False)
product_share = (product_rev / product_rev.sum()) * 100

# Pareto Analysis
pareto_df = product_rev.reset_index()
pareto_df["Revenue Share"] = pareto_df["revenue"] / pareto_df["revenue"].sum()
pareto_df["Cumulative Share"] = pareto_df["Revenue Share"].cumsum()
products_for_80 = (pareto_df["Cumulative Share"] <= 0.80).sum()

# Long Tail & Benchmark Metrics
long_tail_products = (product_share < 0.5).sum()
worst_store = top_store.index[-1]
worst_store_rev = top_store.iloc[-1]
store_gap_pct = ((hero_store_rev - worst_store_rev) / hero_store_rev) * 100

category_share = (hero_category_rev / total_revenue) * 100
store_concentration = (hero_store_rev / total_revenue) * 100
hero_product_share = (hero_product_rev / total_revenue) * 100

tail_products = len(product_share[product_share < 0.5])
performance_gap = ((hero_store_rev - worst_store_rev) / hero_store_rev) * 100

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f'<div style="background-color: white; padding: 20px 16px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;">Revenue</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 24px; font-weight: 600;">${total_revenue:,.0f}</h2></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div style="background-color: white; padding: 20px 16px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;">Hero Product</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 14px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{hero_product}</h2></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div style="background-color: white; padding: 20px 16px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;">Top Category</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 24px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{hero_category}</h2></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div style="background-color: white; padding: 20px 16px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;">Best Store</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 20px; font-weight: 600; white-space: nowrap; overflow: hidden;">{hero_store}</h2></div>', unsafe_allow_html=True)
with k5:
    st.markdown(f'<div style="background-color: white; padding: 20px 16px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;">Menu Tail</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 24px; font-weight: 600;">{tail_products} SKUs</h2></div>', unsafe_allow_html=True)

st.divider()

# Core Bullet Summary
st.markdown(
    f"""
    <div style="background-color:#FDFBF7; padding:28px; border-radius:14px; border:1px solid #D7CCC8; border-left:8px solid #3E2723; margin-top:10px; margin-bottom:25px; box-shadow:0 6px 18px rgba(62,39,35,0.08); font-family: 'Helvetica Neue', sans-serif;">
        <h3 style="color:#3E2723; margin-bottom:18px; font-weight:700; font-size:1.9rem;">📌 Strategic Business Intelligence</h3>
        <ul style="color:#4E342E; font-size:16px; line-height:1.9; margin-bottom:0; padding-left:20px;">
            <li><b>{products_for_80}</b> products generate 80% of company revenue.</li>
            <li><b>{long_tail_products}</b> products contribute less than 0.5% individually and may require review.</li>
            <li><b>{hero_store}</b> outperforms <b>{worst_store}</b> by a margin of <b>{store_gap_pct:.1f}%</b>.</li>
            <li><b>{hero_category}</b> contributes <b>{category_share:.1f}%</b> of total revenue.</li>
            <li>Revenue remains concentrated around a limited number of menu anchors, indicating moderate dependency risk.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# REVENUE RISK ASSESSMENT MATRIX
# ---------------------------------------------------
st.markdown(f'<h2 style="text-align: left; margin: 25px 0 15px 0; color: {COLOR_BEAN}; font-size: 1.9rem; font-weight: 700; letter-spacing: -0.5px;">Revenue Risk Assessment</h2>', unsafe_allow_html=True)
risk_col1, risk_col2 = st.columns(2)

with risk_col1:
    st.markdown(f'<div class="brand-container-box" style="border-top: 5px solid #EF6C00;"><span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase;">⚠️ Core Product Nucleus (80% Yield)</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 2px 0; font-size: 32px; font-weight: 800;">{products_for_80} SKUs</h2><div style="color: #EF6C00; font-size: 14px; font-weight: 600;">Core operational catalog metrics framework density.</div></div>', unsafe_allow_html=True)

with risk_col2:
    st.markdown(f'<div class="brand-container-box" style="border-top: 5px solid #B71C1C;"><span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase;">🚨 Maximum Store Concentration</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 2px 0; font-size: 32px; font-weight: 800;">{store_concentration:.1f}%</h2><div style="color: #B71C1C; font-size: 14px; font-weight: 600;">Share generated by your leading storefront.</div></div>', unsafe_allow_html=True)

# ---------------------------------------------------
# STORE PERFORMANCE BENCHMARK
# ---------------------------------------------------
st.markdown(f'<h2 style="text-align: left; margin: 20px 0; color: {COLOR_BEAN}; font-size: 1.9rem; font-weight: 700; letter-spacing: -0.5px;">Store Performance Benchmark</h2>', unsafe_allow_html=True)
bench1, bench2, bench3 = st.columns(3)

with bench1:
    st.markdown(f'<div class="brand-container-box" style="border-top: 5px solid #2E7D32;"><span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase;">Best Performing Hub</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 2px 0; font-size: 24px; font-weight: 700;">{hero_store}</h2><div style="color: #2E7D32; font-size: 16px; font-weight: 600;">Yield: ${hero_store_rev:,.0f}</div></div>', unsafe_allow_html=True)
with bench2:
    st.markdown(f'<div class="brand-container-box" style="border-top: 5px solid #C62828;"><span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase;">Lowest Performing Hub</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 2px 0; font-size: 24px; font-weight: 700;">{worst_store}</h2><div style="color: #C62828; font-size: 16px; font-weight: 600;">Yield: ${worst_store_rev:,.0f}</div></div>', unsafe_allow_html=True)
with bench3:
    st.markdown(f'<div class="brand-container-box" style="border-left: 5px solid {COLOR_MOCHA}; background-color: #FDFBF7;"><span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase;">Operational Variance</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 2px 0; font-size: 32px; font-weight: 800;">{performance_gap:.1f}%</h2><div style="color: #7B5E57; font-size: 14px; font-weight: 500; font-style: italic;">Cross-regional performance gap.</div></div>', unsafe_allow_html=True)

# ---------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------
recommendations_html = """
<div style="background-color:#FDFBF7; padding:24px; border-radius:12px; border:1px solid #EFEBE9; border-left:8px solid #3E2723; margin-top:15px; margin-bottom:25px; box-shadow:0 4px 12px rgba(62,39,35,0.04); font-family: 'Helvetica Neue', sans-serif;">
    <h3 style="margin:0 0 15px 0; color:#3E2723; font-size:1.95rem; font-weight:700;">Strategic Recommendations</h3>
    <ol style="color:#4E342E; font-size:16px; line-height:1.8; margin:0; padding-left:22px;">
        <li>Protect and promote <b>{hero_prod}</b>, which remains the strongest revenue-generating product.</li>
        <li>Review <b>{tail_prods}</b> low-contribution products that generate less than 0.5% of total revenue individually.</li>
        <li>Replicate operational best practices from <b>{hero_st}</b> across lower-performing locations to improve consistency.</li>
        <li>Reduce concentration risk by expanding high-performing categories beyond <b>{hero_cat}</b>.</li>
    </ol>
</div>
"""
st.markdown(
    recommendations_html.format(
        hero_prod=hero_product,
        tail_prods=long_tail_products,
        hero_st=hero_store,
        hero_cat=hero_category
    ),
    unsafe_allow_html=True
)

# ---------------------------------------------------
# MANAGEMENT CONCLUSION
# ---------------------------------------------------
conclusion_html = """
<div style="background-color: #FDFBF7; padding: 24px; border-radius: 12px; border: 1px solid #EFEBE9; border-left: 8px solid #3E2723; margin-top: 15px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(62,39,35,0.04); font-family: 'Helvetica Neue', sans-serif;">
    <h3 style="margin: 0 0 15px 0; color: #3E2723; font-size: 1.95rem; font-weight: 700;">Executive Management Conclusion</h3>
    <ul style="color: #4E342E; font-size: 16px; line-height: 1.8; margin: 0; padding-left: 22px;">
        <li><b>Core Value Performance:</b> Afficionado Coffee Roasters demonstrates strong baseline revenue performance driven heavily by a concentrated portfolio of high-velocity lines.</li>
        <li style="margin-top: 10px;"><b>Menu Concentration:</b> Metrics confirm that only <b>{prod_80} products</b> account for approximately 80% of entire gross returns, leaving under-indexing items as targets for reduction.</li>
        <li style="margin-top: 10px;"><b>Operational Variance:</b> Retail footprint execution varies significantly, highlighted by the fact that the benchmark hub <b>{top_st} outpaces the lowest-performing branch ({low_st}) by {gap:.1f}%</b>.</li>
    </ul>
</div>
"""
st.markdown(
    conclusion_html.format(
        prod_80=products_for_80,
        top_st=hero_store,
        low_st=worst_store,
        gap=performance_gap
    ),
    unsafe_allow_html=True
)

st.divider()

# Footer Layout
st.markdown(
    """
    <div style="text-align: center; padding: 15px 0 25px 0; color: #7B5E57; font-size: 14px; font-weight: 500; letter-spacing: 0.3px; font-family: 'Helvetica Neue', sans-serif;">
        ☕ <b>Afficionado Coffee Roasters</b> | Strategic Insights Hub
        <br>
        <span style="color: #A1887F; font-size: 14px; font-weight: 400; display: inline-block; margin-top: 5px;">
         Trend Detection Analytics • Anomalies & Key Predictive Discoveries © 2026
        </span>
        <br>
        <span style="color: #BAA6A1; font-size: 13px; font-weight: 400; display: inline-block; margin-top: 6px; letter-spacing: 0.5px; text-transform: uppercase;">
            ⚡ Powered by: Python • Streamlit • Pandas • Plotly Express
        </span>
    </div>
    """,
    unsafe_allow_html=True
)