import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from connection import get_engine

SRC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC_DIR))

from transformations.cleaning import convert_date_columns


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Parent tables must be loaded before their dependent tables.
LOAD_ORDER = [
    "customers",
    "sellers",
    "products",
    "orders",
    "order_items",
    "payments",
    "reviews",
    "category_translation"
]
DATETIME_COLUMNS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": [
        "shipping_limit_date",
    ],
    "reviews": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
}


def load_datasets(engine):

    with engine.begin() as connection:

        # Remove previous data before loading the new data.
        connection.execute(text("""
            TRUNCATE TABLE
                reviews,
                payments,
                order_items,
                orders,
                products,
                sellers,
                customers
            RESTART IDENTITY
        """))

        for table in LOAD_ORDER:

            file_path = PROCESSED_DIR / f"{table}.csv"

            df = pd.read_csv(file_path)
            if table in DATETIME_COLUMNS:
                df = convert_date_columns(df, DATETIME_COLUMNS[table])

            print(f"Loading {table}: {len(df):,} rows")

            df.to_sql(
                name=table,
                con=connection,
                if_exists="append",
                index=False,
                chunksize=100,
                method="multi"
            )

            print(f"Successfully loaded {table}")


def main():

    engine = get_engine()

    try:
        load_datasets(engine)
        print("\nAll datasets loaded successfully!")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
