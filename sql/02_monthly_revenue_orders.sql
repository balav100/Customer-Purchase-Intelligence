-- ============================================================
-- Query 2: Monthly Revenue & Order Trends
-- ============================================================

SELECT
    DATE_TRUNC('month', invoice_date)::DATE AS month,

    SUM(revenue) AS monthly_revenue,

    COUNT(DISTINCT invoice_no) AS monthly_orders,

    SUM(quantity) AS monthly_units_sold,

    ROUND(
        SUM(revenue) / COUNT(DISTINCT invoice_no),
        2
    ) AS average_order_value

FROM retail_transactions

GROUP BY DATE_TRUNC('month', invoice_date)

ORDER BY month;