from scam_detector import extract_text_from_image
from combined_detector import analyze_combined

image_path = input("Enter screenshot image path: ")

text = extract_text_from_image(image_path)

print("\nEXTRACTED TEXT:")
print(text)

if text:
    print("\nSCAM ANALYSIS REPORT")
    print("--------------------")

    result = analyze_combined(text)

    print("Rule Score:", result["rule_score"], "/100")
    print("AI Scam Score:", result["ml_score"], "%")
    print("AI Prediction:", "SCAM" if result["ml_prediction"] == 1 else "GENUINE")
    print("Final Risk Score:", result["final_score"], "/100")
    print("Risk Level:", result["risk_level"])

    print("\nReasons:")
    for reason in result["reasons"]:
        print("-", reason)

else:
    print("No text detected in screenshot.")