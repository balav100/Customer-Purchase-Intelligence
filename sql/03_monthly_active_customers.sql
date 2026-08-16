-- ============================================================
-- Query 3: Monthly Active Customers & Order Volume
-- ============================================================

SELECT
    DATE_TRUNC('month', invoice_date)::DATE AS month,

    COUNT(DISTINCT customer_id) AS active_customers,

    COUNT(DISTINCT invoice_no) AS orders,

    SUM(quantity) AS units_sold,

    ROUND(
        COUNT(DISTINCT invoice_no)::NUMERIC
        / NULLIF(COUNT(DISTINCT customer_id), 0),
        2
    ) AS orders_per_active_customer

FROM retail_transactions

GROUP BY DATE_TRUNC('month', invoice_date)

ORDER BY month;