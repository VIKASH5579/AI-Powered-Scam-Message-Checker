import joblib

# Trained model load karo
model = joblib.load("models/scam_model.pkl")

print("AI SCAM MESSAGE CHECKER")
print("-----------------------")

# User se message lo
message = input("Enter a message: ")

# AI prediction
prediction = model.predict([message])[0]

# Result show karo
if prediction == 1:
    print("\nAI Prediction: SCAM MESSAGE")
else:
    print("\nAI Prediction: GENUINE MESSAGE")