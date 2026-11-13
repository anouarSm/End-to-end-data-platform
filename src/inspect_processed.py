
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

files = [
    "orders.csv",
    "customers.csv",
    "order_items.csv",
    "products.csv",
    "payments.csv",
    "sellers.csv",
    "reviews.csv",
    "geolocation.csv",
    "category_translation.csv",
]

for filename in files:
    df = pd.read_csv(PROCESSED_DIR / filename)

    print(f"\n{'=' * 50}")
    print(f"Dataset: {filename}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print("Column names:", df.columns.tolist())
    print("Missing values:", df.isna().sum().sum())
