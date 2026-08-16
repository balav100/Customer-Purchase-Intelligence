-- ============================================================
-- Query 10: Cohort Retention Analysis
-- ============================================================

WITH customer_first_purchase AS (

    SELECT
        customer_id,

        DATE_TRUNC(
            'month',
            MIN(invoice_date)
        )::DATE AS cohort_month

    FROM retail_transactions

    GROUP BY customer_id
),

customer_activity AS (

    SELECT DISTINCT
        customer_id,

        DATE_TRUNC(
            'month',
            invoice_date
        )::DATE AS activity_month

    FROM retail_transactions
),

cohort_data AS (

    SELECT
        ca.customer_id,
        cfp.cohort_month,
        ca.activity_month,

        (
            (
                EXTRACT(
                    YEAR FROM ca.activity_month
                )
                -
                EXTRACT(
                    YEAR FROM cfp.cohort_month
                )
            ) * 12
            +
            (
                EXTRACT(
                    MONTH FROM ca.activity_month
                )
                -
                EXTRACT(
                    MONTH FROM cfp.cohort_month
                )
            )
        )::INTEGER + 1 AS cohort_index

    FROM customer_activity ca

    JOIN customer_first_purchase cfp
        ON ca.customer_id = cfp.customer_id
),

cohort_counts AS (

    SELECT
        cohort_month,
        cohort_index,
        COUNT(DISTINCT customer_id) AS customers

    FROM cohort_data

    GROUP BY
        cohort_month,
        cohort_index
),

cohort_sizes AS (

    SELECT
        cohort_month,
        customers AS cohort_size

    FROM cohort_counts

    WHERE cohort_index = 1
)

SELECT
    cc.cohort_month,
    cc.cohort_index,
    cc.customers,

    ROUND(
        cc.customers * 100.0 /
        NULLIF(cs.cohort_size, 0),
        2
    ) AS retention_percentage

FROM cohort_counts cc

JOIN cohort_sizes cs
    ON cc.cohort_month = cs.cohort_month

ORDER BY
    cc.cohort_month,
    cc.cohort_index;