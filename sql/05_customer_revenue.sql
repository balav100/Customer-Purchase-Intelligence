-- ============================================================
-- Query 5: Customer Revenue Analysis
-- ============================================================

SELECT
    customer_id,

    COUNT(DISTINCT invoice_no) AS order_count,

    SUM(quantity) AS total_units,

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

GROUP BY customer_id

ORDER BY total_revenue DESC;