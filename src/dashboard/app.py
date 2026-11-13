
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

from sqlalchemy import text

# =====================================================
# IMPORT CONFIGURATION
# =====================================================

SRC_DIR = Path(__file__).resolve().parents[1]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from database.connection import get_engine


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Olist Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Olist E-Commerce Analytics")
st.caption(
    "Business intelligence dashboard | "
    "Olist Brazilian E-Commerce Dataset"
)


# =====================================================
# DATABASE CONNECTION
# =====================================================

@st.cache_resource
def get_db_engine():
    return get_engine()


engine = get_db_engine()


# =====================================================
# DATABASE QUERY FUNCTIONS
# =====================================================

@st.cache_data(ttl=300)
def load_kpis():
    query = text("""
        SELECT *
        FROM kpi_overview;
    """)

    with engine.connect() as connection:
        return pd.read_sql(query, connection)


@st.cache_data(ttl=300)
def load_available_months():
    query = text("""
        SELECT month
        FROM monthly_revenue
        ORDER BY month;
    """)

    with engine.connect() as connection:
        return pd.read_sql(query, connection)["month"].tolist()


@st.cache_data(ttl=300)
def load_monthly_revenue(start_month, end_month):
    query = text("""
        SELECT *
        FROM monthly_revenue
        WHERE month BETWEEN :start_month AND :end_month
        ORDER BY month;
    """)

    with engine.connect() as connection:
        return pd.read_sql(
            query,
            connection,
            params={
                "start_month": start_month,
                "end_month": end_month
            }
        )


@st.cache_data(ttl=300)
def load_category_revenue(start_month, end_month):
    query = text("""
        SELECT
            COALESCE(
                ct.product_category_name_english,
                p.product_category_name,
                'Unknown'
            ) AS category,
            COUNT(*) AS items_sold,
            COUNT(DISTINCT oi.order_id) AS total_orders,
            ROUND(SUM(oi.item_total), 2) AS revenue
        FROM order_items oi
        JOIN orders o
            ON oi.order_id = o.order_id
        JOIN products p
            ON oi.product_id = p.product_id
        LEFT JOIN category_translation ct
            ON p.product_category_name = ct.product_category_name
        WHERE o.order_status = 'delivered'
          AND DATE_TRUNC(
              'month',
              o.order_purchase_timestamp
          )::DATE BETWEEN :start_month AND :end_month
        GROUP BY 1
        ORDER BY revenue DESC;
    """)

    with engine.connect() as connection:
        return pd.read_sql(
            query,
            connection,
            params={
                "start_month": start_month,
                "end_month": end_month
            }
        )


@st.cache_data(ttl=300)
def load_delivery_performance(start_month, end_month):
    query = text("""
        SELECT *
        FROM delivery_performance
        WHERE month BETWEEN :start_month AND :end_month
        ORDER BY month;
    """)

    with engine.connect() as connection:
        return pd.read_sql(
            query,
            connection,
            params={
                "start_month": start_month,
                "end_month": end_month
            }
        )


@st.cache_data(ttl=300)
def load_payment_analysis():
    query = text("""
        SELECT *
        FROM payment_analysis
        ORDER BY total_payment DESC;
    """)

    with engine.connect() as connection:
        return pd.read_sql(query, connection)


# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.title("Dashboard Filters")

try:
    available_months = load_available_months()

    if not available_months:
        st.warning("No monthly revenue data available.")
        st.stop()

    selected_months = st.sidebar.select_slider(
        "Select date range",
        options=available_months,
        value=(
            available_months[0],
            available_months[-1]
        ),
        format_func=lambda month: pd.to_datetime(
            month
        ).strftime("%b %Y")
    )

    start_month, end_month = selected_months

    st.sidebar.caption(
        f"Period: "
        f"{pd.to_datetime(start_month).strftime('%B %Y')} "
        f"— "
        f"{pd.to_datetime(end_month).strftime('%B %Y')}"
    )

except Exception as error:
    st.error(f"Could not load date filters: {error}")
    st.stop()


# =====================================================
# KPI OVERVIEW
# =====================================================

st.header("Business Overview")

try:
    kpis = load_kpis()

    if kpis.empty:
        st.warning("No KPI data available.")
        st.stop()

    metrics = kpis.iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Delivered Orders",
        f"{metrics['total_delivered_orders']:,.0f}"
    )

    col2.metric(
        "Unique Customers",
        f"{metrics['total_unique_customers']:,.0f}"
    )

    col3.metric(
        "Total Revenue",
        f"R$ {metrics['total_revenue']:,.2f}"
    )

    col4.metric(
        "Average Order Value",
        f"R$ {metrics['average_order_value']:,.2f}"
    )

except Exception as error:
    st.error(f"Could not load KPI data: {error}")


