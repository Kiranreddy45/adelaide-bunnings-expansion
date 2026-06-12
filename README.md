# Adelaide Bunnings Expansion — Site Selection Modelling

**A two-phase data project predicting where Bunnings Warehouse should open its next stores in Australia, combining business reasoning, ABS Census demographics, and machine learning — with an honest validation that proved the national model identifies Adelaide's actual store locations *better than a model trained on Adelaide alone*.**

> A skills-demonstration portfolio project across two tracks (analyst + data science) and two phases (Adelaide → National). Built independently using public data; not a production system. Read this README in 3 minutes; the headline finding is in **Phase 0b**.

---

## The headline finding

A model trained on the rest of Australia, blind to Adelaide, identified Adelaide's actual Bunnings locations with **ROC-AUC 0.805** — outperforming a model trained specifically on Adelaide (0.790). The national approach didn't just match the local model; it surpassed it. This validates the project's central thesis: feature relationships learned where statistics have power (292 national positives) transfer better than those fit on a small local sample (14 Adelaide positives).

Population dominates the importance ranking (22%), followed by retail employment density, mortgage-paying home-ownership, broad socio-economic advantage, and competitor spacing — the textbook big-box home-improvement catchment profile, derived from data without being told.

---

## Why this project exists

Most analytics portfolios show a single clean dataset, a single model, a single AUC. This one is different by design. The project began as an Adelaide-only exploration, hit a real statistical limit (14 positives ≠ reliable model comparison), and was then *deliberately expanded* nationally to honestly answer the question Adelaide couldn't. The progression is the point.

The work demonstrates: end-to-end ownership of a business question (where should a real retailer expand?), careful sourcing from authoritative public data, defensive cleaning against known data-quality issues, methodical model selection on the metric aligned with the actual business use, transparent validation through a held-out test, and honest interpretation that names its own limitations rather than hiding them.

---

## Project structure

The repository is organized in folders that reflect the project's evolution:

### **Phase 0b — National Expansion Model** ⭐ (most recent, the centerpiece)
**Folder:** `Bunnings suburb selection/` *(or whichever folder name you used)*

Trains an XGBoost model on the rest of Australia (2,129 SA2s, 279 positives), validates blind on Adelaide (102 SA2s, 13 positives). Compared 8 model families via 5-fold cross-validation on **PR-AUC** (the right metric for top-of-list ranking on imbalanced data), tuned the winner with GridSearchCV (405 model fits), and held Adelaide out completely until final scoring.

This is the current, portable production version. Notebook runs end-to-end on any machine that clones the repo. The README inside this folder contains the full methodology, results table, feature importance, and Adelaide expansion candidates with appropriate caveats.

### **Phase 0a — Adelaide Foundation** (earlier, documents the project's evolution)
Two parallel tracks demonstrating both analyst and data-science skill sets:

- **`bunnings data analyst/`** — SQL queries and Power BI dashboard ranking Adelaide suburbs by a composite demographic score. The analyst-track lens on the same question.
- **`bunnings data scientist/`** — Logistic regression propensity model on Adelaide SA2s (105 suburbs, 14 stores). AUC 0.889 on a small test, with documented multicollinearity diagnosis and a top-5 expansion shortlist.
- **`17_features_Adl/`** — Expanded 17-feature Adelaide model with SEIFA indexes, competitor distances via verified Google Places coordinates, and Random Forest at AUC 0.790 (LeaveOneOut CV).

These earlier-phase notebooks reference local data paths and were the methodological foundation that led to Phase 0b. They document how the analysis grew — from analyst-track scoring to data-science modelling to national validation — rather than presenting a polished single deliverable.

---

## The methodological story (worth a 60-second read)

**Phase 0a** revealed three problems that an honest analyst couldn't ignore:

1. **Statistical fragility.** With only 14 positives, cross-validation folds held 2–3 positives each — model comparison was meaningless and feature importance estimates wide.
2. **Single-city blind spot.** A model fit on Adelaide could not be honestly validated on Adelaide; the AUC reflected fitting noise more than transferable structure.
3. **Strategic tension.** A rule-based "wealthy suburbs" score and the ML "high-population working-class" score disagreed completely — a finding worth presenting, but unprovable at n=14.

