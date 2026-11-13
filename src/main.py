from pathlib import Path
import pandas as pd

#from validation.checks import run_validations
from transformations.cleaning import clean_all
from transformations.transform import transform_all

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

"""datasets = {
    "orders": pd.read_csv("../data/raw/olist_orders_dataset.csv"),
    "customers": pd.read_csv("../data/raw/olist_customers_dataset.csv"),
    "orderItems": pd.read_csv("../data/raw/olist_order_items_dataset.csv"),
    "products": pd.read_csv("../data/raw/olist_products_dataset.csv"),
    "payments": pd.read_csv("../data/raw/olist_order_payments_dataset.csv"),
    "sellers": pd.read_csv("../data/raw/olist_sellers_dataset.csv"),
}"""

def load_raw_data():
    """
    Load all original CSV files into DataFrames.
    """

    datasets = {
        "orders": pd.read_csv(
            RAW_DIR / "olist_orders_dataset.csv"
        ),

        "customers": pd.read_csv(
            RAW_DIR / "olist_customers_dataset.csv"
        ),

        "order_items": pd.read_csv(
            RAW_DIR / "olist_order_items_dataset.csv"
        ),

        "products": pd.read_csv(
            RAW_DIR / "olist_products_dataset.csv"
        ),

        "payments": pd.read_csv(
            RAW_DIR / "olist_order_payments_dataset.csv"
        ),

        "sellers": pd.read_csv(
            RAW_DIR / "olist_sellers_dataset.csv"
        ),

        "reviews": pd.read_csv(
            RAW_DIR / "olist_order_reviews_dataset.csv"
        ),

        "geolocation": pd.read_csv(
            RAW_DIR / "olist_geolocation_dataset.csv"
        ),

        "category_translation": pd.read_csv(
            RAW_DIR / "product_category_name_translation.csv"
        ),
    }

    return datasets

#run_validations(datasets)
def save_processed_data(datasets):
    """
    Save cleaned and transformed DataFrames as CSV files.
    """

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for name, df in datasets.items():

        output_path = PROCESSED_DIR / f"{name}.csv"

        df.to_csv(output_path, index=False)

        print(f"Saved: {output_path.name}")


def main():

    print("Loading raw data...")
    raw_datasets = load_raw_data()

    print("\nCleaning data...")
    cleaned_datasets = clean_all(raw_datasets)

    print("\nTransforming data...")
    transformed_datasets = transform_all(cleaned_datasets)

    print("\nSaving processed data...")
    save_processed_data(transformed_datasets)

    print("\nPipeline completed successfully!")


if __name__ == "__main__":
    main()