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
COLOR_BEAN = "#3E2723"   # Deep Roasted Brown
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

st.markdown(
    f"""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 25px;">
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
    options=sorted(df["product_category"].dropna().unique()),
    default=sorted(df["product_category"].dropna().unique())
)

filtered = df[df["product_category"].isin(category_filter)]
store_table = (
    filtered
    .groupby("store_location")
    .agg(
        Revenue=("revenue", "sum"),
        Transactions=("transaction_id", "nunique"),
        Units=("transaction_qty", "sum"),
        Unique_SKUs=("product_id", "nunique")  # NEW EXTENSION: Capture active menu size
    )
    .reset_index()
    .sort_values("Revenue", ascending=False)
)

# NEW EXTENSION: Vectorized calculation of Product Efficiency Score (Revenue per active SKU)
store_table["Product_Efficiency"] = (store_table["Revenue"] / store_table["Unique_SKUs"]).round(2)

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

total_revenue = filtered["revenue"].sum()
num_stores = filtered["store_location"].nunique()
avg_store_revenue = filtered.groupby("store_location")["revenue"].sum().mean()

top_store = store_table.iloc[0]["store_location"]
top_store_revenue = store_table.iloc[0]["Revenue"]

top_store_share = (
    top_store_revenue
    / store_table["Revenue"].sum()
) * 100


kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
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
                <h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 30px; font-weight: 600;">${total_revenue:,.0f}</h2>
            </div>
            """,
        unsafe_allow_html=True
    )

with kpi2:
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
                   <span style="color: #757575; font-size: 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;"> Stores Analyzed </span>
                   <h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 30px; font-weight: 600;">{num_stores}</h2>
               </div>
               """,
        unsafe_allow_html=True
    )


with kpi3:
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
                       <span style="color: #757575; font-size: 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;"> Top Store </span>
                       <h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 30px; font-weight: 600;">{top_store}</h2>
                   </div>
                   """,
        unsafe_allow_html=True
    )

