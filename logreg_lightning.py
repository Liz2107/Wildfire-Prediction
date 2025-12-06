import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import silhouette_score

import statsmodels.api as sm

# Read in enriched data, remove unknown fires
fire_data = pd.read_csv("fire_data_enriched3.csv")
fire_data = fire_data.dropna(subset=["FLASH_DENSITY"])
fire_data = fire_data[fire_data["CAUSE"] != "U"]

# Target variable
fire_data["FIRE_OCCURRENCE"] = (fire_data['CAUSE'] == 'N').astype(int)

print(fire_data)
print("NaNs per column:\n", fire_data.isna().sum())

# Select logistic regression params
features = ["FLASH_DENSITY"]
target = "FIRE_OCCURRENCE"

X = fire_data[features]
y = fire_data[target]

# Identify numeric and categorical features
numeric_features = ["FLASH_DENSITY"]

# Preprocessing
print("Attempting preprocessing...")
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features)
    ]
)

# Fit and transform data, add intercept
X_processed = preprocessor.fit_transform(X)
X_processed = sm.add_constant(X_processed)

X_df = pd.DataFrame(X_processed)
X_df = X_df.replace([np.inf, -np.inf], np.nan)  
valid_rows = X_df.notna().all(axis=1) & y.notna()

X_processed = X_df[valid_rows]
y = y[valid_rows]

# Run logistic regression
print("Running logistic regression...")
logit_model = sm.Logit(y, X_processed).fit()

# Print model statistics
print("\nLogistic regression results\n")
print(logit_model.summary())

# Get odds ratios
params = logit_model.params
conf = logit_model.conf_int()
conf['OR'] = params
conf.columns = ['2.5%', '97.5%', 'Odds Ratio']
conf = np.exp(conf)

print("\nOdds ratios\n")
print(conf)