st.divider()


# =====================================================
# MONTHLY REVENUE
# =====================================================

st.header("Revenue Analysis")

try:
    monthly_df = load_monthly_revenue(
        start_month,
        end_month
    )

    if not monthly_df.empty:

        fig = px.line(
            monthly_df,
            x="month",
            y="revenue",
            markers=True,
            title="Monthly Revenue Over Time",
            labels={
                "month": "Month",
                "revenue": "Revenue (BRL)"
            }
        )

        fig.update_layout(
            hovermode="x unified",
            yaxis_tickprefix="R$ ",
            xaxis_title=None
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption("Monthly revenue for delivered orders.")

    else:
        st.info("No revenue data for the selected period.")

except Exception as error:
    st.error(f"Could not load monthly revenue: {error}")


st.divider()


# =====================================================
# PRODUCT CATEGORY ANALYSIS
# =====================================================

st.header("Product Category Analysis")

try:
    category_df = load_category_revenue(
        start_month,
        end_month
    )

    if not category_df.empty:

        col1, col2 = st.columns([2, 1])

        with col1:

            top_categories = (
                category_df
                .head(10)
                .sort_values("revenue")
            )

            fig = px.bar(
                top_categories,
                x="revenue",
                y="category",
                orientation="h",
                title="Top 10 Categories by Revenue",
                labels={
                    "revenue": "Revenue (BRL)",
                    "category": "Product Category"
                }
            )

            fig.update_layout(
                xaxis_tickprefix="R$ ",
                yaxis_title=None
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            fig = px.pie(
                category_df.head(10),
                names="category",
                values="revenue",
                title="Revenue Share — Top 10 Categories",
                hole=0.4
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with st.expander("View category data"):
            st.dataframe(
                category_df,
                use_container_width=True,
                hide_index=True
            )

    else:
        st.info("No category data for the selected period.")

except Exception as error:
    st.error(f"Could not load category data: {error}")


st.divider()


# =====================================================
# DELIVERY PERFORMANCE
# =====================================================

st.header("Delivery Performance")

try:
    delivery_df = load_delivery_performance(
        start_month,
        end_month
    )

    if not delivery_df.empty:

        col1, col2 = st.columns(2)

        with col1:

            fig = px.line(
                delivery_df,
                x="month",
                y="avg_delivery_days",
                markers=True,
                title="Average Delivery Time",
                labels={
                    "month": "Month",
                    "avg_delivery_days": "Delivery Time (Days)"
                }
            )

            fig.update_layout(
                yaxis_title="Days",
                xaxis_title=None
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            fig = px.bar(
                delivery_df,
                x="month",
                y="late_delivery_percentage",
                title="Late Delivery Rate",
                labels={
                    "month": "Month",
                    "late_delivery_percentage": "Late Deliveries (%)"
                }
            )

            fig.update_layout(
                yaxis_ticksuffix="%",
                xaxis_title=None
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # Delivery summary
        total_delivered = delivery_df["delivered_orders"].sum()
        total_late = delivery_df["late_orders"].sum()

        overall_late_rate = (
            (total_late / total_delivered) * 100
            if total_delivered > 0
            else 0
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Delivered Orders",
            f"{total_delivered:,.0f}"
        )

        col2.metric(
            "Late Orders",
            f"{total_late:,.0f}"
        )

        col3.metric(
            "Late Delivery Rate",
            f"{overall_late_rate:.2f}%"
        )

        with st.expander("View delivery data"):
            st.dataframe(
                delivery_df,
                use_container_width=True,
                hide_index=True
            )

    else:
        st.info("No delivery data for the selected period.")

except Exception as error:
    st.error(f"Could not load delivery data: {error}")


st.divider()


# =====================================================
# PAYMENT ANALYSIS
# =====================================================

st.header("Payment Analysis")

try:
    payment_df = load_payment_analysis()

    if not payment_df.empty:

        col1, col2 = st.columns(2)

        with col1:

            fig = px.pie(
                payment_df,
                names="payment_type",
                values="total_payment",
                title="Payment Distribution by Method",
                hole=0.4
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            fig = px.bar(
                payment_df,
                x="payment_type",
                y="total_orders",
                title="Orders by Payment Method",
                labels={
                    "payment_type": "Payment Method",
                    "total_orders": "Number of Orders"
                }
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with st.expander("View payment data"):
            st.dataframe(
                payment_df,
                use_container_width=True,
                hide_index=True
            )

    else:
        st.info("No payment data available.")

except Exception as error:
    st.error(f"Could not load payment data: {error}")


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "Olist E-Commerce Analytics Platform | "
    "Built with Python, Pandas, PostgreSQL, "
    "SQLAlchemy, Streamlit and Plotly"
)
