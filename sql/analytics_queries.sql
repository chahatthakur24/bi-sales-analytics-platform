-- =============================================================================
-- BUSINESS INTELLIGENCE & SALES ANALYTICS PLATFORM
-- PostgreSQL Analytical Queries (20 queries)
-- Author: Chahat Thakur
-- =============================================================================


-- =============================================================================
-- SECTION 1: REVENUE & PROFIT ANALYSIS
-- =============================================================================

-- Query 1: Annual Revenue, Profit & YoY Growth
WITH yearly AS (
    SELECT
        EXTRACT(YEAR FROM order_date) AS year,
        SUM(sales)  AS revenue,
        SUM(profit) AS profit
    FROM orders
    GROUP BY 1
)
SELECT
    year,
    ROUND(revenue::NUMERIC, 0)  AS revenue,
    ROUND(profit::NUMERIC, 0)   AS profit,
    ROUND((profit/revenue*100)::NUMERIC, 1) AS margin_pct,
    ROUND(((revenue - LAG(revenue) OVER (ORDER BY year))
           / LAG(revenue) OVER (ORDER BY year) * 100)::NUMERIC, 1) AS yoy_growth_pct
FROM yearly
ORDER BY year;


-- Query 2: Monthly Revenue with Rolling 3-Month Average
SELECT
    DATE_TRUNC('month', order_date)::DATE AS month,
    ROUND(SUM(sales)::NUMERIC, 0)         AS monthly_revenue,
    ROUND(AVG(SUM(sales)) OVER (
        ORDER BY DATE_TRUNC('month', order_date)
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    )::NUMERIC, 0)                         AS rolling_3m_avg,
    ROUND(SUM(profit)::NUMERIC, 0)         AS monthly_profit
FROM orders
GROUP BY 1
ORDER BY 1;


-- Query 3: Revenue by Quarter with Cumulative Total
SELECT
    EXTRACT(YEAR FROM order_date)    AS year,
    EXTRACT(QUARTER FROM order_date) AS quarter,
    ROUND(SUM(sales)::NUMERIC, 0)    AS quarterly_revenue,
    ROUND(SUM(profit)::NUMERIC, 0)   AS quarterly_profit,
    ROUND(SUM(SUM(sales)) OVER (
        PARTITION BY EXTRACT(YEAR FROM order_date)
        ORDER BY EXTRACT(QUARTER FROM order_date)
    )::NUMERIC, 0)                    AS cumulative_ytd
FROM orders
GROUP BY 1, 2
ORDER BY 1, 2;


-- Query 4: Revenue by Region — Ranked
SELECT
    region,
    ROUND(SUM(sales)::NUMERIC, 0)  AS revenue,
    ROUND(SUM(profit)::NUMERIC, 0) AS profit,
    ROUND((SUM(profit)/SUM(sales)*100)::NUMERIC, 1) AS margin_pct,
    COUNT(DISTINCT order_id)        AS orders,
    RANK() OVER (ORDER BY SUM(sales) DESC) AS revenue_rank
FROM orders
GROUP BY region
ORDER BY revenue_rank;


-- Query 5: Category & Sub-Category Performance
SELECT
    category,
    sub_category,
    ROUND(SUM(sales)::NUMERIC, 0)  AS revenue,
    ROUND(SUM(profit)::NUMERIC, 0) AS profit,
    ROUND((SUM(profit)/SUM(sales)*100)::NUMERIC, 1) AS margin_pct,
    COUNT(DISTINCT order_id)        AS orders,
    ROUND(AVG(discount)*100::NUMERIC, 1) AS avg_discount_pct
FROM orders
GROUP BY category, sub_category
ORDER BY revenue DESC;


-- =============================================================================
-- SECTION 2: CUSTOMER ANALYTICS
-- =============================================================================

