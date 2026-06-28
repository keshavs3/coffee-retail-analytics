from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "raw" / "Afficionado_Coffee_Roasters_Transactions.csv"
OUT_PATH = BASE_DIR / "outputs" / "cleaned" / "coffee_shop_clean.csv"

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# Standardize column names
df.columns = (
    df.columns
      .str.strip()
      .str.lower()
      .str.replace(" ", "_")
)

# Remove duplicate rows
df = df.drop_duplicates()

# Convert numeric columns
df["transaction_qty"] = pd.to_numeric(df["transaction_qty"], errors="coerce")
df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

# Create revenue column
df["revenue"] = df["transaction_qty"] * df["unit_price"]

# Parse time
df["transaction_time_parsed"] = pd.to_datetime(
    df["transaction_time"],
    format="%H:%M:%S",
    errors="coerce"
)
df['transaction_time_parsed'] = pd.to_datetime(df['transaction_time_parsed'])

# Save cleaned data
df.to_csv(OUT_PATH, index=False)

print("Saved cleaned file to:", OUT_PATH)
print("Rows:", len(df))