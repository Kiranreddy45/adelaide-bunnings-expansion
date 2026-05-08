USE adelaide_retail;

-- Create a cleaned working view so we stop typing the same filters every query.
-- Senior habit: if you filter the same way 5+ times, make it a view.
CREATE OR ALTER VIEW suburbs_clean AS
SELECT
    SA2_CODE_2021,
    SA2_NAME_2021                                     AS suburb,
    SA3_NAME                                          AS region,
    median_age,
    weekly_personal_income,
    weekly_household_income,
    weekly_rent,
    avg_household_size,
    population,
    bunnings_count,
    -- Derived field: estimated households
    CAST(population / NULLIF(avg_household_size, 0) AS INT) AS households,
    -- Derived field: estimated annual hardware market (1.5% of income)
    CAST(
        (population / NULLIF(avg_household_size, 0))
        * weekly_household_income * 52 * 0.015 
        AS BIGINT
    )                                                 AS annual_spend
FROM suburbs
WHERE weekly_household_income IS NOT NULL
  AND population IS NOT NULL
  AND population >= 8000;    -- exclude industrial/non-residential SA2s

--- we need to eleminate rich suburb with less population 
---lets assume they spend 1.5% of their income annually
--- we need to use bigint when whole numbers bigger than 2billion