-- Query 6: RFM Scoring
WITH snapshot AS (SELECT MAX(order_date) + INTERVAL '1 day' AS snap FROM orders),
rfm_raw AS (
    SELECT
        customer_id,
        customer_name,
        segment,
        (SELECT snap FROM snapshot) - MAX(order_date) AS recency_days,
        COUNT(DISTINCT order_id) AS frequency,
        ROUND(SUM(sales)::NUMERIC, 0) AS monetary
    FROM orders
    GROUP BY customer_id, customer_name, segment
),
rfm_scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency)          AS f_score,
        NTILE(5) OVER (ORDER BY monetary)            AS m_score
    FROM rfm_raw
)
SELECT
    customer_id, customer_name, segment,
    EXTRACT(DAY FROM recency_days)::INT AS recency_days,
    frequency, monetary,
    r_score, f_score, m_score,
    r_score + f_score + m_score AS rfm_total,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3                  THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2                  THEN 'New Customers'
        WHEN r_score >= 3 AND m_score >= 3                  THEN 'Potential Loyalists'
        WHEN r_score = 2  AND f_score >= 3                  THEN 'At Risk'
        WHEN r_score <= 2 AND f_score >= 3                  THEN 'Cant Lose Them'
        WHEN r_score <= 2 AND f_score <= 2                  THEN 'Lost'
        ELSE 'Hibernating'
    END AS segment_label
FROM rfm_scored
ORDER BY rfm_total DESC;


-- Query 7: Customer Lifetime Value (CLV)
SELECT
    customer_id,
    customer_name,
    segment,
    COUNT(DISTINCT order_id)       AS total_orders,
    ROUND(SUM(sales)::NUMERIC, 0)  AS total_revenue,
    ROUND(AVG(sales)::NUMERIC, 0)  AS avg_order_value,
    MIN(order_date)                AS first_order,
    MAX(order_date)                AS last_order,
    MAX(order_date) - MIN(order_date) AS tenure_days,
    ROUND((SUM(sales) / NULLIF(
        EXTRACT(DAY FROM MAX(order_date) - MIN(order_date)), 0
    ) * 365)::NUMERIC, 0)          AS annualized_clv
FROM orders
GROUP BY customer_id, customer_name, segment
ORDER BY annualized_clv DESC NULLS LAST;


-- Query 8: Cohort Retention Analysis
WITH first_purchase AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM orders
    GROUP BY customer_id
),
monthly_activity AS (
    SELECT
        o.customer_id,
        DATE_TRUNC('month', o.order_date) AS order_month,
        fp.cohort_month,
        EXTRACT(MONTH FROM AGE(
            DATE_TRUNC('month', o.order_date), fp.cohort_month
        ))::INT AS months_since_first
    FROM orders o
    JOIN first_purchase fp ON o.customer_id = fp.customer_id
)
SELECT
    cohort_month::DATE,
    months_since_first,
    COUNT(DISTINCT customer_id) AS customers,
    ROUND(
        COUNT(DISTINCT customer_id) * 100.0 /
        FIRST_VALUE(COUNT(DISTINCT customer_id)) OVER (
            PARTITION BY cohort_month ORDER BY months_since_first
        ), 1
    ) AS retention_pct
FROM monthly_activity
GROUP BY cohort_month, months_since_first
ORDER BY cohort_month, months_since_first;


-- Query 9: Top 10 Customers by Revenue
SELECT
    customer_id,
    customer_name,
    segment,
    region,
    COUNT(DISTINCT order_id)        AS orders,
    ROUND(SUM(sales)::NUMERIC, 0)   AS total_revenue,
    ROUND(SUM(profit)::NUMERIC, 0)  AS total_profit,
    ROUND(AVG(sales)::NUMERIC, 0)   AS avg_order_value,
    ROUND((SUM(sales) / SUM(SUM(sales)) OVER () * 100)::NUMERIC, 2) AS revenue_share_pct
FROM orders
GROUP BY customer_id, customer_name, segment, region
ORDER BY total_revenue DESC
LIMIT 10;


