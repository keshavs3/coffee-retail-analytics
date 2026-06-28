from pathlib import Path
import pandas as pd
import numpy as np

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "outputs" / "cleaned" / "coffee_shop_clean.csv"
OUT_PATH = BASE_DIR / "outputs" / "cleaned" / "coffee_shop_fe.csv"

# --------------------------------------------------
# Load data
# --------------------------------------------------
df = pd.read_csv(DATA_PATH)

print(f"Loaded {len(df)} rows")

# --------------------------------------------------
# Ensure required columns exist
# --------------------------------------------------
required_cols = [
    "transaction_time_parsed",
    "product_id",
    "transaction_qty",
    "revenue"
]

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    raise KeyError(
        f"Missing columns in coffee_shop_clean.csv: {missing_cols}"
    )

# --------------------------------------------------
# Datetime features
# --------------------------------------------------
df["transaction_time_parsed"] = pd.to_datetime(
    df["transaction_time_parsed"],
    errors="coerce"
)

df["hour"] = df["transaction_time_parsed"].dt.hour

# --------------------------------------------------
# Time Segments
# --------------------------------------------------
def time_segment(hour):
    if pd.isna(hour):
        return "unknown"
    elif 5 <= hour <= 10:
        return "morning_rush"
    elif 11 <= hour <= 14:
        return "lunch"
    elif 15 <= hour <= 17:
        return "afternoon"
    elif 18 <= hour <= 21:
        return "evening"
    else:
        return "off_hours"

df["time_segment"] = df["hour"].apply(time_segment)

# --------------------------------------------------
# Revenue Contribution %
# --------------------------------------------------
total_revenue = df["revenue"].sum()

product_revenue = (
    df.groupby("product_id")["revenue"]
      .sum()
)

df["revenue_contribution_pct"] = (
    df["product_id"].map(product_revenue)
    / total_revenue
    * 100
)

# --------------------------------------------------
# Revenue Rank
# --------------------------------------------------
revenue_rank = (
    product_revenue
    .rank(ascending=False, method="dense")
    .astype(int)
)

df["revenue_rank"] = (
    df["product_id"]
    .map(revenue_rank)
)

# --------------------------------------------------
# Volume Rank
# --------------------------------------------------
product_volume = (
    df.groupby("product_id")["transaction_qty"]
      .sum()
)

volume_rank = (
    product_volume
    .rank(ascending=False, method="dense")
    .astype(int)
)

df["volume_rank"] = (
    df["product_id"]
    .map(volume_rank)
)

# --------------------------------------------------
# Save Feature Engineered Dataset
# --------------------------------------------------
df.to_csv(OUT_PATH, index=False)

print(f"Feature-engineered file saved to:\n{OUT_PATH}")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")