**Phase 0b** addressed each problem through a single design choice: go national. With 292 positives across Australia, fold sizes became statistically meaningful (~55 positives per fold), 8-model bake-offs became defensible, and — critically — Adelaide could be held out entirely as an honest validation set. The thesis was simple: *if a model trained on the rest of Australia identifies Adelaide's actual Bunnings, the feature relationships transfer.* They did.

---

## Why PR-AUC, not accuracy

This single decision separates rigorous portfolio work from amateur work, so it deserves its own line:

- **Accuracy is disqualified.** 87% of SA2s have no Bunnings, so a "predict no Bunnings everywhere" model scores 87% accuracy while being useless.
- **Precision and recall need a threshold**, but site selection isn't a yes/no decision per SA2 — it's a ranking problem where the property team investigates the *top* of the list.
- **PR-AUC measures whether real sites concentrate at the top of the ranking** — directly aligned with how the model would be used commercially.
- **ROC-AUC** is reported as supporting context but isn't the primary selection metric because, on imbalanced data, it gets free credit for correctly ranking the abundant negatives.

This was the metric used to select XGBoost over Random Forest, even though Random Forest had a marginally higher ROC-AUC. The metric should match the business use; here, it did.

---

## Honest limitations (read these before trusting any recommendation)

A senior advisor names limits up front. This project has them, and they're documented in detail in the Phase 0b README:

- **SA2 ≠ catchment.** Real site selection uses drive-time trade areas spanning multiple SA2s. A high-scoring SA2 without a Bunnings may already be served by one in an adjacent SA2. Phase 0c (future work) would use drive-time isochrones.
- **Demographic suitability ≠ site feasibility.** The model can't see land availability, zoning, lease economics. Example: it ranked Adelaide CBD highly on demographics, but big-box format doesn't fit a CBD core.
- **Small validation set.** 13 Adelaide positives means individual metrics carry ±0.05 noise; the feature-importance ranking (learned from 279 positives) is the more stable finding.
- **No proprietary data.** Public Census + public store locations only — no loyalty, transaction, foot-traffic, or sales data a real retailer would use.

---

## Data sources

All public, all authoritative:

- **ABS Census 2021** — General Community Profile (G01, G02, G56), Time Series Profile (T01)
- **SEIFA 2021** — Index of Relative Socio-economic Disadvantage / Advantage and Disadvantage / Economic Resources / Education and Occupation
- **ABS SA2 2021 boundaries** — official shapefile
- **Bunnings store locations** — geocoded from the official store finder (312 stores)
- **Competitor locations** — Mitre 10, Home Hardware, Total Tools (663 stores after deduplication)

Raw data is not included in this repo — files are large and publicly downloadable. Processed CSVs are included so the modelling sections run for anyone who clones the repo.

---

## Tools

**Data science track:** Python, pandas, NumPy, scikit-learn, XGBoost, geopandas, matplotlib

**Analyst track:** SQL Server, Power BI Desktop

**Project hygiene:** Git, Jupyter Notebook, defensive data cleaning, cross-validation, principled metric selection

---

## What this work demonstrates

Beyond the technical execution:

- **Business framing** — the project began with a real business question (where should a real retailer expand?), not a dataset looking for a problem
- **Statistical judgment** — recognizing when n=14 invalidated multi-model comparison, and *expanding the data* rather than over-claiming on noise
- **Methodological rigor** — model selection before feature selection, hold-out before training, PR-AUC over accuracy, tuning to confirm the ceiling rather than to chase it
- **Domain reasoning** — the SA2 vs catchment caveat, the CBD format mismatch, the "demographic suitability ≠ feasibility" boundary
- **Honest interpretation** — naming what the model can and can't see; flagging candidates *for investigation*, not as build recommendations

---

## Contact

**Kiran Reddy** — Masters in Business Analytics, based in Adelaide, South Australia.

Open to data analyst / data scientist roles — particularly in healthcare (e.g., SAHMRI), agtech (e.g., CSIRO Waite, Wine Australia), and consumer analytics.

[LinkedIn — add your URL] | [Email — add your address]

---

*This project was built independently, end-to-end, as a portfolio demonstration. It does not represent the views or analyses of Bunnings, ABS, or any third party.*
