from combined_detector import analyze_combined
from database import save_analysis

messages = [
    "Aapko Rs5000 cashback mila hai. Claim now.",
    "Your salary has been credited to your bank account.",
    "Share your OTP to receive free reward.",
    "Your UPI payment was successful."
]

for message in messages:

    print("\nMESSAGE:", message)

    result = analyze_combined(message)

    print("AI Prediction:", result["ml_prediction"])
    print("Risk Score:", result["final_score"])
    print("Risk Level:", result["risk_level"])
    print("Scam Category:", result["scam_category"])

    analysis_id = save_analysis(
        "test",
        message,
        result
    )

    print("Database Analysis ID:", analysis_id)