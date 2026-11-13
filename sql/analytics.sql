
-- ============================================================
-- OLIST E-COMMERCE DATA ANALYTICS
-- Project: End-to-End Data Pipeline and Analytics Platform
-- Database: olist_analytics
--
-- Purpose:
-- Analyze business performance, revenue, customers, products,
-- sellers, payments, logistics, and customer satisfaction.
--
-- Important:
-- Revenue = product price + freight value (item_total).
-- Revenue queries generally include delivered orders only.
-- This is not net profit or accounting revenue.
-- ============================================================


-- ============================================================
-- 1. BUSINESS OVERVIEW AND KPIs
-- ============================================================

-- Query 1: Overall business KPIs
-- Calculate the main business indicators:
-- delivered orders, customers, products, sellers,
-- total item revenue, and average order value.

SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS total_customer_records,
    COUNT(DISTINCT oi.product_id) AS unique_products,
    COUNT(DISTINCT oi.seller_id) AS unique_sellers,
    ROUND(SUM(oi.item_total), 2) AS total_item_revenue,
    ROUND(AVG(order_totals.order_total), 2) AS average_order_value
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN (
    SELECT
        order_id,
        SUM(item_total) AS order_total
    FROM order_items
    GROUP BY order_id
) order_totals
    ON o.order_id = order_totals.order_id
WHERE o.order_status = 'delivered';


-- Query 2: Orders by status
-- Count orders in each status and calculate their percentage
-- of all orders.

SELECT
    order_status,
    COUNT(*) AS total_orders,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM orders
GROUP BY order_status
ORDER BY total_orders DESC;


-- Query 3: Monthly order volume
-- Identify how many orders were placed each month.

SELECT
    DATE_TRUNC('month', order_purchase_timestamp) AS month,
    COUNT(*) AS total_orders
FROM orders
GROUP BY month
ORDER BY month;


-- ============================================================
-- 2. REVENUE ANALYSIS
-- ============================================================

-- Query 4: Monthly revenue
-- Calculate total delivered-order item revenue for each month.

SELECT
    DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
    ROUND(SUM(oi.item_total), 2) AS monthly_revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month;


-- Query 5: Yearly revenue
-- Compare total delivered-order revenue across years.

SELECT
    EXTRACT(YEAR FROM o.order_purchase_timestamp) AS year,
    ROUND(SUM(oi.item_total), 2) AS yearly_revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY year
ORDER BY year;


-- Query 6: Monthly revenue growth
-- Use LAG() to compare each month's revenue with the
-- previous month's revenue.
-- Calculate month-over-month growth as a percentage.

WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
        SUM(oi.item_total) AS revenue
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY month
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(
        LAG(revenue) OVER (ORDER BY month),
        2
    ) AS previous_month_revenue,
    ROUND(
        100.0 * (
            revenue - LAG(revenue) OVER (ORDER BY month)
        ) / NULLIF(LAG(revenue) OVER (ORDER BY month), 0),
        2
    ) AS growth_percentage
FROM monthly_revenue
ORDER BY month;


-- Query 7: Revenue by product category
-- Identify which product categories generate the most revenue.
-- Include the number of orders and items sold per category.

SELECT
    COALESCE(
        p.product_category_name_english,
        'Unknown'
    ) AS category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(*) AS total_items,
    ROUND(SUM(oi.item_total), 2) AS revenue
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
JOIN products p
    ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered'
GROUP BY category
ORDER BY revenue DESC;


-- Query 8: Top 10 products by revenue
-- Find the ten products generating the highest revenue.

SELECT
    oi.product_id,
    COALESCE(
        p.product_category_name_english,
        'Unknown'
    ) AS category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(*) AS items_sold,
    ROUND(SUM(oi.item_total), 2) AS revenue
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
JOIN products p
    ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered'
GROUP BY oi.product_id, category
ORDER BY revenue DESC
LIMIT 10;


