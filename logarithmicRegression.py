import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import statsmodels.api as sm

# Read in data
data_2014 = pd.read_csv('fire_data_2014.csv', sep=',', header=0)
data_2015 = pd.read_csv('fire_data_2015.csv', sep=',', header=0)
data_2016 = pd.read_csv('fire_data_2016.csv', sep=',', header=0)
data_2017 = pd.read_csv('fire_data_2017.csv', sep=',', header=0)
data_2018 = pd.read_csv('fire_data_2018.csv', sep=',', header=0)
data_2019 = pd.read_csv('fire_data_2019.csv', sep=',', header=0)
data_2020 = pd.read_csv('fire_data_2020.csv', sep=',', header=0)
data_2021 = pd.read_csv('fire_data_2021.csv', sep=',', header=0)
data_2022 = pd.read_csv('fire_data_2022.csv', sep=',', header=0)
data_2023 = pd.read_csv('fire_data_2023.csv', sep=',', header=0)

# Concatenate and clean data
data = pd.concat([data_2014, data_2015, data_2016, data_2017, data_2018, data_2019, data_2020, data_2021, data_2022, data_2023])
data = data.dropna()
data = data[data['SIZE_HA'] > 0]
data = data[data['TSURF'] != -1]
data = data[data['GWETTOP'] != -1]
data = data[data['LHLAND'] != -1]
data = data[data['SHLAND'] != -1]
data = data[data['PRECTOTLAND'] != -1]
data = data[data['LAI'] != -1]
data = data[data['GRN'] != -1]
data = data[data['SWLAND'] != -1]
data = data[data['EVPTRNS'] != -1]
data = data[data['RZMC'] != -1]

# Take natural log of size data to reduce the effect of outliers            
data['LOG_SIZE_HA'] = np.log(data['SIZE_HA'])

# Select which data to use for independent and dependent variables
X = data[['SPECIFIC_HUMIDITY','TEMP','PRECIP_ICE','PRECIP_WATER','PRECIP_VAPOR','WIND','TSURF','GWETTOP','LHLAND','SHLAND','PRECTOTLAND','LAI','GRN','SWLAND','EVPTRNS','RZMC']]
y = data['LOG_SIZE_HA']

# Standardize features
scaler = StandardScaler()
scaled_X = scaler.fit_transform(X)

# Apply principle component analysis (PCA) and keep 95% of variance
pca = PCA(n_components=0.95)
pca_X = pca.fit_transform(scaled_X)

# Print out PCA results
print("--------------- Running principle component analysis ---------------")
print(f"Original features: {X.shape[1]}")
print(f"Principal components selected: {pca_X.shape[1]}")
print(f"Explained variance ratio (each component): {pca.explained_variance_ratio_}")
print(f"Cumulative explained variance: {np.cumsum(pca.explained_variance_ratio_)[-1]}")
print("--------------------------------------------------------------------\n")

# Add constant term for OLS
const_X = sm.add_constant(pca_X)

# Fit OLS model using PCA components
model = sm.OLS(y, const_X).fit()

# Print out OLS regression results
print(model.summary())

# Get pca component names
components = []
for i in range(pca.n_components_):
    components.append(f'x{i+1}')

# Find the contribution of each original variable to each principal component
loadings = pd.DataFrame(pca.components_.T, columns=components, index=X.columns)

# Display top contributors for each component
for i in range(pca.n_components_):
    print(f"\nTop contributors to {components[i]}:")
    print(loadings.iloc[:, i].sort_values(key=abs, ascending=False))

# Calculate the overall predictive importance of each variable
coefficients = model.params[1:].values
importance = loadings.dot(coefficients)

# Sort by absolute importance
importance = importance.sort_values(key=abs, ascending=False)

# Print importance values
print(f"\nEstimated relative importance of original variables:\n{importance}")