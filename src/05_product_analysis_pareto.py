from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "outputs" / "cleaned" / "coffee_shop_fe.csv"
OUT_PATH = BASE_DIR / "outputs" / "cleaned" / "product_pareto_analysis.csv"

# --------------------------------------------------
# Load data
# --------------------------------------------------
df = pd.read_csv(DATA_PATH)

print(f"Loaded {len(df)} rows")

# --------------------------------------------------
# Product Revenue Summary
# --------------------------------------------------
product_summary = (
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
        revenue=("revenue", "sum"),
        units=("transaction_qty", "sum"),
        transactions=("transaction_id", "nunique")
    )
    .sort_values("revenue", ascending=False)
)

# --------------------------------------------------
# Pareto Analysis (80/20 Rule)
# --------------------------------------------------
total_revenue = product_summary["revenue"].sum()

product_summary["revenue_pct"] = (
    product_summary["revenue"]
    / total_revenue
    * 100
)

product_summary["cumulative_revenue_pct"] = (
    product_summary["revenue_pct"]
    .cumsum()
)

product_summary["pareto_group"] = (
    product_summary["cumulative_revenue_pct"]
    <= 80
)

product_summary["pareto_group"] = (
    product_summary["pareto_group"]
    .map({True: "Top 80% Revenue", False: "Remaining Products"})
)

# --------------------------------------------------
# Save results
# --------------------------------------------------
product_summary.to_csv(OUT_PATH, index=False)

# --------------------------------------------------
# Print summary
# --------------------------------------------------
top_products = product_summary[
    product_summary["cumulative_revenue_pct"] <= 80
]

print("\n===== Pareto Analysis =====")
print(f"Total Products: {len(product_summary)}")
print(f"Products generating first 80% revenue: {len(top_products)}")

print("\nTop 10 Revenue Products")
print(
    product_summary[
        [
            "product_detail",
            "revenue",
            "units",
            "cumulative_revenue_pct"
        ]
    ].head(10)
)

print(f"\nSaved file:\n{OUT_PATH}")