import os
from pathlib import Path
from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st

from dotenv import load_dotenv
from psycopg2.extensions import adapt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Customer Purchase Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = PROJECT_ROOT / "sql"


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def get_connection():
    return psycopg2.connect(**DB_CONFIG)


@st.cache_data(ttl=300)
def run_query(query):
    """
    Execute a PostgreSQL query and return a DataFrame.
    """

    conn = None

    try:
        conn = get_connection()

        return pd.read_sql_query(
            query,
            conn
        )

    finally:

        if conn is not None:
            conn.close()


def load_sql(filename):
    """
    Load an SQL file from the project's sql directory.
    """

    sql_path = SQL_DIR / filename

    if not sql_path.exists():

        raise FileNotFoundError(
            f"SQL file not found:\n{sql_path}"
        )

    return sql_path.read_text(
        encoding="utf-8"
    )


@st.cache_data(ttl=300)
def run_sql_file(filename):
    """
    Execute one of the project's SQL files.
    """

    query = load_sql(filename)

    return run_query(query)


# ============================================================
# GLOBAL FILTER DATA
# ============================================================

@st.cache_data(ttl=300)
def get_filter_options():

    date_df = run_query(
        """
        SELECT
            MIN(invoice_date)::DATE AS min_date,
            MAX(invoice_date)::DATE AS max_date
        FROM retail_transactions;
        """
    )

    country_df = run_query(
        """
        SELECT DISTINCT country
        FROM retail_transactions
        WHERE country IS NOT NULL
        ORDER BY country;
        """
    )

    product_df = run_query(
        """
        SELECT DISTINCT stock_code
        FROM retail_transactions
        WHERE stock_code IS NOT NULL
        ORDER BY stock_code;
        """
    )

    customer_df = run_query(
        """
        SELECT DISTINCT customer_id
        FROM retail_transactions
        WHERE customer_id IS NOT NULL
        ORDER BY customer_id;
        """
    )

    min_date = date_df["min_date"].iloc[0]
    max_date = date_df["max_date"].iloc[0]

    countries = (
        country_df["country"]
        .astype(str)
        .tolist()
    )

    products = (
        product_df["stock_code"]
        .astype(str)
        .tolist()
    )

    customers = (
        customer_df["customer_id"]
        .astype(str)
        .tolist()
    )

    return (
        min_date,
        max_date,
        countries,
        products,
        customers,
    )


# ============================================================
# BUILD GLOBAL FILTER
# ============================================================

def build_global_filter():

    (
        min_date,
        max_date,
        countries,
        products,
        customers,
    ) = get_filter_options()

    with st.sidebar:

        st.markdown("### 🔎 Global Filters")

        # ----------------------------------------------------
        # DATE FILTER
        # ----------------------------------------------------

        selected_dates = st.date_input(
            "Date Range",
            value=(
                min_date,
                max_date,
            ),
            min_value=min_date,
            max_value=max_date,
        )

        # ----------------------------------------------------
        # COUNTRY FILTER
        # ----------------------------------------------------

        selected_countries = st.multiselect(
            "Country",
            options=countries,
            default=[],
            placeholder="All countries",
        )

        # ----------------------------------------------------
        # PRODUCT FILTER
        # ----------------------------------------------------

        selected_products = st.multiselect(
            "Product",
            options=products,
            default=[],
            placeholder="All products",
        )

        # ----------------------------------------------------
        # CUSTOMER FILTER
        # ----------------------------------------------------

        selected_customers = st.multiselect(
            "Customer ID",
            options=customers,
            default=[],
            placeholder="All customers",
        )

        st.divider()

        # ----------------------------------------------------
        # RESET FILTERS
        # ----------------------------------------------------

        if st.button(
            "🔄 Reset Filters",
            use_container_width=True,
        ):

            st.session_state.clear()

            st.rerun()

    # ========================================================
    # BUILD FILTER CONDITIONS
    # ========================================================

    conditions = []

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if (
        isinstance(selected_dates, tuple)
        and len(selected_dates) == 2
    ):

        start_date = selected_dates[0]
        end_date = selected_dates[1]

        conditions.append(
            "invoice_date::DATE BETWEEN "
            f"{adapt(str(start_date)).getquoted().decode()} "
            "AND "
            f"{adapt(str(end_date)).getquoted().decode()}"
        )

    # --------------------------------------------------------
    # COUNTRY
    # --------------------------------------------------------

    if selected_countries:

        country_values = ", ".join(
            adapt(country)
            .getquoted()
            .decode()
            for country in selected_countries
        )

        conditions.append(
            f"country IN ({country_values})"
        )

    # --------------------------------------------------------
    # PRODUCT
    # --------------------------------------------------------

    if selected_products:

        product_values = ", ".join(
            adapt(product)
            .getquoted()
            .decode()
            for product in selected_products
        )

        conditions.append(
            f"stock_code::TEXT IN ({product_values})"
        )

    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    if selected_customers:

        customer_values = ", ".join(
            adapt(customer)
            .getquoted()
            .decode()
            for customer in selected_customers
        )

        conditions.append(
            f"customer_id::TEXT IN ({customer_values})"
        )

    # --------------------------------------------------------
    # FINAL WHERE CLAUSE
    # --------------------------------------------------------

    if conditions:

        return (
            " WHERE "
            + " AND ".join(conditions)
        )

    return ""