-- Query 10: Customer Purchase Frequency Distribution
SELECT
    order_count AS purchases,
    COUNT(customer_id) AS customers,
    ROUND(COUNT(customer_id) * 100.0 / SUM(COUNT(customer_id)) OVER (), 1) AS pct_of_customers
FROM (
    SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
    FROM orders GROUP BY customer_id
) t
GROUP BY order_count
ORDER BY order_count;


-- =============================================================================
-- SECTION 3: PRODUCT & DISCOUNT ANALYTICS
-- =============================================================================

-- Query 11: Discount Impact on Profit Margin
SELECT
    CASE
        WHEN discount = 0              THEN '0 - No Discount'
        WHEN discount BETWEEN 0.01 AND 0.10 THEN '1 - 1 to 10%'
        WHEN discount BETWEEN 0.11 AND 0.20 THEN '2 - 11 to 20%'
        WHEN discount BETWEEN 0.21 AND 0.30 THEN '3 - 21 to 30%'
        ELSE                                    '4 - Over 30%'
    END AS discount_tier,
    COUNT(*)                               AS orders,
    ROUND(SUM(sales)::NUMERIC, 0)          AS total_revenue,
    ROUND(SUM(profit)::NUMERIC, 0)         AS total_profit,
    ROUND((SUM(profit)/SUM(sales)*100)::NUMERIC, 1) AS margin_pct,
    ROUND(AVG(discount)*100::NUMERIC, 1)   AS avg_discount_pct
FROM orders
GROUP BY 1
ORDER BY 1;


-- Query 12: Products with Negative Profit Margins
SELECT
    sub_category,
    category,
    COUNT(*) AS orders,
    ROUND(SUM(sales)::NUMERIC, 0)   AS revenue,
    ROUND(SUM(profit)::NUMERIC, 0)  AS profit,
    ROUND((SUM(profit)/SUM(sales)*100)::NUMERIC, 1) AS margin_pct,
    ROUND(AVG(discount)*100::NUMERIC, 1) AS avg_discount_pct
FROM orders
GROUP BY sub_category, category
HAVING SUM(profit)/SUM(sales) < 0
ORDER BY margin_pct;


