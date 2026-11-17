import pandas as pd

# Original dataset load karo
data = pd.read_csv("dataset/scam_messages.csv")

print("Original Dataset:", len(data))

# Empty messages remove karo
data = data.dropna(subset=["message", "label"])

# Extra spaces remove karo
data["message"] = data["message"].astype(str).str.strip()

# Empty messages remove karo
data = data[data["message"] != ""]

# Duplicate messages remove karo
data = data.drop_duplicates(subset=["message"])

# Sirf valid labels rakho: 0 aur 1
data = data[data["label"].isin([0, 1])]

# Clean dataset save karo
data.to_csv("dataset/cleaned_scam_messages.csv", index=False)

print("\nCleaned Dataset:", len(data))
print("\nLabel Counts:")
print(data["label"].value_counts())

print("\nClean dataset saved successfully!")