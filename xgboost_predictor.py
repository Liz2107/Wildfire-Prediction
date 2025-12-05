import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.model_selection import GroupKFold
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, confusion_matrix, precision_recall_curve
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
import shap

# Flag to indicate whether to only use natural fires (True) or fires of all causes (False)
only_natural_flag = False

# Read in data, association error with 2013-15 data so ignore those files for now
data_2017 = pd.read_csv('fire_data_2017enriched2.csv', sep=',', header=0)
data_2018 = pd.read_csv('fire_data_2018enriched2.csv', sep=',', header=0)
data_2019 = pd.read_csv('fire_data_2019enriched2.csv', sep=',', header=0)
data_2020 = pd.read_csv('fire_data_2020enriched2.csv', sep=',', header=0)
data_2021 = pd.read_csv('fire_data_2021enriched2.csv', sep=',', header=0)
data_2022 = pd.read_csv('fire_data_2022enriched2.csv', sep=',', header=0)
data_2023 = pd.read_csv('fire_data_2023enriched2.csv', sep=',', header=0)

# Concatenate yearly data
data = pd.concat([data_2017, data_2018, data_2019, data_2020, data_2021, data_2022, data_2023])

# Process data to exclude missing values
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

# Only include natural fires in the model and rebalance the negative data if changing the data length significantly
if only_natural_flag:
    data = data[(data['CAUSE'] == 'N') | (data['FID'] == -1)]
    true_data = data[data['FID'] != -1]
    false_data = data[data['FID'] == -1]
    false_data = false_data[:len(data[data['FID'] != -1])]
    data = pd.concat([true_data, false_data])

# Select the prediction attributes
attributes = ['SPECIFIC_HUMIDITY', 'TEMP', 'PRECIP_ICE', 'PRECIP_WATER', 'PRECIP_VAPOR', 'WIND', 'TSURF', 'GWETTOP', 'LHLAND', 'SHLAND', 'PRECTOTLAND', 'LAI', 'GRN', 'SWLAND', 'EVPTRNS', 'RZMC']

# Select prediction attributes to be used for predictor_data and predicted attribute to be used for fire_truth_data
predictor_data = data[attributes]
data['fire'] = (data['FID'] != -1).astype(int)
fire_truth_data = data['fire']

# Perform k-means clustering with 100 clusters, and a random state for repeatability
kmeans = KMeans(n_clusters=100, random_state=1)
groups = kmeans.fit_predict(data[['LATITUDE', 'LONGITUDE']])

# Calculate sample frequency weights, not totally necessary in this case since the data is balanced but good practice
freq_weight = (len(fire_truth_data) - sum(fire_truth_data)) / sum(fire_truth_data)
weights = np.where(fire_truth_data == 1, freq_weight, 1)

# We run k fold cross-validation to test the spatial generalizability of the model
# Run k fold cross-validation with 5 folds
k_fold_cross_validation = GroupKFold(n_splits=5)

# Preinitialize area under curve (AUC) and LogLoss score lists
area_under_curve_scores = []
log_loss_scores = []

# Create an Extreme Gradient Boosting (XGBoost) model
model = XGBClassifier(
    n_estimators=1000,
    learning_rate=0.01,
    max_depth=6,
    subsample=0.9,
    colsample_bytree=0.9,
    gamma=0.01,
    objective='binary:logistic',
    eval_metric=['auc','logloss'],
    tree_method='hist',
    scale_pos_weight=freq_weight
)

# Loop through each fold and fit the XGBoost model
for fold_number, (training_index, validation_index) in enumerate(k_fold_cross_validation.split(predictor_data, fire_truth_data, groups=groups)):

    # Generate the training and validation prediction attributes (predictor_data) and predicted attribute (fire_truth_data) values
    predictor_training_data = predictor_data.iloc[training_index]
    predictor_validation_data = predictor_data.iloc[validation_index]
    predicted_training_data = fire_truth_data.iloc[training_index]
    predicted_validation_data = fire_truth_data.iloc[validation_index]
    training_weights = weights[training_index]

    # Fit the XGBoost model to the training data and then test it with the testing data for this fold
    model.fit(predictor_training_data, predicted_training_data, sample_weight=training_weights, eval_set=[(predictor_training_data, predicted_training_data), (predictor_validation_data, predicted_validation_data)], verbose=False)

    # Pull the AUC and log loss scores from the model to print
    results = model.evals_result()
    print(f"\nFold {fold_number+1}:")
    print("Test Spatial AUC:", round(np.mean(results['validation_0']['auc']),3))
    print("Validation Spatial AUC:", round(np.mean(results['validation_1']['auc']),3))
    print("Test Spatial LogLoss:", round(np.mean(results['validation_0']['logloss']),3))
    print("Validation Spatial LogLoss:", round(np.mean(results['validation_1']['logloss']),3))

    # Make a list of the validation AUC scores and LogLoss scores
    area_under_curve_scores.append(np.mean(results['validation_1']['auc']))
    log_loss_scores.append(np.mean(results['validation_1']['logloss']))

