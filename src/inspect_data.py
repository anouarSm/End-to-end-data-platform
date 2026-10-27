from pathlib import Path
import pandas as pd


DATA_DIR = Path("./data/raw")
csv_files = list(DATA_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {DATA_DIR}. Please ensure the data directory contains CSV files.")
print(f"Found {len(csv_files)} CSV files in {DATA_DIR}.")

for file in csv_files:
    print("="* 60)
    print(f"FILE : {file.name}")

    df = pd.read_csv(file)
    print(df.head())
    print(f"{df.shape[0]} rows and {df.shape[1]} columns")
    print(f"columns names : {df.columns.tolist()}")
    print("columns types :")
    print(df.dtypes)
    print("missing values :")
    print(df.isnull().sum())
