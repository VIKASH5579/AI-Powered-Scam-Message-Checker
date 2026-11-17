import zipfile
import pandas as pd
from pathlib import Path

zip_path = Path("dataset/uci_sms.zip")
output_path = Path("dataset/uci_sms.csv")

with zipfile.ZipFile(zip_path, "r") as archive:
    files = [
        name for name in archive.namelist()
        if name.endswith("SMSSpamCollection")
    ]

    if not files:
        raise FileNotFoundError("SMS dataset not found in ZIP")

    with archive.open(files[0]) as file:
        df = pd.read_csv(
            file,
            sep="\t",
            header=None,
            names=["label", "message"],
            encoding="utf-8"
        )

df["label"] = df["label"].map({
    "ham": 0,
    "spam": 1
})

df = df.dropna()
df = df.drop_duplicates(subset=["message"])
df = df[["message", "label"]]

df.to_csv(output_path, index=False)

print("Dataset imported successfully!")
print("Total messages:", len(df))
print("\nLabel counts:")
print(df["label"].value_counts())
print("\nSaved to:", output_path)