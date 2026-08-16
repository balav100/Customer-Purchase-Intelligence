-- ============================================================
-- Query 7: Country Performance
-- ============================================================

SELECT
    country,

    COUNT(DISTINCT customer_id) AS customers,

    COUNT(DISTINCT invoice_no) AS orders,

    SUM(quantity) AS units_sold,

    ROUND(
        SUM(revenue),
        2
    ) AS total_revenue,

    ROUND(
        SUM(revenue) /
        NULLIF(COUNT(DISTINCT invoice_no), 0),
        2
    ) AS average_order_value

FROM retail_transactions

GROUP BY country

ORDER BY total_revenue DESC;