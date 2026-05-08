
-- Adelaide Bunnings Expansion — Analyst Version
-- File: 02_analysis_queries.sql
-- Purpose: Exploratory queries (Q1–Q5)


USE adelaide_retail;
GO

-- Q1:  How many suburbs are there, with/without Bunnings?

SELECT 
    COUNT(*)                                                AS total_suburbs,
    SUM(CASE WHEN bunnings_count = 0 THEN 1 ELSE 0 END)     AS suburbs_without_bunnings,
    SUM(CASE WHEN bunnings_count > 0 THEN 1 ELSE 0 END)     AS suburbs_with_bunnings,
    SUM(bunnings_count)                                     AS total_stores
FROM suburbs;
GO


-- Q2: Top 15 wealthiest unserved suburbs by addressable market
SELECT TOP 15
    suburb,
    region,
    weekly_household_income AS weekly_income,
    avg_household_size,
    population,
    annual_spend,
    bunnings_count
FROM suburbs_clean
WHERE bunnings_count = 0
ORDER BY annual_spend DESC;
GO


-- Q3: Profile of suburbs that already have Bunnings
-- (Helps us learn what a "good Bunnings suburb" looks like)


SELECT
    CASE WHEN bunnings_count > 0 THEN 'Has Bunnings' ELSE 'No Bunnings' END AS served,
    COUNT(*)                            AS suburb_count,
    AVG(population)                     AS avg_population,
    AVG(weekly_household_income)        AS avg_income,
    AVG(median_age)                     AS avg_median_age,
    AVG(avg_household_size)             AS avg_hh_size,
    AVG(weekly_rent)                    AS avg_rent
FROM suburbs_clean
GROUP BY CASE WHEN bunnings_count > 0 THEN 'Has Bunnings' ELSE 'No Bunnings' END;
GO
-- Q4: Match unserved suburbs against the "successful Bunnings profile"
-- Uses CROSS JOIN with a CTE to compute % of average for each metric


WITH prof AS (
    SELECT
        AVG(CAST(population AS FLOAT))                  AS avg_pop,
        AVG(CAST(weekly_household_income AS FLOAT))     AS avg_income,
        AVG(CAST(avg_household_size AS FLOAT))          AS avg_hh
    FROM suburbs_clean
    WHERE bunnings_count > 0
)
SELECT TOP 20
    s.suburb,
    s.region,
    s.population,
    s.weekly_household_income,
    s.avg_household_size,
    s.annual_spend,
    CAST(100 * s.population / p.avg_pop AS DECIMAL(5,0))             AS pct_of_avg_population,
    CAST(100 * s.weekly_household_income / p.avg_income AS DECIMAL(5,0)) AS pct_of_avg_income,
    CAST(100 * s.avg_household_size / p.avg_hh AS DECIMAL(5,0))      AS pct_of_avg_hh_size
FROM suburbs_clean s
CROSS JOIN prof p
WHERE s.bunnings_count = 0
  AND s.population >= p.avg_pop * 0.75
  AND s.weekly_household_income >= p.avg_income * 0.85
ORDER BY s.annual_spend DESC;
GO


-- Q5: 4-signal composite priority score

WITH ranked AS (
    SELECT 
        suburb,
        region,
        population,
        weekly_household_income,
        annual_spend,
        PERCENT_RANK() OVER (ORDER BY annual_spend)             AS pr_market,
        PERCENT_RANK() OVER (ORDER BY weekly_household_income)  AS pr_income,
        PERCENT_RANK() OVER (ORDER BY population)               AS pr_population,
        PERCENT_RANK() OVER (ORDER BY avg_household_size)       AS pr_hh_size
    FROM suburbs_clean
    WHERE bunnings_count = 0
)
SELECT TOP 15 
    suburb,
    region,
    population,
    weekly_household_income,
    annual_spend,
    ROUND(
        0.40 * pr_market 
      + 0.30 * pr_income 
      + 0.20 * pr_population
      + 0.10 * pr_hh_size, 
        3
    ) AS priority_score
FROM ranked
ORDER BY priority_score DESC;
GO
-- Q6: Cannibalisation check — are recommendations clustered?
-- (Don't recommend 10 stores all in the same region)


WITH top_stores AS (
    SELECT TOP 10
        suburb,
        region,
        annual_spend
    FROM suburbs_clean
    WHERE bunnings_count = 0
      AND weekly_household_income IS NOT NULL
      AND population >= 8000
    ORDER BY annual_spend DESC
)
SELECT 
    region,
    COUNT(*)                         AS stores_in_region,
    STRING_AGG(suburb, ', ')         AS suburb_names,
    SUM(annual_spend)                AS total_market
FROM top_stores
GROUP BY region
ORDER BY stores_in_region DESC;
GO