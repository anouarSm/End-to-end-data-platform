import pandas as pd

def translate_product_categories(products,translation):
    products = products.copy()
    translation = translation.copy()

    products = products.merge(
        translation,
        on = "product_category_name",
        how = "left"
    )

    products["product_category_name_english"]=(
        products["product_category_name_english"]
        .fillna(products["product_category_name"])
        .fillna("unknown")
    )
    return products

def transform_orders(orders):
    orders = orders.copy()
    orders["delivery_time_days"] = (
        orders["order_delivered_customer_date"] - 
        orders["order_purchase_timestamp"]
        ).dt.total_seconds() / 86400
    
    orders["delivery_delay_days"] = (
        orders["order_delivered_customer_date"]
        - orders["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400

    orders["purchase_year"] = (
        orders["order_purchase_timestamp"].dt.year
    )

    orders["purchase_month"] = (
        orders["order_purchase_timestamp"].dt.month
    )

    orders["purchase_day"] = (
        orders["order_purchase_timestamp"].dt.day
    )

    orders["purchase_hour"] = (
        orders["order_purchase_timestamp"].dt.hour
    )

    return orders

def transform_order_items(order_items):
    order_items = order_items.copy()
    order_items["item_total"] = (
        order_items["price"] + order_items["freight_value"]
    )

    return order_items

def transform_reviews(reviews):
    reviews = reviews.copy()

    reviews["review_year"] = (
        reviews["review_creation_date"].dt.year
    )

    reviews["review_month"] = (
        reviews["review_creation_date"].dt.month
    )

    return reviews

def transform_all(datasets):
    transformed = datasets.copy()

    transformed["products"] = translate_product_categories(
        transformed["products"],
        transformed["category_translation"]
    )

    transformed["orders"] = transform_orders(
        transformed["orders"]
    )

    transformed["order_items"] = transform_order_items(
        transformed["order_items"]
    )

    transformed["reviews"] = transform_reviews(
        transformed["reviews"]
    )

    return transformed
    