# Bunnings National Expansion Model phase-0b

Predicting suitable locations for new Bunnings Warehouse stores across Australia using public ABS Census demographics and competitor geography, with a held-out validation on Adelaide.

> **What this is:** a skills-demonstration data science project, not a production site-selection tool. It shows end-to-end work — data sourcing, cleaning, feature engineering, model selection, validation, and honest interpretation — on a real business problem. It is *not* something Bunnings would deploy, because it lacks the data that actually drives site decisions (land availability, zoning, lease economics, foot traffic, transaction data).

## The question

Phase 0a modelled Bunnings locations in **Adelaide only**: 105 SA2s with just **14 stores**. With so few positives, feature-importance estimates were statistically fragile and model comparison was meaningless (cross-validation folds held ~3 positives each).

phase-0b** learn the drivers of Bunnings location *nationally*, where ~292 positives give the statistics real power, then validate that the learned relationships transfer back to Adelaide — a city the model never trains on.

If a model trained on the rest of Australia can correctly identify Adelaide's actual Bunnings locations, the feature relationships are genuinely transferable, which is the entire commercial value of a location model.

## Data

**Geographic unit:** ABS Statistical Area Level 2 (SA2), 2021 boundaries. 2,472 SA2s nationally; 2,231 after filtering to population ≥ 3,000 (excludes airports, industrial estates, and other non-residential areas where store demographics don't reflect a customer base).

**Target:** 312 Bunnings stores geocoded to SA2s → 304 unique positive SA2s → **292** after the population filter.

**Features (16), from 6 sources:**

| Source | Features |
| ABS Census G01 | population |
| ABS Census G02 | median monthly mortgage |
| ABS Census G56 | construction %, retail % of workforce |
| ABS Time Series T01 | population growth 2016→2021 |
| ABS SEIFA 2021 | IRSD, IRSAD, IER, IEO — score + decile (8 features) |
| Competitor geography | nearest-competitor distance, competitors within 5km, within 10km |

**Competitor pool:** 663 stores after deduplication — Mitre 10 / IHG (366), Home Hardware (167), Total Tools (130).

## Method

1. **Hold out Adelaide entirely.** All model selection, tuning, and feature-importance work done on rest-of-Australia (279 positives). Adelaide (102 SA2s, 13 positives) never seen during training.
2. **Model selection — 8 models compared** by 5-fold cross-validated ROC-AUC and PR-AUC.
3. **Metric choice.** Site selection is a ranking task — PR-AUC is the primary metric because it measures whether real sites concentrate at the top of the list (where the property team looks). ROC-AUC reported as supporting context. Accuracy disqualified — the 87% negative class makes it a vanity metric.
4. **Winner: XGBoost** — best PR-AUC and lowest variance. Hyperparameter tuning (GridSearchCV, 81 combinations) moved PR-AUC only 0.361 → 0.367, confirming performance is bounded by feature signal, not configuration.
5. **Validate on Adelaide** — train on rest-of-Australia, predict on the held-out Adelaide SA2s.

## Results

### The national model beat the local model — blind

| Model | Trained on | Adelaide ROC-AUC |
| Phase 0a Random Forest | Adelaide only (14 positives) | 0.790 |
| **Phase 0b XGBoost** | **Rest of Australia (never saw Adelaide)** | **0.805** |

A model that never saw a single Adelaide data point scored higher on Adelaide than the model trained specifically on it. PR-AUC was 0.430 against a 0.13 random baseline — 3.3× better than chance.

### It found Adelaide's real stores

- **8 of 13** real Adelaide Bunnings ranked in the top quartile (random ≈ 3 of 13)
- Six real Bunnings appeared in the top 13 SA2s of 102
- **Precision at top-K:** top-10 = 50%, top-15 = 40%, top-20 = 35%, top-25 = 32% — versus a 13% base rate, roughly a 4× lift at the top of the list

### What drives Bunnings location

| Feature | Importance |
| population | 22.4% |
| retail % | 10.6% |
| median mortgage | 9.9% |
| SEIFA IRSAD score | 9.0% |
| nearest competitor distance | 8.2% |
| SEIFA IER score | 7.7% |

Population dominates — Bunnings is a big-box format that needs a large catchment. The supporting features describe the textbook big-box catchment profile: established retail activity, mortgage-paying homeowners, broad socio-economic advantage, and competitor spacing. The model derived this from data, unprompted.

The four SEIFA *decile* features registered ~0% importance — XGBoost correctly identified them as redundant given the continuous *score* versions. The model performed its own feature selection.

### Adelaide expansion candidates (demographic suitability only)

Highest-scoring SA2s without a current Bunnings, in the same northern growth corridor where Bunnings has recently expanded:

- **Craigmore – Blakeview** — strong score, ~5km from the nearest competitor
- **Davoren Park** — strong score, ~3.4km competitor gap

Both flagged for catchment-level investigation, not as build recommendations.

## Limitations

- **SA2 ≠ catchment.** Real site selection uses drive-time trade areas spanning multiple SA2s. A high-scoring SA2 without a Bunnings may already be served by one in an adjacent SA2. Phase 0c (future work) would use drive-time isochrones.
- **Demographic suitability ≠ site feasibility.** The model can't see land availability, zoning, lease economics. Example: it ranked Adelaide CBD highly on demographics, but big-box format doesn't fit a CBD core.
- **Small validation set.** 13 Adelaide positives means individual metrics carry ±0.05 noise. The feature-importance ranking (learned from 279 positives) is more stable than any single test score.
- **No proprietary data** — public Census + public store locations only.

## Repository

- `*.ipynb` — full analysis notebook (feature engineering, model selection, validation)
- `national_features_v3.csv` — 16-feature matrix, 2,472 SA2s
- `national_model_ready.csv` — filtered, imputed, with target
- `competitors_national.csv` — 663 deduplicated competitor stores
- `sa2_centroids.csv` — SA2 codes, names, centroids
- `sa2_distance_features.csv` — distance features
- `bunnings_complete_with_sa2.csv` — Bunnings stores with SA2 codes

Raw ABS Census, SEIFA, and shapefile data not included (publicly downloadable from abs.gov.au; paths in notebook point to local copies).
