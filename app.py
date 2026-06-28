from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Afficionado Coffee Roasters",
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
        /* Explicit fallback styles for the custom KPI metrics */
        .kpi-card {
            background-color: #FDFBF7;
            border: 1px solid #EFEBE9;
            border-left: 5px solid #5D4037;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            margin-bottom: 15px;
        }
        .kpi-title {
            font-size: 14px;
            color: #757575;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        .kpi-value {
            font-size: 26px;
            color: #3E2723;
            font-weight: 700;
        }
        /* Elegant unified executive container cards */
        .brand-container-box {
            background-color: #FDFBF7;
            border: 1px solid #EFEBE9;
            border-left: 6px solid #5D4037;
            padding: 22px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .brand-container-success {
            background-color: #F8F9FA;
            border: 1px solid #E0E0E0;
            border-left: 6px solid #2E7D32;
            padding: 16px;
            border-radius: 6px;
            margin-bottom: 12px;
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
# CSS
# --------------------------------------------------

css_file = Path(__file__).parent / "assets" / "style.css"

if css_file.exists():
    with open(css_file, encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# --------------------------------------------------
# DATA
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
        BASE_DIR
        / "outputs"
        / "cleaned"
        / "coffee_shop_fe.csv"
)

if not DATA_PATH.exists():
    st.error(f"Dataset not found:\n{DATA_PATH}")
    st.stop()


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    # Remove duplicate rows
    df = df.drop_duplicates()

    return df


df = load_data()
last_updated = pd.Timestamp.now().strftime(
    "%d %b %Y %H:%M"
)

record_count = len(df)


def apply_theme(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13, color="#424242"),
        title_font=dict(size=18, color=COLOR_BEAN, family="sans-serif"),
        margin=dict(
            l=30,
            r=30,
            t=50,
            b=30
        )
    )
    fig.update_xaxes(showgrid=False, linecolor="#E0E0E0")
    fig.update_yaxes(showgrid=True, gridcolor="#F5F5F5", linecolor="#E0E0E0")

    return fig


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown(
    f"""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 25px;">
        <h1 style="color: {COLOR_BEAN}; font-size: 3.5rem; font-weight: 800; margin: 0; letter-spacing: -0.5px;">
            Product Optimization & Revenue Contribution Analysis
        </h1>
        <p style="color: #7B5E57; font-size: 2.4rem; font-weight: 600; margin: 10px 0 0 0; letter-spacing: 0.2px;">
             ☕ Afficionado Coffee Roasters
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

meta1, meta2 = st.columns(2)

with meta1:
    st.caption(
        f"Last Updated: {last_updated}"
    )

with meta2:
    st.markdown(
        f"<p style='text-align:right; margin:0; font-size:0.85rem; color:gray;'>Records Analyzed: <b>{record_count:,}</b></p>",
        unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.markdown(
    """
    # ☕ Coffee Analytics
    
    Executive Dashboard
    
    Monitor revenue, products, categories and store performance.
    """
)

st.sidebar.markdown("---")

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

top_n = st.sidebar.slider(
    "Top Products",
    min_value=5,
    max_value=20,
    value=10
)

# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

filtered = df.copy()

filtered = filtered[
    filtered["store_location"].isin(store_filter)
]

filtered = filtered[
    filtered["product_category"].isin(category_filter)
]

if filtered.empty:
    st.warning(
        "No data available for selected filters."
    )
    st.stop()

# --------------------------------------------------
# COMMON METRICS
# --------------------------------------------------

total_revenue = filtered["revenue"].sum()

total_transactions = (
    filtered["transaction_id"]
    .nunique()
)

total_units = (
    filtered["transaction_qty"]
    .sum()
)

avg_order_value = (
    total_revenue / total_transactions
    if total_transactions > 0
    else 0
)

unique_products = (
    filtered["product_id"]
    .nunique()
)

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

section = st.radio(
    "",
    [
        "Overview",
        "Products",
        "Stores",
        "Insights"
    ],
    horizontal=True
)

st.markdown("---")
# --------------------------------------------------
# DASHBOARD OVERVIEW
# --------------------------------------------------

# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

if section == "Overview":
    st.markdown("## Dashboard Overview")

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------

if section == "Overview":

    total_revenue = filtered["revenue"].sum()

    total_transactions = (
        filtered["transaction_id"]
        .nunique()
    )

    total_units = (
        filtered["transaction_qty"]
        .sum()
    )

    avg_order_value = (
        total_revenue / total_transactions
        if total_transactions > 0
        else 0
    )

    unique_products = (
        filtered["product_id"]
        .nunique()
    )

    # Top Category
    top_category = (
        filtered
        .groupby("product_category")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    top_category_name = (
        top_category.index[0]
        if len(top_category) > 0
        else "N/A"
    )
    # KPI CARDS

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Revenue</div>
                <div class="kpi-value">${total_revenue:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Transactions</div>
                <div class="kpi-value">{total_transactions:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Units Sold</div>
                <div class="kpi-value">{int(total_units):,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Avg Order Value</div>
                <div class="kpi-value">${avg_order_value:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.subheader("Data Quality Summary")
    dq1, dq2, dq3 = st.columns(3)

    with dq1:
        st.metric(
            "Rows",
            f"{len(filtered):,}"
        )

    missing_values = (
        filtered
        .isna()
        .sum()
        .sum()
    )

    duplicate_rows = (
        filtered
        .duplicated()
        .sum()
    )

    with dq2:
        st.metric(
            "Missing Values",
            f"{missing_values:,}"
        )

    with dq3:
        st.metric(
            "Duplicate Rows",
            f"{duplicate_rows:,}"
        )
    st.markdown("---")

    # --------------------------------------------------
    # EXECUTIVE SUMMARY BANNER (Refactored for Unified Palette)
    # --------------------------------------------------

    try:
        top_store = (
            filtered
            .groupby("store_location")["revenue"]
            .sum()
            .idxmax()
        )
    except Exception:
        top_store = "N/A"

    try:
        top_category = (
            filtered
            .groupby("product_category")["revenue"]
            .sum()
            .idxmax()
        )
    except Exception:
        top_category = "N/A"

    st.markdown(
        f"""
        <div class="brand-container-box">
            <h3 style="margin: 0 0 12px 0; color: #3E2723; font-size: 1.9rem;"> Executive Summary</h3>
            <p style="margin: 6px 0; font-size: 18px; color: #4E342E;"> <b>Total Revenue:</b> ${total_revenue:,.0f}</p>
            <p style="margin: 6px 0; font-size: 18px; color: #4E342E;"> <b>Top Performing Store:</b> {top_store}</p>
            <p style="margin: 6px 0; font-size: 18px; color: #4E342E;"> <b>Top Revenue Category:</b> {top_category}</p>
            <p style="margin: 6px 0; font-size: 18px; color: #4E342E;">️ <b>Products Analyzed:</b> {unique_products:,}</p>
            <p style="margin: 12px 0 0 0; font-size: 18px; color: #757575; line-height: 1.5;">
                This dashboard provides a consolidated view of product performance, store performance, revenue contribution, and customer purchasing trends.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # BUSINESS HEALTH SNAPSHOT (Refactored for Balanced Alignment)
    # --------------------------------------------------

    st.subheader(" Business Health Snapshot")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="brand-container-box" style="padding: 16px;">
                <h4 style="margin: 0 0 8px 0; color: #3E2723; font-size: 1.8rem;">Revenue Performance</h4>
                <p style="margin: 4px 0; font-size: 24px; font-weight: bold; color: #5D4037;">${total_revenue:,.0f}</p>
                <p style="margin: 0; font-size: 18px; color: #757575;">generated across <b>{total_transactions:,} transactions</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="brand-container-box" style="padding: 18px; border-left-color: #2E7D32;">
                <h4 style="margin: 0 0 8px 0; color: #1B5E20; font-size: 1.8rem;">Product Portfolio</h4>
                <p style="margin: 4px 0; font-size: 24px; font-weight: bold; color: #2E7D32;">{filtered['product_id'].nunique():,} Products</p>
                <p style="margin: 0; font-size: 16px; color: #757575;">generated <b>{int(total_units):,} Units Sold</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        avg_per_transaction = (
            total_revenue / total_transactions
            if total_transactions > 0
            else 0
        )
        st.markdown(
            f"""
            <div class="brand-container-box" style="padding: 16px; border-left-color: #E65100;">
                <h4 style="margin: 0 0 8px 0; color: #E65100; font-size: 1.8rem;">Average Basket Value</h4>
                <p style="margin: 4px 0; font-size: 24px; font-weight: bold; color: #EF6C00;">${avg_per_transaction:.2f}</p>
                <p style="margin: 0; font-size: 16px; color: #757575;">spent per customer transaction</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --------------------------------------------------
    # ROW 1
    # --------------------------------------------------

    left_col, right_col = st.columns(2)

    # --------------------------------------------------
    # REVENUE TREND
    # --------------------------------------------------

    with left_col:

        st.subheader(" Revenue Trend by Hour")

        if "hour" in filtered.columns:

            hourly = (
                filtered
                .groupby("hour", as_index=False)["revenue"]
                .sum()
                .sort_values("hour")
            )

            fig = px.line(
                hourly,
                x="hour",
                y="revenue",
                markers=True,
                hover_data={
                    "hour": True,
                    "revenue": ":,.0f"
                }
            )

            fig.update_traces(
                line_color=COLOR_BEAN,
                line_width=4,
                marker=dict(size=6, color=COLOR_MOCHA)
            )

            fig = apply_theme(fig)

            # Add a text label pointing directly at the 10 AM sales peak
            fig.add_annotation(
                x=10,  # The X-axis location (Hour 10)
                y=88673,  # The Y-axis location (Revenue amount)
                text="Peak Daily Traffic Peak",  # The text message you want to display
                showarrow=True,  # Draws a clean pointing arrow
                arrowhead=2,  # Sets the style design of the arrowhead
                ax=-40,  # Moves the text 40 pixels left of the arrow tip
                ay=-30,  # Moves the text 30 pixels up from the arrow tip
                font=dict(size=12, color="#3E2723")  # Styles the text color to match your brand
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                theme=None
            )
            st.markdown(
                """
                <p style="font-size: 16px; color: #2E3A47; line-height: 1.6; margin-top: 8px;">
                    <b>➤</b>Data Insight:</b> Sales experience an aggressive upward climb starting at 7:00 AM, accelerating into a definitive daily transaction peak at 10:00 AM. Management should align barista shifts and batch-brewing schedules around this critical 3-hour morning window.
                </p>
                """,
                unsafe_allow_html=True
            )
        else:

            st.warning(
                "Hour column not available in dataset."
            )

    # --------------------------------------------------
    # REVENUE BY CATEGORY
    # --------------------------------------------------

    with right_col:

        st.subheader("Revenue by Category")

        category_rev = (
            filtered
            .groupby("product_category", as_index=False)["revenue"]
            .sum()
            .sort_values(
                "revenue",
                ascending=False
            )
        )

        fig = px.bar(
            category_rev,
            x="product_category",
            y="revenue",
            color="product_category",
            text_auto=".2s",
            color_discrete_sequence=CAFE_PALETTE
        )

        fig = apply_theme(fig)

        fig.update_layout(
            title="Product Category Financial Breakdown",  # Adds your custom chart title here
            title_x=0.0,  # Aligns the title to the left edge
            height=450,
            showlegend=False,
            xaxis_title="Category",
            yaxis_title="Revenue ($)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )
        st.markdown(
            """
            <p style="font-size: 15px; color: #2E3A47; line-height: 1.6; margin-top: 8px;">
                <b>➤</b>Data Insight:</b> 'Coffee' represents your undisputed primary financial foundation, dwarfing secondary product lines. Monitoring this baseline distribution helps isolate inventory requirements and spot shifting consumer flavor trends.
            </p>
            """,
            unsafe_allow_html=True
        )
    # ==================================================
    # PRODUCTS PAGE
    # ==================================================

if section == "Products":
    col_a, col_b = st.columns(2)

    # --------------------------------------------------
    # TOP PRODUCTS (Synchronized Scale)
    # --------------------------------------------------

    with col_a:
        st.subheader(f" Top {top_n} Products")

        top_products = (
            filtered
            .groupby("product_detail", as_index=False)
            .agg(
                revenue=("revenue", "sum")
            )
            .sort_values(
                "revenue",
                ascending=False
            )
            .head(top_n)
        )

        fig = px.bar(
            top_products,
            x="revenue",
            y="product_detail",
            orientation="h",
            color="revenue",
            color_continuous_scale=[[0, COLOR_CREMA], [1, COLOR_BEAN]],
            text_auto=".2s"
        )

        fig = apply_theme(fig)

        fig.update_layout(
            title="Top Revenue Generating Menu Items",  # Added Heading
            title_x=0.02,  # Left Aligned
            height=450,
            coloraxis_showscale=False,
            xaxis_title="Revenue ($)",
            yaxis_title=""
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )
        st.markdown(
            """
            <div style="font-size: 16px; color: #2E3A47; line-height: 1.6; margin-top: 8px;">
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <b>➤</b>Highlights the products generating the highest revenue across the menu and also helps identify key revenue drivers for promotion, inventory planning, and menu optimization.
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------
    # CATEGORY MIX (Synchronized Palette)
    # --------------------------------------------------

    with col_b:
        st.subheader(" Category Revenue Mix")

        category_mix = (
            filtered
            .groupby("product_category", as_index=False)["revenue"]
            .sum()
        )

        fig = px.pie(
            category_mix,
            names="product_category",
            values="revenue",
            hole=0.55,
            color_discrete_sequence=CAFE_PALETTE
        )

        fig = apply_theme(fig)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        # Paste right after fig = apply_theme(fig)
        fig.update_layout(
            title="Portfolio Gross Volume Contribution Share",  # Added Heading
            title_x=0.02,  # Left Aligned
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )
        st.markdown(
            """
            <div style="font-size: 16px; color: #2E3A47; line-height: 1.6; margin-top: 8px;">
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <b>➤</b>Shows how total revenue is distributed across product categories and also highlights category dependence and opportunities for portfolio diversification.
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("---")

    # --------------------------------------------------
    # PARETO ANALYSIS (Contrast-Optimized Overlay)
    # --------------------------------------------------

    st.subheader("🎢 Revenue Concentration (Pareto Analysis)")

    pareto = (
        filtered
        .groupby("product_detail", as_index=False)
        .agg(
            revenue=("revenue", "sum")
        )
        .sort_values(
            "revenue",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # Product Rank
    pareto["rank"] = range(
        1,
        len(pareto) + 1
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

    # Create Pareto Chart
    fig = px.bar(
        pareto,
        x="rank",
        y="revenue",
        labels={
            "rank": "Products Ranked by Revenue",
            "revenue": "Revenue ($)"
        }
    )
    fig.update_traces(marker_color=COLOR_CREMA, opacity=0.85, name="SKU Revenue")

    # Add cumulative line
    fig.add_scatter(
        x=pareto["rank"],
        y=pareto["cum_share"],
        mode="lines",
        line=dict(color=COLOR_BEAN, width=3),
        name="Cumulative Share %",
        yaxis="y2"
    )

    # Add 80% reference line
    fig.add_hline(
        y=80,
        line_dash="dash",
        line_color="#D84315",
        annotation_text="80% Threshold",
        yref="y2"
    )

    fig.update_layout(
        title="Menu SKU Concentration & Cumulative Revenue Arc",  # Added Heading
        title_x=0.02,  # Left Aligned
        height=500,
        yaxis=dict(title="Revenue ($)"),
        yaxis2=dict(
            title="Cumulative Revenue %",
            overlaying="y",
            side="right",
            range=[0, 100]
        ),
        showlegend=True
    )

    fig = apply_theme(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        theme=None
    )
    st.markdown(
        """
        <div style="font-size: 16px; color: #2E3A47; line-height: 1.6; margin-top: 8px;">
            <b>➤</b>Data Insight:</b>
            <ul style="margin-top: 5px; padding-left: 20px;">
                <li>The slope of the cumulative arc visually models portfolio efficiency, showing how quickly revenue accumulates across products.</li>
                <li>A sharper rise toward the 80% cutoff line indicates higher menu concentration, helping identify low-performing long-tail SKUs that may be candidates for pruning, bundling, or promotional strategies.</li>
                <li>This also highlights the 80/20 rule, where a small group of top-selling items generates approximately 80% of total revenue, helps identify slow-moving products that contribute little to overall sales.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
    # --------------------------------------------------
    # HERO PRODUCT & REVENUE CONCENTRATION (Refactored Container Logic)
    # --------------------------------------------------

    product_rev = (
        filtered
        .groupby("product_detail")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    if len(product_rev) > 0:
        hero_product = product_rev.index[0]
        hero_revenue = product_rev.iloc[0]
        total_revenue = product_rev.sum()

        # Calculate individual share for the single hero product
        hero_share = (hero_revenue / total_revenue) * 100

        # Calculate cumulative share for the top 20% Pareto threshold
        top_20_count = max(1, int(len(product_rev) * 0.20))
        pareto_concentration = (product_rev.head(top_20_count).sum() / total_revenue) * 100

        # --- NEW HERO MULTIPLIER BENCHMARK ENGINE ---
        avg_product_revenue = product_rev.mean()
        multiplier = hero_revenue / avg_product_revenue if avg_product_revenue > 0 else 1

        st.markdown("---")

        # Integrated layout containing all old metrics plus the new multiplier card
        st.markdown(
            f"""
                    <div style="background-color: #FDFBF7; padding: 22px; border-radius: 8px; border: 1px solid #EFEBE9; border-left: 6px solid #2E7D32; margin-top: 15px;">
                        <h3 style="margin: 0 0 15px 0; color: #1B5E20; font-size: 2.2rem;"> Portfolio Concentration & Performance</h3>
                        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                            <div style="flex: 1.5; min-width: 280px;">
                                <h4 style="margin: 0 0 4px 0; color: #2E7D32; font-size: 1.8rem;"> 🥇 Hero Product</h4>
                                <p style="margin: 6px 0; font-size: 24px; font-weight: bold; color: #3E2723;"> ➝ {hero_product}</p>
                                <span style="color: #757575; font-size: 15px;">The strongest single revenue driver across your portfolio.</span>
                            </div>
                            <div style="flex: 1; min-width: 180px; background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                                <div style="font-size: 24px; color: #757575; text-transform: uppercase; font-weight: 500;">Hero Product Revenue</div>
                                <div style="font-size: 20px; font-weight: 800; color: #3E2723; margin-top: 2px;">${hero_revenue:,.2f}</div>
                                <div style="font-size: 26px; color: #2E7D32; font-weight: 600; margin-top: 2px;">↑ {hero_share:.1f}% of total</div>
                            </div>
                            <div style="flex: 1; min-width: 180px; background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                                <div style="font-size: 24px; color: #757575; text-transform: uppercase; font-weight: 500;">vs. Catalog Average</div>
                                <div style="font-size: 20px; font-weight: 800; color: #2E7D32; margin-top: 2px;">{multiplier:.1f}x Higher</div>
                                <div style="font-size: 22px; color: #A1887F; margin-top: 2px;">than typical menu items (${avg_product_revenue:,.0f})</div>
                            </div>
                            <div style="flex: 1; min-width: 180px; background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                                <div style="font-size: 24px; color: #757575; text-transform: uppercase; font-weight: 500;">Top 20% Category Share</div>
                                <div style="font-size: 20px; font-weight: 800; color: #3E2723; margin-top: 2px;">{pareto_concentration:.1f}%</div>
                                <div style="font-size: 22px; color: #5D4037; margin-top: 2px;">Generated by top {top_20_count} SKUs</div>
                            </div>
                        </div>
                    </div>
                    """,
            unsafe_allow_html=True
        )

# --------------------------------------------------
# STORE PERFORMANCE ANALYSIS
# --------------------------------------------------

if section == "Stores":

    st.markdown(
        """
        <h2 style="
            text-align:left;
            color:#3E2723;
            font-size:2.3rem;
            font-weight:600;
            margin-bottom:15px;
        ">
            Detailed Store Ranking
        </h2>
        """,
        unsafe_allow_html=True
    )

    store_ranking = (
        filtered
        .groupby("store_location")
        .agg(
            Revenue=("revenue", "sum"),
            Transactions=("transaction_id", "nunique"),
            Units=("transaction_qty", "sum")
        )
        .reset_index()
        .sort_values(
            "Revenue",
            ascending=False
        )
    )

    store_ranking.insert(
        0,
        "Rank",
        range(1, len(store_ranking) + 1)
    )
    store_ranking["Avg Basket"] = (
            store_ranking["Revenue"]
            /
            store_ranking["Transactions"]
    )
    top_store = store_ranking.iloc[0]["store_location"]

    top_revenue = store_ranking.iloc[0]["Revenue"]

    best_store_share = (
                               top_revenue
                               /
                               store_ranking["Revenue"].sum()
                       ) * 100

    # ----------------------------------------------
    # KPI SECTION
    # ----------------------------------------------

    avg_order_value = (
            filtered["revenue"].sum()
            /
            filtered["transaction_id"].nunique()
    )

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            " Top Store",
            top_store
        )

    with k2:
        st.metric(
            " Top Store Revenue",
            f"${top_revenue:,.0f}"
        )

    with k3:
        st.metric(
            " Revenue Contribution",
            f"{best_store_share:.1f}%"
        )

    with k4:
        st.metric(
            " Avg Order Value",
            f"${avg_order_value:.2f}"
        )

    st.markdown("---")
    # --------------------------------------------------
    # STORE REVENUE VISUALIZATION
    # --------------------------------------------------

    chart_col, pie_col = st.columns(2)

    # -----------------------------------------
    # Revenue by Store
    # -----------------------------------------

    with chart_col:

        st.subheader("📈 Revenue by Store")

        store_ranking["Revenue Share %"] = (
                store_ranking["Revenue"]
                /
                store_ranking["Revenue"].sum()
                * 100
        )

        fig = px.bar(
            store_ranking,
            x="store_location",
            y="Revenue",
            text="Revenue Share %",
            color_discrete_sequence=[COLOR_MOCHA]
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig = apply_theme(fig)
        fig.update_layout(
            title="Gross Regional Retail Footprint Size",  # Added Heading
            title_x=0.02,  # Left Aligned
            height=350,
            showlegend=False,
            xaxis_title="Store Location",
            yaxis_title="Revenue ($)",
            margin=dict(l=20, r=20, t=60, b=20)  # Adjusted padding for text
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )
        st.markdown(
            """
            <p style="font-size: 16px; color: #2E3A47; line-height: 1.6; margin-top: 8px;">
                 <b>➤</b> A direct race comparing your store locations. It shows which shop brings in the most total money and which ones are lagging behind.
            </p>
            """,
            unsafe_allow_html=True
        )
    # -----------------------------------------
    # Store Revenue Contribution (Theme Aligned)
    # -----------------------------------------

    with pie_col:

        st.subheader("◔ Store Revenue Contribution")

        fig = px.pie(
            store_ranking,
            names="store_location",
            values="Revenue",
            hole=0.60,
            color_discrete_sequence=CAFE_PALETTE
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        fig = apply_theme(fig)
        fig.update_layout(
            title="Market Foothold Capture Share",  # Added Heading
            title_x=0.02,  # Left Aligned
            height=350,
            margin=dict(l=20, r=20, t=60, b=20),  # Adjusted padding for text
            annotations=[
                dict(
                    text="Store<br>Revenue",
                    showarrow=False,
                    font_size=16
                )
            ]
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )
        st.markdown(
            """
            <div style="font-size: 16px; color: #2E3A47; line-height: 1.6; margin-top: 8px;">
                <ul style="margin-top: 5px; padding-left: 20px;">
                     <b>➤</b>Shows each store's contribution to total company revenue and highlights the strongest performing locations.
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
    # --------------------------------------------------
    # STORE PERFORMANCE ANALYTICS
    # --------------------------------------------------

    analytics_col1, analytics_col2 = st.columns(2)

    # -----------------------------------------
    # Average Basket Value (Theme Aligned)
    # -----------------------------------------

    with analytics_col1:

        st.subheader("🛒 Average Basket Value")

        store_ranking["Avg Basket"] = (
                store_ranking["Revenue"]
                /
                store_ranking["Transactions"]
        )

        avg_basket_company = (
            store_ranking["Avg Basket"]
            .mean()
        )

        fig = px.bar(
            store_ranking,
            x="store_location",
            y="Avg Basket",
            text="Avg Basket",
            color_discrete_sequence=[COLOR_LATTE]
        )

        fig.update_traces(
            texttemplate="$%{text:.2f}",
            textposition="outside"
        )

        fig.add_hline(
            y=avg_basket_company,
            line_dash="dash",
            line_color=COLOR_BEAN,
            annotation_text=f"Company Avg (${avg_basket_company:.2f})"
        )

        fig = apply_theme(fig)

        fig.update_layout(
            title="Store Efficiency Index: Spending Per Ticket",  # Added Heading
            title_x=0.02,  # Left Aligned
            height=450,
            showlegend=False,
            xaxis_title="Store Location",
            yaxis_title="Average Basket ($)",
            margin=dict(l=20, r=20, t=60, b=20)  # Adjusted padding for text
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )
        st.markdown(
            """
            <div style="font-size: 16px; color: #2E3A47; line-height: 1.6; margin-top: 8px;">
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <b>➤</b>Highlights average customer spend per transaction at each store.Higher values indicate stronger basket size performance and revenue efficiency.
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # -----------------------------------------
    # Revenue vs Transactions (Theme Aligned Scatter)
    # -----------------------------------------

    with analytics_col2:

        st.subheader("📝 Revenue vs Transactions")

        fig = px.scatter(
            store_ranking,
            x="Transactions",
            y="Revenue",
            size="Units",
            color="store_location",
            hover_name="store_location",
            size_max=50,
            color_discrete_sequence=CAFE_PALETTE,
            hover_data={
                "Revenue": ":,.0f",
                "Transactions": ":,.0f",
                "Units": ":,.0f"
            }
        )

        fig = apply_theme(fig)

        # Paste right after fig = apply_theme(fig)
        fig.add_annotation(
            x=store_ranking["Transactions"].max(),
            y=store_ranking["Revenue"].max(),
            text="Maximum Volume Anchor",
            showarrow=True,
            arrowhead=1,
            ax=-60,
            ay=-40,
            font=dict(size=11, color=COLOR_BEAN)
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )
        st.markdown(
            """
            <div style="font-size: 16px; color: #2E3A47; line-height: 1.6; margin-top: 8px;">
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <b>➤</b>Visualizes the relationship between customer traffic and revenue generation across stores.
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --------------------------------------------------
    # STORE PERFORMANCE TABLE
    # --------------------------------------------------

    display_store = store_ranking.copy()

    display_store["Revenue"] = (
        display_store["Revenue"]
        .map("${:,.0f}".format)
    )

    display_store["Transactions"] = (
        display_store["Transactions"]
        .map("{:,.0f}".format)
    )

    display_store["Units"] = (
        display_store["Units"]
        .map("{:,.0f}".format)
    )

    display_store["Avg Basket"] = (
        display_store["Avg Basket"]
        .map("${:.2f}".format)
    )

    st.subheader(" Detailed Store Ranking")

    st.dataframe(
        display_store,
        use_container_width=True,
        hide_index=True,
        height=220
    )

    # --------------------------------------------------
    # STORE INSIGHTS (Refactored for Visual Symmetry)
    # --------------------------------------------------

    best_store = (
        store_ranking
        .iloc[0]["store_location"]
    )

    highest_basket = (
        store_ranking
        .sort_values(
            "Avg Basket",
            ascending=False
        )
        .iloc[0]["store_location"]
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            f"""
                <div class="brand-container-box" style="padding:14px; border-left-color:#2E7D32; display:flex; justify-content:space-between; align-items:center; margin-bottom:0;">
                    <span style="font-size:18px; color:#424242; font-weight:700;"> Revenue Leader Store:</span>
                    <span style="background-color:#E8F5E9; color:#2E7D32; padding:4px 12px; border-radius:6px; font-weight:bold; font-size:22px;">{best_store}</span>
                </div>
                """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
                <div class="brand-container-box" style="padding:14px; border-left-color:#EF6C00; display:flex; justify-content:space-between; align-items:center; margin-bottom:0;">
                    <span style="font-size:18px; color:#424242; font-weight:700;"> Highest Basket Value Footprint:</span>
                    <span style="background-color:#FFF3E0; color:#E65100; padding:4px 12px; border-radius:6px; font-weight:bold; font-size:22px;">{highest_basket}</span>
                </div>
                """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------
    # DAILY REVENUE TREND
    # --------------------------------------------------

    if "transaction_date" in filtered.columns:
        st.write("")  # Layout spacer spacing
        st.subheader("📈 Daily Revenue Trend")

        revenue_trend = (
            filtered
            .groupby("transaction_date")["revenue"]
            .sum()
            .reset_index()
        )

        revenue_trend["transaction_date"] = pd.to_datetime(
            revenue_trend["transaction_date"]
        )

        fig = px.line(
            revenue_trend,
            x="transaction_date",
            y="revenue",
            markers=True
        )

        fig.update_traces(
            line=dict(
                color=COLOR_BEAN,
                width=4
            ),
            marker=dict(color=COLOR_MOCHA)
        )

        fig = apply_theme(fig)

        fig.update_layout(
            height=400,
            title="Revenue Trend Over Time",
            xaxis_title="Date",
            yaxis_title="Revenue ($)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )
        st.markdown(
            """
            <p style="font-size: 16px; color: #2E3A47; line-height: 1.6; margin-top: 8px;">
                💡 <b>Data Insight:</b> This ongoing line layout maps operational growth over time, tracking recurring cycle patterns, peak holiday anomalies, or dips to evaluate the long-term effectiveness of dynamic marketing pushes.
            </p>
            """,
            unsafe_allow_html=True
        )
# --------------------------------------------------
# INSIGHTS SECTION
# --------------------------------------------------

if section == "Insights":

    st.subheader("⚠ Products Requiring Review")

    bottom_products = (
        filtered
        .groupby(
            [
                "product_category",
                "product_detail"
            ]
        )
        .agg(
            Revenue=("revenue", "sum"),
            Units=("transaction_qty", "sum"),
            Transactions=("transaction_id", "nunique")
        )
        .reset_index()
        .sort_values(
            "Revenue",
            ascending=True
        )
        .head(10)
    )

    st.dataframe(
        bottom_products,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Products listed above contribute the least revenue and should be reviewed for menu optimization."
    )

    st.markdown("---")

    # ----------------------------------------------
    # EXECUTIVE INSIGHTS (Refactored for Brand Synchronization)
    # ----------------------------------------------

    st.markdown(
        """
        <h2 style="
            text-align:left;
            color:#3E2723;
            font-size:2rem;
            font-weight:600;
            margin-bottom:15px;
        ">
            Executive Insights
        </h2>
        """,
        unsafe_allow_html=True
    )

    try:
        top_store = (
            filtered
            .groupby("store_location")["revenue"]
            .sum()
            .idxmax()
        )
    except Exception:
        top_store = "N/A"

    try:
        top_category = (
            filtered
            .groupby("product_category")["revenue"]
            .sum()
            .idxmax()
        )
    except Exception:
        top_category = "N/A"

    product_revenue = (
        filtered
        .groupby("product_detail")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    top_20_count = max(
        1,
        int(len(product_revenue) * 0.20)
    )

    concentration = (
                            product_revenue
                            .head(top_20_count)
                            .sum()
                            /
                            product_revenue.sum()
                    ) * 100

    st.markdown(
        f"""
            <div class="brand-container-box">
                <h3 style="margin: 0 0 12px 0; color: #3E2723; font-size: 1.6rem;">➤ Key Findings Portfolio Audit</h3>
                <ul style="margin: 0; padding-left: 20px; color: #4E342E; font-size: 18px; line-height: 1.8;">
                    <li>Highest Revenue Store Location: <b>{top_store}</b></li>
                    <li>Highest Revenue Core Category Segment: <b>{top_category}</b></li>
                    <li>Top 20% of Catalog Varieties Generate <b>{concentration:.1f}%</b> of Cumulative Revenue.</li>
                    <li>Gross commercial value behaves with high concentration risk around selected anchor variants.</li>
                    <li>Several long-tail, low-performing products provide minimal structural contribution to sales volume.</li>
                </ul>
            </div>
            """,
        unsafe_allow_html=True
    )

    # ----------------------------------------------
    # BUSINESS RECOMMENDATIONS (Refactored to Neutral Cohesive Aesthetics)
    # ----------------------------------------------

    st.markdown("---")

    st.markdown(
        """
        <h2 style="
            text-align:left;
            color:#3E2723;
            font-size:2rem;
            font-weight:600;
            margin-bottom:15px;
        ">
            Recommended Actions
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
             <div class="brand-container-box">
                 <ul style="margin: 0; padding-left: 20px; color: #4E342E; font-size: 18px; line-height: 1.8;">
                     <li>Increase promotional focus on hero products and top-performing categories.
                     <li>Review low-performing products for redesign, bundling, or removal
                     <li>Replicate operational practices from the best-performing store.
                     <li>"Monitor product revenue concentration monthly to reduce dependency risk.
                     <li>Expand successful categories through cross-selling initiatives.
             """,
        unsafe_allow_html=True
    )

    recommendations = [

    ]

    for rec in recommendations:
        st.markdown(
            f"""
                <div class="brand-container-success">
                    <p style="margin:0; font-size:18px; color:#1B5E20; font-weight:500;"> {rec}</p>
                </div>
                """,
            unsafe_allow_html=True
        )
    # --------------------------------------------------
    # EXECUTIVE INSIGHTS
    # --------------------------------------------------

    st.markdown("---")
    st.markdown(
        """
        <h2 style="
            text-align:left;
            color:#3E2723;
            font-size:2rem;
            font-weight:600;
            margin-bottom:15px;
        ">
            Product Performance Explorer
        </h2>
        """,
        unsafe_allow_html=True
    )
    search_product = st.text_input(
        "Search Product Name"
    )

    product_table = (
        filtered
        .groupby(
            [
                "product_category",
                "product_type",
                "product_detail"
            ]
        )
        .agg(
            Revenue=("revenue", "sum"),
            Units=("transaction_qty", "sum"),
            Transactions=("transaction_id", "nunique")
        )
        .reset_index()
        .sort_values(
            "Revenue",
            ascending=False
        )
    )

    if search_product:
        product_table = product_table[
            product_table["product_detail"]
            .str.contains(
                search_product,
                case=False,
                na=False
            )
        ]

    st.dataframe(
        product_table,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"{len(product_table):,} products displayed"
    )

    # --------------------------------------------------
    # DOWNLOAD SECTION
    # --------------------------------------------------

    csv = product_table.to_csv(
        index=False
    )

    st.download_button(
        label="⬇ Download Product Analysis",
        data=csv,
        file_name="product_analysis.csv",
        mime="text/csv"
    )

    # --------------------------------------------------
    # METRIC DEFINITIONS
    # --------------------------------------------------

    with st.expander(
            "📖 Business Metric Definitions"
    ):

        st.markdown(
            """
### Revenue
Quantity Sold × Unit Price

### Transactions
Unique Purchase Transactions

### Units Sold
Total Product Quantity Purchased

### Revenue Concentration
Percentage of Revenue Generated by Top Products

### Hero Product
Highest Revenue Generating Product

### Product Portfolio
Total Unique Products Sold
"""
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------


# ---------------------------------------------------
# FOOTER: CORPORATE MINIMAL WITH TECH STACK
# ---------------------------------------------------
st.divider()
st.markdown(
    """
    <div style="text-align: center; padding: 15px 0 25px 0; color: #7B5E57; font-size: 14px; font-weight: 500; letter-spacing: 0.3px;">
        ☕ <b>Afficionado Coffee Roasters</b> | Comprehensive Business Intelligence Suite 
        <br>
        <span style="color: #A1887F; font-size: 14px; font-weight: 400; display: inline-block; margin-top: 5px;">
            Product Optimization & Revenue Contribution Analysis • Data Analyst Analytics Platform © 2026
        </span>
        <br>
        <span style="color: #BAA6A1; font-size: 13px; font-weight: 400; display: inline-block; margin-top: 6px; letter-spacing: 0.5px; text-transform: uppercase;">
            ⚡ Powered by: Python • Streamlit • Pandas • Plotly Express
        </span>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================================
# CENTRAL BUSINESS INTELLIGENCE UTILITY: ENGINE CORE EXTENSIONS
# =========================================================================
def compute_product_efficiency_score(df: pd.DataFrame, groupby_column: str) -> pd.DataFrame:
    """
    Computes the Product Efficiency Score (Gross Revenue per SKU).
    Formula: Total Revenue within Category or Location / Count of Active Unique Product IDs
    """
    if 'revenue' not in df.columns:
        df['revenue'] = df['transaction_qty'] * df['unit_price']

    efficiency_map = df.groupby(groupby_column).agg(
        total_revenue=('revenue', 'sum'),
        unique_skus=('product_id', 'nunique')
    ).reset_index()

    efficiency_map['product_efficiency_score'] = (
            efficiency_map['total_revenue'] / efficiency_map['unique_skus']
    ).round(2)

    return efficiency_map.sort_values(by='product_efficiency_score', ascending=False)