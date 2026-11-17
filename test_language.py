from language_support import normalize_hindi_message
from combined_detector import analyze_combined

test_messages = [
    "आपका बैंक खाता बंद हो जाएगा, तुरंत OTP भेजें",
    "आपने लॉटरी जीती है, इनाम पाने के लिए क्लिक करें",
    "अपना पासवर्ड और पिन भेजें",
    "Aap lottery jeet gaye hain, abhi claim karein",
    "Share your OTP to receive free reward",
    "Aapka bank account band ho jayega",
    "Apna OTP bhejo",
    "Aap lottery jeet gaye hain",
    "Turant payment karo",
    "Aapka KYC update nahi hua",
    "Mujhe apna OTP batao",
    "KYC update karne ke liye link kholo",
    "Aapko cashback mila hai claim karo",
    "Bijli connection kat jayega, bill bharo",
    "Aapka account suspend ho jayega, abhi verify karo"
]

for message in test_messages:

    normalized = normalize_hindi_message(message)

    result = analyze_combined(normalized)

    print("\nOriginal Message:", message)
    print("Normalized Message:", normalized)

    print(
        "AI Prediction:",
        "SCAM" if result["ml_prediction"] == 1
        else "GENUINE"
    )

    print("Risk Score:", result["final_score"])
    print("Risk Level:", result["risk_level"])
    print("-" * 40)