with kpi4:
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
                           <span style="color: #757575; font-size: 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;"> Top Store Yield </span>
                           <h2 style="color: {COLOR_BEAN}; margin: 8px 0 0 0; font-size: 30px; font-weight: 600;">{top_store_revenue:,.0f}</h2>
                       </div>
                       """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# ENHANCED DATA ANNOTATION CAPTION (SCALED UP)
# ---------------------------------------------------
st.markdown(
    f"""
    <p style="
        font-size: 16px; 
        color: #7B5E57; 
        font-style: oblique;
        margin-top: 6px; 
        margin-bottom: 20px;
        letter-spacing: 0.2px;
    ">
         {top_store} contributes {top_store_share:.1f}% of company revenue
    </p>
    """,
    unsafe_allow_html=True
)


st.divider()
# ---------------------------------------------------
# STORE PERFORMANCE
# ---------------------------------------------------

chart_col1, chart_col2 = st.columns(2)
with chart_col1:

    st.subheader("$ Revenue by Store")

    fig = px.bar(
        store_table,
        x="store_location",
        y="Revenue",
        text_auto=".1s",
        color="Revenue",
        color_continuous_scale=CAFE_PALETTE,
        title="Revenue Contribution by Store Location"
    )
    fig.update_layout(template="plotly_white", height=500, coloraxis_showscale=False)

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.markdown(
            """
            <div style="font-size: 16px; color: #4E342E; line-height: 1.7; margin-top: 10px; margin-bottom: 25px;">
             <b> ➤ Revenue Distribution Performance Analysis:</b><br>
        Identifies the highest-performing stores and their contribution to overall company revenue.
            </div>
            """,
            unsafe_allow_html=True
        )
with chart_col2:

    st.subheader("🛒 Average Order Value")

    store_table["AOV"] = (
        store_table["Revenue"]
        /
        store_table["Transactions"]
    )

    fig = px.bar(
        store_table,
        x="store_location",
        y="AOV",
        text_auto=".2f",
        color="AOV",
        color_continuous_scale=CAFE_PALETTE,
    )

    fig.update_layout(template="plotly_white", height=500, coloraxis_showscale=False)
    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.markdown(
        """
        <div style="font-size: 16px; color: #4E342E; line-height: 1.7; margin-top: 10px; margin-bottom: 25px;">
         <b> ➤ Average Order Value (AOV) Efficiency Analysis:</b><br>
        Compares average spending per transaction across stores, highlighting locations that generate higher customer value through effective upselling and product mix.
        </div>
       """,
        unsafe_allow_html=True
    )

st.markdown("---")

# ---------------------------------------------------
# NEW EXTENSION: STORE-LEVEL PRODUCT EFFICIENCY METRICS MATRIX
# ---------------------------------------------------
st.markdown(
    f"""
    <h3 style="color: {COLOR_BEAN}; font-size: 1.8rem; font-weight: 700; margin-bottom: 12px;">
        📊 Store Footprint Catalog Efficiency
    </h3>
    """,
    unsafe_allow_html=True
)
st.markdown(
    "Unlike Average Order Value (customer ticket size), the **Product Efficiency Score** isolates asset productivity—"
    "showing how much gross revenue each active SKU generates on average within this specific store location."
)

# Generate multi-column container layout dynamically based on active stores
eff_cols = st.columns(len(store_table))

for index, row in enumerate(store_table.itertuples()):
    with eff_cols[index]:
        st.markdown(
            f"""
            <div style="
                background-color: #FDFBF7;
                padding: 18px 15px;
                border-radius: 12px;
                border: 1px solid #EFEBE9;
                border-top: 5px solid {COLOR_MOCHA};
                box-shadow: 0 2px 6px rgba(0,0,0,0.02);
                text-align: left;
                margin-bottom: 20px;
            ">
                <span style="color: #757575; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;">
                    {row.store_location} Yield
                </span>
                <h3 style="color: {COLOR_BEAN}; margin: 6px 0 2px 0; font-size: 24px; font-weight: 700;">
                    ${row.Product_Efficiency:,.2f} <span style="font-size: 14px; font-weight: 500; color: #757575;">/ SKU</span>
                </h3>
                <span style="color: #7B5E57; font-size: 13.5px; font-weight: 600; font-style: italic;">
                    📋 {int(row.Unique_SKUs)} Distinct Products Sold
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("---")

st.subheader("𖠿 Store Efficiency Comparison")

store_table["Revenue per Unit"] = (
    store_table["Revenue"]
    /
    store_table["Units"]
)

fig = px.bar(
    store_table,
    x="store_location",
    y="Revenue per Unit",
    text_auto=".2f",
    color="Revenue per Unit",
    color_continuous_scale=[
        "#D7CCC8",
        "#A1887F",
        "#3E2723"
    ]
)

fig.update_layout(
    height=350,
    template="plotly_white",
    coloraxis_showscale=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)
