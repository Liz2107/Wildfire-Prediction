import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.model_selection import GroupKFold
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

import shap
from xgboost import plot_importance
from sklearn.calibration import calibration_curve
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import precision_recall_curve, average_precision_score
import matplotlib.pyplot as plt

# ---------------------------
# READ & MERGE DATA
# ---------------------------

years = range(2017, 2024)
dfs = [pd.read_csv(f'NFDB_enriched_population/fire_data_{y}enriched4.csv') for y in years]
all_data = pd.concat(dfs)
data = all_data

required_vars = [
    'TSURF','GWETTOP','LHLAND','SHLAND','PRECTOTLAND','LAI','GRN',
    'SWLAND','EVPTRNS','RZMC'
]

for var in required_vars:
    data = data[data[var] != -1]

data = data[data["CAUSE"] != "U"]

# Classification targets
label_map = {
    0: "No Fire",
    1: "Anthropogenic Fire",
    2: "Natural Fire"
}

def assign_label(row):
    if row['CAUSE'] == 'H':
        return 1
    if row['CAUSE'] == 'N':
        return 2
    else:
        return 0

data['fire_class'] = data.apply(assign_label, axis=1)

# Model attributes
attributes = [
    'SPECIFIC_HUMIDITY', 'TEMP', 'PRECIP_ICE', 'PRECIP_WATER',
    'PRECIP_VAPOR', 'WIND', 'TSURF', 'GWETTOP', 'LHLAND', 'SHLAND',
    'PRECTOTLAND', 'LAI', 'GRN', 'SWLAND', 'EVPTRNS', 'RZMC',
    'FLASH_DENSITY', 'POP_DENSITY'
]

# Model target
predictor_data = data[attributes]
fire_truth_data = data['fire_class']

# ---------------------------
# SPATIAL CLUSTERING
# ---------------------------

kmeans = KMeans(n_clusters=100, random_state=1)
groups = kmeans.fit_predict(data[['LATITUDE', 'LONGITUDE']])

# Weight class counts
class_counts = fire_truth_data.value_counts().sort_index()
weights = fire_truth_data.map(lambda c: class_counts[0] / class_counts[c]).values

# ---------------------------
# MODEL
# ---------------------------

kfold = GroupKFold(n_splits=5)

model = XGBClassifier(
    n_estimators=1000,
    learning_rate=0.01,
    max_depth=6,
    subsample=0.9,
    colsample_bytree=0.9,
    gamma=0.01,
    objective='multi:softprob',
    num_class=3,
    eval_metric='mlogloss',
    tree_method='hist'
)

fold_scores = []

for fold, (train_idx, val_idx) in enumerate(kfold.split(predictor_data, fire_truth_data, groups)):

    # Config training data
    X_train, X_val = predictor_data.iloc[train_idx], predictor_data.iloc[val_idx]
    y_train, y_val = fire_truth_data.iloc[train_idx], fire_truth_data.iloc[val_idx]
    w_train = weights[train_idx]

    model.fit(X_train, y_train, sample_weight=w_train, eval_set=[(X_val, y_val)], verbose=False)

    # Results for a given fold
    preds = np.argmax(model.predict_proba(X_val), axis=1)
    score = roc_auc_score(pd.get_dummies(y_val), model.predict_proba(X_val), multi_class='ovo')
    fold_scores.append(score)

    print(f"\nFold {fold+1} AUC (multiclass OVO): {score:.3f}")

print("\nMean CV AUC:", np.mean(fold_scores))

model.fit(predictor_data, fire_truth_data, sample_weight=weights)

# ---------------------------
# TEST SET EVALUATION
# ---------------------------

test_df = pd.read_csv('NFDB_enriched_population/fire_data_2016enriched4.csv')

for var in required_vars:
    test_df = test_df[test_df[var] != -1]

test_df = test_df[test_df["CAUSE"] != "U"]

