import pandas as pd

def clean_column_names(df):
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    return df

def clean_sellers(sellers):
    sellers = clean_column_names(sellers)

    return sellers

def convert_date_columns(df,columns):
    df = df.copy()
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors = 'coerce')
    return df

def convert_numeric_columns(df,columns):
    df = df.copy()
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column], errors = 'coerce'
            )
    return df

def clean_orders(orders):
    orders = clean_column_names(orders)
    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    orders = convert_date_columns(orders,date_columns)
    return orders

def clean_customers(customers):
    customers = clean_column_names(customers)
    return customers

def clean_order_items(order_items):
    order_items = clean_column_names(order_items)
    print("Order items columns:", order_items.columns.tolist())
    numeric_columns = [
        "order_item_id",
        "price",
        "freight_value",
    ]
    order_items = convert_numeric_columns(order_items,numeric_columns)
    order_items["order_item_id"] = (
        order_items["order_item_id"].astype("Int64")
    )
    return order_items

def clean_products(products):
    products = clean_column_names(products)

    numeric_columns = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]

    products = convert_numeric_columns(
        products,
        numeric_columns
    )

    return products

def clean_payments(payments):
    payments = clean_column_names(payments)

    numeric_columns = [
        "payment_sequential",
        "payment_installments",
        "payment_value",
    ]

    payments = convert_numeric_columns(
        payments,
        numeric_columns
    )

    payments["payment_sequential"] = (
        payments["payment_sequential"].astype("Int64")
    )

    payments["payment_installments"] = (
        payments["payment_installments"].astype("Int64")
    )

    return payments

def clean_reviews(reviews):
    reviews = clean_column_names(reviews)

    reviews["review_score"] = pd.to_numeric(
        reviews["review_score"],
        errors="coerce"
    ).astype("Int64")

    reviews["review_creation_date"] = pd.to_datetime(
        reviews["review_creation_date"],
        errors="coerce"
    )

    reviews["review_answer_timestamp"] = pd.to_datetime(
        reviews["review_answer_timestamp"],
        errors="coerce"
    )

    return reviews

def clean_geolocation(geolocation):
    geolocation = clean_column_names(geolocation)

    geolocation = convert_numeric_columns(
        geolocation,
        ["geolocation_lat", "geolocation_lng"]
    )

    return geolocation

def clean_category_translation(translation):
    translation = clean_column_names(translation)

    return translation

def clean_all(datasets):
    cleaned = {
        "orders": clean_orders(datasets["orders"]),
        "customers": clean_customers(datasets["customers"]),
        "order_items": clean_order_items(datasets["order_items"]),
        "products": clean_products(datasets["products"]),
        "payments": clean_payments(datasets["payments"]),
        "sellers": clean_sellers(datasets["sellers"]),
        "reviews": clean_reviews(datasets["reviews"]),
        "geolocation": clean_geolocation(datasets["geolocation"]),
        "category_translation": clean_category_translation(
            datasets["category_translation"]
        ),
    }

    return cleaned