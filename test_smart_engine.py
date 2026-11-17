from combined_detector import analyze_combined

test_messages = [
    ("Tell me your OTP", "SCAM"),
    ("Share your UPI PIN", "SCAM"),
    ("Never share your OTP with anyone", "GENUINE"),
    ("Your salary has been credited", "GENUINE"),
    ("Share your OTP to receive free reward", "SCAM"),
    ("Your bank account will be blocked. Send OTP", "SCAM"),
    ("Aap lottery jeet gaye hain, abhi claim karein", "SCAM"),
    ("Aapko cashback mila hai claim karo", "NEEDS CAUTION"),
    ("Your electricity bill is due. Please pay", "GENUINE"),
    ("Your account will be suspended, verify now", "NEEDS CAUTION"),
    ("You won a lottery, click here to claim", "SCAM"),
    ("Your KYC update is pending", "NEEDS CAUTION"),
    ("Do not share your password with anyone", "GENUINE"),
    ("Your bank account has been credited with salary", "GENUINE"),
    ("Send your password immediately", "SCAM")
]

passed = 0

print("\n========== SMART ENGINE TEST ==========\n")

for message, expected in test_messages:

    result = analyze_combined(message)

    actual = result["final_decision"]

    status = "PASS" if actual == expected else "CHECK"

    if status == "PASS":
        passed += 1

    print("Message:", message)
    print("Expected:", expected)
    print("Actual:", actual)
    print("Risk Score:", result["final_score"])
    print("Status:", status)
    print("--------------------------------------")

print("\nTEST SUMMARY")
print("Total Tests:", len(test_messages))
print("Passed:", passed)
print("Need Review:", len(test_messages) - passed)
print("======================================")