test_df['fire_class'] = test_df.apply(assign_label, axis=1)

X_test = test_df[attributes]
y_test = test_df['fire_class']

# Evaluate test data
probs = model.predict_proba(X_test)
preds = np.argmax(probs, axis=1)
auc_test = roc_auc_score(pd.get_dummies(y_test), probs, multi_class='ovo')

print("\nTEST METRICS")
print("Test AUC (multiclass OVO):", auc_test)
print("\nClassification Report:\n", classification_report(y_test, preds))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, preds))

# ---------------------------
# PLOTTING
# ---------------------------

# Model AUC plotting
plt.figure(figsize=(7,6))
ax = plt.gca()
for class_id, class_name in label_map.items():
    # Binarize true labels for this class (one-vs-rest)
    y_binary = (y_test == class_id).astype(int)
    # Probabilities for this class
    y_scores = probs[:, class_id]
    # Compute ROC
    fpr, tpr, _ = roc_curve(y_binary, y_scores)
    roc_auc = auc(fpr, tpr)
    ax.plot(fpr, tpr, label=f"{class_name} (AUC={roc_auc:.3f})", linewidth=2)

# Add random guess line
ax.plot([0,1],[0,1],'--',color='gray')

ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("One-vs-Rest ROC Curves (Multiclass)")
ax.legend(loc="lower right")
ax.grid(True, linestyle="--", alpha=0.4)
plt.show()

# Calibration curve plotting
plt.figure(figsize=(7,6))
for i, name in label_map.items():
    y_bin = (y_test == i).astype(int)
    prob_true, prob_pred = calibration_curve(y_bin, probs[:, i], n_bins=10)
    plt.plot(prob_pred, prob_true, marker='o', label=name)

plt.plot([0,1],[0,1],'--',color='gray')
plt.xlabel("Predicted Probability")
plt.ylabel("Observed Frequency")
plt.title("Calibration Curves")
plt.legend()
plt.show()

plot_importance(model, max_num_features=20)
plt.title("XGBoost Feature Importance")
plt.show()

# Precision-recall plotting
plt.figure(figsize=(7,6))
for class_id, class_name in label_map.items():
    # Binary indicator for this class
    y_binary = (y_test == class_id).astype(int)
    # Model probabilities for this specific class
    y_scores = probs[:, class_id]
    precision, recall, _ = precision_recall_curve(y_binary, y_scores)
    # Compute Average Precision score (area under PR curve)
    ap = average_precision_score(y_binary, y_scores)
    plt.plot(recall, precision, label=f"{class_name} (AP={ap:.3f})")

plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-Recall Curves (One-vs-Rest)")
plt.legend(loc="lower left")
plt.grid(True, linestyle="--", alpha=0.4)
plt.show()

# ---------------------------
# UNLABELED DATA
# ---------------------------

unlabeled_df = all_data

for var in required_vars:
    unlabeled_df = unlabeled_df[unlabeled_df[var] != -1]

unlabeled_df = unlabeled_df[unlabeled_df["CAUSE"] == "U"]

X_unlabeled = unlabeled_df[attributes]

# Evaluate unlabeled data
probs = model.predict_proba(X_unlabeled)
preds = model.predict(X_unlabeled)

# Output predictions
unlabeled_df["Predicted_Class"] = preds
unlabeled_df["Confidence_Score"] = probs.max(axis=1)

# Count predictions and score mean confidence
class_counts = unlabeled_df["Predicted_Class"].value_counts().sort_index()
for cls, count in class_counts.items():
    print(f"Class {cls} ({label_map.get(cls, 'Unknown')}): {count}")

    idx = np.where(preds == cls)[0]
    conf = probs[idx, cls]
    print(f"Class {cls} average confidence: {conf.mean()}")

print("\nTotal classified fires:", len(unlabeled_df))

unlabeled_df.to_csv("classified_unknown_fire_causes.csv", index=False)