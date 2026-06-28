import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Data Explorer | Afficionado Coffee Roasters",
    page_icon="🔍",
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
# ENVIRONMENT AND DIRECTORY RESOLUTION (Cloud-Safe Relative Look-up)
# --------------------------------------------------
CURRENT_SCRIPT_DIR = Path(__file__).resolve().parent
DATA_PATH = CURRENT_SCRIPT_DIR.parent / "outputs" / "cleaned" / "coffee_shop_fe.csv"
CSS_PATH = CURRENT_SCRIPT_DIR.parent / "assets" / "style.css"

if CSS_PATH.exists():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(
            "<style>" + f.read() + "</style>",
            unsafe_allow_html=True
        )


# ---------------------------------------------------
# LOAD DATA WITH SAFE FALLBACK
# ---------------------------------------------------
@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        st.error(f"Dataset not found at targeted cloud route: {DATA_PATH}")
        st.stop()
    return pd.read_csv(DATA_PATH)


df = load_data()

# ---------------------------------------------------
# HEADER (ENHANCED SCALE & BRAND-STYLED)
# ---------------------------------------------------
st.markdown(
    f"""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 25px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
        <h1 style="color: {COLOR_BEAN}; font-size: 3.5rem; font-weight: 800; margin: 0; letter-spacing: -0.5px;">
            🔍 Data Explorer
        </h1>
        <p style="color: #7B5E57; font-size: 1.60rem; font-weight: 600; margin: 10px 0 0 0; letter-spacing: 0.2px;">
            Interactive Exploration of Coffee Shop Transactions
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

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
    Explore transaction records, assess data quality, review metadata, and uncover revenue insights using interactive filters and detailed dataset exploration.
    """
)

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------
st.sidebar.header("Filters")

store_filter = st.sidebar.multiselect(
    "Store Location",
    options=sorted(df["store_location"].dropna().unique()) if not df.empty else [],
    default=sorted(df["store_location"].dropna().unique()) if not df.empty else []
)

category_filter = st.sidebar.multiselect(
    "Product Category",
    options=sorted(df["product_category"].dropna().unique()) if not df.empty else [],
    default=sorted(df["product_category"].dropna().unique()) if not df.empty else []
)
search_product = st.sidebar.text_input("🔍 Search Product")

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------
filtered = df[df["store_location"].isin(store_filter)]
filtered = filtered[filtered["product_category"].isin(category_filter)]

if search_product:
    filtered = filtered[filtered["product_detail"].str.contains(search_product, case=False, na=False)]

if filtered.empty:
    st.warning("No records found for selected filters.")
    st.stop()

