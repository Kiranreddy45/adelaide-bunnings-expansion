# Set project root works for anyone who clones the repo
import os
DATA_DIR = 'data'
RAW_DIR = os.path.join(DATA_DIR, 'raw')

import pandas as pd
xls = pd.ExcelFile(os.path.join(RAW_DIR, 'seifa_2021_sa2.xlsx'))
print("Sheet names:", xls.sheet_names)
for sheet in ['Table 1', 'Table 2', 'Table 3', 'Table 4', 'Table 5', 'Table 6']:
    print(f"  {sheet}")
    df = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=8)
    for i, row in df.iterrows():
        print(row.tolist())

# Load SEIFA Table 1 — skip the 5 header rows
seifa = pd.read_excel(
    os.path.join(RAW_DIR, 'seifa_2021_sa2.xlsx'),
    sheet_name='Table 1',
    header=5  # row 6 becomes the header (0-indexed)
)

# Check what we got
print(seifa.columns.tolist())
print(seifa.shape)
print(seifa.head(3))
master = pd.read_csv(os.path.join(DATA_DIR, 'adelaide_master.csv'))
print(master.columns.tolist())
print(master.shape)
print(master.head(2))
# Rename SEIFA columns to something clean
seifa_clean = seifa.rename(columns={
    '2021 Statistical Area Level 2  (SA2) 9-Digit Code': 'SA2_CODE_2021',
    'Score': 'seifa_irsd_score',
    'Decile': 'seifa_irsd_decile',
    'Score.1': 'seifa_irsad_score',
    'Decile.1': 'seifa_irsad_decile',
    'Score.2': 'seifa_ier_score',
    'Decile.2': 'seifa_ier_decile',
    'Score.3': 'seifa_ieo_score',
    'Decile.3': 'seifa_ieo_decile'
})

# Keep only what we need
seifa_cols = ['SA2_CODE_2021', 
              'seifa_irsd_score', 'seifa_irsd_decile',
              'seifa_irsad_score', 'seifa_irsad_decile', 
              'seifa_ier_score', 'seifa_ier_decile',
              'seifa_ieo_score', 'seifa_ieo_decile']
seifa_clean = seifa_clean[seifa_cols]

# Load your master
master = pd.read_csv(os.path.join(DATA_DIR, 'adelaide_master.csv'))

# Merge
master_seifa = master.merge(seifa_clean, on='SA2_CODE_2021', how='left')
# Check the result
print(f"Before: {master.shape}")
print(f"After:  {master_seifa.shape}")
print(f"Null SEIFA values: {master_seifa['seifa_irsd_score'].isna().sum()}")
print(master_seifa[['SA2_NAME_2021', 'seifa_irsd_score', 'seifa_irsad_score', 
                      'seifa_ier_score', 'seifa_ieo_score']].head(5))
# 6nulls we need to see what they are
missing = master_seifa[master_seifa['seifa_irsd_score'].isna()]
print(missing[['SA2_CODE_2021', 'SA2_NAME_2021', 'bunnings_count']])
#"6 SA2s excluded from ABS SEIFA (industrial/airport zones) were imputed with Adelaide median values. 
#Two of these contain Bunnings stores (Parafield, Adelaide Airport).
# Check which SEIFA columns have nulls
seifa_score_cols = ['seifa_irsd_score', 'seifa_irsad_score', 
                    'seifa_ier_score', 'seifa_ieo_score']
seifa_decile_cols = ['seifa_irsd_decile', 'seifa_irsad_decile',
                     'seifa_ier_decile', 'seifa_ieo_decile']
# Fill scores with Adelaide median
for col in seifa_score_cols + seifa_decile_cols:
    master_seifa[col] = pd.to_numeric(master_seifa[col], errors='coerce')
    median_val = master_seifa[col].median()
    master_seifa[col] = master_seifa[col].fillna(median_val)