-- ============================================================
-- 3. CUSTOMER ANALYSIS
-- ============================================================

-- Query 9: Top 10 customers by spending
-- Identify customers who have spent the most.
-- Use customer_unique_id to identify customers across
-- potentially multiple customer records.

SELECT
    c.customer_unique_id,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.item_total), 2) AS total_spent
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_unique_id
ORDER BY total_spent DESC
LIMIT 10;


-- Query 10: Repeat customer analysis
-- Count one-time customers and repeat customers.
-- A repeat customer is someone with more than one order.

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS total_orders
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
)
SELECT
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (
        WHERE total_orders = 1
    ) AS one_time_customers,
    COUNT(*) FILTER (
        WHERE total_orders > 1
    ) AS repeat_customers,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE total_orders > 1
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS repeat_customer_percentage
FROM customer_orders;


-- Query 11: Revenue by customer state
-- Analyze customer distribution, order volume, and revenue
-- across Brazilian states.

SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
    ROUND(SUM(oi.item_total), 2) AS revenue
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY revenue DESC;


-- ============================================================
-- 4. PRODUCT AND SELLER ANALYSIS
-- ============================================================

-- Query 12: Top 10 sellers by revenue
-- Identify the sellers generating the highest revenue.

SELECT
    s.seller_id,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(*) AS items_sold,
    ROUND(SUM(oi.item_total), 2) AS revenue
FROM sellers s
JOIN order_items oi
    ON s.seller_id = oi.seller_id
JOIN orders o
    ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY s.seller_id, s.seller_state
ORDER BY revenue DESC
LIMIT 10;


-- Query 13: Average product price by category
-- Compare average product prices and freight costs
-- across product categories.

SELECT
    COALESCE(
        p.product_category_name_english,
        'Unknown'
    ) AS category,
    ROUND(AVG(oi.price), 2) AS average_price,
    ROUND(AVG(oi.freight_value), 2) AS average_freight,
    COUNT(*) AS total_items
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
GROUP BY category
ORDER BY average_price DESC;


-- ============================================================
-- 5. PAYMENT ANALYSIS
-- ============================================================

-- Query 14: Payment methods
-- Analyze payment methods by number of payment records,
-- orders, total payment value, and average payment value.

SELECT
    payment_type,
    COUNT(*) AS payment_records,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(payment_value), 2) AS total_payment,
    ROUND(AVG(payment_value), 2) AS average_payment
FROM payments
GROUP BY payment_type
ORDER BY total_payment DESC;


-- Query 15: Payment installment analysis
-- Understand how customers use installment payments.

SELECT
    payment_installments,
    COUNT(*) AS payment_records,
    ROUND(AVG(payment_value), 2) AS average_payment,
    ROUND(SUM(payment_value), 2) AS total_payment
FROM payments
GROUP BY payment_installments
ORDER BY payment_installments;


-- ============================================================
-- 6. DELIVERY AND LOGISTICS ANALYSIS
-- ============================================================

-- Query 16: Average delivery time by month
-- Calculate the average number of days between purchase
-- and customer delivery for delivered orders.

SELECT
    DATE_TRUNC('month', order_purchase_timestamp) AS month,
    ROUND(AVG(delivery_time_days), 2) AS average_delivery_days
FROM orders
WHERE order_status = 'delivered'
  AND delivery_time_days IS NOT NULL
GROUP BY month
ORDER BY month;


-- Query 17: Late delivery analysis
-- Compare late and on-time deliveries.
-- Calculate the percentage of late deliveries.

SELECT
    COUNT(*) AS delivered_orders,
    COUNT(*) FILTER (
        WHERE order_delivered_customer_date >
              order_estimated_delivery_date
    ) AS late_orders,
    COUNT(*) FILTER (
        WHERE order_delivered_customer_date <=
              order_estimated_delivery_date
    ) AS on_time_orders,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE order_delivered_customer_date >
                  order_estimated_delivery_date
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS late_delivery_percentage
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
  AND order_estimated_delivery_date IS NOT NULL;


