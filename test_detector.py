from scam_detector import analyze_message

message = "Congratulations! You won a lottery."

result = analyze_message(message)

print("Risk Score:", result["risk_score"])
print("Risk Level:", result["risk_level"])
print("Detected Keywords:", result["keywords"])