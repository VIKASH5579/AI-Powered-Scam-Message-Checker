import pandas as pd

public_data = pd.read_csv("dataset/uci_sms.csv")
original_data = pd.read_csv("dataset/scam_messages.csv")

combined = pd.concat(
    [public_data, original_data],
    ignore_index=True
)

combined["message"] = (
    combined["message"].astype(str).str.strip()
)

combined["label"] = pd.to_numeric(
    combined["label"], errors="coerce"
)

combined = combined.dropna()
combined = combined[combined["label"].isin([0, 1])]
combined = combined.drop_duplicates(
    subset=["message"]
)

combined.to_csv(
    "dataset/combined_messages.csv",
    index=False
)

print("Combined dataset ready!")
print("Total messages:", len(combined))
print(combined["label"].value_counts())