from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "outputs" / "cleaned" / "coffee_shop_fe.csv"
CHART_DIR = BASE_DIR / "outputs" / "charts"

CHART_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Load Data
# --------------------------------------------------
df = pd.read_csv(DATA_PATH)

print(f"Loaded {len(df)} rows")

# --------------------------------------------------
# Product KPIs
# --------------------------------------------------
product_kpis = (
    df.groupby(
        [
            "product_id",
            "product_detail",
            "product_category",
            "product_type"
        ],
        as_index=False
    )
    .agg(
        units=("transaction_qty", "sum"),
        revenue=("revenue", "sum"),
        txns=("transaction_id", "nunique")
    )
    .sort_values("revenue", ascending=False)
)

# --------------------------------------------------
# Top Products
# --------------------------------------------------
top10_rev = product_kpis.head(10)

top10_units = (
    product_kpis
    .sort_values("units", ascending=False)
    .head(10)
)

print("\nTop 10 Products by Revenue")
print(
    top10_rev[
        ["product_detail", "revenue", "units", "txns"]
    ]
)

print("\nTop 10 Products by Units Sold")
print(
    top10_units[
        ["product_detail", "units", "revenue", "txns"]
    ]
)

# --------------------------------------------------
# Chart 1: Top Revenue Products
# --------------------------------------------------
plt.figure(figsize=(12, 6))

sns.barplot(
    data=top10_rev,
    x="revenue",
    y="product_detail"
)

plt.title("Top 10 Products by Revenue")
plt.xlabel("Revenue")
plt.ylabel("Product")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "top10_products_by_revenue.png",
    bbox_inches="tight"
)

plt.show()

# --------------------------------------------------
# Category Revenue
# --------------------------------------------------
category_revenue = (
    df.groupby(
        "product_category",
        as_index=False
    )
    .agg(
        revenue=("revenue", "sum")
    )
    .sort_values("revenue", ascending=False)
)

print("\nRevenue by Category")
print(category_revenue)

# --------------------------------------------------
# Chart 2: Revenue by Category
# --------------------------------------------------
plt.figure(figsize=(12, 6))

sns.barplot(
    data=category_revenue,
    x="revenue",
    y="product_category"
)

plt.title("Revenue by Product Category")
plt.xlabel("Revenue")
plt.ylabel("Category")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "revenue_by_category.png",
    bbox_inches="tight"
)

plt.show()

# --------------------------------------------------
# Time Segment Revenue
# --------------------------------------------------
if "time_segment" in df.columns:

    segment_revenue = (
        df.groupby(
            "time_segment",
            as_index=False
        )
        .agg(
            revenue=("revenue", "sum")
        )
        .sort_values("revenue", ascending=False)
    )

    print("\nRevenue by Time Segment")
    print(segment_revenue)

    plt.figure(figsize=(10, 5))

    sns.barplot(
        data=segment_revenue,
        x="time_segment",
        y="revenue"
    )

    plt.title("Revenue by Time Segment")

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / "revenue_by_time_segment.png",
        bbox_inches="tight"
    )

    plt.show()

print("\nEDA Complete")
print(f"Charts saved to: {CHART_DIR}")