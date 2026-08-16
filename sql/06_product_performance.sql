-- ============================================================
-- Query 6: Product Performance
-- ============================================================

SELECT
    stock_code,

    MAX(description) AS description,

    SUM(quantity) AS units_sold,

    COUNT(DISTINCT invoice_no) AS order_count,

    ROUND(
        SUM(revenue),
        2
    ) AS total_revenue,

    ROUND(
        SUM(revenue) /
        NULLIF(SUM(quantity), 0),
        2
    ) AS average_revenue_per_unit

FROM retail_transactions

GROUP BY stock_code

ORDER BY total_revenue DESC;