st.markdown(
    """
    <div style="font-size: 16px; color: #4E342E; line-height: 1.7; margin-top: 10px; margin-bottom: 25px;">
         <b> ➤ Revenue per Unit Efficiency Analysis:</b><br>
        Stores with higher values generate more revenue from each product sold, indicating stronger pricing power and premium product performance.
    </div>
    """,
    unsafe_allow_html=True
)
tab1, tab2 = st.tabs(
    [
        "⏰ Operational Peak Hours",
        "📋 Store Performance Ledger"
    ]
)
with tab1:
    peak_hour_data = (
        filtered
        .groupby("hour")["revenue"]
        .sum()
    )

    peak_hour = peak_hour_data.idxmax()

    peak_hour_revenue = peak_hour_data.max()

    st.subheader("⏱️ Peak Hour Insights")

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Peak Revenue Hour",
            f"{peak_hour}:00"
        )

    with c2:
        st.metric(
            "Revenue During Peak Hour",
            f"${peak_hour_revenue:,.0f}"
        )
    hr = (
        filtered
        .groupby("hour")["revenue"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        hr,
        x="hour",
        y="revenue",
        markers=True,
        title="Hourly Revenue Trend"
    )

    fig.add_vline(
        x=peak_hour,
        line_dash="dash",
        line_color="red"
    )

    fig.add_annotation(
        x=peak_hour,
        y=peak_hour_revenue,
        text=f"Peak Hour ({peak_hour}:00)",
        showarrow=True
    )

    fig.update_layout(
        height=400,
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.markdown(
        """
        <div style="font-size: 16px; color: #4E342E; line-height: 1.7; margin-top: 10px; margin-bottom: 25px;">
             <b> ➤ Hourly Revenue Profile Performance Analysis:</b><br>
            Shows revenue patterns throughout the day, highlighting peak business hours and customer demand trends. 
        Useful for optimizing staffing, inventory planning, and promotional timing.
        </div>
        """,
        unsafe_allow_html=True
    )
    # ---------------------------------------------------
    # PEAK HOUR INTERPRETATION PANEL (THEMED OVERHAUL)
    # ---------------------------------------------------
    st.divider()

    peak_store_hour = (
        filtered
        .groupby(
            ["store_location", "hour"]
        )["revenue"]
        .sum()
        .reset_index()
    )
    peak_store_hour = (
        peak_store_hour
        .sort_values("revenue", ascending=False)
        .groupby("store_location")
        .first()
        .reset_index()
    )
    st.subheader("𖠿 Peak Hour by Store")

    st.dataframe(
        peak_store_hour.rename(
            columns={
                "hour": "Peak Hour",
                "revenue": "Revenue"
            }
        ),
        use_container_width=True,
        hide_index=True
    )
st.divider()
# ---------------------------------------------------
# HOURLY REVENUE
# ---------------------------------------------------

with tab2:
    store_table["Revenue Rank"] = (
        store_table["Revenue"]
        .rank(
            ascending=False
        )
    )
    store_table["AOV"] = (
            store_table["Revenue"]
            /
            store_table["Transactions"]
    )

    store_table["Revenue per Unit"] = (
            store_table["Revenue"]
            /
            store_table["Units"]
    )
    store_table = store_table[
        [
            "Revenue Rank",
            "store_location",
            "Revenue",
            "Transactions",
            "Units",
            "AOV",
            "Revenue per Unit"
        ]
    ]
    st.dataframe(
        store_table.style.background_gradient(
            subset=["Revenue"],
            cmap="Oranges"
        ),
        use_container_width=True
    )

best_store = (
    store_table.iloc[0]["store_location"]
)

worst_store = (
    store_table.iloc[-1]["store_location"]
)
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
            ⫶☰ Peak Hour Executive Summary
        </h3>
        <ul style="color: #4E342E; font-size: 18px; line-height: 1.8; margin: 0; padding-left: 20px;">
            <li> <b>**{top_store}**</b> is the highest-performing location, contributing <b>**{top_store_share:.1f}%**</b> of total revenue.</li>
            <li> The business currently operates across <b>**{num_stores} stores**</b> generating <b>**${total_revenue:,.0f}**</b> in revenue.</li>
            <li> Store-level performance remains relatively concentrated, making top-store performance critical to overall business success.</li>
            <li>Highest net operational volume is generated systematically at <b>{peak_hour}:00</b>.</li>
            <li>This singular daily peak hour contributes approximately <b>${peak_hour_revenue:,.0f}</b> in gross returns.</li>
           
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

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
            📌 Strategic Recommendations
        </h3>
        <ol style="color: #4E342E; font-size: 18px; line-height: 1.8; margin: 0; padding-left: 20px;">
            <li><b>Replicate operational practices</b> from the top-performing benchmark hub <b>{top_store}</b> across auxiliary branches.</li>
            <li><b>Schedule additional staffing allocation</b> carefully around <b>{peak_hour}:00</b> to protect customer service metrics.</li>
            <li><b>Focus marketing and promotion mechanics</b> toward retail footprints generating a lower Average Order Value (AOV).</li>
            <li><b>Improve active product assortments</b> within underperforming regional spaces to match localized demand.</li>
            <li><b>Track Revenue per Transaction and AOV</b> monthly to maintain strong profit margins.</li>
             <li>Consider optimizing floor staff schedules and kitchen inventory staging explicitly during this premium performance frame.</li>
            <li><b>Continuously benchmark baseline store location units</b> against the peak efficiency metrics of <b>{top_store}</b>.</li>
        </ol>
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
