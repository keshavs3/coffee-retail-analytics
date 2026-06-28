from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Product Analysis | Afficionado Coffee Roasters",
    page_icon="📦",
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
CAFE_PIE_COLORS = [COLOR_BEAN, COLOR_MOCHA, COLOR_LATTE, COLOR_CREMA, "#EFEBE9"]

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
else:
    # Safe production string fallback rule to prevent any unhandled file errors
    st.markdown(
        """
        <style>
            .brand-container-box {
                background-color: #FDFBF7;
                border: 1px solid #EFEBE9;
                border-left: 6px solid #5D4037;
                padding: 22px;
                border-radius: 12px;
                margin-bottom: 20px;
            }
        </style>
        """,
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

# Global safeguard extracting unique lists before filter processing engine runs
if not df.empty:
    all_stores = sorted(df["store_location"].dropna().unique())
    all_categories = sorted(df["product_category"].dropna().unique())
else:
    all_stores = []
    all_categories = []
df = df.drop_duplicates()


# NEW EXTENSION: Vectorized Product Efficiency Score Calculator
def compute_product_efficiency_score(data_frame: pd.DataFrame, groupby_column: str) -> pd.DataFrame:
    """
    Computes the Product Efficiency Score (Gross Revenue per unique SKU).
    Formula: Total Gross Revenue Grouped / Count of Unique Active Product IDs
    """
    if data_frame.empty:
        return pd.DataFrame(columns=[groupby_column, "total_revenue", "unique_skus", "product_efficiency_score"])

    efficiency_df = data_frame.groupby(groupby_column).agg(
        total_revenue=('revenue', 'sum'),
        unique_skus=('product_id', 'nunique')
    ).reset_index()

    efficiency_df['product_efficiency_score'] = (
            efficiency_df['total_revenue'] / efficiency_df['unique_skus']
    ).round(2)

    return efficiency_df.sort_values(by='product_efficiency_score', ascending=False)


# Global safeguard extracting unique lists before filter processing engine runs
# ---------------------------------------------------
# HEADER (CENTERED & BRAND-STYLED)
# ---------------------------------------------------
st.markdown(
    f"""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 25px;">
        <h1 style="color: {COLOR_BEAN}; font-size: 3.5rem; font-weight: 800; margin: 0; letter-spacing: -0.5px;">
            ☕ Product Analysis
        </h1>
        <p style="color: #7B5E57; font-size: 1.80rem; font-weight: 500; margin: 10px 0 0 0; letter-spacing: 0.2px;">
            Detailed Product Performance & Revenue Contribution
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

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
A consolidated view of key business findings, revenue drivers, performance risks, and strategic recommendations derived from transaction analysis.
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
            <li>Rank products by sales and revenue metrics</li>
            <li>Compare product volumetric velocity vs profitability</li>
            <li>Identify hero products and low performers across active stores</li>
            <li>Support business optimization and menu restructuring decisions</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

st.sidebar.title("📦 Product Filters")

store_filter = st.sidebar.multiselect(
    "Store Location",
    options=all_stores,
    default=all_stores
)

category_filter = st.sidebar.multiselect(
    "Product Category",
    options=all_categories,
    default=all_categories
)

top_n = st.sidebar.slider("Top Products", min_value=5, max_value=30, value=10)

# Filter Engine Fallbacks (Prevents blank screens if inputs are cleared)
actual_stores = store_filter if store_filter else all_stores
actual_categories = category_filter if category_filter else all_categories

filtered = df[df["store_location"].isin(actual_stores)]
filtered = filtered[filtered["product_category"].isin(actual_categories)]

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

total_revenue = filtered["revenue"].sum()
total_units = filtered["transaction_qty"].sum()
unique_products = filtered["product_id"].nunique()

k1, k2, k3 = st.columns(3)

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
               <span style="color: #757575; font-size: 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;"> Total Revenue </span>
               <h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 28px; font-weight: 600;">${total_revenue:,.0f}</h2>
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
            <span style="color: #757575; font-size: 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;"> Units Sold </span>
            <h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 28px; font-weight: 600;">{int(total_units):,}</h2>
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
            <span style="color: #757575; font-size: 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;"> Unique Products</span>
            <h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 28px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{unique_products:,}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ---------------------------------------------------
# ADVANCED PRODUCT INSIGHTS
# ---------------------------------------------------

st.markdown(
    """
    <h2 style="
        font-size:28px;
        color:#3E2723;
        font-weight:700;
        margin-bottom:10px;
    ">
        ᯓ➤ Product Intelligence Dashboard
    </h2>
    """,
    unsafe_allow_html=True
)
product_summary = (
    filtered
    .groupby("product_detail")
    .agg(
        Revenue=("revenue", "sum"),
        Units=("transaction_qty", "sum"),
        Transactions=("transaction_id", "nunique")
    )
    .reset_index()
    .sort_values("Revenue", ascending=False)
)

hero_product = product_summary.iloc[0]
hero_revenue_share = (hero_product['Revenue'] / total_revenue) * 100 if total_revenue > 0 else 0

# Streamlined Consolidated Hero Product Display Panel
# Streamlined Consolidated Hero Product Display Panel (Premium Branded Layout)
hero_col1, hero_col2 = st.columns([2.2, 0.8])

with hero_col1:
    st.markdown(
        f"""
        <div style="
            background-color: #FDFBF7; 
            padding: 24px; 
            border-radius: 12px; 
            border: 1px solid #EFEBE9; 
            border-left: 8px solid {COLOR_BEAN}; 
            box-shadow: 0 4px 12px rgba(62, 39, 35, 0.04);
        ">
            <h3 style="margin: 0 0 14px 0; color: {COLOR_BEAN}; font-size: 1.8rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                 Hero Product: ☆ {hero_product['product_detail']} ☆
            </h3>
            <div style="display: flex; gap: 24px; margin-bottom: 12px;">
                <div>
                    <span style="font-size: 16px; color: #757575; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">Revenue Generated</span>
                    <p style="margin: 2px 0 0 0; font-size: 26px; font-weight: 700; color: #5D4037;">${hero_product['Revenue']:,.0f}</p>
                </div>
                <div style="border-left: 1px dashed #E0E0E0; padding-left: 24px;">
                    <span style="font-size: 16px; color: #757575; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">Total Volume Sold</span>
                    <p style="margin: 2px 0 0 0; font-size: 26px; font-weight: 700; color: #5D4037;">{hero_product['Units']:,.0f} Units</p>
                </div>
                <div style="border-left: 1px dashed #E0E0E0; padding-left: 24px;">
                    <span style="font-size: 16px; color: #757575; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;">Total Revenue Share</span>
                    <p style="margin: 2px 0 0 0; font-size: 26px; font-weight: 700; color: {COLOR_BEAN};"> ▲ {hero_revenue_share:.1f}%</p>
                </div>
            </div>
            <p style="margin: 14px 0 0 0; font-size: 16px; color: #5D4037; line-height: 1.5; font-style: italic; border-top: 1px solid #F5EBE6; padding-top: 10px;">
                This product variant stands out as the highest income anchor across filtered retail locations.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with hero_col2:
    st.markdown(
        f"""
        <div style="
            background: white; 
            padding: 20px; 
            border-radius: 12px; 
            border: 1px solid #EFEBE9; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.03); 
            text-align: center;
            height: 240px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <span style="font-size: 18px; color: #757575; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Hero Product Share</span>
            <h2 style="margin: 8px 0 0 0; font-size: 40px; font-weight: 800; color: {COLOR_BEAN};">{hero_revenue_share:.1f}%</h2>
            <span style="font-size: 18px; color: #2E7D32; font-weight: 600; margin-top: 4px;">↑ Top Portfolio Anchor</span>
        </div>
        """,
        unsafe_allow_html=True
    )
# Best vs Lowest Performing Metrics Row


top_10_share = (product_summary.head(10)["Revenue"].sum() / total_revenue) * 100 if total_revenue > 0 else 0

st.markdown("---")

# ---------------------------------------------------
# SIDE-BY-SIDE CATEGORY ANALYSIS ROW (REFACTOR CORRECTED)
# ---------------------------------------------------
# ---------------------------------------------------
# SIDE-BY-SIDE CATEGORY ANALYSIS ROW
# ---------------------------------------------------
chart_col1, chart_col2 = st.columns(2)

category_rev = (
    filtered
    .groupby("product_category")["revenue"]
    .sum()
    .reset_index()
    .sort_values("revenue", ascending=False)
)

with chart_col1:
    st.subheader("𝄜 Revenue by Product Category")
    fig_bar = px.bar(
        category_rev,
        x="product_category",
        y="revenue",
        color="revenue",
        text_auto=".2s",
        color_continuous_scale=CAFE_PALETTE,
        labels={"product_category": "Category", "revenue": "Revenue ($)"}
    )
    fig_bar.update_layout(
        template="plotly_white",
        height=380,
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_bar, use_container_width=True, theme=None)

with chart_col2:
    st.subheader("◔ Revenue Contribution by Category")
    fig_pie = px.pie(
        category_rev,
        names="product_category",
        values="revenue",
        hole=0.55,
        color_discrete_sequence=CAFE_PIE_COLORS
    )
    fig_pie.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )
    fig_pie.update_layout(
        template="plotly_white",
        height=380,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_pie, use_container_width=True, theme=None)

# ---------------------------------------------------
# VISUALLY PROMINENT INSIGHT MATRIX UNDERNEATH
# ---------------------------------------------------
desc_col1, desc_col2 = st.columns(2)

with desc_col1:
    st.markdown(
        f"""
        <div style="
            background-color: #FDFBF7; 
            padding: 16px 20px; 
            border-radius: 8px; 
            border-left: 5px solid {COLOR_BEAN}; 
            margin-top: -10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        ">
            <p style="margin: 0; font-size: 16px; color: #4E342E; line-height: 1.5;">
                ➝ <b>Bar Chart Analysis:</b> Evaluates the gross financial return generated across broad category structures. Monitoring this allows management to pinpoint volume drivers and protect operational margins against sudden ingredient cost changes.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with desc_col2:
    st.markdown(
        f"""
        <div style="
            background-color: #FDFBF7; 
            padding: 16px 20px; 
            border-radius: 8px; 
            border-left: 5px solid {COLOR_MOCHA}; 
            margin-top: -10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        ">
            <p style="margin: 0; font-size: 16px; color: #4E342E; line-height: 1.5;">
                ➝ <b>Donut Mix Analysis:</b> Displays the percentage slice of total sales that each category owns. It highlights macro portfolio health, signaling immediately if your business relies too heavily on a single catalog division.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")
# Recommendations Panel
# ---------------------------------------------------
# EXECUTIVE STRATEGIC RECOMMENDATIONS PANEL (PREMIUM OVERHAUL)
# ---------------------------------------------------
st.markdown(
    f"""
    <div style="
        background-color: #FFFDFB; 
        padding: 24px; 
        border-radius: 12px; 
        border: 1px solid #F5EBE6; 
        border-left: 8px solid #7B5E57; 
        margin-top: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(123, 94, 87, 0.04);
    ">
        <h3 style="margin: 0 0 16px 0; color: #3E2723; font-size: 2.0rem; font-weight: 500; display: flex; align-items: center; gap: 8px;">
             Executive Strategic Recommendations
        </h3>
        <div style="display: flex; flex-direction: column; gap: 14px;">
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <span style="font-size: 24px; line-height: 1;"></span>
                <p style="margin: 0; font-size: 18px; color: #4E342E; line-height: 1.5;">
                    <b>Targeted Growth:</b> Direct core marketing campaigns and promotional budget toward 
                    <span style="color: #3E2723; font-weight: 700;">{hero_product['product_detail']}</span> to continuously exploit its massive sales velocity.
                </p>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 12px; border-top: 1px solid #FDF6F0; padding-top: 12px;">
                <span style="font-size: 24px; line-height: 1;"></span>
                <p style="margin: 0; font-size: 18px; color: #4E342E; line-height: 1.5;">
                    <b>Revenue Safeguarding:</b> Your top 10 products generate <span style="color: #3E2723; font-weight: 700;">{top_10_share:.1f}%</span> 
                    of total gross revenue. Protect these listings against raw inventory supply disruptions at all costs.
                </p>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 12px; border-top: 1px solid #FDF6F0; padding-top: 12px;">
                <span style="font-size: 24px; line-height: 1;"></span>
                <p style="margin: 0; font-size: 18px; color: #4E342E; line-height: 1.5;">
                    <b>Catalog Pruning & Bundling:</b> Audit weak-performing items at the baseline of the ledger. Re-evaluate their inclusion on the menu or bundle them alongside high-volume items to flush slow inventory.
                </p>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 12px; border-top: 1px solid #FDF6F0; padding-top: 12px;">
                <span style="font-size: 24px; line-height: 1;"></span>
                <p style="margin: 0; font-size: 18px; color: #4E342E; line-height: 1.5;">
                    <b>Cross-Category Scaling:</b> Expand high-grossing product lines through strategic cross-selling strategies and localized seasonal menu extensions.
                </p>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 12px; border-top: 1px solid #FDF6F0; padding-top: 12px;">
                <span style="font-size: 24px; line-height: 1;">⚠️</span>
                <p style="margin: 0; font-size: 18px; color: #4E342E; line-height: 1.5;">
                    <b>Risk Mitigation:</b> Monitor concentration indexes monthly to keep asset diversification healthy and reduce reliance on a single flavor variant.
                </p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# NEW EXTENSION: PRODUCT EFFICIENCY ANALYSIS COMPONENT
# ---------------------------------------------------
st.markdown(
    f"""
    <h2 style="
        font-size:26px;
        color:{COLOR_BEAN};
        font-weight:700;
        margin-top:10px;
        margin-bottom:10px;
    ">
        📊 Category Product Efficiency Matrix
    </h2>
    """,
    unsafe_allow_html=True
)
st.markdown(
    "This data layer breaks down **Asset Productivity (Revenue per SKU)** rather than standard transaction sizes—"
    "isolating exactly how much top-line value an individual active item generates on average inside its parent category grouping."
)

# Call the calculation engine running against the dynamically filtered dataframe
cat_efficiency = compute_product_efficiency_score(filtered, 'product_category')

if not cat_efficiency.empty:
    display_eff = cat_efficiency.copy()
    display_eff['total_revenue'] = display_eff['total_revenue'].map("${:,.2f}".format)
    display_eff['unique_skus'] = display_eff['unique_skus'].map("{:,} active SKUs".format)
    display_eff['product_efficiency_score'] = display_eff['product_efficiency_score'].map("${:,.2f} / SKU".format)

    st.dataframe(
        display_eff.rename(columns={
            "product_category": "Product Category Segment",
            "total_revenue": "Total Generated Revenue",
            "unique_skus": "Catalog Footprint Size",
            "product_efficiency_score": "Product Efficiency Score"
        }),
        use_container_width=True,
        hide_index=True
    )
st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------
# TABS FOR PRODUCT ANALYSIS
# ---------------------------------------------------

# ---------------------------------------------------
# TABS FOR PRODUCT ANALYSIS
# ---------------------------------------------------
st.markdown(
    """
    <style>
        /* Safely target only the navigation tab buttons text */
        button[data-baseweb="tab"] p {
            font-size: 17px !important;
            font-weight: 500 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs([
    "🏆 Top Products Leaderboard",
    "📊 Revenue vs Units Matrix",
    "📋 Granular Product Ledger"
])

# TAB 1: TOP PRODUCTS LEADERBOARD
with tab1:
    st.subheader(f"Top {top_n} Products by Revenue")
    top_products = filtered.groupby("product_detail").agg(
        revenue=("revenue", "sum"),
        units=("transaction_qty", "sum")
    ).reset_index().sort_values("revenue", ascending=False).head(top_n)

    fig = px.bar(
        top_products,
        x="revenue",
        y="product_detail",
        orientation="h",
        color="revenue",
        color_continuous_scale=CAFE_PALETTE,
        labels={"revenue": "Revenue ($)", "product_detail": ""}
    )
    fig.update_traces(
        texttemplate="$%{x:,.0s}",
        textposition="outside",
        hovertemplate="<b>Product:</b> %{y}<br><b>Revenue:</b> $% {x:,.2f}<extra></extra>"
    )
    fig.update_layout(
        template="plotly_white",
        height=500,
        title="Top Products by Revenue Value Generation",
        title_font=dict(size=16, color=COLOR_BEAN),
        coloraxis_showscale=False,
        yaxis={"categoryorder": "total ascending"}
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

    st.markdown(
        """
        <p style="font-size: 18px; color: #2E3A47; line-height: 1.6; margin-top: 8px;">
            ➤ </b> A clean leaderboard ranking your top revenue-generating menu items. It highlights which items pull in the most gross volume for the selected parameters.
        </p>
        """,
        unsafe_allow_html=True
    )

# TAB 2: POPULARITY VS REVENUE MATRIX
with tab2:
    st.subheader("Product Profitability Positioning Matrix")
    scatter = filtered.groupby("product_detail").agg(
        revenue=("revenue", "sum"),
        units=("transaction_qty", "sum")
    ).reset_index()

    # REMOVED text="product_detail" from the main constructor to fix label crowding
    fig = px.scatter(
        scatter,
        x="units",
        y="revenue",
        size="revenue",
        color="revenue",
        color_continuous_scale=CAFE_PALETTE,
        labels={"units": "Units Sold", "revenue": "Revenue ($)"}
    )

    # ADDED hover details and refined text position safely
    fig.update_traces(
        text=scatter["product_detail"],
        textposition="top center",
        hovertemplate="<b>Product:</b> %{text}<br><b>Units Sold:</b> %{x:,}<br><b>Revenue:</b> $% {y:,.2f}<extra></extra>"
    )

    fig.update_layout(
        template="plotly_white",
        height=520,
        title="Product Popularity Volume vs. Financial Returns",
        title_font=dict(size=16, color=COLOR_BEAN),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

    st.markdown(
        """
        <p style="font-size: 18px; color: #2E3A47; line-height: 1.6; margin-top: 8px;">
            ➤ </b> This maps individual sales metrics against total profit returns. Menu items in the <b>top-right quadrant</b> are your core business drivers, achieving high sales volume alongside high profit margins.
        </p>
        """,
        unsafe_allow_html=True
    )



# TAB 3: GRANULAR PRODUCT LEDGER
with tab3:
    st.subheader("Granular SKU Performance Ledger")
    product_table = filtered.groupby(
        ["product_category", "product_type", "product_detail"]
    ).agg(
        Revenue=("revenue", "sum"),
        Units=("transaction_qty", "sum"),
        Transactions=("transaction_id", "nunique")
    ).reset_index().sort_values("Revenue", ascending=False)

    display_table = product_table.copy()
    display_table["Revenue"] = display_table["Revenue"].map("${:,.2f}".format)
    display_table["Units"] = display_table["Units"].map("{:,.0f}".format)
    display_table["Transactions"] = display_table["Transactions"].map("{:,.0f}".format)

    st.dataframe(display_table, use_container_width=True, hide_index=True)

    csv = product_table.to_csv(index=False)
    st.download_button("⬇️ Download Cleaned Product Analysis (CSV)", csv, file_name="product_analysis.csv",
                       mime="text/csv")

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown(
    """
    <div style="text-align: center; padding: 15px 0 25px 0; color: #7B5E57; font-size: 14px; font-weight: 500; letter-spacing: 0.3px;">
        ☕ <b>Afficionado Coffee Roasters</b> | Product Performance Deep-Dive
        <br>
        <span style="color: #A1887F; font-size: 14px; font-weight: 400; display: inline-block; margin-top: 5px;">
           Menu Optimization Matrix • SKU Concentration & Pareto Revenue Contribution © 2026
        </span>
        <br>
        <span style="color: #BAA6A1; font-size: 13px; font-weight: 400; display: inline-block; margin-top: 6px; letter-spacing: 0.5px; text-transform: uppercase;">
            ⚡ Powered by: Python • Streamlit • Pandas • Plotly Express
        </span>
    </div>
    """,
    unsafe_allow_html=True
)
