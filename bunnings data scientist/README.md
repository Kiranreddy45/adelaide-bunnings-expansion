# Adelaide Bunnings Expansion — Data Science Version

> Propensity-score modelling to identify Adelaide suburbs most demographically similar to existing Bunnings locations, using logistic regression on ABS Census 2021 data.

![ROC Curve](reports/phase1_roc.png)

---

## TL;DR

Trained a **logistic regression classifier** to predict whether an Adelaide SA2 suburb has a Bunnings store, then applied the model to score all 91 unserved suburbs by their predicted "Bunnings-likeness."

| Metric | Value |
|---|---|
| **Test AUC** | **0.889** |
| Baseline AUC (majority class) | 0.500 |
| Improvement over baseline | +0.389 |
| Training set size | 84 suburbs (11 positives) |
| Test set size | 21 suburbs (3 positives) |

---

## Top 5 Predicted Expansion Candidates

| Rank | Suburb | Region | Population | Weekly HH Income | P(Bunnings) |
|---|---|---|---|---|---|
| 1 | Adelaide (CBD) | Adelaide City | 18,202 | $1,365 | 0.997 |
| 2 | Plympton | West Torrens | 26,480 | $1,551 | 0.929 |
| 3 | North Adelaide | Adelaide City | 6,823 | $1,867 | 0.872 |
| 4 | Hindmarsh - Brompton | Charles Sturt | 19,076 | $1,631 | 0.846 |
| 5 | Enfield - Blair Athol | Port Adelaide - East | 25,578 | $1,428 | 0.805 |

---

## Methodology

### 1. Reframing as a propensity score problem
- Target: binary `has_bunnings` (1 if SA2 contains a Bunnings, else 0)
- Class balance: 13% positive — heavily imbalanced

### 2. Feature engineering and selection
- 6 demographic features: median age, weekly personal income, weekly household income, weekly rent, average household size, population
- Excluded leakage columns (`bunnings_count`, target, identifiers)
- Median imputation for missing values

### 3. Train/test split
- Stratified 80/20 split preserving 13% positive rate in both folds
- Fixed random_state for reproducibility

### 4. Baseline models
- **Dummy classifier** (always predict majority): AUC 0.500
- **Random ranking**: AUC ~0.5
These confirm the metric pipeline works correctly.

### 5. Logistic regression
- StandardScaler applied (fit on train only, transform on test — no leakage)
- `class_weight='balanced'` to compensate for class imbalance
- L2 regularisation (sklearn default)

### 6. Multicollinearity diagnosis
- Spotted a 0.90 correlation between `weekly_personal_income` and `weekly_household_income`
- The model gave them opposite-signed coefficients (a classic multicollinearity fingerprint)
- Tested a reduced 4-feature model — AUC dropped from 0.89 to 0.80, but coefficients became consistently signed
- Decision: kept the 6-feature model for headline AUC; documented the limitation; scheduled proper fix for Phase 0 with national data

### 7. Predict on unserved suburbs
- Applied the trained model to all 91 unserved SA2s
- Ranked by predicted probability of being "Bunnings-like"

---

## What the Model Learned

| Feature | Coefficient | Direction |
|---|---|---|
| `population` | +0.67 | Strong positive — bigger suburbs more likely |
| `weekly_personal_income` | +0.61 | Positive — higher individual income correlates |
| `weekly_rent` | +0.34 | Mild positive |
| `avg_household_size` | -0.84 | Strong negative — bigger households *less* likely |
| `median_age` | -0.88 | Strong negative — older suburbs less likely |
| `weekly_household_income` | -0.97 | Strong negative (multicollinearity artefact) |

**Interpretation:** Bunnings clusters in **high-population, working-age, mid-income suburbs** — not the wealthiest postcodes. The model is mimicking Bunnings's revealed strategy: warehouse-format retail prefers volume over wealth.

---

## Files

| File | Purpose |
|---|---|
| `notebooks/01_baseline_and_setup.ipynb` | End-to-end Phase 1 modelling notebook |
| `reports/phase1_roc.png` | ROC curve visualisation |
| `reports/phase1_metrics.json` | Model card (metrics, coefficients, limitations) |

---

## Known Limitations

- **Small sample size**: only 14 positive training examples
- **Test set variance**: AUC has wide confidence intervals with only 3 positives in test
- **Multicollinearity** between income features inflates some coefficients
- **Adelaide-only**: model cannot generalise to other Australian markets without national data

These are addressed in the in-progress **Phase 0** (national data pull):
- All 8 states of ABS Census data
- ~250 Bunnings stores nationwide
- Adelaide held out as the test region for genuine geographic validation

---

## Comparison with the Analyst Version

The companion `analyst-version/` uses a rule-based composite score and produces a **completely different top 5** — Unley, Burnside, Aldgate, Goodwood, Mitcham (wealthy inner suburbs).

**The disagreement itself is a finding.** The rule-based score optimises for revenue per customer (income-heavy weighting). The ML model mimics existing Bunnings strategy (population-heavy). Whether Bunnings's revealed preference for working-class suburbs is optimal — or a strategic blind spot — is the question worth presenting to the expansion team.

---

## Reproducing the Analysis

### Prerequisites
- Python 3.10+ with: pandas, scikit-learn, matplotlib, joblib

### Steps
1. Place `adelaide_master.csv` from the analyst-version into `data/processed/` (or symlink)
2. Run `notebooks/01_baseline_and_setup.ipynb` from top to bottom
3. Output artefacts will be written to `reports/`

---

## Tools

- **Python**: pandas, scikit-learn (LogisticRegression, StandardScaler, train_test_split)
- **Visualisation**: matplotlib (ROC curve)
- **Validation**: Stratified train/test split, ROC AUC for ranking, classification report for binary diagnostics