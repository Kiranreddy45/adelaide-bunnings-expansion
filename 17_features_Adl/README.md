# Adelaide Bunnings Expansion — Site Selection Model

## Project Overview

A data science portfolio project that predicts optimal locations for new Bunnings Warehouse stores across Adelaide, South Australia. The project uses ABS Census data, competitor analysis, and geospatial features to identify underserved suburbs with high expansion potential.

## Project Phases

### Phase 1 — Baseline (Complete)
- Logistic regression with 6 demographic features on 112 Adelaide SA2s
- AUC: 0.889 (simple train/test split, 3 positives in test — likely optimistic)
- Two versions: analyst-version (SQL + Power BI) and data-science-version (Python + sklearn)

### Phase 0a — Adelaide Feature-Rich (Complete)
- Expanded from 6 to 17 engineered features across 105 Adelaide SA2s
- Compared 3 models (Logistic Regression, Random Forest, XGBoost) × 2 feature sets (17 auto-selected vs 7 domain-curated)
- Best model: Random Forest with 7 domain features, AUC = 0.790 (Leave-One-Out cross-validation)
- 7 non-residential SA2s removed (industrial zones, airports, reservoirs) to eliminate median-imputed fake data

### Phase 0b — National (Planned)
- Expand to ~2,500 SA2s and ~250 Bunnings stores across all 8 states
- Hold Adelaide out as test region
- Validate feature importance at scale where statistics have real power

## Features Engineered (Phase 0a)

### Original Demographics (Phase 1)
- median_age, weekly_personal_income, weekly_household_income
- weekly_rent, avg_household_size, population

### SEIFA Socioeconomic Indices (Phase 0a.1)
- Source: ABS SEIFA 2021, SA2 level
- seifa_irsd_score, seifa_irsad_score, seifa_ier_score, seifa_ieo_score
- Four deciles also extracted but excluded from modelling (redundant with scores)

### Competitor & Distance Features (Phase 0a.2)
- Source: Mitre 10, Total Tools, Home Hardware store locations (24 verified stores)
- Coordinates: Google Places API (exact building-level accuracy)
- dist_nearest_competitor_km: haversine distance to closest hardware competitor
- competitors_within_5km: count of competitor stores within 5km radius
- competitors_within_10km: count within 10km radius
- dist_nearest_bunnings_km: distance to nearest existing Bunnings (excluded from training — data leakage)

### Construction & Employment (Phase 0a.3)
- Source: ABS Census 2021 DataPack, Table G56 (Industry of Employment)
- construction_pct: percentage of employed residents working in construction
- retail_trade_pct: percentage in retail trade

### Growth Signals (Phase 0a.4)
- Source: ABS Census Time Series DataPack Table T01, Census DataPack Table G02
- pop_growth_pct: population change 2016 to 2021
- median_mortgage_monthly: proxy for dwelling values and renovation budgets

## Data Quality Decisions

### Removed SA2s
Seven non-residential SA2s were excluded from analysis: Torrens Island (power station, pop 4), Dry Creek South (industrial, pop 0), Dry Creek North (industrial), Lonsdale (industrial, pop 23), Adelaide Airport (pop 4), Parafield (airport/defence zone), Happy Valley Reservoir. These SA2s had no ABS Census data for SEIFA, employment, or housing, and filling with Adelaide medians introduced fake data that degraded model performance.

Two of these (Adelaide Airport, Parafield) contained Bunnings stores, reducing positive examples from 16 to 14. Despite losing training examples, model performance improved across all three algorithms after removal, confirming that clean data matters more than sample size.

### Competitor Data Verification
Initial competitor dataset from web aggregator sites contained 6 non-existent stores (25% error rate). Verified against official Mitre 10, Total Tools, and Home Hardware store finder websites. Final dataset: 14 Mitre 10, 8 Total Tools, 2 Home Hardware = 24 verified stores.

## Model Comparison

### Evaluation Method
Leave-One-Out cross-validation (105 rounds). Each suburb predicted by a model that never saw it during training. This is the most honest validation method for small datasets — unlike a simple train/test split, every prediction is genuinely out-of-sample.

### Results — All Features (17), Lasso Auto-Selection
| Model | AUC |
|-------|-----|
| Logistic Regression (Lasso) | 0.651 |
| Random Forest | 0.779 |
| XGBoost | 0.728 |