# Verify no nulls remain
print(f"\nRemaining nulls: {master_seifa[seifa_score_cols].isna().sum().sum()}")
# here we need to check whether all 6 nulls got SEIFA values or not we need to get the same values for every null value because we wanted to replace with the median value
check_codes = [402041039, 402041042, 403041081, 404021098, 404021103, 404031104]
print(master_seifa[master_seifa['SA2_CODE_2021'].isin(check_codes)][
    ['SA2_NAME_2021', 'seifa_irsd_score', 'seifa_ier_score', 'bunnings_count']
])
# we need to add SA2ahapefile which have coordinates of bunnings store
import geopandas as gpd
sa2_gdf=gpd.read_file(os.path.join(RAW_DIR, 'sa2_shapefile'))
master=pd.read_csv(os.path.join(DATA_DIR, 'adelaide_master.csv'))
comps=pd.read_csv(os.path.join(RAW_DIR, 'adelaide_competitors.csv'))
# now matching SA2codes with coordinates
# remove non-numeric in sa2codes
sa2_gdf = sa2_gdf[sa2_gdf['SA2_CODE21'].str.isnumeric()]
sa2_gdf['SA2_CODE21']=sa2_gdf['SA2_CODE21'].astype('int')
adl_sa2=sa2_gdf[sa2_gdf['SA2_CODE21'].isin(master['SA2_CODE_2021'])]
 # calculate centroids
adl_sa2=adl_sa2.copy()
adl_sa2['centroid']=adl_sa2.geometry.centroid
adl_sa2['sa2_lat']=adl_sa2['centroid'].y
adl_sa2['sa2_lon']=adl_sa2['centroid'].x
print(adl_sa2[['SA2_NAME21','sa2_lat','sa2_lon','centroid']].head())
# Get Bunnings centroids  — bunnings_count is already in master
bunnings_codes = master[master['bunnings_count'] > 0]['SA2_CODE_2021'].values
bunnings_centroids = adl_sa2[adl_sa2['SA2_CODE21'].isin(bunnings_codes)]
bunnings_lats = bunnings_centroids['sa2_lat'].values
bunnings_lons = bunnings_centroids['sa2_lon'].values
from math import radians, sin, cos, sqrt, atan2
import pandas as pd

# Inline testing with taking values whether that giving correct answer or not
lat1, lon1 = radians(-34.9285), radians(138.6007)
lat2, lon2 = radians(-34.9163), radians(138.6232)
dlat = lat2 - lat1
dlon = lon2 - lon1
a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
test = 6371 * 2 * atan2(sqrt(a), sqrt(1-a))
print(f"Inline test: {test:.2f} km")

