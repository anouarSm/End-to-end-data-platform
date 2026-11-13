import pandas as pd

#--------------------- GENERAL CHECKS ---------------------

def check_duplicates(df,name):
    print(f"{name} - duplicate rows: {df.duplicated().sum()}")
    print(
        f"{name} - duplicate column names : "
        f"{df.columns.duplicated().sum()}"
    )

def check_missing_values(df,name):
    missing = df.isna().sum()
    missing = missing[missing>0]

    print(f"{name} missing values : ")
    if missing.empty :
        print("no value is missing")
    else :
        print(missing)
        print(f"total missing values : {missing.sum()}")

def check_key(df,column,name):
    duplicate_count = df.duplicated(subset = column).sum()
    print(
        f"{name} key is : {column}"
        f"{'unique' if duplicate_count == 0 else f'{duplicated_count} duplicate key rows'}"
    )
#--------------------- RELATIONSHIPS CHECKS ---------------------

def check_relationship(source_df,source_column,target_df,target_column,name):
    matches = source_df[source_column].isin(target_df[target_column])
    missing_count = (~matches).sum()
    print(f"{name}: {missing_count} source rows with no matching ID")

    if missing_count:
        print(source_df.loc[~matches, [source_column]].drop_duplicates())

#--------------------- ORDER DATE CHECKS ---------------------

def check_order_dates(orders):
    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for column in date_columns:
        orders[column] = pd.to_datetime(orders[column], errors = 'coerce')

    print("\nOrder status counts:")
    print(orders["order_status"].value_counts(dropna=False))

    date_rules = [
         ("order_purchase_timestamp", "order_approved_at"),
        ("order_approved_at", "order_delivered_carrier_date"),
        ("order_delivered_carrier_date", "order_delivered_customer_date"),
    ]
    for earlier , later in date_rules:
        valid_dates = orders[earlier].notna() & orders[later].notna()
        invalid = valid_dates & (orders[earlier] > orders[later])
        print(f"{earlier} later than {later} : {invalid.sum()} rows")
        if invalid.any():
            print(orders.loc[invalid, ["order_id",earlier,later]])
    
    valid_delivery_dates = (
        orders["order_delivered_customer_date"].notna()
        &
        orders["order_estimated_delivery_date"].notna()
    )
    late = (
        valid_delivery_dates &
        (orders["order_delivered_customer_date"] > orders["order_estimated_delivery_date"])
    )
    print(f"the number of late delivery orders is: {late.sum()}")
    # Investigate approval/carrier inconsistencies
    bad_approval_carrier = orders.loc[
    orders["order_approved_at"].notna()
    & orders["order_delivered_carrier_date"].notna()
    & (
        orders["order_approved_at"]
        > orders["order_delivered_carrier_date"]
    )].copy()

    print("\nInconsistent records by order status:")
    print(bad_approval_carrier["order_status"].value_counts())

    # Calculate the time difference in hours
    bad_approval_carrier["difference_hours"] = (bad_approval_carrier["order_approved_at"]- bad_approval_carrier["order_delivered_carrier_date"]).dt.total_seconds() / 3600

    print("\nDifference in hours:")
    print(bad_approval_carrier["difference_hours"].describe())

#--------------------- NUMERIC CHECKS ---------------------
def check_nonnegative(df,column,name):
    invalid = df[column].notna() & (df[column]< 0)
    print(f"{name} negative {column} values are : {invalid.sum()}")

    if invalid.any():
        print(df.loc[invalid, [column]])

#--------------------- RUN ALL VALIDATION CHECKS ---------------------    
def run_validations(datasets):
    # General checks
    for name,df in datasets.items():
        check_duplicates(df,name)
        check_missing_values(df,name)

    check_key(datasets["orders"], ["order_id"], "orders")
    check_key(datasets["customers"], ["customer_id"], "customers")
    check_key(datasets["products"], ["product_id"], "products")
    check_key(datasets["orderItems"],["order_id", "order_item_id"],"orderItems",)
    check_key(datasets["payments"],["order_id", "payment_sequential"],"payments",)
    check_key(datasets["sellers"], ["seller_id"], "sellers")
    # Relationships: IDs in the first dataset should exist in the second.
    check_relationship(
        datasets["orders"], "customer_id",
        datasets["customers"], "customer_id",
        "Orders → Customers",
    )
    check_relationship(
        datasets["orderItems"], "order_id",
        datasets["orders"], "order_id",
        "Order items → Orders",
    )
    check_relationship(
        datasets["orderItems"], "product_id",
        datasets["products"], "product_id",
        "Order items → Products",
    )
    check_relationship(
        datasets["orderItems"], "seller_id",
        datasets["sellers"], "seller_id",
        "Order items → Sellers",
    )

    # Order-specific checks
    check_order_dates(datasets["orders"])

    # Numeric checks
    check_nonnegative(datasets["orderItems"], "price", "orderItems")
    check_nonnegative(
        datasets["orderItems"], "freight_value", "orderItems"
    )
    check_nonnegative(datasets["payments"], "payment_value", "payments")