# ============================================================
# FILTERED QUERY EXECUTION
# ============================================================

@st.cache_data(ttl=300)
def run_filtered_query(
    filename,
    filter_clause,
):
    """
    Executes an SQL file while applying the global
    transaction filters.

    The original SQL files remain unchanged.
    """

    query = load_sql(filename)

    if not filter_clause:

        return run_query(query)

    # --------------------------------------------------------
    # Apply filter to the main transaction table.
    #
    # This works for the analytical SQL files that use
    # retail_transactions as their source.
    # --------------------------------------------------------

    query = query.replace(
        "FROM retail_transactions",
        f"FROM retail_transactions{filter_clause}",
    )

    return run_query(query)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       APPLICATION
    -------------------------------------------------------- */

    .stApp {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }


    /* --------------------------------------------------------
       SIDEBAR
    -------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #263244;
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }


    /* --------------------------------------------------------
       HEADER
    -------------------------------------------------------- */

    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }


    /* --------------------------------------------------------
       KPI CARDS
    -------------------------------------------------------- */

    div[data-testid="stMetric"] {
        background-color: #151b26;
        border: 1px solid #263244;
        border-radius: 12px;
        padding: 18px;

        box-shadow:
            0 4px 15px rgba(0, 0, 0, 0.15);
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc;
        font-weight: 700;
    }


    /* --------------------------------------------------------
       SECTION HEADINGS
    -------------------------------------------------------- */

    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #f8fafc;

        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }


    /* --------------------------------------------------------
       DATABASE STATUS
    -------------------------------------------------------- */

    .status-connected {
        background-color: #123524;
        border: 1px solid #1f6f46;

        color: #86efac;

        padding: 8px 12px;

        border-radius: 8px;

        font-size: 0.85rem;
    }


    /* --------------------------------------------------------
       HEADER
    -------------------------------------------------------- */

    header[data-testid="stHeader"] {
        background-color: transparent;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size:1.35rem;
            font-weight:700;
            color:#f8fafc;
            margin-bottom:0.2rem;
        ">
            📊 CPI Analytics
        </div>

        <div style="
            color:#94a3b8;
            font-size:0.85rem;
            margin-bottom:1.5rem;
        ">
            Customer Purchase Intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "Customer Intelligence",
            "Product Performance",
            "Geographic Analysis",
            "RFM Analysis",
            "Cohort Analysis",
        ],
    )

    st.divider()

    st.caption("DATA SOURCE")

    st.markdown(
        """
        **PostgreSQL**

        `retail_transactions`
        """
    )


# ============================================================
# TEST DATABASE CONNECTION
# ============================================================

try:

    run_query(
        """
        SELECT 1 AS connection_status;
        """
    )

    database_connected = True

except Exception as error:

    database_connected = False
    database_error = error