# Print the average AUC and LogLoss scores
print("\nMean Spatial AUC:", round(np.mean(area_under_curve_scores),3))
print("Mean Spatial LogLoss:", round(np.mean(log_loss_scores),3), '\n')

# Fit the model to the full data after using cross-validation to verify spatial robustness
model.fit(predictor_data, fire_truth_data, sample_weight=weights)

# Read in test data
test_data = pd.read_csv('fire_data_2016enriched2.csv', sep=',', header=0)

# Process test data to exclude missing values
test_data = test_data[test_data['TSURF'] != -1]
test_data = test_data[test_data['GWETTOP'] != -1]
test_data = test_data[test_data['LHLAND'] != -1]
test_data = test_data[test_data['SHLAND'] != -1]
test_data = test_data[test_data['PRECTOTLAND'] != -1]
test_data = test_data[test_data['LAI'] != -1]
test_data = test_data[test_data['GRN'] != -1]
test_data = test_data[test_data['SWLAND'] != -1]
test_data = test_data[test_data['EVPTRNS'] != -1]
test_data = test_data[test_data['RZMC'] != -1]

# Only include natural fires in the model and rebalance the negative data if changing the data length significantly
if only_natural_flag:
    test_data = test_data[(test_data['CAUSE'] == 'N') | (test_data['FID'] == -1)]
    true_data = test_data[test_data['FID'] != -1]
    false_data = test_data[test_data['FID'] == -1]
    false_data = false_data[:len(test_data[test_data['FID'] != -1])]
    test_data = pd.concat([true_data, false_data])

# Select prediction attributes to be used for predictor_data_test and predicted attribute to be used for fire_truth_data_test
predictor_data_test = test_data[attributes]
test_data['fire'] = (test_data['FID'] != -1).astype(int)
fire_truth_data_test = test_data['fire']

# Predict the fire probabilities for each set of fire attributes in the test data
fire_probability = model.predict_proba(predictor_data_test)[:,1]

# If the probability of a fire is more than 50%, say the model does predict a fire
fire_prediction = (fire_probability > 0.5).astype(int)

# Print out the resulting model AUC, precision, recall, and F1 score
print("Test Data AUC:", round(roc_auc_score(fire_truth_data_test, fire_probability),3))
print("Test Data Precision:", round(precision_score(fire_truth_data_test, fire_prediction),3))
print("Test Data Recall:", round(recall_score(fire_truth_data_test, fire_prediction),3))
print("Test Data F1 Score:", round(f1_score(fire_truth_data_test, fire_prediction),3))
print("Test Data Confusion Matrix:\n", confusion_matrix(fire_truth_data_test, fire_prediction))

# Calculate the precision and recall curve values of the model
precision, recall, threshold = precision_recall_curve(fire_truth_data_test, fire_probability)

# Calculate the true versus predicted probability calibration curve values
true_probability, predicted_probability = calibration_curve(fire_truth_data_test, fire_probability, n_bins=15)

# Calculate Shapley (SHAP) values
# Allows us to see the contribution of each attribute to a prediction, taking into account attribute interactions
shap_values = shap.TreeExplainer(model).shap_values(predictor_data_test)

# Plot the precision-recall curve
plt.figure(1)
plt.plot(recall, precision)
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-Recall Curve")
plt.grid()

# Plot the calibration curve
plt.figure(2)
plt.plot(predicted_probability, true_probability, marker="o", label="Calibration Curve")
plt.plot([0,1],[0,1], "--", label="Ideal Calibration")
plt.xlabel("Mean Predicted probability")
plt.ylabel("Fraction of Positives")
plt.title("Calibration Curve")
plt.legend()
plt.grid()

# Plot the SHAP values summary "beeswarm" plot
# Red values on the right side (positive axis) indicate the attribute increases wildfire chance,
# blue values on the right side indicate the attribute decreases wildfire chance. The attributes
# are sorted from top to bottom based on their impact on the prediction
plt.figure(3)
shap.summary_plot(shap_values, predictor_data_test)
plt.show()