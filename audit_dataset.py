import pandas as pd

FILE_PATH = "dataset/combined_messages.csv"

df = pd.read_csv(FILE_PATH)

print("\n========== DATASET QUALITY AUDIT ==========\n")

required_columns = ["message", "label"]

if not all(col in df.columns for col in required_columns):
    raise ValueError("Dataset must contain message and label columns.")

print("Total messages:", len(df))

print("\nMissing values:")
print(df[required_columns].isnull().sum())

df = df.dropna(subset=required_columns).copy()

df["message"] = df["message"].astype(str).str.strip()
df["label"] = pd.to_numeric(df["label"], errors="coerce")

df = df.dropna(subset=["label"])

print("\nLabel distribution:")
print(df["label"].value_counts().sort_index())

print("\nClass percentages:")
print(
    (df["label"].value_counts(normalize=True) * 100)
    .round(2)
)

df["normalized_message"] = (
    df["message"].str.lower().str.strip()
)

print("\nExact duplicate rows:", df.duplicated(
    subset=["normalized_message", "label"]
).sum())

print("Duplicate messages:", df.duplicated(
    subset=["normalized_message"]
).sum())

# Find same message with conflicting labels
conflicts = (
    df.groupby("normalized_message")["label"]
    .nunique()
)

conflicts = conflicts[conflicts > 1]

print("\nConflicting messages:", len(conflicts))

if len(conflicts) > 0:
    print("\nExamples of conflicting messages:")

    for message in conflicts.index[:10]:
        print("\nMessage:", message)

        print(
            df[df["normalized_message"] == message][
                ["message", "label"]
            ].to_string(index=False)
        )

print("\nMessage length statistics:")
print(df["message"].str.len().describe())

print("\n========== AUDIT COMPLETED ==========")