# ============================================================
# DATABASE ERROR
# ============================================================

if not database_connected:

    st.error(
        "❌ PostgreSQL connection failed."
    )

    st.code(
        str(database_error)
    )

    st.info(
        "Check your .env configuration and "
        "make sure PostgreSQL is running."
    )

    st.stop()


# ============================================================
# BUILD GLOBAL FILTERS
# ============================================================

global_filter = build_global_filter()


# ============================================================
# ACTIVE FILTER INDICATOR
# ============================================================

if global_filter:

    st.info(
        "🔎 Global filters are active. "
        "Dashboard metrics reflect the selected filters."
    )


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    st.markdown(
        '<div class="dashboard-title">'
        'Customer Purchase Intelligence'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Executive sales and customer analytics '
        'powered by PostgreSQL'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="status-connected">'
        '● PostgreSQL Connected'
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # KPI SECTION
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Executive KPIs'
        '</div>',
        unsafe_allow_html=True,
    )

    kpi_df = run_filtered_query(
        "01_executive_kpis.sql",
        global_filter,
    )

    kpi = kpi_df.iloc[0]

    total_revenue = float(
        kpi["total_revenue"]
    )

    total_orders = int(
        kpi["total_orders"]
    )

    total_customers = int(
        kpi["total_customers"]
    )

    total_units = int(
        kpi["total_units_sold"]
    )

    aov = float(
        kpi["average_order_value"]
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Revenue",
        f"£{total_revenue:,.2f}",
    )

    col2.metric(
        "Total Orders",
        f"{total_orders:,}",
    )

    col3.metric(
        "Customers",
        f"{total_customers:,}",
    )

    col4.metric(
        "Units Sold",
        f"{total_units:,}",
    )

    col5.metric(
        "Average Order Value",
        f"£{aov:,.2f}",
    )

    # --------------------------------------------------------
    # MONTHLY REVENUE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Monthly Revenue Performance'
        '</div>',
        unsafe_allow_html=True,
    )

    monthly_df = run_filtered_query(
        "02_monthly_revenue_orders.sql",
        global_filter,
    )

    monthly_df["month"] = pd.to_datetime(
        monthly_df["month"]
    )

    fig_revenue = px.line(
        monthly_df,
        x="month",
        y="monthly_revenue",
        markers=True,
        template="plotly_dark",
    )

    fig_revenue.update_layout(
        height=420,
        xaxis_title=None,
        yaxis_title="Revenue (£)",
        hovermode="x unified",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20,
        ),
    )

    st.plotly_chart(
        fig_revenue,
        use_container_width=True,
    )

    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

    col_left, col_right = st.columns(2)

    with col_left:

        st.markdown(
            '<div class="section-title">'
            'Monthly Orders'
            '</div>',
            unsafe_allow_html=True,
        )

        fig_orders = px.bar(
            monthly_df,
            x="month",
            y="monthly_orders",
            template="plotly_dark",
        )

        fig_orders.update_layout(
            height=350,
            xaxis_title=None,
            yaxis_title="Orders",
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
        )

        st.plotly_chart(
            fig_orders,
            use_container_width=True,
        )

    # --------------------------------------------------------
    # ACTIVE CUSTOMERS
    # --------------------------------------------------------

    with col_right:

        st.markdown(
            '<div class="section-title">'
            'Monthly Active Customers'
            '</div>',
            unsafe_allow_html=True,
        )

        active_df = run_filtered_query(
            "03_monthly_active_customers.sql",
            global_filter,
        )

        active_df["month"] = pd.to_datetime(
            active_df["month"]
        )

        fig_customers = px.line(
            active_df,
            x="month",
            y="active_customers",
            markers=True,
            template="plotly_dark",
        )

        fig_customers.update_layout(
            height=350,
            xaxis_title=None,
            yaxis_title="Active Customers",
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
        )

        st.plotly_chart(
            fig_customers,
            use_container_width=True,
        )


# ============================================================
# CUSTOMER INTELLIGENCE
# ============================================================

