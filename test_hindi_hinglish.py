from combined_detector import analyze_combined
from language_support import normalize_hindi_message


# Expected label:
# 1 = Suspicious / should be flagged
# 0 = Genuine / should not be flagged

test_cases = [

    # HINDI SCAM MESSAGES
    ("आपका बैंक खाता बंद हो जाएगा, तुरंत OTP भेजें", 1),
    ("मुझे अपना OTP बताओ", 1),
    ("आपने लॉटरी जीती है, इनाम पाने के लिए क्लिक करें", 1),
    ("अपना पासवर्ड और पिन भेजें", 1),
    ("बिजली कनेक्शन कट जाएगा, अभी बिल भरो", 1),

    # HINGLISH SCAM MESSAGES
    ("Aap lottery jeet gaye hain, abhi claim karein", 1),
    ("Aapka bank account band ho jayega, OTP bhejo", 1),
    ("Mujhe apna OTP batao", 1),
    ("Bijli connection kat jayega, bill bharo", 1),
    ("Aapko cashback mila hai, claim karo", 1),

    # MIXED LANGUAGE SCAM MESSAGES
    ("Aapka KYC blocked hai, update details using this link", 1),
    ("Aapka parcel rok diya gaya hai, delivery fee do", 1),
    ("Screen share karo payment receive karne ke liye", 1),
    ("Install this app aur payment receive karo", 1),
    ("Your account band ho jayega, send OTP now", 1),

    # HINDI GENUINE MESSAGES
    ("आपका वेतन आपके बैंक खाते में जमा हो गया है", 0),
    ("आपका बिजली बिल सफलतापूर्वक जमा हो गया है", 0),
    ("आपका मोबाइल रिचार्ज सफल रहा", 0),

    # HINGLISH GENUINE MESSAGES
    ("Aapka salary bank account mein credit ho gaya hai", 0),
    ("Aapka payment successfully complete ho gaya hai", 0),
    ("Aapka mobile recharge successful ho gaya hai", 0),
    ("Aapka order dispatch ho gaya hai", 0),

    # SAFETY / AWARENESS MESSAGES
    ("अपना OTP किसी के साथ साझा न करें", 0),
    ("Never share your OTP kisi ke saath", 0),
    ("Apna password kisi ko mat batana", 0)
]


def main():

    total = len(test_cases)

    passed = 0
    failed = 0
    errors = 0

    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0

    print("\n========== HINDI / HINGLISH TESTING ==========")
    print("Total test messages:", total)

    for index, (message, expected) in enumerate(test_cases, 1):

        try:

            normalized = normalize_hindi_message(message)

            result = analyze_combined(message)

            decision = result["final_decision"]

            # SCAM and NEEDS CAUTION both count as flagged
            actual = 0 if decision == "GENUINE" else 1

            if actual == expected:
                passed += 1
                status = "PASS"
            else:
                failed += 1
                status = "CHECK"

            if expected == 1 and actual == 1:
                true_positive += 1

            elif expected == 0 and actual == 1:
                false_positive += 1

            elif expected == 0 and actual == 0:
                true_negative += 1

            else:
                false_negative += 1

            expected_name = (
                "FLAGGED" if expected == 1 else "GENUINE"
            )

            print("\nTest:", index, "-", status)
            print("Original:", message)
            print("Normalized:", normalized)
            print("Expected:", expected_name)
            print("Actual:", decision)
            print("Risk Score:", result["final_score"])
            print("Risk Level:", result["risk_level"])
            print("Category:", result["scam_category"])

            if result["reasons"]:
                print("Reasons:", result["reasons"])

        except Exception as error:

            errors += 1

            print("\nTest:", index, "- ERROR")
            print("Original:", message)
            print("Error:", error)

    completed = total - errors

    accuracy = (
        (passed / completed) * 100
        if completed else 0
    )

    scam_recall = (
        true_positive / (true_positive + false_negative) * 100
        if (true_positive + false_negative) else 0
    )

    genuine_specificity = (
        true_negative / (true_negative + false_positive) * 100
        if (true_negative + false_positive) else 0
    )

    print("\n========== FINAL SUMMARY ==========")

    print("Total tests:", total)
    print("Completed:", completed)
    print("Passed:", passed)
    print("Need Review:", failed)
    print("Errors:", errors)

    print("\nSAFETY FLAGGING METRICS")
    print("Accuracy:", round(accuracy, 2), "%")
    print("Scam Recall:", round(scam_recall, 2), "%")
    print("Genuine Specificity:", round(genuine_specificity, 2), "%")

    print("\nTrue Positives:", true_positive)
    print("False Positives:", false_positive)
    print("True Negatives:", true_negative)
    print("False Negatives:", false_negative)

    print("\n========== TESTING COMPLETED ==========")


if __name__ == "__main__":
    main()