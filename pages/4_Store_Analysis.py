import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Store Analysis | Afficionado Coffee Roasters",
    page_icon="🏬",
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

# ---------------------------------------------------
# ENVIRONMENT AND DIRECTORY RESOLUTION (Cloud-Safe Fix)
# ---------------------------------------------------
ROOT_DIR = Path(os.getcwd())
DATA_PATH = ROOT_DIR / "outputs" / "cleaned" / "coffee_shop_fe.csv"
CSS_PATH = ROOT_DIR / "assets" / "style.css"

if CSS_PATH.exists():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(
            "<style>" + f.read() + "</style>",
            unsafe_allow_html=True
        )


@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        return pd.DataFrame(columns=[
            "revenue", "transaction_id", "transaction_qty", "unit_price",
            "product_id", "product_detail", "product_category", "store_location", "hour"
        ])
    return pd.read_csv(DATA_PATH)


df = load_data()

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown(
    f"""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 25px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
        <h1 style="color: {COLOR_BEAN}; font-size: 3.5rem; font-weight: 800; margin: 0; letter-spacing: -0.5px;">
            𖠿 Store Analysis
        </h1>
        <p style="color: #7B5E57; font-size: 1.60rem; font-weight: 800; margin: 10px 0 0 0; letter-spacing: 0.2px;">
            Revenue Contribution by Store & Hourly Trends
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

# Sidebar About Information
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
    Evaluate store-level performance, compare revenue contribution, identify top-performing locations, and uncover operational trends through hourly sales analysis.
    """
)