results = []
for _, sa2 in adl_sa2.iterrows():
    sa2_code = sa2['SA2_CODE21']
    lat1 = radians(sa2['sa2_lat'])
    lon1 = radians(sa2['sa2_lon'])
    
    comp_distances = []
    for _, comp in comps.iterrows():
        lat2 = radians(comp['latitude'])
        lon2 = radians(comp['longitude'])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        a = min(a, 1.0)
        dist = 6371 * 2 * atan2(sqrt(a), sqrt(1-a))
        comp_distances.append(dist)
    # Distance to Bunnings — same maths, different target locations    
    bunnings_distances = []
    for blat, blon in zip(bunnings_lats, bunnings_lons):
        lat2 = radians(blat)
        lon2 = radians(blon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        a = min(a, 1.0)
        dist = 6371 * 2 * atan2(sqrt(a), sqrt(1-a))
        bunnings_distances.append(dist)
    
    results.append({
        'SA2_CODE_2021': sa2_code,
        'dist_nearest_competitor_km': min(comp_distances),
        'competitors_within_5km': sum(1 for d in comp_distances if d <= 5),
        'competitors_within_10km': sum(1 for d in comp_distances if d <= 10),
        'dist_nearest_bunnings_km': min(bunnings_distances),
    })

dist_df = pd.DataFrame(results)
master_v3 = master.merge(dist_df, on='SA2_CODE_2021', how='left')
print(f"\nClosest to a competitor:")
print(master_v3.nsmallest(10, 'dist_nearest_bunnings_km')[
    ['SA2_NAME_2021', 'dist_nearest_bunnings_km', 'dist_nearest_competitor_km', 
     'competitors_within_5km', 'bunnings_count']])

print(f"\nFurthest from any competitor:")
print(master_v3.nlargest(10, 'dist_nearest_bunnings_km')[
    ['SA2_NAME_2021', 'dist_nearest_bunnings_km', 'dist_nearest_competitor_km', 
     'competitors_within_5km', 'bunnings_count']])
# we got features like total construction workers and retail tradie workers and we are using that to find the percentage of those workers in total employed
# merging these features into our master_v3 dataframe
g56=pd.read_csv(os.path.join(RAW_DIR, 'census_2021_gcp', '2021Census_G56A_SA_SA2.csv'))
master_v3=pd.read_csv(os.path.join(DATA_DIR, 'adelaide_master_v3.csv'))
# calculating total employment(sum of all industry except ID_NS which is not stated
industry_tots=[c for c in g56.columns if c.endswith('_Tot') and c!='ID_NS_Tot']
g56['total_employed']=g56[industry_tots].sum(axis=1)

#constructing features
g56_clean=pd.DataFrame({
    'SA2_CODE_2021': g56['SA2_CODE_2021'],
    'construction_workers': g56['Construction_Tot'],
    'total_employed': g56['total_employed'],
    'construction_pct': (g56['Construction_Tot'] / g56['total_employed'] * 100).round(2),
    'retail_trade_workers': g56['RetTde_Tot'],
    'retail_trade_pct': (g56['RetTde_Tot'] / g56['total_employed'] * 100).round(2)
})
# merge this with master_v3
master_v4=master_v3.merge(g56_clean,on='SA2_CODE_2021', how='left')

print(f"Shape: {master_v4.shape}")
print(f"Nulls: {master_v4['construction_pct'].isna().sum()}")
print(master_v4.nlargest(10, 'construction_pct')[
    ['SA2_NAME_2021', 'construction_pct', 'construction_workers', 
     'dist_nearest_bunnings_km', 'bunnings_count']])
# fill these nulls with median
noise = ['Torrens Island', 'Dry Creek - South', 'Dry Creek - North', 
         'Lonsdale', 'Adelaide Airport', 'Parafield',
         'Happy Valley Reservoir']

master_v4 = master_v4[~master_v4['SA2_NAME_2021'].isin(noise)].copy()
# we need to have population growth 2016-2021 and housing costs(higher mortgages =expensive homes=spending on renovation)
g02=pd.read_csv(os.path.join(RAW_DIR, 'census_2021_gcp', '2021Census_G02_SA_SA2.csv'))
t01=pd.read_csv(os.path.join(RAW_DIR, 'census_2021_tsp', '2021Census_T01_SA_SA2.csv'))
master_v4=pd.read_csv(os.path.join(DATA_DIR, 'adelaide_master_v4.csv'))
# updating with median mortgage
mortgage_df=g02[['SA2_CODE_2021','Median_mortgage_repay_monthly']].rename(
    columns={'Median_mortgage_repay_monthly': 'median_mortgage_monthly'}
)
# updating with population growth from 2016 to 2021
pop_df=t01[['SA2_CODE_2021','Tot_persons_C16_P','Tot_persons_C21_P']].rename(
    columns={'Tot_persons_C16_P': 'pop_2016', 'Tot_persons_C21_P': 'pop_2021'}
)
pop_df['pop_growth_pct']=((pop_df['pop_2021']-pop_df['pop_2016'])/pop_df['pop_2016']*100).round(2)
#merge these into master file
master_v5=master_v4.merge(mortgage_df,on='SA2_CODE_2021', how='left')
master_v5 = master_v5.merge(pop_df[['SA2_CODE_2021', 'pop_2016', 'pop_growth_pct']], on='SA2_CODE_2021', how='left')
# now handling nulls
print(f"Nulls - mortgage: {master_v5['median_mortgage_monthly'].isna().sum()}")
print(f"Nulls - pop_growth: {master_v5['pop_growth_pct'].isna().sum()}")
# replacing nulls with median
for col in ['median_mortgage_monthly', 'pop_2016', 'pop_growth_pct']:
    median_val = master_v5[col].median()
    master_v5[col] = master_v5[col].fillna(median_val)
# updting master_v5 and saving
master_v5.to_csv(os.path.join(DATA_DIR, 'adelaide_master_v5.csv'), index=False)
print(f"\nFastest growing suburbs:")
print(master_v5.nlargest(10, 'pop_growth_pct')[
    ['SA2_NAME_2021', 'pop_growth_pct', 'pop_2016', 'population', 
     'dist_nearest_bunnings_km', 'bunnings_count']])
# for Adelaide airport population in 2016 is 0, so we can't divide anything by 0. So, np.inf is positive infinity and -np.inf is negative infinity, so we replace that with 0
import numpy as np
master_v5['pop_growth_pct']=master_v5['pop_growth_pct'].replace([np.inf,-np.inf],0)
master_v5.to_csv(os.path.join(DATA_DIR, 'adelaide_master_v5.csv'), index=False)
print(master_v5.nlargest(10, 'pop_growth_pct')[
    ['SA2_NAME_2021', 'pop_growth_pct', 'pop_2016', 'population', 
     'dist_nearest_bunnings_km', 'bunnings_count','dist_nearest_competitor_km']])
# dataset is now cleaned and ready to train models
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LeaveOneOut,cross_val_predict
#when you have small datset like this we use LeaveOneOut beacuse it trains on 111 suburbs and tests on 1 remaining suburb
# and this repeats on all 112 suburbs so every suburb gets chance to be in testcase suburb
# this end up with a prediction for every suburb, and every prediction made by model that neever saw that suburb during training
#cross_val_predict automates this process
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score,classification_report
import warnings
warnings.filterwarnings('ignore')
master=pd.read_csv(os.path.join(DATA_DIR, 'adelaide_master_v5.csv'))
# define target
y= (master['bunnings_count']>0).astype(int)
# drop identifiers,target, and leaky features
drop_cols=['SA2_CODE_2021','SA2_NAME_2021','SA3_NAME','bunnings_count',
           'dist_nearest_bunnings_km',  # data leakage
           'seifa_irsd_decile', 'seifa_irsad_decile',  # redundant with scores
           'seifa_ier_decile', 'seifa_ieo_decile',
           'construction_workers', 'total_employed',    # redundant with pct
           'retail_trade_workers', 'pop_2016']          # redundant with growth pct
x=master.drop(columns=drop_cols)
for col in x.columns:
    print(f" {col}")
print(x.isna().sum())
#unexpected column Unnamed so we need to drop that as well
unnamed_cols = [c for c in x.columns if 'Unnamed' in c]
if unnamed_cols:
    x = x.drop(columns=unnamed_cols)
    print(f"Dropped: {unnamed_cols}")
else:
    print("No Unnamed columns — already clean")

for col in x.columns:
    print(f"  {col}")

# we used lasso to pick model their top useful fetures but it doesn't work properly beacuse of small postives in that dataset 96 with no bunnings and 16 with bunnings
# so we used our features with our basic knowledge
x_all=x.copy()
domain_features=['population', 'seifa_ier_score', 'dist_nearest_competitor_km',
                   'competitors_within_5km', 'construction_pct',
                   'median_mortgage_monthly', 'pop_growth_pct']
x_domain=x[domain_features]
#scale both
scaler_all = StandardScaler()
scaler_domain = StandardScaler()
x_all_scaled = pd.DataFrame(scaler_all.fit_transform(x_all), columns=x_all.columns)
x_domain_scaled = pd.DataFrame(scaler_domain.fit_transform(x_domain), columns=x_domain.columns)


for col in x_all_scaled.columns:
    print(f"  {col}")
print(f"\nDomain features list:")
for col in x_domain_scaled.columns:
    print(f"  {col}")
## defining models
loo=LeaveOneOut()
#LogisticRegression
lr=LogisticRegression(penalty='l1', solver='saga',C=0.5,max_iter=5000, random_state=42)
lr_d_probs=cross_val_predict(lr, x_domain_scaled,y,cv=loo, method='predict_proba')[:,1]
lr_d_auc=roc_auc_score(y,lr_d_probs)
print(f"Logistic Regression (Lasso): AUC = {lr_d_auc:.3f}")

##RandomForest
rf=RandomForestClassifier(n_estimators=500,max_depth=4,min_samples_leaf=5,
                          class_weight='balanced',random_state=42)
rf_d_probs=cross_val_predict(rf, x_domain_scaled,y,cv=loo, method='predict_proba')[:,1]
rf_d_auc=roc_auc_score(y,rf_d_probs)
print(f"Random Forest:AUC = {rf_d_auc:.3f}")


## XGBoost
from xgboost import XGBClassifier
xgb = XGBClassifier(
        n_estimators=200, max_depth=2, learning_rate=0.05,
        scale_pos_weight=6, eval_metric='logloss',
        random_state=42, use_label_encoder=False
    )
xgb_d_probs = cross_val_predict(xgb, x_domain_scaled, y, cv=loo, method='predict_proba')[:, 1]
xgb_d_auc = roc_auc_score(y, xgb_d_probs)
print(f"XGBoost:AUC = {xgb_d_auc:.3f}")
#from here this cell and following cell we used lasso model selecting features on its own it didn't pick great features so we used our domain features in above cell
#scale features on same scale
scaler=StandardScaler()
x_scaled=pd.DataFrame(scaler.fit_transform(x), columns=x.columns)
# fit does check every column and calculates its mean and std then transform converts it in this formula scaled_value=(orginal_value-mean)/std
loo=LeaveOneOut()
#LogicalRegression with Lasso
lr=LogisticRegression(penalty='l1', solver='saga',C=0.5,max_iter=5000, random_state=42)
#penality='l1' is lasso regularisation that removes unimportant fetures by making their weights to 0 and it is automatic selection
# solver='saga' its mathematical algorithm used to find best feature weights as saga is the best that supports l1 penality
#c=0.5 controls how aggresively lasso removes features as lower c it means strong regularisation means removes everything, so we use c=0.5 which is moderate
lr_probs=cross_val_predict(lr, x_scaled,y,cv=loo, method='predict_proba')[:,1]
#cross_val_predict(lr, x_scaled,y,cv=loo this runs 112 rounds of training and testing
#method='predict_proba' gives probability instead of giving yes/no
lr_auc=roc_auc_score(y,lr_probs)
# it gives the probability that the model gave Bunnings Suburb a higher score when it picks one bunnings suburb and non bunnings suburb it works in pairs
print(f"Logistic Regression (Lasso): AUC = {lr_auc:.3f}")

#RandomForest
rf=RandomForestClassifier(n_estimators=500,max_depth=4,min_samples_leaf=5,
                          class_weight='balanced',random_state=42)
rf_probs=cross_val_predict(rf, x_scaled,y,cv=loo, method='predict_proba')[:,1]
rf_auc=roc_auc_score(y,rf_probs)
print(f"Random Forest:AUC = {rf_auc:.3f}")
#n_estimators- build 500 decision trees. Each tree sees a random sample of suburbs and features
# max_depth=4-- each tree can make at most 4 splits(4 decisons) preventing model from memorising
#min_leaf_samples=5-- every final group(leaf) in a tree must contain atleast 5 suburbs
# class_weight --- this address imbalanced problem as we have 16 suburbs with bunnings so model could predict no bunnings for everything and be almost 85% right so we used" balanced"

#XGBoost
#RandomForest build trees and works alone but in XGBoost build trees sequentially where each new tree learns from the mistakes of previous tree
#learning_rate--this controll how much each new tree is allowed to change the overall prediction.its like each tree only gets adjust prediction by 5% after 200 small nudges will get most refined answer
#scale_pos_weight=6-- we have 96negatives(no_bunnings) 16 positives so XGBoost treat that when it make mistake on bunnings suburb, treat it as 6 times worse than a mistake on non_bunnings suburb(96%16)it same like class_weight in randomforest
#eval_metric---its is internal scoring function it uses itself during training if one new tree is added it checks whether it get betteror worse? using this metric
#use_label_encoder--XGBoost automatically convert target labels into(0 and 1)using label_encoder. so we dont need to that beacuse we already formatted it so we use false
from xgboost import XGBClassifier
xgb = XGBClassifier(
        n_estimators=200, max_depth=2, learning_rate=0.05,
        scale_pos_weight=6, eval_metric='logloss',
        random_state=42, use_label_encoder=False
    )
xgb_probs = cross_val_predict(xgb, x_scaled, y, cv=loo, method='predict_proba')[:, 1]
xgb_auc = roc_auc_score(y, xgb_probs)
print(f"XGBoost:AUC = {xgb_auc:.3f}")
# Train Lasso on full data to see coefficients
lr_full = LogisticRegression(penalty='l1', solver='saga', C=0.5, max_iter=5000, random_state=42)
lr_full.fit(x_scaled, y)

print("Lasso feature coefficients:")
for name, coef in sorted(zip(x.columns, lr_full.coef_[0]), key=lambda x: abs(x[1]), reverse=True):
    status = "KEPT" if coef != 0 else "dropped"
    print(f"  {name:35s} {coef:+.4f}  {status}")

print(f"\nFeatures kept: {sum(lr_full.coef_[0] != 0)}")
print(f"Features dropped: {sum(lr_full.coef_[0] == 0)}")

# Where are actual Bunnings suburbs ranking?
print(f"\nActual Bunnings suburbs and their predicted probabilities:")
bunnings_mask = y == 1
for i in bunnings_mask[bunnings_mask].index:
    print(f"  {master['SA2_NAME_2021'].iloc[i]:35s} prob={lr_probs[i]:.3f}")
## as RandomForest have high score now we need to train RandomForest on the full dataset before we use LeaveOneOut, which trains each model individually 
rf_best = RandomForestClassifier(n_estimators=500, max_depth=3, min_samples_leaf=5,
                                  class_weight='balanced', random_state=42)
rf_best.fit(x_domain_scaled, y)
#after training model we use feature_importances which gives each feature values upto 1 how much that feature responsible to output it given
importances=rf_best.feature_importances_
#zip(domain_features,importances thsi gives the pair of eachfeature and beside it how imp is that feature
#sorted(..., key=lambda x: x[1], reverse=True) sorts these pairs by imp value it given as we asked x[1]
for name,imp in sorted(zip(domain_features,importances),key=lambda x :x[1],reverse=True):
# it gives bar with those red blocks as highest imp feature gets 20 blocks  with it calculates percentage of max imp this feature has
    bar = '█' * int(imp / max(importances) * 20)
    print(f"  {name:35s} {imp:.4f}  {bar}")
master['expansion_score']=rf_d_probs
#it filter out suburbs with no_bunnings and gives top 15 suburbs along with expansion_scor
recommendations=master[master['bunnings_count']==0].nlargest(15,'expansion_score')
print(f'{"="*60}')
for rank, (_, row) in enumerate(recommendations.iterrows(), 1):
    print(f"  {rank:>2}. {row['SA2_NAME_2021']:30s} score={row['expansion_score']:.3f}  "
          f"pop={int(row['population']):>6,}  "
          f"dist_bunnings={row['dist_nearest_bunnings_km']:.1f}km  "
          f"competitors_5km={int(row['competitors_within_5km'])}")
