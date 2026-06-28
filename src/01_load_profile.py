from pathlib import Path
import pandas as pd
import numpy as np

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Input and output paths
DATA_PATH = BASE_DIR / "data" / "raw" / "Afficionado_Coffee_Roasters_Transactions.csv"
OUT_PATH = BASE_DIR / "outputs" / "cleaned" / "coffee_shop_clean.csv"

# Create output folder if it doesn't exist
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Load file
df = pd.read_csv(DATA_PATH)

# Standardize columns
df.columns = (
    df.columns
      .str.strip()
      .str.lower()
      .str.replace(" ", "_")
)

print("Columns found:")
print(df.columns.tolist())

# Convert only if columns exist
if "transaction_id" in df.columns:
    df["transaction_id"] = df["transaction_id"].astype(str).str.strip()

if "store_id" in df.columns:
    df["store_id"] = df["store_id"].astype(str).str.strip()

if "product_id" in df.columns:
    df["product_id"] = df["product_id"].astype(str).str.strip()

if "year" in df.columns:
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

if "transaction_qty" in df.columns:
    df["transaction_qty"] = pd.to_numeric(df["transaction_qty"], errors="coerce")

if "unit_price" in df.columns:
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

# Parse time column if present
if "transaction_time" in df.columns:
    df["transaction_time_parsed"] = pd.to_datetime(
        df["transaction_time"],
        errors="coerce"
    )

# Revenue calculation
if {"transaction_qty", "unit_price"}.issubset(df.columns):
    df["revenue"] = df["transaction_qty"] * df["unit_price"]

# Cleaning filter
required_cols = ["product_id", "transaction_qty", "unit_price"]

if all(col in df.columns for col in required_cols):

    df_clean = df[
        (df["product_id"].notna()) &
        (df["product_id"].astype(str).str.len() > 0) &
        (df["transaction_qty"].notna()) &
        (df["transaction_qty"] > 0) &
        (df["unit_price"].notna()) &
        (df["unit_price"] > 0)
    ].copy()

else:
    print("Some required columns are missing.")
    df_clean = df.copy()

# Save cleaned file
df_clean.to_csv(OUT_PATH, index=False)

print(f"\nSaved cleaned file to: {OUT_PATH}")
print(f"Raw rows: {len(df)}")
print(f"Clean rows: {len(df_clean)}")