st.markdown(
    """
    <div style="
        padding:20px;
        border-radius:12px;
        background-color:white;
        box-shadow:0px 2px 8px rgba(0,0,0,0.05);
        margin-bottom:20px;
        border-left: 6px solid #3E2723;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    ">
        <h3 style="color:#3E2723; margin-top:0; font-size:30px;">Analysis Objectives</h3>
        <ul style="color:#424242; line-height:1.6; font-size:16px;">
            <li>Measure revenue concentration across products</li>
            <li>Compare revenue performance across store locations</li>
            <li>Identify high-performing and low-performing stores</li>
            <li>Analyze hourly revenue trends for operational insights</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------
st.sidebar.title("🏠︎ Store Filters")

category_filter = st.sidebar.multiselect(
    "Product Category",
    options=sorted(df["product_category"].dropna().unique()) if not df.empty else [],
    default=sorted(df["product_category"].dropna().unique()) if not df.empty else []
)

if df.empty or not category_filter:
    st.warning("Please verify your data ingestion streams or select valid categories.")
    st.stop()

filtered = df[df["product_category"].isin(category_filter)]

# Core Metrics Data Aggregation Mapping
store_table = (
    filtered
    .groupby("store_location")
    .agg(
        Revenue=("revenue", "sum"),
        Transactions=("transaction_id", "nunique"),
        Units=("transaction_qty", "sum"),
        Unique_SKUs=("product_id", "nunique")
    )
    .reset_index()
    .sort_values("Revenue", ascending=False)
)

# Compute Engine Target Matrix Metrics
store_table["Product_Efficiency"] = (store_table["Revenue"] / store_table["Unique_SKUs"]).round(2)
store_table["AOV"] = (store_table["Revenue"] / store_table["Transactions"]).round(2)
store_table["Revenue per Unit"] = (store_table["Revenue"] / store_table["Units"]).round(2)

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------
total_revenue = filtered["revenue"].sum()
num_stores = filtered["store_location"].nunique()

if not store_table.empty:
    top_store = store_table.iloc[0]["store_location"]
    top_store_revenue = store_table.iloc[0]["Revenue"]
    top_store_share = (top_store_revenue / total_revenue) * 100
else:
    top_store, top_store_revenue, top_store_share = "N/A", 0, 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(
        f'<div style="background-color: white; padding: 20px 16px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">Total Revenue</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 26px; font-weight: 600;">${total_revenue:,.0f}</h2></div>',
        unsafe_allow_html=True)
with kpi2:
    st.markdown(
        f'<div style="background-color: white; padding: 20px 16px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">Stores Analyzed</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 26px; font-weight: 600;">{num_stores}</h2></div>',
        unsafe_allow_html=True)
with kpi3:
    st.markdown(
        f'<div style="background-color: white; padding: 20px 16px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">Top Store</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 26px; font-weight: 600;">{top_store}</h2></div>',
        unsafe_allow_html=True)
with kpi4:
    st.markdown(
        f'<div style="background-color: white; padding: 20px 16px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">Top Store Yield</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 26px; font-weight: 600;">${top_store_revenue:,.0f}</h2></div>',
        unsafe_allow_html=True)

st.markdown(
    f'<p style="font-size: 15px; color: #7B5E57; font-style: oblique; margin-top: 8px; margin-bottom: 20px; letter-spacing: 0.2px;">{top_store} contributes {top_store_share:.1f}% of core corporate revenues.</p>',
    unsafe_allow_html=True)
st.divider()

# ---------------------------------------------------
# STORE VISUALIZATIONS SECTION
# ---------------------------------------------------
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.subheader("$ Revenue by Store")
    fig = px.bar(store_table, x="store_location", y="Revenue", text_auto=".1s", color="Revenue",
                 color_continuous_scale=CAFE_PALETTE, title="Revenue Contribution by Store Location")
    fig.update_layout(template="plotly_white", height=450, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        '<div style="font-size: 15px; color: #4E342E; line-height: 1.6; margin-top: 10px;"><b>➤ Revenue Distribution Performance Analysis:</b><br>Identifies regional outperforming margins and direct asset yields.</div>',
        unsafe_allow_html=True)

with chart_col2:
    st.subheader("🛒 Average Order Value")
    fig = px.bar(store_table, x="store_location", y="AOV", text_auto=".2f", color="AOV",
                 color_continuous_scale=CAFE_PALETTE)
    fig.update_layout(template="plotly_white", height=450, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        '<div style="font-size: 15px; color: #4E342E; line-height: 1.6; margin-top: 10px;"><b>➤ Average Order Value (AOV) Efficiency Analysis:</b><br>Tracks customer transaction ticket density and upselling effectiveness margins.</div>',
        unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------
# STORE CATALOG EFFICIENCY SCORE METRIC MATRIX
# ---------------------------------------------------
st.markdown(
    f'<h3 style="color: {COLOR_BEAN}; font-size: 1.8rem; font-weight: 700; margin-bottom: 12px;">📊 Store Footprint Catalog Efficiency</h3>',
    unsafe_allow_html=True)
st.markdown(
    "The **Product Efficiency Score** isolates item asset productivity—tracking how much gross revenue each distinct active SKU delivers inside this location.")

eff_cols = st.columns(len(store_table))
for index, row in enumerate(store_table.itertuples()):
    with eff_cols[index]:
        st.markdown(
            f"""
            <div style="
                background-color: #FDFBF7; padding: 18px 15px; border-radius: 12px; border: 1px solid #EFEBE9; border-top: 5px solid {COLOR_MOCHA};
                box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; margin-bottom: 20px; font-family: 'Helvetica Neue', sans-serif;
            ">
                <span style="color: #757575; font-size: 13px; font-weight: 700; text-transform: uppercase;">{row.store_location} Yield</span>
                <h3 style="color: {COLOR_BEAN}; margin: 6px 0 2px 0; font-size: 22px; font-weight: 700;">
                    ${row.Product_Efficiency:,.2f} <span style="font-size: 13px; font-weight: 500; color: #757575;">/ SKU</span>
                </h3>
                <span style="color: #7B5E57; font-size: 13px; font-style: italic; font-weight: 600;">📋 {int(row.Unique_SKUs)} Active SKUs</span>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("---")

st.subheader("𖠿 Store Efficiency Comparison")
fig = px.bar(store_table, x="store_location", y="Revenue per Unit", text_auto=".2f", color="Revenue per Unit",
             color_continuous_scale=["#D7CCC8", "#A1887F", "#3E2723"])
fig.update_layout(height=350, template="plotly_white", coloraxis_showscale=False)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# TAB STRUCTURE: TIMING & DATAFRAMES LEDGERS
# ---------------------------------------------------
tab1, tab2 = st.tabs(["⏰ Operational Peak Hours", "📋 Store Performance Ledger"])

with tab1:
    if "hour" in filtered.columns and not filtered.empty:
        peak_hour_data = filtered.groupby("hour")["revenue"].sum()
        peak_hour = peak_hour_data.idxmax()
        peak_hour_revenue = peak_hour_data.max()

        st.subheader("⏱️ Peak Hour Insights")
        c1, c2 = st.columns(2)
        c1.metric("Peak Revenue Hour", f"{peak_hour}:00")
        c2.metric("Revenue During Peak Hour", f"${peak_hour_revenue:,.0f}")

        hr = filtered.groupby("hour")["revenue"].sum().reset_index()
        fig = px.line(hr, x="hour", y="revenue", markers=True, title="Hourly Revenue Trend")
        fig.add_vline(x=peak_hour, line_dash="dash", line_color="red")
        fig.add_annotation(x=peak_hour, y=peak_hour_revenue, text=f"Peak Hour ({peak_hour}:00)", showarrow=True)
        fig.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("𖠿 Peak Hour Matrix Breakdown by Store")
        peak_store_hour = filtered.groupby(["store_location", "hour"])["revenue"].sum().reset_index()
        peak_store_hour = peak_store_hour.sort_values("revenue", ascending=False).groupby(
            "store_location").first().reset_index()
        st.dataframe(peak_store_hour.rename(columns={"hour": "Peak Hour", "revenue": "Revenue"}),
                     use_container_width=True, hide_index=True)
    else:
        st.warning("Hourly operational dimensions missing inside current data schema logs.")

with tab2:
    store_table["Revenue Rank"] = store_table["Revenue"].rank(ascending=False).astype(int)

    # Isolate formatting columns cleanly for output styling
    ledger_display = store_table[[
        "Revenue Rank", "store_location", "Revenue", "Transactions", "Units", "AOV", "Revenue per Unit"
    ]].copy()

    # RESTRICT SUBSET INTERFACE GRADIENT PATHWAY TO EXCLUDE TEXT OR STRINGS BREAKING CONSTRAINTS
    st.dataframe(
        ledger_display.style.background_gradient(subset=["Revenue", "Transactions", "Units"], cmap="Oranges").format({
            "Revenue": "${:,.2f}",
            "AOV": "${:,.2f}",
            "Revenue per Unit": "${:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

# ---------------------------------------------------
# THEMED EXECUTIVE SUMMARY & RECOMMENDATIONS PANELS
# ---------------------------------------------------
st.divider()
try:
    peak_hour_val = f"{peak_hour}:00"
    peak_hour_rev_val = f"${peak_hour_revenue:,.0f}"
except Exception:
    peak_hour_val, peak_hour_rev_val = "N/A", "$0"

st.markdown(
    f"""
    <div style="
        background-color: #FDFBF7; padding: 24px; border-radius: 12px; border: 1px solid #EFEBE9; border-left: 8px solid {COLOR_BEAN};
        margin-top: 15px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(62, 39, 35, 0.04); font-family: 'Helvetica Neue', sans-serif;
    ">
        <h3 style="margin: 0 0 12px 0; color: {COLOR_BEAN}; font-size: 1.8rem; font-weight: 700;">⫶☰ Peak Hour Executive Summary</h3>
        <ul style="color: #4E342E; font-size: 16px; line-height: 1.8; margin: 0; padding-left: 20px;">
            <li><b>{top_store}</b> is your leading regional asset model hub, anchoring <b>{top_store_share:.1f}%</b> of total network gross income volumes.</li>
            <li>Operational workflows map across <b>{num_stores} active units</b> returning a combined yield framework of <b>${total_revenue:,.0f}</b>.</li>
            <li>Systematic structural peaks focus cleanly around the <b>{peak_hour_val}</b> workflow interval frame.</li>
            <li>This single performance spike hour manages approximately <b>{peak_hour_rev_val}</b> across local transaction cash register ledgers daily.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div style="
        background-color: #FFFDFB; padding: 24px; border-radius: 12px; border: 1px solid #F5EBE6; border-left: 8px solid {COLOR_MOCHA}; 
        margin-bottom: 30px; box-shadow: 0 4px 12px rgba(123, 94, 87, 0.04); font-family: 'Helvetica Neue', sans-serif;
    ">
        <h3 style="margin: 0 0 14px 0; color: #3E2723; font-size: 1.8rem; font-weight: 700;">📌 Strategic Recommendations</h3>
        <ol style="color: #4E342E; font-size: 16px; line-height: 1.8; margin: 0; padding-left: 20px;">
            <li><b>Replicate baseline logistics</b> and inventory management systems from high-performance hub <b>{top_store}</b> onto smaller target areas.</li>
            <li><b>Align floor staffing depth</b> and equipment pre-heating routines actively ahead of the <b>{peak_hour_val}</b> daily bottleneck.</li>
            <li><b>Introduce upselling incentives</b> and bundled snack offerings across locations lagging behind network average values.</li>
            <li><b>Audit local SKU catalog counts</b> monthly against asset velocity performance registers to lower backroom footprint waste patterns.</li>
        </ol>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# CORPORATE SYSTEM FOOTER
# ---------------------------------------------------
st.markdown(
    """
    <div style="text-align: center; padding: 15px 0 25px 0; color: #7B5E57; font-size: 14px; font-weight: 500; letter-spacing: 0.3px; font-family: 'Helvetica Neue', sans-serif;">
        ☕ <b>Afficionado Coffee Roasters</b> | Retail Operations & Location Analytics
        <br>
        <span style="color: #A1887F; font-size: 14px; font-weight: 400; display: inline-block; margin-top: 5px;">
          Store Performance Ranking • Transaction Density & Regional Revenue Benchmarking © 2026
        </span>
        <br>
        <span style="color: #BAA6A1; font-size: 13px; font-weight: 400; display: inline-block; margin-top: 6px; letter-spacing: 0.5px; text-transform: uppercase;">
            ⚡ Powered by: Python • Streamlit • Pandas • Plotly Express
        </span>
    </div>
    """,
    unsafe_allow_html=True
)