# Adelaide Bunnings Expansion — Analyst Version

Rule-based methodology to identify top expansion candidates for Bunnings Warehouse using SQL analytics and Power BI visualisation.

## Methodology

1. **Cleaned ABS Census data** in Python — merged G01 (population) and G02 (income/age/rent) tables at SA2 level for South Australia
2. **Mapped Bunnings store locations** to SA2 codes using a manual name_mapping dictionary
3. **Built reusable SQL views** in MS SQL Server:
   - `suburbs_clean` — applied a 1.5% spending rate (per ABS HES benchmark) to derive annual addressable spend
   - `ranked` — added PERCENT_RANK percentile features for each demographic dimension
4. **Composite priority score** weighted across:
   - 40% market potential (annual spend)
   - 35% income (household income percentile)
   - 25% population (catchment size)
5. **Visualised findings** in Power BI with KPI cards, scatter plots, and regional analysis

## Top 5 Recommendations

| Rank | Suburb | Annual Spend | Score |
|---|---|---|---|
| 1 | Unley - Parkside | $14.2M | 0.94 |
| 2 | Burnside - Wattle Park | $12.4M | 0.93 |
| 3 | Aldgate - Stirling | $12.1M | 0.91 |
| 4 | Goodwood - Millswood | $12.0M | 0.86 |
| 5 | Mitcham (SA) | $10.9M | 0.85 |

Combined annual addressable market: **~$37M**.

## Files

| File | Purpose |
|---|---|
| `notebooks/01_clean.ipynb` | Python cleaning pipeline (ABS + stores → master CSV) |
| `sql/01_create_views.sql` | Build `suburbs_clean` and `ranked` views in SQL Server |
| `sql/02_analysis_queries.sql` | Exploratory queries (Q1–Q6) |
| `sql/03_final_recommendations.sql` | The Q7 final composite score query |
| `dashboard/dashboard_screenshot.png` | Power BI dashboard preview |
| `data/processed/adelaide_master.csv` | Cleaned Adelaide dataset (105 suburbs × 10 columns) |
| `data/processed/stores.csv` | Bunnings store locations |

## Tools

- **Python**: pandas (data cleaning)
- **MS SQL Server**: views, CTEs, window functions (`PERCENT_RANK`, `NTILE`)
- **Power BI Desktop**: KPI cards, DAX measures, scatter plots
- **ABS Census 2021**: General Community Profile DataPack (SA2 level)

## Reproducing

1. Run `notebooks/01_clean.ipynb` to generate `adelaide_master.csv`
2. In SQL Server Management Studio, run scripts in order: `01_create_views.sql` → `02_analysis_queries.sql` → `03_final_recommendations.sql`
3. Open the Power BI file (or recreate the dashboard from the queries above)

## Key Insight

The rule-based composite score heavily weights income (~50% effective weight when combined with market-potential calculation). This produces recommendations focused on **inner-suburban wealthy postcodes** — Unley, Burnside, Aldgate. The companion data-science version uses logistic regression and produces a completely different top 5, surfacing a strategic tension worth exploring.