-- ============================================================
-- Query 4: Repeat vs One-Time Customers
-- ============================================================

WITH customer_orders AS (

    SELECT
        customer_id,
        COUNT(DISTINCT invoice_no) AS order_count

    FROM retail_transactions

    GROUP BY customer_id
),

customer_type AS (

    SELECT
        customer_id,
        order_count,

        CASE
            WHEN order_count = 1 THEN 'One-Time'
            ELSE 'Repeat'
        END AS customer_type

    FROM customer_orders
)

SELECT
    customer_type,

    COUNT(*) AS customer_count,

    ROUND(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (),
        2
    ) AS customer_percentage

FROM customer_type

GROUP BY customer_type

ORDER BY customer_count DESC;