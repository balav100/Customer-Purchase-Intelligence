-- ============================================================
-- Query 8: Price-Tier Performance
-- ============================================================

WITH price_tiers AS (

    SELECT
        *,
        CASE
            WHEN unit_price < 1 THEN 'Low'
            WHEN unit_price < 5 THEN 'Medium'
            WHEN unit_price < 10 THEN 'High'
            ELSE 'Premium'
        END AS price_tier

    FROM retail_transactions
)

SELECT
    price_tier,

    COUNT(*) AS transaction_lines,

    SUM(quantity) AS units_sold,

    ROUND(
        SUM(revenue),
        2
    ) AS total_revenue,

    ROUND(
        SUM(revenue) * 100.0 /
        SUM(SUM(revenue)) OVER (),
        2
    ) AS revenue_share_percentage

FROM price_tiers

GROUP BY price_tier

ORDER BY
    CASE price_tier
        WHEN 'Low' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'High' THEN 3
        WHEN 'Premium' THEN 4
    END;