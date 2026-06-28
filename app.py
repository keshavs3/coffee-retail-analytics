import os
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
        .kpi-card {
            background-color: #FDFBF7;
            border: 1px solid #EFEBE9;
            border-left: 5px solid #5D4037;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            margin-bottom: 15px;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        .kpi-title {
            font-size: 14px;
            color: #757575;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        .kpi-value {
            font-size: 26px;
            color: #3E2723;
            font-weight: 700;
        }
        .brand-container-box {
            background-color: #FDFBF7;
            border: 1px solid #EFEBE9;
            border-left: 6px solid #5D4037;
            padding: 22px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        .brand-container-success {
            background-color: #F8F9FA;
            border: 1px solid #E0E0E0;
            border-left: 6px solid #2E7D32;
            padding: 16px;
            border-radius: 6px;
            margin-bottom: 12px;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Corporate Theme Color Constants
COLOR_BEAN = "#3E2723"
COLOR_MOCHA = "#7B5E57"
COLOR_LATTE = "#A1887F"
COLOR_CREMA = "#D7CCC8"
CAFE_PALETTE = [COLOR_BEAN, COLOR_MOCHA, COLOR_LATTE, COLOR_CREMA, "#EFEBE9"]

# --------------------------------------------------
# ENVIRONMENT AND DIRECTORY RESOLUTION (Cloud-Safe Fix)
# --------------------------------------------------
ROOT_DIR = Path(os.getcwd())

DATA_PATH = ROOT_DIR / "outputs" / "cleaned" / "coffee_shop_fe.csv"
CSS_PATH = ROOT_DIR / "assets" / "style.css"

if CSS_PATH.exists():
    with open(CSS_PATH, encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

if not DATA_PATH.exists():
    st.error(f"Dataset not found at the targeted route: {DATA_PATH}")
    st.info("Ensure your outputs directory path is checked into GitHub correctly.")
    st.stop()


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df = df.drop_duplicates()
    return df


df = load_data()
last_updated = pd.Timestamp.now().strftime("%d %b %Y %H:%M")
record_count = len(df)


def apply_theme(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13, color="#424242", family="'Helvetica Neue', Helvetica, Arial, sans-serif"),
        title_font=dict(size=18, color=COLOR_BEAN, family="'Helvetica Neue', Helvetica, Arial, sans-serif"),
        margin=dict(l=30, r=30, t=50, b=30)
    )
    fig.update_xaxes(showgrid=False, linecolor="#E0E0E0")
    fig.update_yaxes(showgrid=True, gridcolor="#F5F5F5", linecolor="#E0E0E0")
    return fig


# --------------------------------------------------
# HEADER UI
# --------------------------------------------------
st.markdown(
    f"""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 25px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
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
    st.caption(f"Last Updated: {last_updated}")
with meta2:
    st.markdown(
        f"<p style='text-align:right; margin:0; font-size:0.85rem; color:gray;'>Records Analyzed: <b>{record_count:,}</b></p>",
        unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR CONTROL FILTER ENGINE
# --------------------------------------------------
st.sidebar.markdown(
    """
    # ☕ Coffee Analytics
    Executive Dashboard  
    Monitor revenue, products, categories and store performance workflows.
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

top_n = st.sidebar.slider("Top Products Display Range", min_value=5, max_value=20, value=10)

# --------------------------------------------------
# FILTER EXECUTION DATA-STREAM
# --------------------------------------------------
filtered = df.copy()
filtered = filtered[filtered["store_location"].isin(store_filter)]
filtered = filtered[filtered["product_category"].isin(category_filter)]

if filtered.empty:
    st.warning("No data available matching your selected dashboard filter limits.")
    st.stop()

# METRICS CALCULATIONS
total_revenue = filtered["revenue"].sum()
total_transactions = filtered["transaction_id"].nunique()
total_units = filtered["transaction_qty"].sum()
avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0
unique_products = filtered["product_id"].nunique()

# Navigation Router
section = st.radio("", ["Overview", "Products", "Stores", "Insights"], horizontal=True)
st.markdown("---")

# ==================================================
# OVERVIEW METRICS ROUTE
# ==================================================
if section == "Overview":
    st.markdown("## Dashboard Overview")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-title">Revenue</div><div class="kpi-value">${total_revenue:,.0f}</div></div>',
            unsafe_allow_html=True)
    with k2:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-title">Transactions</div><div class="kpi-value">{total_transactions:,}</div></div>',
            unsafe_allow_html=True)
    with k3:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-title">Units Sold</div><div class="kpi-value">{int(total_units):,}</div></div>',
            unsafe_allow_html=True)
    with k4:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-title">Avg Order Value</div><div class="kpi-value">${avg_order_value:,.2f}</div></div>',
            unsafe_allow_html=True)

    st.subheader("Data Quality Summary")
    dq1, dq2, dq3 = st.columns(3)
    with dq1:
        st.metric("Rows", f"{len(filtered):,}")
    with dq2:
        st.metric("Missing Values", f"{filtered.isna().sum().sum():,}")
    with dq3:
        st.metric("Duplicate Rows", f"{filtered.duplicated().sum():,}")

    st.markdown("---")

    # EXECUTIVE SUMMARY LAYER
    try:
        top_store = filtered.groupby("store_location")["revenue"].sum().idxmax()
    except Exception:
        top_store = "N/A"

    try:
        top_category_name = filtered.groupby("product_category")["revenue"].sum().idxmax()
    except Exception:
        top_category_name = "N/A"

    st.markdown(
        f"""
        <div class="brand-container-box">
            <h3 style="margin: 0 0 12px 0; color: #3E2723; font-size: 1.9rem;">Executive Summary</h3>
            <p style="margin: 6px 0; font-size: 18px; color: #4E342E;"><b>Total Revenue:</b> ${total_revenue:,.0f}</p>
            <p style="margin: 6px 0; font-size: 18px; color: #4E342E;"><b>Top Performing Store:</b> {top_store}</p>
            <p style="margin: 6px 0; font-size: 18px; color: #4E342E;"><b>Top Revenue Category:</b> {top_category_name}</p>
            <p style="margin: 6px 0; font-size: 18px; color: #4E342E;"><b>Products Analyzed:</b> {unique_products:,}</p>
            <p style="margin: 12px 0 0 0; font-size: 16px; color: #757575; line-height: 1.5;">
                This workspace provides an administrative analysis overview tracking portfolio health metrics, structural dependency thresholds, and sales metrics.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # REVENUE TREND CHART BY HOUR
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Revenue Trend by Hour")
        if "hour" in filtered.columns:
            hourly = filtered.groupby("hour", as_index=False)["revenue"].sum().sort_values("hour")
            fig = px.line(hourly, x="hour", y="revenue", markers=True, hover_data={"hour": True, "revenue": ":,.0f"})
            fig.update_traces(line_color=COLOR_BEAN, line_width=4, marker=dict(size=6, color=COLOR_MOCHA))
            fig = apply_theme(fig)
            st.plotly_chart(fig, use_container_width=True, theme=None)

            # Data Narrative description for the Time-Series chart
            st.markdown(
                """
                <div style="font-size: 14.5px; color: #4E342E; line-height: 1.6; margin-top: 8px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
                    <b>➤ Hourly Revenue Distribution Profile:</b><br>
                    Tracks intra-day transaction density and sales velocities across operational windows. 
                    Use this distribution to align barista shift pacing, batch-brewing schedules, 
                    and inventory prep around peak consumer traffic blocks.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("Hour dimension metrics not parsed in active dataset profiles.")

    with right_col:
        st.subheader("Revenue by Category")
        category_rev = filtered.groupby("product_category", as_index=False)["revenue"].sum().sort_values("revenue",
                                                                                                         ascending=False)
        fig = px.bar(category_rev, x="product_category", y="revenue", color="product_category", text_auto=".2s",
                     color_discrete_sequence=CAFE_PALETTE)
        fig = apply_theme(fig)
        fig.update_layout(showlegend=False, xaxis_title="Category", yaxis_title="Revenue ($)")
        st.plotly_chart(fig, use_container_width=True, theme=None)

        # Data Narrative description for the Category Pareto breakdown chart
        st.markdown(
            """
            <div style="font-size: 14.5px; color: #4E342E; line-height: 1.6; margin-top: 8px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
                <b>➤ Product Category Contribution Mix:</b><br>
                Isolates macro gross volume contributions across primary inventory segments. 
                Monitoring this baseline spread helps gauge catalog diversification, track product dependency, 
                and flag shifting customer category preference cycles.
            </div>
            """,
            unsafe_allow_html=True
        )

# ==================================================
# PRODUCTS ROUTE
# ==================================================
if section == "Products":
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader(f"Top {top_n} Products Performance")
        top_products = filtered.groupby("product_detail", as_index=False).agg(revenue=("revenue", "sum")).sort_values(
            "revenue", ascending=False).head(top_n)
        fig = px.bar(top_products, x="revenue", y="product_detail", orientation="h", color="revenue",
                     color_continuous_scale=[[0, COLOR_CREMA], [1, COLOR_BEAN]], text_auto=".2s")
        fig = apply_theme(fig)
        fig.update_layout(coloraxis_showscale=False, xaxis_title="Revenue ($)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True, theme=None)

        # Description for Top Products Horizontal Bar Chart
        st.markdown(
            """
            <div style="font-size: 14.5px; color: #4E342E; line-height: 1.6; margin-top: 8px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
                <b>➤ Product Velocity Leaderboard:</b><br>
                Ranks individual menu SKUs based on absolute gross returns. 
                Use this breakdown to pinpoint high-volume menu assets, validate promotional campaigns, 
                and identify premium items for premium placement or cross-selling.
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_b:
        st.subheader("Category Revenue Share Mix")
        category_mix = filtered.groupby("product_category", as_index=False)["revenue"].sum()
        fig = px.pie(category_mix, names="product_category", values="revenue", hole=0.55,
                     color_discrete_sequence=CAFE_PALETTE)
        fig = apply_theme(fig)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True, theme=None)

        # Description for Category Share Donut Chart
        st.markdown(
            """
            <div style="font-size: 14.5px; color: #4E342E; line-height: 1.6; margin-top: 8px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
                <b>➤ Category Dependency Distribution:</b><br>
                Illustrates the percentage share that each product line contributes to the total portfolio. 
                Monitoring this mix helps ensure macro portfolio diversification and flags structural over-reliance 
                on a single segment.
            </div>
            """,
            unsafe_allow_html=True
        )
    # PARETO DENSITY FRAMEWORK
    st.markdown("---")
    st.subheader("Revenue Concentration (Pareto Analysis)")
    pareto = filtered.groupby("product_detail", as_index=False).agg(revenue=("revenue", "sum")).sort_values("revenue",
                                                                                                            ascending=False).reset_index(
        drop=True)
    pareto["rank"] = range(1, len(pareto) + 1)
    pareto["share"] = pareto["revenue"] / pareto["revenue"].sum()
    pareto["cum_share"] = pareto["share"].cumsum() * 100

    fig = px.bar(pareto, x="rank", y="revenue", labels={"rank": "Products Ranked by Revenue", "revenue": "Revenue ($)"})
    fig.update_traces(marker_color=COLOR_CREMA, opacity=0.85, name="SKU Revenue")
    fig.add_scatter(x=pareto["rank"], y=pareto["cum_share"], mode="lines", line=dict(color=COLOR_BEAN, width=3),
                    name="Cumulative Share %", yaxis="y2")
    fig.add_hline(y=80, line_dash="dash", line_color="#D84315", annotation_text="80% Threshold", yref="y2")
    fig.update_layout(height=500, yaxis=dict(title="Revenue ($)"),
                      yaxis2=dict(title="Cumulative Revenue %", overlaying="y", side="right", range=[0, 100]),
                      showlegend=True)
    fig = apply_theme(fig)
    st.plotly_chart(fig, use_container_width=True, theme=None)

    # Brand-aligned Pareto Analysis narrative block placed beneath the figure canvas
    st.markdown(
        """
        <div style="font-size: 14.5px; color: #4E342E; line-height: 1.6; margin-top: 8px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
            <b>➤ Pareto Principle Revenue Concentration Audit:</b><br>
            Visualizes the 80/20 rule by plotting individual SKU yields against their cumulative percentage share. 
            Items to the left of the intersecting 80% threshold represent your vital core revenue anchors, 
            while columns to the right isolate the low-velocity tail candidates prime for menu simplification or elimination.
        </div>
        """,
        unsafe_allow_html=True
    )

    # PORTFOLIO METRIC INFO ENGINE CARD BLOCK
    product_rev = filtered.groupby("product_detail")["revenue"].sum().sort_values(ascending=False)
    if len(product_rev) > 0:
        hero_product = product_rev.index[0]
        hero_revenue = product_rev.iloc[0]
        hero_share = (hero_revenue / total_revenue) * 100
        avg_product_revenue = product_rev.mean()
        multiplier = hero_revenue / avg_product_revenue if avg_product_revenue > 0 else 1
        top_20_count = max(1, int(len(product_rev) * 0.20))
        pareto_concentration = (product_rev.head(top_20_count).sum() / total_revenue) * 100

        st.markdown(
            f"""
            <div style="background-color: #FDFBF7; padding: 22px; border-radius: 8px; border: 1px solid #EFEBE9; border-left: 6px solid #2E7D32; margin-top: 15px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
                <h3 style="margin: 0 0 15px 0; color: #1B5E20; font-size: 2.2rem;">Portfolio Concentration & Performance</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                    <div style="flex: 1.5; min-width: 280px;">
                        <h4 style="margin: 0 0 4px 0; color: #2E7D32; font-size: 1.8rem;">🥇 Hero Product</h4>
                        <p style="margin: 6px 0; font-size: 24px; font-weight: bold; color: #3E2723;">➝ {hero_product}</p>
                    </div>
                    <div style="flex: 1; min-width: 180px; background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                        <div style="font-size: 14px; color: #757575; text-transform: uppercase;">Hero Revenue</div>
                        <div style="font-size: 20px; font-weight: 800; color: #3E2723;">${hero_revenue:,.2f}</div>
                        <div style="font-size: 16px; color: #2E7D32; font-weight: 600;">{hero_share:.1f}% share</div>
                    </div>
                    <div style="flex: 1; min-width: 180px; background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                        <div style="font-size: 14px; color: #757575; text-transform: uppercase;">Catalog Multiplier</div>
                        <div style="font-size: 20px; font-weight: 800; color: #2E7D32;">{multiplier:.1f}x Higher</div>
                        <div style="font-size: 16px; color: #A1887F;">than average variant</div>
                    </div>
                    <div style="flex: 1; min-width: 180px; background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                        <div style="font-size: 14px; color: #757575; text-transform: uppercase;">Top 20% Pareto Share</div>
                        <div style="font-size: 20px; font-weight: 800; color: #3E2723;">{pareto_concentration:.1f}%</div>
                        <div style="font-size: 16px; color: #5D4037;">Generated by {top_20_count} core SKUs</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ==================================================
# STORES ROUTE
# ==================================================
if section == "Stores":
    st.markdown("## Detailed Store Performance Profile Matrix")

    store_ranking = filtered.groupby("store_location").agg(
        Revenue=("revenue", "sum"),
        Transactions=("transaction_id", "nunique"),
        Units=("transaction_qty", "sum")
    ).reset_index().sort_values("Revenue", ascending=False)

    store_ranking.insert(0, "Rank", range(1, len(store_ranking) + 1))
    store_ranking["Avg Basket"] = store_ranking["Revenue"] / store_ranking["Transactions"]

    top_store = store_ranking.iloc[0]["store_location"]
    top_revenue = store_ranking.iloc[0]["Revenue"]
    best_store_share = (top_revenue / store_ranking["Revenue"].sum()) * 100

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.metric("Top Revenue Location", top_store)
    with sc2:
        st.metric("Top Location Yield", f"${top_revenue:,.0f}")
    with sc3:
        st.metric("Corporate Contribution Share", f"{best_store_share:.1f}%")

    st.markdown("---")

    chart_col, pie_col = st.columns(2)

    with chart_col:
        st.subheader("Gross Store Revenue Profile")
        fig = px.bar(store_ranking, x="store_location", y="Revenue", color_discrete_sequence=[COLOR_MOCHA])
        fig = apply_theme(fig)
        st.plotly_chart(fig, use_container_width=True, theme=None)

        # Description for Store Revenue Bar Chart
        st.markdown(
            """
            <div style="font-size: 14.5px; color: #4E342E; line-height: 1.6; margin-top: 8px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
                <b>➤ Location Yield Comparison:</b><br>
                Ranks absolute gross revenue performance across active retail locations. 
                Use this metric to quickly identify regional benchmark hubs and pinpoint locations 
                requiring strategic intervention or targeted promotion support.
            </div>
            """,
            unsafe_allow_html=True
        )

    with pie_col:
        st.subheader("Market Share Footprint Breakdowns")
        fig = px.pie(store_ranking, names="store_location", values="Revenue", hole=0.6,
                     color_discrete_sequence=CAFE_PALETTE)
        fig = apply_theme(fig)
        st.plotly_chart(fig, use_container_width=True, theme=None)

        # Description for Market Share Donut Chart
        st.markdown(
            """
            <div style="font-size: 14.5px; color: #4E342E; line-height: 1.6; margin-top: 8px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
                <b>➤ Store Location Revenue Share:</b><br>
                Illustrates the percentage slice of total brand revenue owned by each store hub. 
                Monitoring this proportional mix flags structural concentration risks and highlights how heavily 
                overall business success relies on a single storefront asset.
            </div>
            """,
            unsafe_allow_html=True
        )

    # DATAFRAME DATA VIEW TABLE
    st.divider()
    st.subheader("Store Core Performance Rankings Ledger")
    display_store = store_ranking.copy()
    display_store["Revenue"] = display_store["Revenue"].map("${:,.0f}".format)
    display_store["Avg Basket"] = display_store["Avg Basket"].map("${:,.2f}".format)
    st.dataframe(display_store, use_container_width=True, hide_index=True)

    # Description for the Core Performance Ledger Table
    st.markdown(
        """
        <div style="font-size: 14.5px; color: #4E342E; line-height: 1.6; margin-top: 8px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
            <b>➤ Operational Performance Scorecard:</b><br>
            Consolidates raw transaction tallies, overall volume metrics, and ticket-level averages (Avg Basket) into a clean corporate ledger. 
            It allows management to contrast sheer scaling power against true customer ticket efficiency.
        </div>
        """,
        unsafe_allow_html=True
    )
# ==================================================
# INSIGHTS ENGINE MANAGEMENT ROUTE
# ==================================================
if section == "Insights":
    st.subheader("⚠️ High Concentration Risk & Low-Velocity Menu SKUs")
    bottom_products = filtered.groupby(["product_category", "product_detail"]).agg(
        Revenue=("revenue", "sum"),
        Units=("transaction_qty", "sum")
    ).reset_index().sort_values("Revenue", ascending=True).head(10)

    st.dataframe(bottom_products, use_container_width=True, hide_index=True)
    st.markdown("---")

    # EXECUTIVE INSIGHT LABELS STRINGS (Fixed Unclosed HTML Tags Error)
    st.markdown(
        """
        <div class="brand-container-box">
            <h3 style="margin: 0 0 12px 0; color: #3E2723; font-size: 1.6rem;">Key Operational Findings</h3>
            <ul style="margin: 0; padding-left: 20px; color: #4E342E; font-size: 16px; line-height: 1.8;">
                <li>High portfolio distribution reliance exists within core signature product lines.</li>
                <li>Long-tail variance drag reduces backroom catalog asset performance.</li>
                <li>Strategic inventory padding should track cross-regional demand spikes.</li>
            </ul>
        </div>

        <div class="brand-container-box" style="border-left-color: #2E7D32;">
            <h3 style="margin: 0 0 12px 0; color: #1B5E20; font-size: 1.6rem;">Recommended Administrative Interventions</h3>
            <ul style="margin: 0; padding-left: 20px; color: #1B5E20; font-size: 16px; line-height: 1.8;">
                <li>Accelerate floor labor patterns around morning peak metrics.</li>
                <li>Prune long-tail items with low revenue velocity.</li>
                <li>Deploy cross-selling initiatives across secondary categories.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # SEARCH PRODUCT EXPLORER PIPELINE CONTAINER
    st.subheader("Product Performance Explorer Matrix Engine")
    search_product = st.text_input("Search Product Database File Target String")

    product_table = filtered.groupby(["product_category", "product_type", "product_detail"]).agg(
        Revenue=("revenue", "sum"),
        Units=("transaction_qty", "sum")
    ).reset_index().sort_values("Revenue", ascending=False)

    if search_product:
        product_table = product_table[
            product_table["product_detail"].str.contains(search_product, case=False, na=False)]

    st.dataframe(product_table, use_container_width=True, hide_index=True)

    st.download_button(
        label="⬇ Download Exported Product CSV Matrix Ledger",
        data=product_table.to_csv(index=False),
        file_name="product_performance_extract.csv",
        mime="text/csv"
    )

# ---------------------------------------------------
# CORPORATE SYSTEM ENGINE FOOTER INFRASTRUCTURE
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