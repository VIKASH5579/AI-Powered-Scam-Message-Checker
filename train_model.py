import os
import shutil
from datetime import datetime

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support
)


# --------------------------------
# STEP 1: LOAD AND CLEAN DATASET
# --------------------------------

DATASET_PATH = "dataset/combined_messages.csv"
MODEL_PATH = "models/scam_model.pkl"
REPORT_PATH = "reports/model_evaluation.txt"

os.makedirs("models", exist_ok=True)
os.makedirs("reports", exist_ok=True)

df = pd.read_csv(DATASET_PATH)

df = df.dropna(subset=["message", "label"]).copy()
df["message"] = df["message"].astype(str).str.strip()
df["label"] = df["label"].astype(int)

# Keep only valid labels
df = df[df["label"].isin([0, 1])]

# Remove duplicate messages before splitting
df["_duplicate_key"] = (
    df["message"].str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
)

df = df.drop_duplicates(
    subset=["_duplicate_key"],
    keep="first"
)

df = df.drop(columns=["_duplicate_key"])

X = df["message"]
y = df["label"]

print("DATASET SUMMARY")
print("-----------------------")
print("Total messages:", len(df))
print("Genuine messages:", int((y == 0).sum()))
print("Scam messages:", int((y == 1).sum()))


# --------------------------------
# STEP 2: TRAIN / VALIDATION / TEST
# --------------------------------

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

X_validation, X_test, y_validation, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp
)

print("\nDATA SPLIT")
print("-----------------------")
print("Training:", len(X_train))
print("Validation:", len(X_validation))
print("Testing:", len(X_test))


# --------------------------------
# STEP 3: CREATE MODEL PIPELINE
# --------------------------------

def create_model(class_weight):

    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=20000,
            sublinear_tf=True
        )),
        ("classifier", LogisticRegression(
            max_iter=1000,
            class_weight=class_weight
        ))
    ])


# --------------------------------
# STEP 4: COMPARE TWO MODELS
# --------------------------------

models = {
    "BASELINE": create_model(None),
    "BALANCED": create_model("balanced")
}

results = {}

print("\nMODEL COMPARISON")
print("-----------------------")

for name, candidate in models.items():

    print("\nTraining", name, "model...")

    candidate.fit(X_train, y_train)

    predictions = candidate.predict(X_validation)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_validation,
        predictions,
        labels=[1],
        zero_division=0
    )

    accuracy = accuracy_score(y_validation, predictions)

    results[name] = {
        "model": candidate,
        "accuracy": accuracy,
        "precision": precision[0],
        "recall": recall[0],
        "f1": f1[0]
    }

    print("\n", name)
    print("Accuracy:", round(accuracy * 100, 2), "%")
    print("Scam Precision:", round(precision[0], 4))
    print("Scam Recall:", round(recall[0], 4))
    print("Scam F1:", round(f1[0], 4))


# --------------------------------
# STEP 5: SELECT BEST MODEL
# --------------------------------

best_name = max(
    results,
    key=lambda name: (
        results[name]["f1"],
        results[name]["precision"],
        results[name]["recall"]
    )
)

print("\nSELECTED MODEL:", best_name)


# --------------------------------
# STEP 6: RETRAIN ON TRAIN + VALIDATION
# --------------------------------

X_final_train = pd.concat([X_train, X_validation])
y_final_train = pd.concat([y_train, y_validation])

best_model = create_model(
    None if best_name == "BASELINE" else "balanced"
)

print("\nTraining selected model on combined training data...")

best_model.fit(X_final_train, y_final_train)


# --------------------------------
# STEP 7: FINAL TEST EVALUATION
# --------------------------------

test_predictions = best_model.predict(X_test)

accuracy = accuracy_score(y_test, test_predictions)

report = classification_report(
    y_test,
    test_predictions,
    target_names=["GENUINE", "SCAM"],
    zero_division=0
)

matrix = confusion_matrix(
    y_test,
    test_predictions,
    labels=[0, 1]
)

print("\nFINAL MODEL EVALUATION")
print("-----------------------")
print("Selected Model:", best_name)
print("Training Messages:", len(X_final_train))
print("Testing Messages:", len(X_test))
print("Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(report)

print("Confusion Matrix:")
print(matrix)


# --------------------------------
# STEP 8: BACKUP OLD MODEL
# --------------------------------

if os.path.exists(MODEL_PATH):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_path = f"models/scam_model_backup_{timestamp}.pkl"

    shutil.copy2(MODEL_PATH, backup_path)

    print("\nOld model backup created:")
    print(backup_path)


# --------------------------------
# STEP 9: SAVE NEW MODEL
# --------------------------------

joblib.dump(best_model, MODEL_PATH)

print("\nNew model saved successfully!")
print("Location:", MODEL_PATH)


# --------------------------------
# STEP 10: SAVE EVALUATION REPORT
# --------------------------------

with open(REPORT_PATH, "w", encoding="utf-8") as file:

    file.write("SCAM DETECTOR MODEL EVALUATION\n")
    file.write("==============================\n\n")

    file.write(f"Dataset messages: {len(df)}\n")
    file.write(f"Selected model: {best_name}\n")
    file.write(f"Training messages: {len(X_final_train)}\n")
    file.write(f"Testing messages: {len(X_test)}\n")
    file.write(f"Accuracy: {accuracy * 100:.2f}%\n\n")

    file.write("Classification Report:\n")
    file.write(report)

    file.write("\nConfusion Matrix:\n")
    file.write(str(matrix))

print("\nEvaluation report saved:")
print(REPORT_PATH)

print("\nTRAINING COMPLETED!")