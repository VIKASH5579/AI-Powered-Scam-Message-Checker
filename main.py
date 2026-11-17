import pandas as pd

print("====================================")
print(" AI-POWERED SCAM MESSAGE CHECKER")
print("====================================")

# Dataset load karo
data = pd.read_csv("dataset/scam_messages.csv")

print("\nFirst 5 Messages:")
print(data.head())

print("\nTotal Messages:", len(data))

print("\nMessage Categories:")
print(data["label"].value_counts())

print("\nMissing Values:")
print(data.isnull().sum())

print("\nDataset checking completed!")