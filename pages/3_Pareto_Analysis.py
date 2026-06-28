from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Pareto Analysis | Afficionado Coffee Roasters",
    page_icon="📈",
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
# CUSTOM CSS
# ---------------------------------------------------

CSS_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "style.css"
)

# ---------------------------------------------------
# CUSTOM CSS LOADING CENTER (FIXED CRASH-PROOF)
# ---------------------------------------------------
if CSS_PATH.exists():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        # Removed the 'f' prefix to isolate the file string from Python's variable parser
        st.markdown(
            "<style>" + f.read() + "</style>",
            unsafe_allow_html=True
        )

# ---------------------------------------------------
# PATHS & DATA
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "outputs" / "cleaned" / "coffee_shop_fe.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

df = load_data()

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

# ---------------------------------------------------
# HEADER (CENTERED & BRAND-STYLED)
# ---------------------------------------------------
st.markdown(
    f"""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 25px;">
        <h1 style="color: {COLOR_BEAN}; font-size: 3.5rem; font-weight: 800; margin: 0; letter-spacing: -0.5px;">
            🎢 Pareto Analysis
        </h1>
        <p style="color: #7B5E57; font-size: 1.60rem; font-weight: 800; margin: 10px 0 0 0; letter-spacing: 0.2px;">
            Revenue Concentration & Menu Balance
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

st.markdown(
    """
    <div style="
        padding:20px;
        border-radius:12px;
        background-color:white;
        box-shadow:0px 2px 8px rgba(0,0,0,0.05);
        margin-bottom:20px;
        border-left: 6px solid #3E2723;
    ">
        <h3 style="
    color:#3E2723;
    margin-top:0;
    font-size:30px;
    ">
    Analysis Objectives
    </h3>
        <ul style="
    color:#424242;
    line-height:1.6;
    font-size:20px;
    ">
 <li>Measure revenue concentration across products</li>
            <li>Identify hero products driving majority of sales</li>
            <li>Highlight long-tail products with minimal impact</li>
            <li>Support menu simplification and risk evaluation</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------
st.sidebar.markdown(
    """
    <h3 style="
        color:#3E2723;
        font-size:1.3rem;
        font-weight:600;
        margin-bottom:10px;
    ">
         About This Page
    </h3>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    """
Analyze revenue concentration, identify hero products, and evaluate how a small group of items drives overall business performance.

    """
)


st.sidebar.title("🎢 Pareto Filters")

store_filter = st.sidebar.multiselect(
    "Store Location",
    options=sorted(df["store_location"].dropna().unique()),
    default=sorted(df["store_location"].dropna().unique())
)

category_filter = st.sidebar.multiselect(
    "Product Category",
    options=sorted(df["product_category"].dropna().unique()),
    default=sorted(df["product_category"].dropna().unique())
)

filtered = df[df["store_location"].isin(store_filter)]
filtered = filtered[filtered["product_category"].isin(category_filter)]


# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

total_revenue = filtered["revenue"].sum()

# GLOBAL DEFINITION: Calculate category totals first so the entire page can use them safely
if not filtered.empty:
    category_rev = (
        filtered.groupby("product_category")["revenue"]
        .sum()
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
else:
    category_rev = pd.DataFrame(columns=["product_category", "revenue"])

# Your base group sorting sequence continues downstream smoothly...
pareto = (
    filtered
    .groupby("product_detail")["revenue"]
    .sum()
    .reset_index()
    .sort_values(
        "revenue",
        ascending=False
    )
    .reset_index(drop=True)
)

pareto["share"] = (
    pareto["revenue"]
    /
    pareto["revenue"].sum()
)

pareto["cum_share"] = (
    pareto["share"]
    .cumsum()
    * 100
)

hero_product = pareto.iloc[0]["product_detail"]

top_products_80 = len(
    pareto[
        pareto["cum_share"] <= 80
    ]
)

revenue_concentration = (
    pareto.head(
        max(
            1,
            int(len(pareto) * 0.20)
        )
    )["revenue"].sum()
    /
    pareto["revenue"].sum()
) * 100

avg_product_revenue = (
    pareto["revenue"]
    .mean()
)
# NEW EXTENSION: Explicit Data Slicing for Side-by-Side Tables
if not filtered.empty:
    # Anchor SKUs are those whose cumulative share up to that item is <= 80%
    # (Or include the first item crossing the boundary to make up exactly 80%)
    anchor_base = filtered.groupby(["product_category", "product_detail"])["revenue"].sum().reset_index()
    anchor_base = anchor_base.sort_values(by="revenue", ascending=False).reset_index(drop=True)
    anchor_base["share"] = anchor_base["revenue"] / anchor_base["revenue"].sum()
    anchor_base["cum_share"] = anchor_base["share"].cumsum() * 100

    # Split using the 80% logical index rule matching your Figure C threshold lines
    anchor_skus_df = anchor_base[anchor_base["cum_share"] <= 80.0001].copy()
    long_tail_skus_df = anchor_base[anchor_base["cum_share"] > 80.0001].copy()

    # Format currency strings cleanly for the data tables
    for target_df in [anchor_skus_df, long_tail_skus_df]:
        target_df["Revenue Share %"] = (target_df["share"] * 100).round(2).map("{:.2f}%".format)
        target_df["revenue"] = target_df["revenue"].map("${:,.2f}".format)
        target_df.drop(columns=["share", "cum_share"], errors="ignore", inplace=True)
        target_df.columns = ["Category", "Product SKU Nomenclature", "Gross Returns", "Revenue Share"]
else:
    anchor_skus_df = pd.DataFrame(columns=["Category", "Product SKU Nomenclature", "Gross Returns", "Revenue Share"])
    long_tail_skus_df = pd.DataFrame(columns=["Category", "Product SKU Nomenclature", "Gross Returns", "Revenue Share"])

hero_product = pareto.iloc[0]["product_detail"] if not pareto.empty else "N/A"

# ---------------------------------------------------
# HIGH-PROMINENCE 4-COLUMN KPI CARDS GRID
# ---------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f"""
        <div style="
            background-color: white;
            padding: 20px 16px;
            border-radius: 12px;
            border: 1px solid #EFEBE9;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
            text-align: left;
        ">
            <span style="color: #757575; font-size: 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;"> Revenue Concentration </span>
            <h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 30px; font-weight: 600;">{revenue_concentration:.1f}%</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with k2:
    st.markdown(
        f"""
        <div style="
            background-color: white;
            padding: 20px 16px;
            border-radius: 12px;
            border: 1px solid #EFEBE9;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
            text-align: left;
        ">
            <span style="color: #757575; font-size: 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;"> Products Driving 80% of Revenue </span>
            <h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 28px; font-weight: 600;">{top_products_80}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with k3:
    st.markdown(
        f"""
        <div style="
            background-color: white;
            padding: 20px 16px;
            border-radius: 12px;
            border: 1px solid #EFEBE9;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
            text-align: left;
        ">
            <span style="color: #757575; font-size: 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;"> Hero Product</span>
            <h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 24px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{hero_product}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with k4:
    st.markdown(
        f"""
        <div style="
            background-color: white;
            padding: 20px 16px;
            border-radius: 12px;
            border: 1px solid #EFEBE9;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
            text-align: left;
        ">
            <span style="color: #757575; font-size: 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;"> Avg Revenue per Product </span>
            <h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 28px; font-weight: 600;">${avg_product_revenue:,.0f}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)
st.divider()
# ---------------------------------------------------
# PARETO ANALYSIS
# ---------------------------------------------------

import plotly.graph_objects as go

# ---------------------------------------------------
# SUBSECTION HEADER (ENHANCED LEFT-ALIGNED SCALE)
# ---------------------------------------------------
st.markdown(
    f"""
    <h2 style="
        text-align: left; 
        margin: 25px 0 15px 0; 
        color: {COLOR_BEAN}; 
        font-size: 2.4rem; 
        font-weight: 620;
        letter-spacing: -0.5px;
    ">
        🎢 Pareto Analysis
    </h2>
    """,
    unsafe_allow_html=True
)

pareto = (
    filtered
    .groupby("product_detail")["revenue"]
    .sum()
    .reset_index()
    .sort_values(
        "revenue",
        ascending=False
    )
)

# Revenue Share
pareto["share"] = (
    pareto["revenue"]
    /
    pareto["revenue"].sum()
)

# Cumulative Share
pareto["cum_share"] = (
    pareto["share"]
    .cumsum()
    * 100
)

# Product Rank
pareto["rank"] = range(
    1,
    len(pareto) + 1
)

# Create Figure
fig = go.Figure()

# Revenue Bars (UNCHANGED Original Color)
fig.add_bar(
    x=pareto["rank"],
    y=pareto["revenue"],
    name="Revenue",
)

# Cumulative Curve (UNCHANGED Original Color)
fig.add_trace(
    go.Scatter(
        x=pareto["rank"],
        y=pareto["cum_share"],
        mode="lines+markers",
        name="Cumulative %",
        yaxis="y2"
    )
)

# 80% Threshold (UNCHANGED Original Color)
fig.add_hline(
    y=80,
    line_dash="dash",
    line_color="red",
    annotation_text="80% Threshold",
    yref="y2"
)

fig.update_layout(
    height=600,
    template="plotly_white",
    title="Pareto Analysis of Product Revenue",
    xaxis=dict(
        title="Products Ranked by Revenue"
    ),
    yaxis=dict(
        title="Revenue ($)"
    ),
    yaxis2=dict(
        title="Cumulative Revenue %",
        overlaying="y",
        side="right",
        range=[0, 105]
    ),
    legend=dict(
        orientation="h",
        y=1.1
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)
# ---------------------------------------------------
# SINGLE-ROW CONTEXTUAL INSIGHT TEXT UNDERNEATH CHART
# ---------------------------------------------------
st.markdown(
    """
    <div style="
        padding: 10px 0px; 
        margin-top: 8px;
        margin-bottom: 25px;
    ">
        <h4 style="margin: 0 0 14px 0; color: #3E2723; font-size: 18px; font-weight: 600; letter-spacing: 0.3px;">
            ➤ Decoding the Pareto Concentration Chart
        </h4>
        <div style="font-size: 16px; color: #4E342E; line-height: 1.8; display: flex; flex-direction: column; gap: 8px;">
            <div>
                ● <b>The Descending Bars:</b> These evaluate individual revenue generated by each unique product variant SKU, sorted cleanly from peak volume down to baseline.
            </div>
            <div style="border-top: 1px dashed #EFEBE9; padding-top: 8px;">
                ● <b>The Cumulative Curve:</b> This tracks the running percentage share total as it aggregates toward the 100% ceiling.
            </div>
            <div style="border-top: 1px dashed #EFEBE9; padding-top: 8px;">
                ● <b>The 80% Threshold Guideline:</b> Where the curve crosses this baseline highlights your vital menu anchors, mathematically proving how a narrow selection of offerings drives the vast majority of business financial returns.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")
# ---------------------------------------------------
# PARETO INSIGHTS
# ---------------------------------------------------

top_20_count = max(
    1,
    int(len(pareto) * 0.20)
)

concentration = (
    pareto.head(top_20_count)["revenue"].sum()
    /
    pareto["revenue"].sum()
) * 100

hero_product = pareto.iloc[0]["product_detail"]
hero_revenue = pareto.iloc[0]["revenue"]

# ---------------------------------------------------
# EXECUTIVE INTERPRETATION PANEL (UPDATED AND THEMED)
# ---------------------------------------------------
st.markdown(
    f"""
    <div style="
        background-color: #FDFBF7; 
        padding: 24px; 
        border-radius: 12px; 
        border: 1px solid #EFEBE9; 
        border-left: 8px solid {COLOR_BEAN};
        margin-top: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(62, 39, 35, 0.04);
    ">
        <h3 style="margin: 0 0 12px 0; color: {COLOR_BEAN}; font-size: 1.8rem; font-weight: 700;">
            ★ Executive Interpretation
        </h3>
        <p style="color: #5D4037; font-size: 20px; line-height: 1.6; margin-bottom: 8px; font-weight: 600;">
            What the Pareto Analysis Shows:
        </p>
        <ul style="color: #4E342E; font-size: 18px; line-height: 1.7; margin: 0; padding-left: 20px;">
            <li>The highest revenue generating product is <b>{hero_product}</b>.</li>
            <li>The top 20% of products contribute approximately <b>{concentration:.1f}%</b> of total revenue.</li>
            <li>Only <b>{top_products_80} products</b> are required to generate 80% of revenue.</li>
            <li>Products on the left side of the chart drive most of the business value.</li>
            <li>Products on the far right contribute very little revenue and should be reviewed.</li>
            <li>Management should continuously monitor hero products and reduce concentration risk.</li>
            <li>This analysis helps identify menu optimization opportunities and revenue concentration risk.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# OPERATIONAL RECOMMENDATIONS PANEL (UPDATED AND THEMED)
# ---------------------------------------------------
st.markdown(
    f"""
    <div style="
        background-color: #FFFDFB; 
        padding: 24px; 
        border-radius: 12px; 
        border: 1px solid #F5EBE6; 
        border-left: 8px solid {COLOR_MOCHA}; 
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(123, 94, 87, 0.04);
    ">
        <h3 style="margin: 0 0 14px 0; color: #3E2723; font-size: 1.8rem; font-weight: 700;">
            𓂃🖋 Recommendations
        </h3>
        <ol style="color: #4E342E; font-size: 18px; line-height: 1.7; margin: 0; padding-left: 20px;">
            <li><b>Protect hero products</b> with strong inventory availability.</li>
            <li><b>Increase promotion</b> of top-performing products.</li>
            <li><b>Bundle medium-performing products</b> alongside hero products.</li>
            <li><b>Review bottom-performing products</b> for potential removal.</li>
            <li><b>Track revenue concentration</b> monthly to significantly reduce macro business risk.</li>
        </ol>
    </div>
    """,
    unsafe_allow_html=True
)

top_contributors = pareto[
    pareto["cum_share"] <= 80
].copy()

top_contributors["Revenue Share %"] = (
    top_contributors["share"] * 100
)

top_contributors = (
    top_contributors[
        [
            "product_detail",
            "revenue",
            "Revenue Share %",
            "cum_share"
        ]
    ]
)

st.subheader("𝄜 Products Driving 80% Revenue")

st.dataframe(
    top_contributors,
    use_container_width=True,
    hide_index=True
)

# =========================================================================
# NEW EXTENSION: SIDE-BY-SIDE PORTFOLIO EXPLICIT CATEGORIZATION INTERFACE
# =========================================================================
st.markdown("---")
st.markdown(
    f"""
    <h2 style="color: {COLOR_BEAN}; font-size: 1.75rem; font-weight: 700; margin-bottom: 4px;">
        📋 Explicit Asset Portfolio Mapping (Vital Core vs. Long Tail)
    </h2>
    """,
    unsafe_allow_html=True
)
st.markdown(
    f"""
    <div style="
        background-color: #FDFBF7;
        border-left: 5px solid {COLOR_BEAN};
        border: 1px solid #EFEBE9;
        padding: 18px 22px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.01);
        margin-bottom: 20px;
    ">
        <p style="
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 18px;
            line-height: 1.6;
            color: #4E342E;
            margin: 0;
        ">
            This table clears up menu confusion by showing your 
            <strong style="color: {COLOR_BEAN};">Top-Selling Items (Vital Revenue Anchors)</strong> directly next to your 
            <strong style="color: {COLOR_BEAN};">Slow-Moving Items (Underperforming Long Tail)</strong>. By comparing them side-by-side, 
            management can instantly see which products are worth keeping, which should be bundled together, 
            and which ones should be removed from the menu completely.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
# =========================================================================
# PRODUCTION-GRADE SIDE-BY-SIDE ASSET DISAGGREGATION INTERFACE
# =========================================================================

# 1. Compute dynamic group totals for in-header metrics card context
if not anchor_skus_df.empty:
    # Safely strip formatting if already mapped, otherwise sum numeric values
    try:
        anchor_rev_total = anchor_base[anchor_base["cum_share"] <= 80.0001]["revenue"].sum()
        tail_rev_total = anchor_base[anchor_base["cum_share"] > 80.0001]["revenue"].sum()
    except Exception:
        anchor_rev_total = total_revenue * 0.80  # Fallback mathematical approximation
        tail_rev_total = total_revenue * 0.20

    anchor_count = len(anchor_skus_df)
    tail_count = len(long_tail_skus_df)
else:
    anchor_rev_total, tail_rev_total, anchor_count, tail_count = 0, 0, 0, 0

# 2. Establish side-by-side execution columns layout
split_col1, split_col2 = st.columns(2)

with split_col1:
    # Refined Minimalist Vital Core Card
    st.markdown(
        f"""
        <div style="
            background-color: white; 
            padding: 16px 20px; 
            border: 1px solid #EFEBE9;
            border-left: 6px solid #2E7D32;
            border-radius: 12px 12px 0 0;
            margin-bottom: 0px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; color: #1B5E20; font-size: 1.45rem; font-weight: 700;">
                    ☆ Vital Core Anchors
                </h4>
                <span style="background-color: #E8F5E9; color: #2E7D32; font-size: 18px; font-weight: 700; padding: 3px 8px; border-radius: 20px;">
                    {anchor_count} Active SKUs
                </span>
            </div>
            <p style="margin: 6px 0 0 0; font-size: 16px; color: #616161; line-height: 1.4;">
                Core menu items capturing roughly 80% of aggregate enterprise financial inflow.
            </p>
            <div style="margin-top: 10px; font-size: 17px; font-weight: 700; color: #1B5E20;">
                Group Revenue Yield: ${anchor_rev_total:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Auto-sized and padded dataframe config
    st.dataframe(
        anchor_skus_df,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "Category": st.column_config.TextColumn("Category Group", width="small"),
            "Product SKU Nomenclature": st.column_config.TextColumn("Product Menu Item", width="medium"),
            "Gross Returns": st.column_config.TextColumn("Revenue ($)", width="small"),
            "Revenue Share": st.column_config.TextColumn("Share", width="small")
        }
    )

with split_col2:
    # Refined Minimalist Over-Diversified Long Tail Card
    st.markdown(
        f"""
        <div style="
            background-color: white; 
            padding: 16px 20px; 
            border: 1px solid #EFEBE9;
            border-left: 6px solid #C62828;
            border-radius: 12px 12px 0 0;
            margin-bottom: 0px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; color: #B71C1C; font-size: 1.45rem; font-weight: 700;">
                    ⚠ Over-Diversified Long Tail
                </h4>
                <span style="background-color: #FFEBEE; color: #C62828; font-size: 18px; font-weight: 700; padding: 3px 8px; border-radius: 20px;">
                    {tail_count} Drag SKUs
                </span>
            </div>
            <p style="margin: 6px 0 0 0; font-size: 16px; color: #616161; line-height: 1.4;">
                Slow-moving inventory layers candidate for immediate menu pruning or bundling.
            </p>
            <div style="margin-top: 10px; font-size: 17px; font-weight: 700; color: #B71C1C;">
                Group Revenue Yield: ${tail_rev_total:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Auto-sized and padded dataframe config
    st.dataframe(
        long_tail_skus_df,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "Category": st.column_config.TextColumn("Category Group", width="small"),
            "Product SKU Nomenclature": st.column_config.TextColumn("Product Menu Item", width="medium"),
            "Gross Returns": st.column_config.TextColumn("Revenue ($)", width="small"),
            "Revenue Share": st.column_config.TextColumn("Share", width="small")
        }
    )
# =========================================================================
# NEW EXTENSION: DYNAMIC MENU DIVERSIFICATION RISK & STRESS-TEST ENGINE
# =========================================================================
st.markdown("---")
st.markdown(
    f"""
    <h2 style="color: {COLOR_BEAN}; font-size: 1.85rem; font-weight: 700; margin-bottom: 4px;">
        ☣️ Menu Diversification Risk & Stress-Test Simulator
    </h2>
    """,
    unsafe_allow_html=True
)

st.markdown(f"""
    <div style="background-color: #FDFBF7; padding: 15px 20px; border: 1px solid #EFEBE9; border-radius: 8px;  font-size: 18px; margin-bottom: 15px;">
        <span style="font-weight: 500; color: {COLOR_BEAN};">Because your business relies heavily on core beverage pillars, shocks to your primary supply chain 
    or commuter changes represent structural threats. Use this simulator to stress-test your portfolio baseline.</span> 
    </div>
""", unsafe_allow_html=True)

# 1. Isolate the top category name and its total revenue share dynamically
if not filtered.empty:
    top_category_name = category_rev.iloc[0]["product_category"]
    top_category_rev_actual = category_rev.iloc[0]["revenue"]
    top_cat_share_pct = (top_category_rev_actual / total_revenue) * 100
else:
    top_category_name = "Coffee"
    top_category_rev_actual = 0
    top_cat_share_pct = 0

# 2. Build user-interactive simulation controls inside an explicit container card
st.markdown(f"""
    <div style="
        background-color: #FDFBF7; 
        padding: 18px 22px; 
        border: 1px solid #EFEBE9; 
        border-radius: 8px; 
        margin-bottom: 20px;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 18px;
        line-height: 1.5;
    ">
        <span style="font-weight: 700; color: {COLOR_BEAN};">Active Risk Profile:</span> 
        Your top category <span style='color: #B71C1C; font-weight: 700;'>{top_category_name}</span> accounts for 
        <span style='color: #B71C1C; font-weight: 700;'>{top_cat_share_pct:.2f}%</span> of all corporate cash intake.
    </div>
""", unsafe_allow_html=True)
# Interactive Stress-Test Slider
decline_pct = st.slider(
    f"Simulate a sudden Market Decline in '{top_category_name}' (%)",
    min_value=0,
    max_value=100,
    value=25,
    step=5,
    help="Simulates a major drop in top-line coffee sales due to supply shocks, crop disease, or inflation."
)

# 3. Compute Simulated Mathematical Realities
simulated_top_cat_rev = top_category_rev_actual * (1 - (decline_pct / 100))
revenue_loss = top_category_rev_actual - simulated_top_cat_rev
simulated_total_revenue = total_revenue - revenue_loss

# Evaluate New Risk Scores
new_top_cat_share = (simulated_top_cat_rev / simulated_total_revenue * 100) if simulated_total_revenue > 0 else 0

# Determine Institutional Risk Rating Bounds
if top_cat_share_pct > 35 and decline_pct < 30:
    risk_status = "⚠️ ELEVATED DEPENDENCY"
    risk_color = "#EF6C00" # Amber
elif decline_pct >= 30:
    risk_status = "🚨 SEVERE PORTFOLIO CRASH"
    risk_color = "#C62828" # Red
else:
    risk_status = "✅ STABLE BALANCE"
    risk_color = "#2E7D32" # Green

# 4. Display Simulation Impact Dashboard Grid
sc1, sc2, sc3 = st.columns(3)

with sc1:
    st.markdown(
        f"""
        <div style="background-color: white; padding: 16px; border: 1px solid #EFEBE9; border-radius: 8px; text-align: left;">
            <span style="color: #757575; font-size: 16px; font-weight: 600; text-transform: uppercase;">Simulated Revenue Loss</span>
            <h3 style="color: #C62828; margin: 4px 0 0 0; font-size: 24px; font-weight: 700;">-${revenue_loss:,.2f}</h3>
            <p style="margin: 2px 0 0 0; font-size: 18px; color: #757575;">Drop in top-line cash flow</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with sc2:
    st.markdown(
        f"""
        <div style="background-color: white; padding: 16px; border: 1px solid #EFEBE9; border-radius: 8px; text-align: left;">
            <span style="color: #757575; font-size: 16px; font-weight: 600; text-transform: uppercase;">New Total Revenue</span>
            <h3 style="color: #3E2723; margin: 4px 0 0 0; font-size: 24px; font-weight: 700;">${simulated_total_revenue:,.2f}</h3>
            <p style="margin: 2px 0 0 0; font-size: 18px; color: #757575;">Adjusted corporate yield</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with sc3:
    st.markdown(
        f"""
        <div style="background-color: white; padding: 16px; border: 1px solid #EFEBE9; border-radius: 8px; text-align: left;">
            <span style="color: #757575; font-size: 18px; font-weight: 600; text-transform: uppercase;">System Threat Level</span>
            <h3 style="color: {risk_color}; margin: 4px 0 0 0; font-size: 24px; font-weight: 700;">{risk_status}</h3>
            <p style="margin: 2px 0 0 0; font-size: 16px; color: #757575;">New {top_category_name} Share: {new_top_cat_share:.1f}%</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# 5. Contextual Actionable Insights Generated Based on User Input

if decline_pct > 0:
    try:
        bakery_base = category_rev[category_rev['product_category'] == 'Bakery'].iloc[0]['revenue']
        bakery_boost_pct = (revenue_loss / bakery_base * 100) if bakery_base > 0 else 0
    except Exception:
        bakery_boost_pct = 0

    st.markdown(
        f"""
        <div style="
            background-color: #FFFDEB;
            border-left: 5px solid #EF6C00;
            border: 1px solid #FFF3E0;
            padding: 16px 20px;
            border-radius: 8px;
            margin-top: 15px;
            margin-bottom: 25px;
            box-shadow: 0 2px 6px rgba(239, 108, 0, 0.02);
        ">
            <p style="
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 17px;
                font-weight: 530;
                line-height: 1.6;
                color: #4E342E;
                margin: 0;
            ">
                <strong>Data Analyst Strategic Insight:</strong> A {decline_pct}% drop in '{top_category_name}' 
                wipes out <strong style="color: #B71C1C;">${revenue_loss:,.2f}</strong> in gross receipts. To absorb this shock, 
                the business must aggressively scale secondary revenue streams—specifically boosting underperforming 
                <em style="color: {COLOR_BEAN}; font-weight: 600;">Bakery</em> impulse sales by at least 
                <strong style="color: #2E7D32;">{bakery_boost_pct:.1f}%</strong> to maintain original capital margins.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown(
    """
    <div style="text-align: center; padding: 15px 0 25px 0; color: #7B5E57; font-size: 14px; font-weight: 500; letter-spacing: 0.3px;">
        ☕ <b>Afficionado Coffee Roasters</b> | Revenue Concentration Analytics
        <br>
        <span style="color: #A1887F; font-size: 14px; font-weight: 400; display: inline-block; margin-top: 5px;">
          The 80/20 Rule Principle • Core Category Dependency & Risk Mitigation Review © 2026
        </span>
        <br>
        <span style="color: #BAA6A1; font-size: 13px; font-weight: 400; display: inline-block; margin-top: 6px; letter-spacing: 0.5px; text-transform: uppercase;">
            ⚡ Powered by: Python • Streamlit • Pandas • Plotly Express
        </span>
    </div>
    """,
    unsafe_allow_html=True
)
