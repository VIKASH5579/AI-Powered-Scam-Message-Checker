import pandas as pd

old_df = pd.read_csv("dataset/combined_messages.csv")
scam_df = pd.read_csv("dataset/indian_scam_messages.csv")
genuine_df = pd.read_csv("dataset/indian_genuine_messages.csv")

combined_df = pd.concat(
    [old_df, scam_df, genuine_df],
    ignore_index=True
)

combined_df = combined_df.drop_duplicates(
    subset=["message"]
)

combined_df.to_csv(
    "dataset/combined_messages.csv",
    index=False
)

print("Indian datasets added successfully!")
print(combined_df["label"].value_counts())
print("Total messages:", len(combined_df))