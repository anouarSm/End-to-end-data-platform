from pathlib import Path
import pandas as pd

orders = pd.read_csv("data/raw/olist_orders_dataset.csv")
customers = pd.read_csv("data/raw/olist_customers_dataset.csv")
orderItems = pd.read_csv("data/raw/olist_order_items_dataset.csv")
products = pd.read_csv("data/raw/olist_products_dataset.csv")
payments = pd.read_csv("data/raw/olist_order_payments_dataset.csv")

def duplicates(df):
    print("duplicated values : ")
    print(df.duplicated().sum())
    print(df.columns.duplicated().sum())

def missingValues(df):
    countedMissingValues = df.isnull().sum()
    print(f"total missing values is : \n{countedMissingValues}")

def uniqueId(df):
    print(F"is all ids are unique ? {df.iloc[:, 0].is_unique}")


print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~orders~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
duplicates(orders)
missingValues(orders)
uniqueId(orders)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~customers~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
duplicates(customers)
missingValues(customers)
uniqueId(customers)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~orderItems~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
duplicates(orderItems)
missingValues(orderItems)
uniqueId(orderItems)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~products~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
duplicates(products)
missingValues(products)
uniqueId(products)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~payments~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
duplicates(payments)
missingValues(payments)
uniqueId(payments)