-- Query 18: Average delivery delay by state
-- Calculate average delivery delay in days for each
-- customer state.
-- Positive values mean deliveries were late.
-- Negative values mean deliveries were early.

SELECT
    c.customer_state,
    COUNT(*) AS delivered_orders,
    ROUND(
        AVG(
            EXTRACT(
                EPOCH FROM (
                    o.order_delivered_customer_date -
                    o.order_estimated_delivery_date
                )
            ) / 86400
        ),
        2
    ) AS average_delay_days
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY average_delay_days DESC;


-- ============================================================
-- 7. CUSTOMER SATISFACTION ANALYSIS
-- ============================================================

-- Query 19: Review score distribution
-- Analyze how customers rate their shopping experience.

SELECT
    review_score,
    COUNT(*) AS total_reviews,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM reviews
WHERE review_score IS NOT NULL
GROUP BY review_score
ORDER BY review_score DESC;


-- Query 20: Average review score by product category
-- Associate order reviews with the categories of products
-- purchased in those orders.
--
-- Note: An order containing multiple categories can cause
-- its review to be associated with multiple categories.
-- This is an order-item-level association.

SELECT
    COALESCE(
        p.product_category_name_english,
        'Unknown'
    ) AS category,
    ROUND(AVG(r.review_score), 2) AS average_review_score,
    COUNT(*) AS review_item_associations
FROM reviews r
JOIN orders o
    ON r.order_id = o.order_id
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
WHERE r.review_score IS NOT NULL
GROUP BY category
ORDER BY average_review_score DESC;


-- Query 21: Delivery status and customer satisfaction
-- Compare average review scores for orders delivered
-- on time and orders delivered late.

SELECT
    CASE
        WHEN o.order_delivered_customer_date >
             o.order_estimated_delivery_date
        THEN 'Late'
        ELSE 'On time'
    END AS delivery_status,
    ROUND(AVG(r.review_score), 2) AS average_review_score,
    COUNT(*) AS total_reviews
FROM reviews r
JOIN orders o
    ON r.order_id = o.order_id
WHERE r.review_score IS NOT NULL
  AND o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL
GROUP BY delivery_status;


-- ============================================================
-- 8. ADVANCED SQL: WINDOW FUNCTIONS AND RANKINGS
-- ============================================================

-- Query 22: Rank product categories by revenue
-- Use RANK() to order categories from highest to lowest
-- revenue.

WITH category_revenue AS (
    SELECT
        p.product_category_name_english AS category,
        SUM(oi.item_total) AS revenue
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.product_category_name_english
)
SELECT
    category,
    ROUND(revenue, 2) AS revenue,
    RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM category_revenue
ORDER BY revenue_rank;


-- Query 23: Top three products in each category
-- Use ROW_NUMBER() with PARTITION BY to rank products
-- separately within each category.

WITH product_revenue AS (
    SELECT
        p.product_category_name_english AS category,
        oi.product_id,
        SUM(oi.item_total) AS revenue
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    WHERE o.order_status = 'delivered'
    GROUP BY category, oi.product_id
),
ranked_products AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY category
            ORDER BY revenue DESC
        ) AS product_rank
    FROM product_revenue
)
SELECT
    category,
    product_id,
    ROUND(revenue, 2) AS revenue,
    product_rank
FROM ranked_products
WHERE product_rank <= 3
ORDER BY category, product_rank;


-- Query 24: Cumulative monthly revenue
-- Use a running SUM() window function to calculate
-- cumulative revenue over time.

WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
        SUM(oi.item_total) AS revenue
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY month
)
SELECT
    month,
    ROUND(revenue, 2) AS monthly_revenue,
    ROUND(
        SUM(revenue) OVER (ORDER BY month),
        2
    ) AS cumulative_revenue
FROM monthly_revenue
ORDER BY month;


-- ============================================================
-- END OF ANALYTICS QUERIES
-- ============================================================
