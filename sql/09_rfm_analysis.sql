-- ============================================================
-- Query 9: RFM Customer Analysis
-- Matches Python EDA methodology
-- ============================================================
 WITH reference_date AS
    (SELECT MAX(invoice_date) + INTERVAL '1 day' AS snapshot_date
     FROM retail_transactions),
      rfm AS
    (SELECT customer_id,
            EXTRACT(DAY
                    FROM (
                              (SELECT snapshot_date
                               FROM reference_date) - MAX(invoice_date)))::INTEGER AS recency,
            COUNT(DISTINCT invoice_no) AS frequency,
            ROUND(SUM(revenue), 2) AS monetary
     FROM retail_transactions
     GROUP BY customer_id)
SELECT customer_id,
       recency,
       frequency,
       monetary
FROM rfm
ORDER BY customer_id;