### Results — Domain-Curated Features (7)
| Model | AUC |
|-------|-----|
| Logistic Regression (Lasso) | 0.651 |
| Random Forest | **0.790** |
| XGBoost | 0.775 |

### Domain Feature Selection Rationale
With only 14 positive examples, automated feature selection (Lasso) dropped SEIFA scores, construction employment, mortgage values, and population growth — features with clear business relevance. Domain-curated selection retained 7 features based on retail site selection logic:
1. population — customer volume
2. seifa_ier_score — economic resources and renovation spending power
3. dist_nearest_competitor_km — competitive gaps in the market
4. competitors_within_5km — local competitive density
5. construction_pct — tradie population (Bunnings' core customers)
6. median_mortgage_monthly — dwelling values and renovation budgets
7. pop_growth_pct — growing suburbs need new stores

Domain features outperformed auto-selected features for tree-based models, demonstrating that human expertise adds value when data is limited.

## Feature Importance (Random Forest)

| Feature | Importance |
|---------|-----------|
| pop_growth_pct | 22.4% |
| seifa_ier_score | 21.8% |
| dist_nearest_competitor_km | 18.7% |
| population | 16.0% |
| median_mortgage_monthly | 9.8% |
| construction_pct | 5.8% |
| competitors_within_5km | 5.6% |

## Top 10 Expansion Recommendations

| Rank | Suburb | Score | Population | Dist to Bunnings | Competitors 5km |
|------|--------|-------|-----------|-----------------|----------------|
| 1 | Mitchell Park | 0.684 | 16,516 | 1.9 km | 2 |
| 2 | Northgate - Northfield | 0.629 | 18,188 | 2.1 km | 2 |
| 3 | Plympton | 0.620 | 26,480 | 2.2 km | 2 |
| 4 | Paradise - Newton | 0.614 | 21,601 | 2.9 km | 2 |
| 5 | The Parks | 0.595 | 19,645 | 2.7 km | 1 |
| 6 | Elizabeth East | 0.587 | 14,047 | 9.0 km | 1 |
| 7 | Enfield - Blair Athol | 0.581 | 25,578 | 3.4 km | 2 |
| 8 | Morphettville | 0.570 | 16,531 | 2.1 km | 3 |
| 9 | Hindmarsh - Brompton | 0.552 | 19,076 | 2.8 km | 2 |
| 10 | Brighton (SA) | 0.536 | 15,191 | 1.8 km | 3 |

## Known Limitations

- **Small sample size**: 14 positive examples limit statistical reliability. Feature importance rankings and AUC scores should be interpreted as directional, not definitive.
- **Missing location factors**: The model cannot capture land availability, zoning, road access, lease costs, or traffic patterns. These explain why the model gives low scores to some existing Bunnings locations (e.g., Prospect 0.030, Hope Valley 0.016).
- **Adelaide-only training**: Results reflect Adelaide's specific market structure and cannot generalise to other Australian cities. Phase 0b addresses this.
- **Static snapshot**: All data is from 2021 Census. Market conditions may have changed.

## Technical Setup
- Python 3.11, Anaconda/Jupyter
- Key libraries: pandas, sklearn, xgboost, geopandas, geopy
- Data sources: ABS Census 2021 (General Community Profile, Time Series Profile, SEIFA), ABS ASGS 2021 digital boundaries
- Platform: Windows, MS SQL Server, Power BI Desktop

## Repository Structure
```
adelaide-bunnings-expansion/
├── analyst-version/          # Phase 1 SQL + Power BI version
├── data-science-version/
│   ├── data/
│   │   ├── raw/              # ABS downloads, competitor CSVs, shapefiles
│   │   └── adelaide_master_v5_clean.csv
│   └── notebooks/            # Jupyter notebooks
└── README.md
```

## Next Steps — Phase 0b (National)
1. Pull ABS Census data for all ~2,500 Australian SA2s
2. Compile ~250 Bunnings store locations nationwide
3. Engineer same 17 features at national scale
4. Run feature selection with statistical power (250 positives vs 14)
5. Hold Adelaide out as test region — validate model generalisation
6. Revisit Adelaide with nationally-validated features