-- Query 13: Return Rate Analysis
SELECT
    category,
    sub_category,
    COUNT(*)                                             AS total_orders,
    SUM(CASE WHEN returned = 'Yes' THEN 1 ELSE 0 END)  AS returns,
    ROUND(SUM(CASE WHEN returned='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) AS return_rate_pct,
    ROUND(SUM(CASE WHEN returned='Yes' THEN sales ELSE 0 END)::NUMERIC, 0)   AS returned_revenue
FROM orders
GROUP BY category, sub_category
ORDER BY return_rate_pct DESC;


-- =============================================================================
-- SECTION 4: OPERATIONS & SHIPPING
-- =============================================================================

-- Query 14: Shipping Performance by Mode
SELECT
    ship_mode,
    COUNT(*)  AS orders,
    ROUND(AVG(ship_date - order_date), 1) AS avg_ship_days,
    MIN(ship_date - order_date) AS min_days,
    MAX(ship_date - order_date) AS max_days,
    ROUND(SUM(sales)::NUMERIC, 0)  AS revenue,
    ROUND((COUNT(*)*100.0 / SUM(COUNT(*)) OVER ())::NUMERIC, 1) AS pct_of_orders
FROM orders
GROUP BY ship_mode
ORDER BY avg_ship_days;


-- Query 15: Late Shipments by Region
SELECT
    region,
    ship_mode,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN (ship_date - order_date) >
        CASE ship_mode
            WHEN 'Standard Class' THEN 7
            WHEN 'Second Class'   THEN 4
            WHEN 'First Class'    THEN 3
            WHEN 'Same Day'       THEN 1
        END
        THEN 1 ELSE 0 END) AS late_shipments,
    ROUND(SUM(CASE WHEN (ship_date - order_date) >
        CASE ship_mode
            WHEN 'Standard Class' THEN 7
            WHEN 'Second Class'   THEN 4
            WHEN 'First Class'    THEN 3
            WHEN 'Same Day'       THEN 1
        END
        THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) AS late_pct
FROM orders
GROUP BY region, ship_mode
ORDER BY late_pct DESC;


-- =============================================================================
-- SECTION 5: ADVANCED ANALYTICS
-- =============================================================================

-- Query 16: Revenue Decile Analysis (Pareto)
WITH customer_rev AS (
    SELECT
        customer_id,
        SUM(sales) AS total_revenue
    FROM orders GROUP BY customer_id
),
deciles AS (
    SELECT *,
        NTILE(10) OVER (ORDER BY total_revenue DESC) AS decile
    FROM customer_rev
)
SELECT
    decile,
    COUNT(*)                                    AS customers,
    ROUND(SUM(total_revenue)::NUMERIC, 0)       AS revenue,
    ROUND(SUM(total_revenue)*100.0/SUM(SUM(total_revenue)) OVER (), 1) AS revenue_pct,
    ROUND(SUM(SUM(total_revenue)) OVER (ORDER BY decile)
          *100.0/SUM(SUM(total_revenue)) OVER (), 1) AS cumulative_pct
FROM deciles
GROUP BY decile
ORDER BY decile;


-- Query 17: Month-over-Month Revenue Change
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(sales) AS revenue
    FROM orders GROUP BY 1
)
SELECT
    month::DATE,
    ROUND(revenue::NUMERIC, 0) AS revenue,
    ROUND(LAG(revenue) OVER (ORDER BY month)::NUMERIC, 0) AS prev_month,
    ROUND((revenue - LAG(revenue) OVER (ORDER BY month))::NUMERIC, 0) AS mom_change,
    ROUND(((revenue - LAG(revenue) OVER (ORDER BY month))
           / LAG(revenue) OVER (ORDER BY month) * 100)::NUMERIC, 1) AS mom_growth_pct
FROM monthly ORDER BY month;


-- Query 18: Segment Revenue Contribution Over Time
SELECT
    EXTRACT(YEAR FROM order_date) AS year,
    segment,
    ROUND(SUM(sales)::NUMERIC, 0) AS revenue,
    ROUND(SUM(sales)*100.0 / SUM(SUM(sales)) OVER (
        PARTITION BY EXTRACT(YEAR FROM order_date)
    ), 1) AS pct_of_annual_revenue
FROM orders
GROUP BY 1, 2
ORDER BY 1, revenue DESC;


-- Query 19: Running Total Revenue by Category
SELECT
    DATE_TRUNC('month', order_date)::DATE AS month,
    category,
    ROUND(SUM(sales)::NUMERIC, 0) AS monthly_revenue,
    ROUND(SUM(SUM(sales)) OVER (
        PARTITION BY category
        ORDER BY DATE_TRUNC('month', order_date)
    )::NUMERIC, 0) AS running_total
FROM orders
GROUP BY 1, 2
ORDER BY 2, 1;


-- Query 20: Executive KPI Summary
SELECT
    COUNT(DISTINCT order_id)               AS total_orders,
    COUNT(DISTINCT customer_id)            AS total_customers,
    ROUND(SUM(sales)::NUMERIC, 0)          AS total_revenue,
    ROUND(SUM(profit)::NUMERIC, 0)         AS total_profit,
    ROUND((SUM(profit)/SUM(sales)*100)::NUMERIC, 1) AS overall_margin_pct,
    ROUND(AVG(sales)::NUMERIC, 0)          AS avg_order_value,
    ROUND(SUM(sales)/COUNT(DISTINCT customer_id)::NUMERIC, 0) AS revenue_per_customer,
    SUM(CASE WHEN returned='Yes' THEN 1 ELSE 0 END) AS total_returns,
    ROUND(SUM(CASE WHEN returned='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) AS return_rate_pct,
    COUNT(DISTINCT product_id)             AS unique_products
FROM orders;
