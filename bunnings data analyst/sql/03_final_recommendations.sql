-- Adelaide Bunnings Expansion — Analyst Version
-- Purpose: Final top 5 expansion candidates
-- 5 strongest expansion candidates.
-- Refined from 4-signal Q5 to 3-signal version — sensitivity analysis
-- showed the top 3 candidates were stable across both weightings.

USE adelaide_retail;
GO

WITH ranked AS (
    -- Step A: Score every unserved suburb on 3 normalised signals
    SELECT
        suburb,
        region,
        population,
        weekly_household_income,
        annual_spend,
        PERCENT_RANK() OVER (ORDER BY annual_spend)             AS pr_market,
        PERCENT_RANK() OVER (ORDER BY weekly_household_income)  AS pr_income,
        PERCENT_RANK() OVER (ORDER BY population)               AS pr_population
    FROM suburbs_clean
    WHERE bunnings_count = 0
      AND weekly_household_income IS NOT NULL
      AND population >= 8000
),
scored AS (
    -- Step B: Blend signals into weighted priority score
    -- Weights: 40% market, 35% income, 25% population
    SELECT
        *,
        ROUND(
            0.40 * pr_market
          + 0.35 * pr_income
          + 0.25 * pr_population,
            3
        ) AS priority_score
    FROM ranked
),
regional_context AS (
    -- Step C: Region-level reality check
    -- (How big is the unserved population in each region?)
    SELECT
        region,
        SUM(CASE WHEN bunnings_count = 0 THEN population ELSE 0 END) AS unserved_pop_in_region,
        SUM(bunnings_count) AS existing_stores_in_region
    FROM suburbs_clean
    GROUP BY region
)
SELECT TOP 5
    s.suburb,
    s.region,
    s.population,
    s.weekly_household_income      AS weekly_income,
    s.annual_spend                 AS est_annual_market_aud,
    s.priority_score,
    rc.unserved_pop_in_region,
    rc.existing_stores_in_region   AS stores_existing_in_region
FROM scored s
JOIN regional_context rc ON s.region = rc.region
ORDER BY s.priority_score DESC;
GO