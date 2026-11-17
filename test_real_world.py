from combined_detector import analyze_combined


# 1 = SCAM, 0 = GENUINE
test_cases = [

    # SCAM MESSAGES
    ("Tell me your OTP to verify your bank account", 1),
    ("Your bank account will be blocked. Send OTP immediately", 1),
    ("You won a lottery. Click here to claim your prize", 1),
    ("Aap lottery jeet gaye hain, abhi claim karein", 1),
    ("Aapko cashback mila hai. Claim now", 1),
    ("Share your UPI PIN to receive your refund", 1),
    ("Your KYC is blocked. Update details using this link", 1),
    ("Pay registration fee to confirm your job offer", 1),
    ("Your electricity connection will be disconnected. Pay now", 1),
    ("Send your password immediately for account verification", 1),
    ("Congratulations! You won Rs 50000. Claim your reward now", 1),
    ("Your parcel is on hold. Pay customs fee using this link", 1),
    ("Install this app and share your screen to receive payment", 1),
    ("Your bank account is suspended. Verify your OTP now", 1),
    ("Aapka account band ho jayega, apna OTP bhejo", 1),

    # GENUINE MESSAGES
    ("Your salary has been credited to your bank account", 0),
    ("Your electricity bill payment was successful", 0),
    ("Your UPI transaction of Rs 500 was successful", 0),
    ("Your order has been shipped and is on the way", 0),
    ("Your appointment is confirmed for tomorrow", 0),
    ("Never share your OTP or PIN with anyone", 0),
    ("Your bank statement is ready to download", 0),
    ("Your monthly account balance is available", 0),
    ("Thank you for making your payment on time", 0),
    ("Your refund has been processed successfully", 0),
    ("Do not share your password with anyone", 0),
    ("Your insurance premium payment was received", 0),
    ("Your mobile recharge was successful", 0),
    ("Your KYC documents have been successfully verified", 0),
    ("Aapka bank account mein salary credit ho gayi hai", 0)
]


def main():

    total = len(test_cases)

    strict_tp = 0
    strict_fp = 0
    strict_tn = 0
    strict_fn = 0

    flagged_tp = 0
    flagged_fp = 0
    flagged_tn = 0
    flagged_fn = 0

    caution_count = 0
    errors = 0

    print("\n========== REAL-WORLD TESTING ==========")
    print("Total test messages:", total)

    for index, (message, expected) in enumerate(test_cases, start=1):

        try:
            result = analyze_combined(message)

            decision = result["final_decision"]

            # Strict prediction: only SCAM counts as positive
            strict_prediction = 1 if decision == "SCAM" else 0

            # Safety prediction: SCAM and NEEDS CAUTION are flagged
            flagged_prediction = (
                0 if decision == "GENUINE" else 1
            )

            if decision == "NEEDS CAUTION":
                caution_count += 1

            # Strict confusion matrix
            if expected == 1 and strict_prediction == 1:
                strict_tp += 1
            elif expected == 0 and strict_prediction == 1:
                strict_fp += 1
            elif expected == 0 and strict_prediction == 0:
                strict_tn += 1
            else:
                strict_fn += 1

            # Flagged confusion matrix
            if expected == 1 and flagged_prediction == 1:
                flagged_tp += 1
            elif expected == 0 and flagged_prediction == 1:
                flagged_fp += 1
            elif expected == 0 and flagged_prediction == 0:
                flagged_tn += 1
            else:
                flagged_fn += 1

            status = (
                "PASS"
                if strict_prediction == expected
                else "CHECK"
            )

            expected_name = "SCAM" if expected == 1 else "GENUINE"

            print("\nTest:", index, "-", status)
            print("Message:", message)
            print("Expected:", expected_name)
            print("Actual:", decision)
            print("Risk Score:", result["final_score"])
            print("Risk Level:", result["risk_level"])

        except Exception as error:
            errors += 1
            print("\nTest:", index, "- ERROR")
            print("Message:", message)
            print("Error:", error)

    # Calculate metrics
    completed = total - errors

    strict_accuracy = (
        (strict_tp + strict_tn) / completed * 100
        if completed else 0
    )

    flagged_accuracy = (
        (flagged_tp + flagged_tn) / completed * 100
        if completed else 0
    )

    scam_precision = (
        strict_tp / (strict_tp + strict_fp) * 100
        if (strict_tp + strict_fp) else 0
    )

    scam_recall = (
        strict_tp / (strict_tp + strict_fn) * 100
        if (strict_tp + strict_fn) else 0
    )

    print("\n========== FINAL SUMMARY ==========")
    print("Total tests:", total)
    print("Completed:", completed)
    print("Errors:", errors)
    print("Needs Caution decisions:", caution_count)

    print("\nSTRICT SCAM DECISION")
    print("Accuracy:", round(strict_accuracy, 2), "%")
    print("Scam Precision:", round(scam_precision, 2), "%")
    print("Scam Recall:", round(scam_recall, 2), "%")
    print("True Positives:", strict_tp)
    print("False Positives:", strict_fp)
    print("True Negatives:", strict_tn)
    print("False Negatives:", strict_fn)

    print("\nSAFETY FLAGGING (SCAM + CAUTION)")
    print("Accuracy:", round(flagged_accuracy, 2), "%")
    print("Flagged True Positives:", flagged_tp)
    print("Flagged False Positives:", flagged_fp)
    print("Flagged True Negatives:", flagged_tn)
    print("Flagged False Negatives:", flagged_fn)

    print("\n========== TESTING COMPLETED ==========")


if __name__ == "__main__":
    main()