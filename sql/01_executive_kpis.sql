-- ============================================================
-- Query 1: Executive Business KPIs
-- ============================================================

SELECT
    SUM(revenue) AS total_revenue,

    COUNT(DISTINCT invoice_no) AS total_orders,

    COUNT(DISTINCT customer_id) AS total_customers,

    SUM(quantity) AS total_units_sold,

    ROUND(
        SUM(revenue) / COUNT(DISTINCT invoice_no),
        2
    ) AS average_order_value,

    ROUND(
        SUM(revenue) / COUNT(DISTINCT customer_id),
        2
    ) AS revenue_per_customer

FROM retail_transactions;