elif page == "Customer Intelligence":

    st.markdown(
        '<div class="dashboard-title">'
        'Customer Intelligence'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Customer behavior, loyalty and revenue analysis'
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # REPEAT VS ONE-TIME
    # --------------------------------------------------------

    customer_type_df = run_filtered_query(
        "04_repeat_one_time_customers.sql",
        global_filter,
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            '<div class="section-title">'
            'Repeat vs One-Time Customers'
            '</div>',
            unsafe_allow_html=True,
        )

        fig_customer_type = px.pie(
            customer_type_df,
            names="customer_type",
            values="customer_count",
            hole=0.55,
            template="plotly_dark",
        )

        fig_customer_type.update_layout(
            height=400,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
        )

        st.plotly_chart(
            fig_customer_type,
            use_container_width=True,
        )

    with col2:

        st.markdown(
            '<div class="section-title">'
            'Customer Type Summary'
            '</div>',
            unsafe_allow_html=True,
        )

        st.dataframe(
            customer_type_df,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # TOP CUSTOMERS
    # --------------------------------------------------------

    customer_df = run_filtered_query(
        "05_customer_revenue.sql",
        global_filter,
    )

    st.markdown(
        '<div class="section-title">'
        'Top Customers by Revenue'
        '</div>',
        unsafe_allow_html=True,
    )

    top_customers = (
        customer_df
        .head(10)
        .copy()
    )

    fig_top_customers = px.bar(
        top_customers.sort_values(
            "total_revenue"
        ),
        x="total_revenue",
        y="customer_id",
        orientation="h",
        template="plotly_dark",
    )

    fig_top_customers.update_layout(
        height=450,
        xaxis_title="Revenue (£)",
        yaxis_title="Customer ID",
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
    )

    st.plotly_chart(
        fig_top_customers,
        use_container_width=True,
    )


# ============================================================
# PRODUCT PERFORMANCE
# ============================================================

elif page == "Product Performance":

    st.markdown(
        '<div class="dashboard-title">'
        'Product Performance'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Product sales and revenue performance'
        '</div>',
        unsafe_allow_html=True,
    )

    product_df = run_filtered_query(
        "06_product_performance.sql",
        global_filter,
    )

    top_products = (
        product_df
        .head(10)
        .copy()
    )

    top_products["label"] = (
        top_products["stock_code"]
        .astype(str)
        + " - "
        + top_products["description"]
        .fillna("")
        .str.slice(0, 35)
    )

    fig_products = px.bar(
        top_products.sort_values(
            "total_revenue"
        ),
        x="total_revenue",
        y="label",
        orientation="h",
        template="plotly_dark",
    )

    fig_products.update_layout(
        height=550,
        xaxis_title="Revenue (£)",
        yaxis_title=None,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
    )

    st.plotly_chart(
        fig_products,
        use_container_width=True,
    )

    st.dataframe(
        product_df.head(20),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# GEOGRAPHIC ANALYSIS
# ============================================================

elif page == "Geographic Analysis":

    st.markdown(
        '<div class="dashboard-title">'
        'Geographic Analysis'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Revenue and customer performance by country'
        '</div>',
        unsafe_allow_html=True,
    )

    country_df = run_filtered_query(
        "07_country_performance.sql",
        global_filter,
    )

    top_countries = country_df.head(15)

    fig_country = px.bar(
        top_countries.sort_values(
            "total_revenue"
        ),
        x="total_revenue",
        y="country",
        orientation="h",
        template="plotly_dark",
    )

    fig_country.update_layout(
        height=600,
        xaxis_title="Revenue (£)",
        yaxis_title=None,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
    )

    st.plotly_chart(
        fig_country,
        use_container_width=True,
    )

    st.dataframe(
        country_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# RFM ANALYSIS
# ============================================================

elif page == "RFM Analysis":

    st.markdown(
        '<div class="dashboard-title">'
        'RFM Customer Intelligence'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'RFM-based customer segmentation using K-Means clustering'
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Load RFM data
    # --------------------------------------------------------

    rfm_df = run_filtered_query(
        "09_rfm_analysis.sql",
        global_filter,
    )

    if rfm_df.empty:

        st.warning(
            "No customer data matches the selected filters."
        )

        st.stop()

    rfm_model = rfm_df.copy()

    # --------------------------------------------------------
    # RFM TRANSFORMATION
    # --------------------------------------------------------

    rfm_model["Recency_Log"] = np.log1p(
        rfm_model["recency"]
    )

    rfm_model["Frequency_Log"] = np.log1p(
        rfm_model["frequency"]
    )

    rfm_model["Monetary_Log"] = np.log1p(
        rfm_model["monetary"]
    )

    # --------------------------------------------------------
    # STANDARD SCALING
    # --------------------------------------------------------

    scaler = StandardScaler()

    scaled_data = scaler.fit_transform(
        rfm_model[
            [
                "Recency_Log",
                "Frequency_Log",
                "Monetary_Log",
            ]
        ]
    )

    rfm_scaled = pd.DataFrame(
        scaled_data,
        columns=[
            "Recency_Scaled",
            "Frequency_Scaled",
            "Monetary_Scaled",
        ]
    )

    # --------------------------------------------------------
    # K-MEANS
    # --------------------------------------------------------

    final_kmeans = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=10,
    )

    rfm_model["Cluster"] = (
        final_kmeans
        .fit_predict(rfm_scaled)
    )

    # --------------------------------------------------------
    # PERSONA MAPPING
    # --------------------------------------------------------

    persona_map = {
        0: "Champions (High Value)",
        1: "At Risk / Dormant",
        2: "New / Low-Value",
        3: "Loyal Customers",
    }

    rfm_model["Customer_Segment"] = (
        rfm_model["Cluster"]
        .map(persona_map)
    )

    # --------------------------------------------------------
    # SEGMENT SUMMARY
    # --------------------------------------------------------

    segment_distribution = (
        rfm_model
        .groupby("Customer_Segment")
        .agg(
            Customer_Count=(
                "customer_id",
                "count",
            ),

            Recency_Avg=(
                "recency",
                "mean",
            ),

            Frequency_Avg=(
                "frequency",
                "mean",
            ),

            Monetary_Avg=(
                "monetary",
                "mean",
            ),

            Total_Revenue=(
                "monetary",
                "sum",
            ),
        )
        .reset_index()
    )

    total_segment_revenue = (
        rfm_model["monetary"].sum()
    )

    segment_distribution[
        "Revenue_Share_%"
    ] = (
        segment_distribution[
            "Total_Revenue"
        ]
        / total_segment_revenue
        * 100
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Customer Segmentation Overview'
        '</div>',
        unsafe_allow_html=True,
    )

    segment_lookup = {
        row["Customer_Segment"]: row
        for _, row
        in segment_distribution.iterrows()
    }

    col1, col2, col3, col4 = st.columns(4)

    for col, segment_name in zip(
        [
            col1,
            col2,
            col3,
            col4,
        ],
        [
            "Champions (High Value)",
            "Loyal Customers",
            "At Risk / Dormant",
            "New / Low-Value",
        ],
    ):

        if segment_name in segment_lookup:

            row = segment_lookup[
                segment_name
            ]

            col.metric(
                segment_name,
                f"{int(row['Customer_Count']):,}",
                f"{row['Revenue_Share_%']:.2f}% revenue",
            )

        else:

            col.metric(
                segment_name,
                "0",
            )

    # --------------------------------------------------------
    # CHARTS
    # --------------------------------------------------------

    col_left, col_right = st.columns(2)

    with col_left:

        st.markdown(
            '<div class="section-title">'
            'Customer Segment Distribution'
            '</div>',
            unsafe_allow_html=True,
        )

        fig_segments = px.pie(
            segment_distribution,
            names="Customer_Segment",
            values="Customer_Count",
            hole=0.55,
            template="plotly_dark",
        )

        fig_segments.update_layout(
            height=450,
            margin=dict(
                l=20,
                r=20,
                t=30,
                b=20,
            ),
        )

        st.plotly_chart(
            fig_segments,
            use_container_width=True,
        )

    with col_right:

        st.markdown(
            '<div class="section-title">'
            'Revenue Contribution by Segment'
            '</div>',
            unsafe_allow_html=True,
        )

        revenue_chart = (
            segment_distribution
            .sort_values(
                "Total_Revenue"
            )
        )

        fig_revenue = px.bar(
            revenue_chart,
            x="Total_Revenue",
            y="Customer_Segment",
            orientation="h",
            template="plotly_dark",
        )

        fig_revenue.update_layout(
            height=450,
            xaxis_title="Revenue (£)",
            yaxis_title=None,
            margin=dict(
                l=20,
                r=20,
                t=30,
                b=20,
            ),
        )

        st.plotly_chart(
            fig_revenue,
            use_container_width=True,
        )

    # --------------------------------------------------------
    # CUSTOMER VALUE MAP
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Customer Value Map'
        '</div>',
        unsafe_allow_html=True,
    )

    fig_rfm = px.scatter(
        rfm_model,
        x="frequency",
        y="monetary",
        color="Customer_Segment",
        size="monetary",
        hover_data=[
            "customer_id",
            "recency",
            "frequency",
            "monetary",
        ],
        log_x=True,
        log_y=True,
        template="plotly_dark",
    )

    fig_rfm.update_layout(
        height=600,
        xaxis_title="Purchase Frequency",
        yaxis_title="Customer Revenue (£)",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20,
        ),
    )

    st.plotly_chart(
        fig_rfm,
        use_container_width=True,
    )

    # --------------------------------------------------------
    # SEGMENT PROFILE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Segment Profiles'
        '</div>',
        unsafe_allow_html=True,
    )

    display_segments = (
        segment_distribution.copy()
    )

    display_segments[
        "Recency_Avg"
    ] = display_segments[
        "Recency_Avg"
    ].round(2)

    display_segments[
        "Frequency_Avg"
    ] = display_segments[
        "Frequency_Avg"
    ].round(2)

    display_segments[
        "Monetary_Avg"
    ] = display_segments[
        "Monetary_Avg"
    ].round(2)

    display_segments[
        "Total_Revenue"
    ] = display_segments[
        "Total_Revenue"
    ].round(2)

    display_segments[
        "Revenue_Share_%"
    ] = display_segments[
        "Revenue_Share_%"
    ].round(2)

    st.dataframe(
        display_segments,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # CUSTOMER-LEVEL DATA
    # --------------------------------------------------------

    with st.expander(
        "🔎 Explore Customer-Level RFM Data"
    ):

        customer_view = (
            rfm_model[
                [
                    "customer_id",
                    "recency",
                    "frequency",
                    "monetary",
                    "Cluster",
                    "Customer_Segment",
                ]
            ]
            .sort_values(
                "monetary",
                ascending=False,
            )
        )

        st.dataframe(
            customer_view,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# COHORT ANALYSIS
# ============================================================

elif page == "Cohort Analysis":

    st.markdown(
        '<div class="dashboard-title">'
        'Cohort Retention Analysis'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Customer retention by acquisition cohort'
        '</div>',
        unsafe_allow_html=True,
    )

    cohort_df = run_filtered_query(
        "10_cohort_retention.sql",
        global_filter,
    )

    if cohort_df.empty:

        st.warning(
            "No cohort data matches the selected filters."
        )

        st.stop()

    cohort_pivot = cohort_df.pivot(
        index="cohort_month",
        columns="cohort_index",
        values="retention_percentage",
    )

    cohort_pivot.columns = [
        f"Month {int(column)}"
        for column in cohort_pivot.columns
    ]

    fig_cohort = px.imshow(
        cohort_pivot,
        text_auto=".1f",
        aspect="auto",
        template="plotly_dark",
        labels={
            "x": "Cohort Period",
            "y": "Cohort Month",
            "color": "Retention %",
        },
    )

    fig_cohort.update_layout(
        height=650,
        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20,
        ),
    )

    st.plotly_chart(
        fig_cohort,
        use_container_width=True,
    )

    st.dataframe(
        cohort_df,
        use_container_width=True,
        hide_index=True,
    )