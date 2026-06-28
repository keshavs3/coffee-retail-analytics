from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

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
# Pareto Analysis
# --------------------------------------------------
total_revenue = product_summary["revenue"].sum()

product_summary["revenue_pct"] = (
    product_summary["revenue"] / total_revenue * 100
)

product_summary["cumulative_revenue_pct"] = (
    product_summary["revenue_pct"].cumsum()
)

product_summary["pareto_group"] = (
    product_summary["cumulative_revenue_pct"]
    <= 80
)

product_summary["pareto_group"] = (
    product_summary["pareto_group"]
    .map({
        True: "Top 80% Revenue",
        False: "Remaining Products"
    })
)

# --------------------------------------------------
# Save table
# --------------------------------------------------
product_summary.to_csv(OUT_PATH, index=False)

# --------------------------------------------------
# Pareto Chart
# --------------------------------------------------
FIGURE_DIR = BASE_DIR / "outputs" / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

chart_path = FIGURE_DIR / "pareto_product_revenue.png"

plt.figure(figsize=(12, 6))

plt.bar(
    range(len(product_summary)),
    product_summary["revenue"],
    label="Revenue"
)

plt.plot(
    range(len(product_summary)),
    product_summary["cumulative_revenue_pct"],
    color="red",
    linewidth=2,
    label="Cumulative %"
)

plt.axhline(
    y=80,
    color="green",
    linestyle="--",
    label="80% Threshold"
)

plt.title("Pareto Analysis of Product Revenue")
plt.xlabel("Products (sorted by revenue)")
plt.ylabel("Revenue / Cumulative %")
plt.legend()

plt.tight_layout()
plt.savefig(chart_path, dpi=150)
plt.close()

# --------------------------------------------------
# Summary
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

print(f"\nSaved table: {OUT_PATH}")
print(f"Saved chart: {chart_path}")