# ---------------------------------------------------
# MASTER COMBINED HIGHLIGHT OVERVIEW PANEL
# ---------------------------------------------------
st.markdown(
    f"""
    <h3 style="color: {COLOR_BEAN}; font-size: 1.70rem; font-weight: 500; margin-top: 15px; margin-bottom: 18px; letter-spacing: 0.3px; font-family: 'Helvetica Neue', sans-serif;">
         Data Scope & System Health Metrics
    </h3>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f'<div style="background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase;">Total Rows</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 26px; font-weight: 700;">{len(filtered):,}</h2></div>',
        unsafe_allow_html=True)
with col2:
    st.markdown(
        f'<div style="background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase;">Total Revenue</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 26px; font-weight: 700;">${filtered["revenue"].sum():,.0f}</h2></div>',
        unsafe_allow_html=True)
with col3:
    st.markdown(
        f'<div style="background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #EFEBE9; box-shadow: 0 2px 6px rgba(0,0,0,0.02); text-align: left; font-family: \'Helvetica Neue\', sans-serif;"><span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase;">🛍 Unique Products</span><h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 26px; font-weight: 700;">{filtered["product_id"].nunique()}</h2></div>',
        unsafe_allow_html=True)

st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------
# DATASET HEALTH OVERVIEW EXPANDER
# ---------------------------------------------------
with st.expander("📋 Dataset Health Overview", expanded=False):
    date_cols = [col for col in df.columns if "date" in col.lower()]
    if len(date_cols) > 0:
        date_col = date_cols[0]
        start_date = pd.to_datetime(df[date_col]).min()
        end_date = pd.to_datetime(df[date_col]).max()
        st.markdown(
            f"""
            **📅 Dataset Coverage**
            * Start Date: {start_date.date()}
            * End Date: {end_date.date()}
            * Total Days Covered: {(end_date - start_date).days}
            """
        )

    st.markdown(
        f"""
        **Dataset Metadata**
        * Total Records: {len(df):,}
        * Total Features: {len(df.columns)}
        * Memory Usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB
        """
    )
    st.markdown(
        '<div style="padding:12px 0px; color:#4E342E; font-size:15px; font-weight:500;">Quick assessment of dataset quality readiness for analysis.</div>',
        unsafe_allow_html=True)

    missing_values = df.isna().sum().sum()
    duplicate_rows = df.duplicated().sum()

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("Rows", f"{len(df):,}")
    with k2: st.metric("Columns", len(df.columns))
    with k3: st.metric("Missing Values", missing_values)
    with k4: st.metric("Duplicate Rows", duplicate_rows)

st.divider()

# ---------------------------------------------------
# EXPLORER TAB SYSTEMS LAYER
# ---------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Data Preview",
    "🧹 Data Quality",
    "📚 Data Dictionary",
    "📊 Data Insights"
])

with tab1:
    st.subheader("Transaction Data Explorer")
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_columns = st.multiselect("Select Columns", filtered.columns.tolist(),
                                          default=filtered.columns.tolist()[:8])
    with col2:
        selected_column = st.selectbox("Column Summary Descriptive Focus", filtered.columns)

    st.markdown(
        f"<div style='font-size:15px; color:{COLOR_BEAN}; font-weight:600; margin-bottom:8px;'>📋 Summary statistics for {selected_column}</div>",
        unsafe_allow_html=True)
    st.write(filtered[selected_column].describe())

    display_df = filtered[selected_columns].copy()
    if "revenue" in display_df.columns:
        display_df["revenue"] = display_df["revenue"].map(lambda x: f"${x:,.2f}")

    st.dataframe(display_df, use_container_width=True, height=500, hide_index=True)

with tab2:
    st.subheader("Data Quality Assessment")
    missing_values = df.isna().sum().sum()
    duplicate_rows = df.duplicated().sum()

    q1, q2, q3, q4 = st.columns(4)
    with q1:
        st.metric("Missing Values", f"{missing_values:,}")
    with q2:
        st.metric("Duplicate Rows", f"{duplicate_rows:,}")
    with q3:
        st.metric("Columns", len(df.columns))
    with q4:
        st.metric("Records", f"{len(df):,}")

    st.divider()
    st.subheader("Missing Values Analysis")
    null_df = pd.DataFrame({
        "Column": df.columns,
        "Missing Values": df.isna().sum().values,
        "Missing %": (df.isna().sum() / len(df) * 100).round(2)
    })
    st.dataframe(null_df.sort_values("Missing Values", ascending=False), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Schema Overview")
    dtype_df = pd.DataFrame({"Column": df.columns, "Data Type": df.dtypes.astype(str)})
    st.dataframe(dtype_df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Dataset Quality Status")
    if missing_values == 0 and duplicate_rows == 0:
        status_text = "<b>Dataset Status:</b> Passed health validation checks. No missing values or duplicate records detected safely."
    elif missing_values > 0 and duplicate_rows == 0:
        status_text = f"<b>Dataset Warning:</b> {missing_values:,} missing values detected. Review affected metrics before final deep-dive analysis."
    elif duplicate_rows > 0 and missing_values == 0:
        status_text = f"<b>Dataset Warning:</b> {duplicate_rows:,} duplicate records detected. Deduplication recommended."
    else:
        status_text = f"<b>Dataset Critical Alert:</b> {missing_values:,} missing entries alongside {duplicate_rows:,} duplicate records detected."

    # PATCHED: Added the missing closing </div> tag to preserve page layouts
    st.markdown(
        f"""
        <div style="
            background-color: #FDFBF7; padding: 24px; border-radius: 12px; border: 1px solid #EFEBE9; border-left: 8px solid {COLOR_BEAN};
            margin-top: 15px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(62, 39, 35, 0.04); font-family: 'Helvetica Neue', sans-serif;
        ">\n<div style="font-size: 16px; color: #4E342E; line-height: 1.6; padding: 5px 0px;">⚠️ {status_text}</div>\n</div>
        """,
        unsafe_allow_html=True
    )

with tab3:
    st.subheader("Data Dictionary")
    st.caption("Business glossary and metadata reference for all fields used across the dashboard.")

    dictionary = pd.DataFrame({
        "Column": ["transaction_id", "transaction_date", "transaction_time", "store_location", "product_category",
                   "product_type", "product_detail", "transaction_qty", "unit_price", "revenue", "hour"],
        "Description": ["Unique transaction identifier", "Date of customer purchase", "Time of transaction",
                        "Store branch location", "High-level product grouping", "Product sub-category",
                        "Individual product SKU", "Units purchased", "Selling price per unit",
                        "Total revenue generated", "Hour extracted from transaction time"],
        "Data Type": ["Integer", "Date", "Time", "Categorical", "Categorical", "Categorical", "Categorical", "Integer",
                      "Float", "Float", "Integer"],
        "Business Use": ["Transaction tracking", "Trend analysis", "Peak hour analysis", "Store performance analysis",
                         "Category analysis", "Product mix analysis", "Pareto analysis", "Demand measurement",
                         "Pricing analysis", "Revenue analysis", "Operational planning"]
    })

    search_column = st.text_input("🔍 Search Metadata Fields")
    if search_column:
        dictionary = dictionary[dictionary["Column"].str.contains(search_column, case=False, na=False)]

    st.dataframe(dictionary, use_container_width=True, hide_index=True, height=400)

with tab4:
    st.subheader("Revenue Distribution Analysis")
    st.caption(
        "Analyze transaction value patterns, spending behavior, and revenue concentration across all customer purchases.")

    r1, r2, r3, r4 = st.columns(4)
    with r1: st.metric("Average Revenue", f"${filtered['revenue'].mean():.2f}")
    with r2: st.metric("Median Revenue", f"${filtered['revenue'].median():.2f}")
    with r3: st.metric("Highest Transaction", f"${filtered['revenue'].max():.2f}")
    with r4: st.metric("Lowest Transaction", f"${filtered['revenue'].min():.2f}")

    st.divider()

    fig = px.histogram(filtered, x="revenue", nbins=30, color_discrete_sequence=[COLOR_MOCHA],
                       title="Transaction Revenue Distribution Pattern")
    fig.update_layout(
        template="plotly_white", height=450, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Revenue Check Volume ($)", yaxis_title="Transaction Frequency Count"
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

    st.divider()
    st.subheader("Revenue Percentile Breakdown")
    q2 = filtered["revenue"].quantile(0.50)
    q3 = filtered["revenue"].quantile(0.75)

    q_df = pd.DataFrame({
        "Metric": ["25th Percentile", "Median (50%)", "75th Percentile"],
        "Revenue": [f"${filtered['revenue'].quantile(0.25):.2f}", f"${q2:.2f}", f"${q3:.2f}"]
    })
    st.dataframe(q_df, use_container_width=True, hide_index=True)
    st.divider()

    st.markdown(
        f"""
        <div style="
            background-color: #FDFBF7; padding: 24px; border-radius: 12px; border: 1px solid #EFEBE9; border-left: 8px solid {COLOR_BEAN};
            margin-top: 15px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(62, 39, 35, 0.04); font-family: 'Helvetica Neue', sans-serif;
            ">
            <h3 style="margin: 0 0 14px 0; color: #3E2723; font-size: 1.50rem; font-weight: 700;">⬩➤ Revenue Distribution Insights</h3>
            <div style="font-size: 16px; color: #4E342E; line-height: 1.8; display: flex; flex-direction: column; gap: 8px;">
                <div><b>Average Baseline:</b> The global average transaction value yields exactly <b>${filtered['revenue'].mean():.2f}</b> per customer visit.</div>
                <div style="border-top: 1px dashed #EFEBE9; padding-top: 8px;"><b>Median Threshold:</b> 50% of entire filtered customer ticket bills generate less than <b>${q2:.2f}</b>.</div>
                <div style="border-top: 1px dashed #EFEBE9; padding-top: 8px;"><b>Premium Segment:</b> High-ticket purchases surpassing the 75th percentile line of <b>${q3:.2f}</b> isolate your high-value target core segment.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# DOWNLOAD CENTER LAYER
# ---------------------------------------------------
st.subheader("⬇ Export Corporate Datasets")
st.download_button("Download Filtered Dataset (CSV)", filtered.to_csv(index=False), "filtered_dataset.csv", "text/csv")

# ---------------------------------------------------
# FOOTER SYSTEM
# ---------------------------------------------------
st.markdown(
    """
    <div style="text-align: center; padding: 15px 0 25px 0; color: #7B5E57; font-size: 14px; font-weight: 500; letter-spacing: 0.3px; font-family: 'Helvetica Neue', sans-serif;">
        ☕ <b>Afficionado Coffee Roasters</b> | Granular Data Exploration Hub
        <br>
        <span style="color: #A1887F; font-size: 14px; font-weight: 400; display: inline-block; margin-top: 5px;">
         Dataset Schema Mining • Custom Multi-Dimensional Filtering & Raw Ledger Auditing © 2026
        </span>
        <br>
        <span style="color: #BAA6A1; font-size: 13px; font-weight: 400; display: inline-block; margin-top: 6px; letter-spacing: 0.5px; text-transform: uppercase;">
            ⚡ Powered by: Python • Streamlit • Pandas • Plotly Express
        </span>
    </div>
    """,
    unsafe_allow_html=True
)